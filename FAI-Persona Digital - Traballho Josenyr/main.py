import streamlit as st
import PIL.Image as Image
import requests
import time
import os


fai_status_idle = r"WhatsApp_Image_2026-05-17_at_15.34.09-removebg-preview.png"      
fai_status_thinking = r"1.pensando-removebg-preview.png" 
fai_status_talking = r"Gemini_Generated_Image_eopgh7eopgh7eopg.png"  
logo_fatec_path = r"fatec-identidade.webp"

st.set_page_config(page_title="Secretaria FAI", page_icon=r"fatec-identidade.webp")

def obter_avatar(caminho_imagem, emoji_padrao):
    if os.path.exists(caminho_imagem):
        return caminho_imagem
    return emoji_padrao


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


col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    if os.path.exists(logo_fatec_path,):
        st.image(logo_fatec_path, width=800)
    else:
        st.write("A")  
with col_titulo:
    st.title("Atendimento Virtual - FAI")
    st.caption("Secretaria Digital | FATEC Zona Sul")


if "lista_mensagens" not in st.session_state:
    st.session_state["lista_mensagens"] = []


for msg in st.session_state["lista_mensagens"]:
    avatar_msg = obter_avatar(fai_status_idle, "🤖") if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar_msg):
        st.write(msg["content"])


pergunta_usuario = st.chat_input("Digite sua dúvida para a Secretaria...")

if pergunta_usuario:
    if not nome or not email:
        st.warning("Por favor, preencha o seu Nome e E-mail na barra lateral!")
    else:
    
        with st.chat_message("user", avatar="👤"):
            st.write(pergunta_usuario)
        st.session_state["lista_mensagens"].append({"role": "user", "content": pergunta_usuario})
        
        texto_ia = ""
        sucesso = False

      
        avatar_thinking = obter_avatar(fai_status_thinking, "🤖")
        with st.chat_message("assistant", avatar=avatar_thinking):
            with st.spinner("FAI está verificando os registros..."):
                try:
                    payload = {
                        "session_id": "sessao_fai_caio", 
                        "user_email": email, 
                        "user_name": nome, 
                        "message": pergunta_usuario,
                        "unidade": fatec_selecionada,
                        "curso": curso_selecionado
                    }
                    res = requests.post("https://caiotiago52.app.n8n.cloud/webhook/Fai-ChatBot", json=payload, timeout=30)
                    
                    if res.status_code == 200:
                        texto_ia = res.text
                        sucesso = True
                    else:
                        st.error(f"Erro na resposta da FAI (Código {res.status_code}).")
                except Exception as e:
                    st.error("Não foi possível conectar ao n8n. O servidor está ativo?")

        
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
