import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd

# =====================================================================
# 1. SEUS CAMINHOS REAIS (Verifique a extensão do .json)
# =====================================================================
CAMINHO_CREDENCIAIS = r"C:\Users\Desktop\Documents\FAI-Persona Digital - Traballho Josenyr\credenciais.json.json"
CAMINHO_PLANILHA = r"C:\Users\Desktop\Documents\FAI-Persona Digital - Traballho Josenyr\Cadastro_Alunos_FATEC.csv"
CAMINHO_OUTRA_PLANILHA = r"C:\Users\Desktop\Documents\FAI-Persona Digital - Traballho Josenyr\Horario_Aulas_FATEC.csv"
# =====================================================================
# 2. Autenticar no Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(CAMINHO_CREDENCIAIS)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# =====================================================================
# ETAPA A: IMPORTAÇÃO DOS ALUNOS
# =====================================================================
print("--- Lendo Planilha de Alunos ---")
df_alunos = pd.read_csv(CAMINHO_PLANILHA, sep=";")
print(f"Sucesso! Linhas para importar (Alunos): {len(df_alunos)}")

for index, row in df_alunos.iterrows():
    dados_aluno = {
        "nome": row["Nome do Aluno"],
        "email": row["E-mail Institucional"],
        "curso": row["Curso"],
        "turno": row["Turno"],
        "situacao": row["Situacao"]
    }
    
    ra_id = str(row["RA"])
    
    # Envia para a coleção 'alunos' usando o RA como ID
    db.collection("alunos").document(ra_id).set(dados_aluno)
    print(f"-> Aluno {row['Nome do Aluno']} (RA: {ra_id}) enviado!")

print("🎉 Importação de alunos concluída com sucesso!\n")

# =====================================================================
# ETAPA B: IMPORTAÇÃO DOS HORÁRIOS (MAPEADO COM A PLANILHA REAL)
# =====================================================================
print("--- Lendo Planilha de Horários ---")
# O separador é o ponto e vírgula (;) e vamos usar o encoding correto para os acentos
df_horarios = pd.read_csv(CAMINHO_OUTRA_PLANILHA, sep=";", encoding="utf-8")
print(f"Sucesso! Linhas para importar (Horários): {len(df_horarios)}")

for index, row in df_horarios.iterrows():
    # Mapeando exatamente as colunas reais do seu arquivo CSV
    dados_horario = {
        "curso": "Análise e Desenvolvimento de Sistemas", 
        "ciclo": 1,                                        
        "dia_semana": row["Dia da Semana"],
        "codigo_materia": row["Codigo"],
        "materia": row["Disciplina"],
        "professor": row["Professor"],
        "horario_aula": row["Horario"],
        "sala": "A definir"                                
    }
    
    # Criando um ID de documento único para cada bloco de horário usando o index do loop
    id_documento = f"ads_1c_{row['Dia da Semana']}_{index}".replace(" ", "_").lower()
    
    # Envia para a coleção 'horarios' no Firebase
    db.collection("horarios").document(id_documento).set(dados_horario)
    print(f"-> Horário de {row['Disciplina']} ({row['Horario']}) importado!")

print("\n🚀 Tudo pronto! Ambas as planilhas estão seguras no Firebase.")