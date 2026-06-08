import streamlit as st
import requests
import time
import os


# Garante que os caminhos das imagens sejam lidos corretamente independente da pasta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(BASE_DIR, filename)

fai_status_idle = get_path("WhatsApp_Image_2026-05-17_at_15.34.09-removebg-preview.png")
fai_status_thinking = get_path("1.pensando-removebg-preview.png")
fai_status_talking = get_path("Gemini_Generated_Image_eopgh7eopgh7eopg.png")
logo_fatec_path = get_path("fatec-identidade.webp")

st.set_page_config(page_title="Secretaria FAI", page_icon=logo_fatec_path, layout="wide")


def obter_avatar(caminho_imagem, emoji_padrao):
    return caminho_imagem if os.path.exists(caminho_imagem) else emoji_padrao


with st.sidebar:
    st.image(obter_avatar(fai_status_idle, "🤖"), caption="FAI - Online", width=150)
    st.header("Seus Dados")
    nome = st.text_input("Nome Completo:")
    email = st.text_input("E-mail Institucional:")
    
    st.divider()
    fatec_selecionada = st.selectbox("Unidade:", ["Zona Sul", "Zona Leste", "Ipiranga", "Baixada Santista"])
    curso_selecionado = st.selectbox("Curso:", ["ADS", "Segurança da Informação", "Redes", "Gestão de TI"])


col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    if os.path.exists(logo_fatec_path):
        st.image(logo_fatec_path, width=150)
with col_titulo:
    st.title("Atendimento Virtual - FAI")
    st.caption("Secretaria Digital | FATEC Zona Sul")

if "lista_mensagens" not in st.session_state:
    st.session_state["lista_mensagens"] = []

for msg in st.session_state["lista_mensagens"]:
    avatar = obter_avatar(fai_status_idle, "🤖") if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

pergunta_usuario = st.chat_input("Digite sua dúvida...")

if pergunta_usuario:
    if not nome or not email:
        st.warning("Preencha Nome e E-mail na barra lateral!")
    else:
        st.session_state["lista_mensagens"].append({"role": "user", "content": pergunta_usuario})
        with st.chat_message("user", avatar="👤"):
            st.write(pergunta_usuario)
        
        
        with st.chat_message("assistant", avatar=obter_avatar(fai_status_thinking, "🤖")):
            with st.spinner("FAI processando..."):
                try:
                    payload = {
                        "session_id": "sessao_fai_caio", 
                        "user_email": email, 
                        "user_name": nome, 
                        "message": pergunta_usuario,
                        "unidade": fatec_selecionada,
                        "curso": curso_selecionado
                    }
                   
                    res = requests.post("https://caiotiago52.app.n8n.cloud/webhook/Fai-ChatBot", json=payload, timeout=60)
                    res.raise_for_status() 
                    texto_ia = res.text
                except requests.exceptions.Timeout:
                    texto_ia = "Desculpe, a FAI está demorando para acordar. Tente novamente em alguns segundos!"
                except Exception as e:
                    texto_ia = f"Erro de conexão: {str(e)}"

        
        with st.chat_message("assistant", avatar=obter_avatar(fai_status_talking, "🤖")):
            st.write(texto_ia)
            st.session_state["lista_mensagens"].append({"role": "assistant", "content": texto_ia})

