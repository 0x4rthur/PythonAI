Sempre exibir os detalhes

Copiar
# Create a Streamlit app, an Excel template, and a README with instructions.
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import os

# 1) Build a realistic Excel template with example data for two months
today = datetime.today().date()
first_day_this_month = today.replace(day=1)
first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)

def sample_rows(month_start, bank, card_name):
    rows = []
    dates = [month_start + timedelta(days=i) for i in [1,3,6,8,10,13,17,20,24,26]]
    categorias = ["Mercado","Restaurantes","Transporte","Assinaturas","Educação","Moradia","Saúde","Lazer","Compras","Outros"]
    valores = [210.50, 78.90, 42.30, 34.90, 550.00, 970.00, 60.00, 120.00, 199.90, 45.00]
    descr = ["Supermercado BomPreço","Hamburgueria","Uber","Spotify","Mensalidade faculdade",
             "Parcela apartamento","Farmácia","Cinema","Loja online","Chave cópia"]
    for d,c,v,ds in zip(dates,categorias,valores,descr):
        rows.append([d, bank, card_name, c, ds, v if c!="Moradia" else 0.0 if bank!="Conta" else v, "Cartão" if c!="Moradia" else ("Fixa" if bank=="Conta" else "Cartão")])
    return rows

# Compose dataset
data = []
# Fixed expenses set on bank "Conta" for clarity (e.g., boleto/conta-corrente)
data += [
    [first_day_this_month + timedelta(days=2), "Conta", "Débito", "Moradia", "Parcela apartamento", 970.00, "Fixa"],
    [first_day_this_month + timedelta(days=4), "Conta", "Débito", "Educação", "Mensalidade faculdade", 550.00, "Fixa"],
]
data += sample_rows(first_day_this_month, "Nubank", "Nubank Gold")
data += sample_rows(first_day_this_month, "Itaú", "Itaú Click")

# Previous month
data += [
    [first_day_last_month + timedelta(days=2), "Conta", "Débito", "Moradia", "Parcela apartamento", 970.00, "Fixa"],
    [first_day_last_month + timedelta(days=4), "Conta", "Débito", "Educação", "Mensalidade faculdade", 550.00, "Fixa"],
]
data += sample_rows(first_day_last_month, "Nubank", "Nubank Gold")
data += sample_rows(first_day_last_month, "Itaú", "Itaú Click")

df = pd.DataFrame(data, columns=["Data","Banco","Cartao","Categoria","Descricao","Valor","Tipo"])
df["Data"] = pd.to_datetime(df["Data"]).dt.date

excel_path = "/mnt/data/financas_template.xlsx"
with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Transacoes")

# 2) Create the Streamlit app code
app_code = r'''
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px

RENDA_MENSAL = 3685.00

st.set_page_config(page_title="Controle Financeiro", layout="wide", page_icon="💸")

# ---------- Styles (minimal + soft animations) ----------
st.markdown("""
<style>
:root {
  --card-bg: #ffffff;
  --muted: #6b7280;
  --ring: #e5e7eb;
}
* { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial, "Apple Color Emoji", "Segoe UI Emoji"; }
.block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
.card {
  background: var(--card-bg);
  border: 1px solid var(--ring);
  border-radius: 18px;
  padding: 18px 18px 14px 18px;
  box-shadow: 0 4px 20px rgba(15,23,42,.05);
  animation: fadeInUp .6s ease;
}
.metric { font-size: 28px; font-weight: 700; }
.label { color: var(--muted); font-size: 13px; margin-top: -6px; }
.badge {
  display:inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px;
  background:#eef2ff; color:#4338ca; border:1px solid #e0e7ff;
}
.progress-bg { height:10px; background:#eef2ff; border-radius:999px; overflow:hidden; }
.progress-fill { height:10px; background:linear-gradient(90deg, #6366f1, #22d3ee); width:0%; transition: width .9s ease; }
@keyframes fadeInUp { 0% {opacity:0; transform:translate3d(0,10px,0);} 100% {opacity:1; transform:translate3d(0,0,0);} }
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
@st.cache_data
def load_excel(bytes_or_path):
    if bytes_or_path is None:
        return None
    try:
        df = pd.read_excel(bytes_or_path, sheet_name="Transacoes")
        # Normalização
        df.columns = [c.strip().title() for c in df.columns]
        if "Data" in df:
            df["Data"] = pd.to_datetime(df["Data"])
            df["Ano"] = df["Data"].dt.year
            df["Mes"] = df["Data"].dt.month
            df["Dia"] = df["Data"].dt.day
        df["Banco"] = df.get("Banco","Desconhecido").astype(str)
        df["Categoria"] = df.get("Categoria","Outros").astype(str)
        df["Valor"] = pd.to_numeric(df.get("Valor", 0.0), errors="coerce").fillna(0.0)
        df["Tipo"] = df.get("Tipo","Cartão").astype(str)
        return df
    except Exception as e:
        st.error(f"Falha ao ler a planilha: {e}")
        return None

def gerar_insights(df_mes: pd.DataFrame, renda: float, df_prev: pd.DataFrame|None):
    insights = []
    total = df_mes["Valor"].sum()
    if total > renda:
        insights.append(f"⚠️ Você gastou **{total:,.2f}** e ultrapassou a renda de **{renda:,.2f}**. Considere cortes imediatos.")
    else:
        sobra = renda - total
        insights.append(f"✅ Você está dentro da renda. **Sobra: {sobra:,.2f}** neste mês.")
    # categoria > 20% da renda
    cat = df_mes.groupby("Categoria")["Valor"].sum().sort_values(ascending=False)
    for c,v in cat.items():
        if v >= 0.2 * renda:
            insights.append(f"• **{c}** consumiu **{(v/renda*100):.1f}%** da sua renda. Avalie reduzir.")
    # assinaturas
    if "Assinaturas" in cat and cat["Assinaturas"] >= 0.05*renda:
        insights.append("• **Assinaturas** acima de 5% da renda. Cancele ou renegocie o que não usa.")
    # concentração por banco
    by_bank = df_mes.groupby("Banco")["Valor"].sum()
    if not by_bank.empty:
        lead_bank = by_bank.idxmax()
        share = by_bank.max() / by_bank.sum() * 100
        if share >= 50:
            insights.append(f"• **{lead_bank}** concentra **{share:.0f}%** dos gastos. Verifique limites/benefícios e tente redistribuir.")
    # variação vs mês anterior
    if df_prev is not None and not df_prev.empty:
        cat_prev = df_prev.groupby("Categoria")["Valor"].sum()
        for c,v in cat.items():
            pv = cat_prev.get(c,0.0)
            if pv>0 and (v-pv)/pv >= .15:
                insights.append(f"• **{c}** subiu **{((v-pv)/pv*100):.0f}%** vs mês anterior.")
    return insights

def fmt_currency(x):
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------- Sidebar ----------
st.sidebar.header("Configuração")
uploaded = st.sidebar.file_uploader("Carregue sua planilha (Excel .xlsx)", type=["xlsx"], accept_multiple_files=False)
default_msg = "Use o template se ainda não tiver sua planilha."
st.sidebar.caption(default_msg)

df = None
if uploaded is not None:
    df = load_excel(uploaded)
else:
    # tenta abrir arquivo local com nome padrão
    try:
        df = load_excel("financas.xlsx")
    except Exception:
        pass

if df is None:
    st.info("Nenhuma planilha carregada. Você pode usar o **template** para começar: na lateral, baixe o arquivo 'financas_template.xlsx'.")
    # cria um df vazio só para não quebrar o app
    df = pd.DataFrame(columns=["Data","Banco","Cartao","Categoria","Descricao","Valor","Tipo","Ano","Mes","Dia"])

# Deriva meses disponíveis
if not df.empty and "Ano" in df and "Mes" in df:
    anos = sorted(df["Ano"].dropna().unique())
    ano = st.sidebar.selectbox("Ano", anos, index=len(anos)-1 if anos else 0)
    meses = df.loc[df["Ano"]==ano, "Mes"].dropna().unique()
    meses = sorted(meses)
    mes = st.sidebar.selectbox("Mês", meses, index=len(meses)-1 if meses else 0)
else:
    ano = datetime.today().year
    mes = datetime.today().month

# ---------- Header ----------
left, right = st.columns([1,1])
with left:
    st.markdown("### 💸 Controle Financeiro Pessoal")
    st.caption("Dashboard minimalista. Atualize a planilha mensalmente com gastos dos cartões e despesas fixas.")
with right:
    with st.container():
        st.write("")
        st.markdown('<span class="badge">Renda Mensal Fixa</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric"> {fmt_currency(RENDA_MENSAL)} </div>', unsafe_allow_html=True)

# ---------- Filtered frames ----------
df_mes = df[(df.get("Ano")==ano) & (df.get("Mes")==mes)]
df_prev = df[(df.get("Ano")==ano) & (df.get("Mes")==mes-1)]
total_mes = df_mes["Valor"].sum() if not df_mes.empty else 0.0
saldo = RENDA_MENSAL - total_mes
perc_gasto = 0 if RENDA_MENSAL==0 else round(total_mes / RENDA_MENSAL * 100, 1)

# ---------- Top cards ----------
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">Despesas no mês</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric">{fmt_currency(total_mes)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="label">Soma de cartões + fixas</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">Uso da renda</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric">{perc_gasto:.1f}%</div>', unsafe_allow_html=True)
    st.markdown('<div class="progress-bg"><div class="progress-fill" id="pf"></div></div>', unsafe_allow_html=True)
    st.markdown(f"""<script>
        const pf = window.parent.document.querySelector('#pf');
        if (pf) {{ pf.style.width = '{min(100,perc_gasto)}%'; }}
    </script>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">Saldo do mês</div>', unsafe_allow_html=True)
    saldo_color = "#16a34a" if saldo >= 0 else "#ef4444"
    st.markdown(f'<div class="metric" style="color:{saldo_color}">{fmt_currency(saldo)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="label">Renda - despesas</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Charts ----------
col1, col2 = st.columns([1.2, 1])
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Gastos por Banco")
    if df_mes.empty:
        st.caption("Sem dados para o período selecionado.")
    else:
        by_bank = df_mes.groupby("Banco")["Valor"].sum().reset_index().sort_values("Valor", ascending=False)
        fig = px.bar(by_bank, x="Banco", y="Valor", text="Valor")
        fig.update_traces(texttemplate="R$ %{y:,.2f}", textposition="outside")
        fig.update_layout(margin=dict(l=10,r=10,t=10,b=10), xaxis_title="", yaxis_title="R$",
                          transition_duration=500)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Categorias do mês")
    if df_mes.empty:
        st.caption("Sem dados.")
    else:
        by_cat = df_mes.groupby("Categoria")["Valor"].sum().reset_index().sort_values("Valor", ascending=False)
        fig2 = px.pie(by_cat, names="Categoria", values="Valor", hole=0.5)
        fig2.update_layout(margin=dict(l=10,r=10,t=10,b=10), transition_duration=500)
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Insights ----------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Onde gastar menos")
insights = gerar_insights(df_mes, RENDA_MENSAL, df_prev if df_prev is not None and not df_prev.empty else None)
for tip in insights:
    st.markdown(f"- {tip}")
st.markdown('</div>', unsafe_allow_html=True)

# ---------- Tabela ----------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Transações do mês")
if df_mes.empty:
    st.caption("Nenhuma transação encontrada.")
else:
    st.dataframe(
        df_mes[["Data","Banco","Cartao","Categoria","Descricao","Valor","Tipo"]]
        .sort_values("Data"),
        use_container_width=True, hide_index=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# ---------- Download template ----------
from io import BytesIO
st.sidebar.download_button(
    "⬇️ Baixar template (Excel)",
    data=open("financas_template.xlsx","rb").read() if os.path.exists("financas_template.xlsx") else b"",
    file_name="financas_template.xlsx",
    disabled=not os.path.exists("financas_template.xlsx"),
    help="Modelo com colunas: Data, Banco, Cartao, Categoria, Descricao, Valor, Tipo"
)

st.sidebar.markdown("---")
st.sidebar.caption("Dica: adicione novas linhas todos os meses. **Tipo** = 'Cartão' para faturas e 'Fixa' para despesas recorrentes (faculdade, apartamento etc.).")

""".strip()

app_path = "/mnt/data/app_financas.py"
with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_code)

# 3) Create README
readme = f"""
# App de Finanças Pessoais (Python + Pandas + Streamlit)

**Renda mensal fixa**: R$ 3.685,00.