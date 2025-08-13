# Importa as bibliotecas necessárias
import pandas as pd
import streamlit as st

# --- Configurações Iniciais ---
# Título da página no navegador e um layout mais amplo
st.set_page_config(
    page_title="Controle de Finanças Pessoais",
    layout="wide",
)

# --- Leitura e Processamento de Dados ---
# Define a receita mensal fixa
RECEITA_MENSAL = 3685.00

# Tenta carregar o arquivo CSV. Se não encontrar, exibe uma mensagem de erro.
try:
    df_gastos = pd.read_csv("gastos.csv")
except FileNotFoundError:
    st.error("Arquivo 'gastos.csv' não encontrado. Por favor, crie o arquivo e adicione os dados.")
    st.stop()

# --- Estrutura do Painel ---
st.title("💸 Controle de Finanças Pessoais")
st.markdown("---") # Linha divisória para separar o título do conteúdo

# Aqui é onde vamos adicionar a visualização dos dados
# e o restante da lógica do seu aplicativo.

# --- Exemplo simples (para você testar se está tudo funcionando) ---
st.header("Dados Brutos (para verificação)")
st.dataframe(df_gastos)

st.header("Soma dos gastos por banco")
gastos_por_banco = df_gastos.groupby("Banco")["Valor"].sum().reset_index()
st.dataframe(gastos_por_banco)
