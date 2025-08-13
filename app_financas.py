# Importa as bibliotecas necessárias.
# pandas é usada para manipulação e análise de dados.
# json é usada para formatar a saída de dados para o frontend.
import pandas as pd
import json

# Define o nome do arquivo de dados e a renda mensal fixa.
# A renda mensal fixa será usada para calcular o saldo.
FILE_PATH = 'gastos_mensais.csv'
RENDA_MENSAL = 3685.00

def processar_gastos():
    """
    Processa o arquivo CSV de gastos, calcula os totais e gera um arquivo JSON.
    """
    try:
        # Tenta ler o arquivo CSV.
        # Usa 'sep=,' para garantir que as colunas sejam separadas por vírgula.
        # Usa 'encoding="utf-8"' para evitar problemas de caracteres.
        df = pd.read_csv(FILE_PATH, sep=',', encoding="utf-8")

        # Mostra o conteúdo inicial do DataFrame para verificar se foi lido corretamente.
        print("Conteúdo inicial do DataFrame:")
        print(df)
        print("-" * 50)

        # Remove a coluna 'Total' para evitar duplicar a soma.
        # 'inplace=True' modifica o DataFrame diretamente.
        if 'Total' in df.columns:
            df.drop('Total', axis=1, inplace=True)
            print("Coluna 'Total' removida.")
            print("-" * 50)

        # Remove qualquer linha que esteja completamente vazia.
        # 'how="all"' garante que apenas linhas totalmente vazias sejam removidas.
        df.dropna(how='all', inplace=True)
        print("Linhas vazias removidas.")
        print("-" * 50)

        # Preenche os valores vazios (NaN) com 0 para que possam ser somados.
        df.fillna(0, inplace=True)
        print("Valores NaN preenchidos com 0.")
        print("-" * 50)

        # Transforma os dados em formato numérico.
        # As colunas de gastos estão no formato 'R$ X.XXX,XX', então precisamos limpar isso.
        # Aplica uma função lambda para remover 'R$', pontos e substituir vírgulas por pontos.
        # Depois, converte a coluna para o tipo numérico (float).
        for col in df.columns[1:]:  # Pula a coluna 'Data'
            # A nova regex limpa 'R$' e espaços em branco, depois substitui a vírgula por ponto.
            df[col] = df[col].astype(str).str.replace(r'[R$\s.]', '', regex=True).str.replace(',', '.', regex=False)
            # Tenta converter para float, substituindo erros por 0.
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        print("DataFrame após a limpeza e conversão de dados:")
        print(df)
        print("-" * 50)

        # Define a coluna 'Data' como índice para facilitar a manipulação.
        df.set_index('Data', inplace=True)
        print("Coluna 'Data' definida como índice.")
        print("-" * 50)

        # Calcula a soma total de gastos para cada coluna (bancos, despesas fixas).
        gastos_totais = df.sum(axis=0)

        # Calcula o gasto total no último mês, que será o último item da coluna 'Total'.
        # O .iloc[-1] pega a última linha.
        ultimo_mes = df.index[-1]
        gastos_ultimo_mes = df.loc[ultimo_mes].sum()

        # Calcula o saldo.
        saldo = RENDA_MENSAL - gastos_ultimo_mes

        # Converte a série de gastos totais em um dicionário para facilitar a exportação para JSON.
        # Exclui a coluna 'Total' para evitar duplicidade.
        gastos_totais_dict = gastos_totais.to_dict()

        # Prepara os dados para serem salvos em JSON.
        data_to_save = {
            'gastos_por_categoria': gastos_totais_dict,
            'gastos_ultimo_mes': gastos_ultimo_mes,
            'renda_mensal': RENDA_MENSAL,
            'saldo': saldo
        }

        # Salva os dados processados em um arquivo JSON.
        # 'w' abre o arquivo para escrita. 'indent=4' formata o JSON de forma legível.
        with open('gastos.json', 'w') as f:
            json.dump(data_to_save, f, indent=4)
        
        print(f"Dados processados e salvos em 'gastos.json':\n{json.dumps(data_to_save, indent=4)}")
        
    except FileNotFoundError:
        # Se o arquivo CSV não for encontrado, exibe uma mensagem de erro.
        print(f"Erro: O arquivo '{FILE_PATH}' não foi encontrado.")
    except Exception as e:
        # Captura e exibe qualquer outro erro que possa ocorrer.
        print(f"Ocorreu um erro: {e}")

# Executa a função principal quando o script é chamado.
if __name__ == "__main__":
    processar_gastos()
