import pandas as pd
import streamlit as st
import altair as alt

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

# Limpeza e Transformação dos Dados
df_gastos = df_gastos.drop(columns=["Total"])
colunas_gastos = ['BTG', 'Inter', 'Itaú', 'Mercado Pago', 'Nubank', 'Apartamento', 'Faculdade']
df_gastos[colunas_gastos] = df_gastos[colunas_gastos].fillna(0)

for col in colunas_gastos:
    df_gastos[col] = df_gastos[col].astype(str).str.strip().str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.').astype(float)

df_long = df_gastos.melt(id_vars=["Data"],
                       value_vars=colunas_gastos,
                       var_name="Tipo_Gasto",
                       value_name="Valor")

# --- Lógica do Aplicativo ---
st.title("💸 Controle de Finanças Pessoais")
st.markdown("---")

# Seletor para escolher o mês
meses = df_gastos["Data"].unique()
mes_selecionado = st.selectbox("Selecione o Mês:", meses)

# Filtra os dados com base no mês selecionado
df_mes = df_long[df_long["Data"] == mes_selecionado]

# Calcula o total de gastos do mês
total_gastos = df_mes["Valor"].sum()
saldo = RECEITA_MENSAL - total_gastos

# Exibe o dashboard de métricas
st.header("Resumo Mensal")
col1, col2, col3 = st.columns(3)
col1.metric("Receita Mensal", f"R$ {RECEITA_MENSAL:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col2.metric("Total de Gastos", f"R$ {total_gastos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("Saldo Restante", f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

# Visualização de Gastos por Tipo (Gráfico de Barras)
st.header("Análise de Gastos por Tipo")

# Agrupa os dados para a visualização
df_gastos_agrupado = df_mes.groupby("Tipo_Gasto")["Valor"].sum().reset_index()

# Cria o gráfico de barras com Altair
chart = alt.Chart(df_gastos_agrupado).mark_bar().encode(
    x=alt.X("Tipo_Gasto", title="Tipo de Gasto"),
    y=alt.Y("Valor", title="Valor (R$)"),
    tooltip=["Tipo_Gasto", alt.Tooltip("Valor", format=".2f", title="Valor")]
).properties(
    title=f"Gastos no mês de {mes_selecionado}"
)
st.altair_chart(chart, use_container_width=True)

st.markdown("---")

# Visualização da meta de economia (inspirado na imagem de referência)
st.header("Meta de Economia")

# Calcula o percentual de economia
percentual_economia = (saldo / RECEITA_MENSAL) if RECEITA_MENSAL > 0 else 0

st.subheader(f"Você economizou {percentual_economia:.2%}")
st.progress(percentual_economia)
st.write(f"Sua meta é economizar R$ {RECEITA_MENSAL:,.2f} por mês. Seu saldo atual é de R$ {saldo:,.2f}.")