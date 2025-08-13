import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from PIL import Image

# -------------------- Parte 1: Processamento de Dados (pandas) --------------------
# A lógica de processamento de dados foi integrada ao aplicativo para ser autocontida

# Carregar o arquivo CSV
try:
    df = pd.read_csv('gastos_mensais.csv')
except FileNotFoundError:
    print("Erro: O arquivo 'gastos_mensais.csv' não foi encontrado. Por favor, verifique o nome do arquivo.")
    exit()

# Preencher valores ausentes com 0
df.fillna(0, inplace=True)

# Função para limpar e converter valores para numérico
def clean_currency(value):
    if isinstance(value, str):
        value = value.replace('R$', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0

# Colunas a serem limpas e convertidas
columns_to_clean = ['BTG', 'Inter', 'Itaú', 'Mercado Pago', 'Nubank', 'Apartamento', 'Faculdade', 'Total']
for col in columns_to_clean:
    df[col] = df[col].apply(clean_currency)

# Definir a renda mensal
renda_mensal = 3685.00

# Calcular os gastos por categoria
gastos_bancos = ['BTG', 'Inter', 'Itaú', 'Mercado Pago', 'Nubank']
despesas_fixas = ['Apartamento', 'Faculdade']
gastos_por_banco = df[gastos_bancos].sum().to_dict()
total_despesas_fixas = df[despesas_fixas].sum().sum()

# Criar um DataFrame para o gráfico
gastos_totais_df = pd.DataFrame(gastos_por_banco.items(), columns=['Categoria', 'Gasto Total'])
gastos_totais_df.loc[len(gastos_totais_df.index)] = ['Despesas Fixas', total_despesas_fixas]

# Calcular o gasto total e o saldo
gasto_total = gastos_totais_df['Gasto Total'].sum()
saldo_restante = renda_mensal - gasto_total

# -------------------- Parte 2: Geração do Gráfico (matplotlib) --------------------

def generate_plot():
    df_gastos = gastos_totais_df.sort_values(by='Gasto Total', ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5), facecolor='#2b2b2b')
    ax.set_facecolor('#2b2b2b')
    cores = plt.cm.plasma(df_gastos['Gasto Total'] / max(df_gastos['Gasto Total']))
    bars = ax.bar(df_gastos['Categoria'], df_gastos['Gasto Total'], color=cores)
    ax.set_title('Gastos Mensais por Categoria', fontsize=14, color='white')
    ax.set_xlabel('Categoria', fontsize=10, color='white')
    ax.set_ylabel('Gasto (R$)', fontsize=10, color='white')
    ax.tick_params(axis='x', colors='white', labelsize=8)
    ax.tick_params(axis='y', colors='white', labelsize=8)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    formatter = ticker.FuncFormatter(lambda x, p: f'R$ {x:,.2f}')
    ax.yaxis.set_major_formatter(formatter)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'R$ {height:,.2f}',
                ha='center', va='bottom', color='white', fontsize=7)
    plt.tight_layout()
    plt.savefig('gastos_por_categoria.png', transparent=True)
    plt.close()

# Gerar o gráfico antes de iniciar a GUI
generate_plot()

# -------------------- Parte 3: Interface Gráfica (customtkinter) --------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Meu Gestor de Finanças Pessoais")
        self.geometry("900x600")

        # Configurar layout da grade (2 colunas)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # Frame da barra lateral para o resumo financeiro
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Título da barra lateral
        self.sidebar_title = ctk.CTkLabel(self.sidebar_frame, text="Resumo Financeiro", font=ctk.CTkFont(size=20, weight="bold"))
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Renda
        self.renda_label = ctk.CTkLabel(self.sidebar_frame, text=f"Renda Mensal:\n R$ {renda_mensal:,.2f}", font=ctk.CTkFont(size=14))
        self.renda_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # Gasto Total
        self.gasto_total_label = ctk.CTkLabel(self.sidebar_frame, text=f"Gasto Total:\n R$ {gasto_total:,.2f}", font=ctk.CTkFont(size=14))
        self.gasto_total_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        # Saldo
        saldo_color = "green" if saldo_restante >= 0 else "red"
        self.saldo_label = ctk.CTkLabel(self.sidebar_frame, text=f"Saldo Restante:\n R$ {saldo_restante:,.2f}", font=ctk.CTkFont(size=14, weight="bold"), text_color=saldo_color)
        self.saldo_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        # Frame principal para o gráfico e recomendações
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Título da área principal
        self.main_title = ctk.CTkLabel(self.main_frame, text="Visão Geral dos Gastos", font=ctk.CTkFont(size=20, weight="bold"))
        self.main_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Carregar e exibir o gráfico
        self.plot_image = ctk.CTkImage(light_image=Image.open("gastos_por_categoria.png"), size=(600, 350))
        self.plot_label = ctk.CTkLabel(self.main_frame, text="", image=self.plot_image)
        self.plot_label.grid(row=1, column=0, padx=20, pady=10)

        # Seção de Recomendações
        self.recommendations_label_title = ctk.CTkLabel(self.main_frame, text="Recomendações:", font=ctk.CTkFont(size=16, weight="bold"))
        self.recommendations_label_title.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="nw")

        # Lógica de recomendação
        maior_gasto = gastos_totais_df.loc[gastos_totais_df['Gasto Total'].idxmax()]
        recommendation_text = f"Sua maior despesa é com '{maior_gasto['Categoria']}', totalizando R$ {maior_gasto['Gasto Total']:,.2f}. "
        if saldo_restante < 0:
            recommendation_text += "Seu saldo está negativo, por isso é crucial analisar os gastos e buscar cortes de despesas."
        else:
            recommendation_text += "Mantenha o controle e continue monitorando seus gastos!"

        self.recommendations_label = ctk.CTkLabel(self.main_frame, text=recommendation_text, font=ctk.CTkFont(size=12), wraplength=550, justify="left")
        self.recommendations_label.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nw")


if __name__ == "__main__":
    app = App()
    app.mainloop()