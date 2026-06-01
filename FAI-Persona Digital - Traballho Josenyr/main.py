import streamlit as st
import PIL.Image as Image
import requests
import time
import os

# --- CONFIGURAÇÃO DE CAMINHOS (PNG) ---
# DICA: Verifique se as extensões estão exatamente em minúsculo ou maiúsculo (.png / .PNG)
fai_status_idle = r"c:\Users\Desktop\Downloads\WhatsApp_Image_2026-05-17_at_15.34.09-removebg-preview.png"      
fai_status_thinking = r"c:\Users\Desktop\Downloads\1.pensando-removebg-preview.png" 
fai_status_talking = r"c:\Users\Desktop\Downloads\Gemini_Generated_Image_eopgh7eopgh7eopg.png"  
logo_fatec_path = r"c:\Users\Desktop\Downloads\fatec-identidade.webp"

st.set_page_config(page_title="Secretaria FAI", page_icon=r"c:\Users\Desktop\Downloads\fatec-identidade.webp")

# --- FUNÇÃO RESPONSÁVEL POR VERIFICAR SE O AVATAR EXISTE ---
def obter_avatar(caminho_imagem, emoji_padrao):
    # Se o arquivo existir no seu computador, usa a imagem. Se não, usa o emoji para não travar o site!
    if os.path.exists(caminho_imagem):
        return caminho_imagem
    return emoji_padrao

# --- BARRA LATERAL ---
with st.sidebar:
    avatar_lateral = obter_avatar(fai_status_idle, "🤖")
    st.image(avatar_lateral, caption="FAI - Online")
    st.header("Seus Dados")
    nome = st.text_input("Nome Completo:", placeholder="Digite seu nome completo")
    email = st.text_input("E-mail Institucional:", placeholder="Digite seu e-mail institucional")
    
    st.divider()
    unidades_fatec = ["Zona Sul", "Zona Leste", "Ipiranga", "Baixada Santista"]
    fatec_selecionada = st.selectbox("Unidade:", options=unidades_fatec)
    cursos = ["ADS", "Segurança da Informação", "Redes", "Gestão de TI"]
    curso_selecionado = st.selectbox("Curso:", options=cursos)
    
    st.divider()
    st.subheader("Anexar Documentos")
    arquivo = st.file_uploader("Enviar arquivo (+)", type=['pdf', 'png', 'jpg'])
    if arquivo:
        st.success(f"📎 {arquivo.name} pronto!")

# --- CABEÇALHO DA PÁGINA PRINCIPAL ---
col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    if os.path.exists(logo_fatec_path,):
        st.image(logo_fatec_path, width=800)
    else:
        st.write("🏫")  # Emoji de escola como fallback
with col_titulo:
    st.title("Atendimento Virtual - FAI")
    st.caption("Secretaria Digital | FATEC Zona Sul")

# --- HISTÓRICO DE MENSAGENS ---
if "lista_mensagens" not in st.session_state:
    st.session_state["lista_mensagens"] = []

# Mostra o histórico salvo
for msg in st.session_state["lista_mensagens"]:
    avatar_msg = obter_avatar(fai_status_idle, "🤖") if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar_msg):
        st.write(msg["content"])

# --- INPUT DO CHAT PRINCIPAL ---
pergunta_usuario = st.chat_input("Digite sua dúvida para a Secretaria...")

# --- LÓGICA DE PROCESSAMENTO CORRIGIDA ---
if pergunta_usuario:
    if not nome or not email:
        st.warning("Por favor, preencha o seu Nome e E-mail na barra lateral!")
    else:
        # 1. Envia a mensagem do usuário imediatamente
        with st.chat_message("user", avatar="👤"):
            st.write(pergunta_usuario)
        st.session_state["lista_mensagens"].append({"role": "user", "content": pergunta_usuario})
        
        texto_ia = ""
        sucesso = False

        # 2. Exibe o estado de "Pensando"
        avatar_thinking = obter_avatar(fai_status_thinking, "🤖")
        with st.chat_message("assistant", avatar=avatar_thinking):
            with st.spinner("FAI está verificando os registros..."):
                try:
                    # ADICIONADO: session_id para o nó de memória do n8n não quebrar
                    payload = {
                        "session_id": "sessao_fai_caio", # ID estável para a memória do sub-node
                        "user_email": email, 
                        "user_name": nome, 
                        "message": pergunta_usuario,
                        "unidade": fatec_selecionada,
                        "curso": curso_selecionado
                    }
                    res = requests.post("http://localhost:5678/webhook/Fai-ChatBot", json=payload, timeout=30)
                    
                    if res.status_code == 200:
                        texto_ia = res.text
                        sucesso = True
                    else:
                        st.error(f"Erro na resposta da FAI (Código {res.status_code}).")
                except Exception as e:
                    st.error("Não foi possível conectar ao n8n. O servidor está ativo?")

        # 3. Exibe o estado de "Falando"
        if sucesso and texto_ia:
            avatar_talking = obter_avatar(fai_status_talking, "🤖")
            with st.chat_message("assistant", avatar=avatar_talking):
                placeholder = st.empty()
                full_res = ""
                for palavra in texto_ia.split(" "):
                    full_res += palavra + " "
                    placeholder.markdown(full_res + "▌")
                    time.sleep(0.03)
                placeholder.markdown(full_res)

            
            st.session_state["lista_mensagens"].append({"role": "assistant", "content": texto_ia})