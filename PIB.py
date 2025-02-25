import requests
import os
import json
import pandas as pd  # Necessário para salvar como CSV

# Configuração do diretório para salvar os dados
output_dir = "/lakehouse/default/Files/PIB"
os.makedirs(output_dir, exist_ok=True)

# URL base da API do IBGE
base_url = "https://servicodados.ibge.gov.br/api/v3/agregados/5938/periodos/{ano}/variaveis/37?localidades=N6[all]"

# Arquivo de controle para anos já processados
controle_file = f"{output_dir}/anos_processados.txt"

def salvar_como_csv(json_data, ano):
    """
    Converte os dados JSON em CSV e salva no mesmo diretório.
    """
    # Normaliza os dados do JSON em uma estrutura tabular
    try:
        resultados = json_data[0]["resultados"][0]["series"]
        linhas = []
        for serie in resultados:
            municipio = serie["localidade"]["nome"]
            valores = serie["serie"]
            for ano_data, valor in valores.items():
                linhas.append({"Ano": ano_data, "Município": municipio, "PIB": valor})

        # Converte a lista de dicionários em um DataFrame
        df = pd.DataFrame(linhas)

        # Salva o DataFrame como CSV
        csv_path = f"{output_dir}/pib_{ano}.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"Dados do PIB do ano {ano} salvos como CSV em: {csv_path}")
    except Exception as e:
        print(f"Erro ao salvar o ano {ano} como CSV: {e}")

def verificar_e_atualizar_pib():
    """
    Função para verificar e resgatar dados do PIB da API do IBGE.
    """
    # Carregar anos já processados
    try:
        with open(controle_file, "r") as f:
            anos_processados = set(f.read().splitlines())
    except FileNotFoundError:
        anos_processados = set()

    # Resgatar dados do PIB dos anos de 2018 até o último disponível
    novos_dados = []
    for ano in range(2018, 2024):  # Atualize o intervalo de anos conforme necessário
        if str(ano) not in anos_processados:
            print(f"Buscando dados do ano {ano}...")
            url = base_url.format(ano=ano)
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    dados = response.json()
                    
                    # Salvar os dados no diretório como arquivo JSON
                    json_path = f"{output_dir}/pib_{ano}.json"
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(dados, file, ensure_ascii=False, indent=4)
                    
                    print(f"Dados do PIB do ano {ano} salvos como JSON em: {json_path}")
                    
                    # Salvar os dados como CSV
                    salvar_como_csv(dados, ano)
                    
                    novos_dados.append(str(ano))
                else:
                    print(f"Erro ao buscar dados do ano {ano}: {response.status_code}")
            except Exception as e:
                print(f"Erro ao processar o ano {ano}: {e}")

    # Atualizar o arquivo de controle com novos anos processados
    if novos_dados:
        try:
            with open(controle_file, "a") as f:
                f.write("\n".join(novos_dados) + "\n")
            print(f"Anos atualizados: {', '.join(novos_dados)}")
        except Exception as e:
            print(f"Erro ao atualizar o arquivo de controle: {e}")
    else:
        print("Nenhum dado novo encontrado.")

# Chamar a função
verificar_e_atualizar_pib()


