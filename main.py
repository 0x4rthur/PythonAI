import pandas as pd
import streamlit as st

# --- Configurações Iniciais ---
st.set_page_config(
    page_title="Controle de Finanças Pessoais",
    layout="wide",
)

# --- Leitura e Processamento de Dados ---
RECEITA_MENSAL = 3685.00

try:
    df_gastos = pd.read_csv("gastos_mensais.csv")
except FileNotFoundError:
    st.error("Arquivo 'gastos_mensais.csv' não encontrado. Por favor, verifique se o arquivo está na mesma pasta.")
    st.stop()

# --- Limpeza e Transformação dos Dados ---
# Remove a coluna 'Total' para que possamos recalcular
df_gastos = df_gastos.drop(columns=["Total"])

# Lista de colunas que contêm valores de gastos
colunas_gastos = ['BTG', 'Inter', 'Itaú', 'Mercado Pago', 'Nubank', 'Apartamento', 'Faculdade']

# Preenche os valores ausentes (NaN) com 0
df_gastos[colunas_gastos] = df_gastos[colunas_gastos].fillna(0)

# Limpa e converte as colunas de gastos para o tipo numérico (float)
for col in colunas_gastos:
    df_gastos[col] = df_gastos[col].astype(str).str.replace('R$', '', regex=False).str.replace(',', '.').astype(float)

# Transforma a planilha do formato 'wide' para o formato 'long'
# Isso facilita a criação de gráficos
df_long = df_gastos.melt(id_vars=["Data"],
                       value_vars=colunas_gastos,
                       var_name="Tipo_Gasto",
                       value_name="Valor")

# --- Estrutura do Painel ---
st.title("💸 Controle de Finanças Pessoais")
st.markdown("---")

# --- Exemplo de visualização para testar a limpeza ---
st.header("Dados Limpos e Transformados")
st.write("Aqui estão os seus dados prontos para análise:")
st.dataframe(df_long)