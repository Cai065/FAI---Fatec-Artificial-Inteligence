import requests # Certifique-se de ter instalado (pip install requests)
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore

# 1. Inicializa o Firebase (Evita inicializar múltiplos apps no recarregamento do Streamlit)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Inicializa o estado de login
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_email = ""

# --- FUNÇÃO DE LOGIN ---
def tela_login():
    st.title("🔑 Acessar o Sistema")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        try:
            # O SDK Admin do Firebase não faz login direto com senha por questões de segurança de servidor.
            # No entanto, podemos verificar se o usuário existe para validar o fluxo de backend administrativo:
            user = auth.get_user_by_email(email)
            
            # NOTA: Em produção, para validar a SENHA no cliente com Firebase de forma nativa,
            # costuma-se usar requisições HTTP para a API REST do Firebase Identity Toolkit.
            # Para este exemplo simplificado de back-end:
            st.session_state.logado = True
            st.session_state.usuario_email = email
            st.success("Login realizado com sucesso!")
            st.rerun()
            
        except auth.UserNotFoundError:
            st.error("Usuário não encontrado. Crie uma conta.")
        except Exception as e:
            st.error(f"Erro ao fazer login: {e}")

# --- FUNÇÃO DE CADASTRO ---
def tela_cadastro():
    st.title("📝 Criar Nova Conta")
    nome = st.text_input("Nome Completo")
    email = st.text_input("E-mail para Cadastro")
    senha = st.text_input("Escolha uma Senha", type="password")
    curso = st.text_input("Seu Curso (Ex: ADS)")
    
    if st.button("Cadastrar Conta"):
        if not email or not senha or not nome:
            st.warning("Por favor, preencha os campos obrigatórios (Nome, E-mail e Senha).")
            return
            
        try:
            # 1. Cria o usuário no Firebase Authentication (Segurança de login)
            user = auth.create_user(
                email=email,
                password=senha,
                display_name=nome
            )
            
            # 2. Salva os dados adicionais no Firestore Database
            dados_usuario = {
                "nome": nome,
                "email": email,
                "curso": curso,
                "criado_em": firestore.SERVER_TIMESTAMP
            }
            # Usamos o e-mail como ID do documento para facilitar a busca depois
            db.collection("usuarios").document(email).set(dados_usuario)
            
            st.success("Conta criada com sucesso! Mude para a aba de Login para entrar.")
            
        except auth.EmailAlreadyExistsError:
            st.error("Este e-mail já está cadastrado.")
        except Exception as e:
            st.error(f"Erro ao criar conta: {e}")

# --- FLUXO PRINCIPAL DA APLICAÇÃO ---
if not st.session_state.logado:
    # Interface dividida em abas para Login e Cadastro
    aba_login, aba_cadastro = st.tabs(["Login", "Quero me Cadastrar"])
    
    with aba_login:
        tela_login()
        
    with aba_cadastro:
        tela_cadastro()
else:
    # --- ÁREA LOGADA (CONTEÚDO) ---
    st.sidebar.title(f"Olá, {st.session_state.usuario_email}")
    if st.sidebar.button("Sair/Logout"):
        st.session_state.logado = False
        st.session_state.usuario_email = ""
        st.rerun()
        
    st.title("🚀 Área Restrita")
    st.write("Se você está vendo isso, significa que passou pela autenticação do Firebase!")
    
    # Buscando dados adicionais do usuário logado direto do Firestore
    try:
        user_doc = db.collection("usuarios").document(st.session_state.usuario_email).get()
        if user_doc.exists:
            dados = user_doc.to_dict()
            st.info(f"Dados recuperados do Firestore: Nome: {dados.get('nome')} | Curso: {dados.get('curso')}")
    except Exception as e:
        st.error(f"Erro ao buscar dados adicionais: {e}")
# ... seu código anterior de cadastro ...
db.collection("usuarios").document(email).set(dados_usuario)

# --- ENVIO PARA O N8N ---
url_webhook_n8n = "http://localhost:5678/webhook-test/Fai-ChatBot"
dados_para_n8n = {
    "evento": "novo_cadastro",
    "nome": nome,
    "email": email,
    "curso": curso
}

try:
    # Dispara o gatilho em segundo plano para o n8n
    requests.post(url_webhook_n8n, json=dados_para_n8n)
except Exception as e:
    print(f"Erro ao avisar o n8n: {e}")
# ------------------------

st.success("Conta criada com sucesso!")