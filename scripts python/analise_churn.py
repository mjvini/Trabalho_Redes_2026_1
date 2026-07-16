import requests
import pandas as pd
import matplotlib.pyplot as plt

def coletar_bgp_churn(prefixo, start_time, end_time):
    print(f"Coletando BGP Updates para o prefixo {prefixo}...")
    url = "https://stat.ripe.net/data/bgp-updates/data.json"
    params = {"resource": prefixo, "starttime": start_time, "endtime": end_time}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            updates = data['data'].get('updates', [])
            df = pd.DataFrame(updates)
            
            # Verifica se há dados e se a coluna correta (timestamp) veio na resposta
            if not df.empty and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # A API retorna 'A' para Anúncios e 'W' para Withdrawals
                df['announcements'] = (df['type'] == 'A').astype(int)
                df['withdrawals'] = (df['type'] == 'W').astype(int)
                
                # Selecionamos apenas as colunas numéricas [['announcements', 'withdrawals']] antes do .sum()
                df_agrupado = df.set_index('timestamp')[['announcements', 'withdrawals']].resample('1h').sum().reset_index()
                return df_agrupado
            else:
                print("Nenhum dado de update encontrado nesta janela ou formato inesperado.")
        else:
            print(f"Erro na API: {response.status_code}")
    except Exception as e:
        print(f"Falha de conexão ou processamento: {e}")
    return pd.DataFrame()

def gerar_grafico_churn(df, prefixo):
    if df.empty:
        print("Sem dados para gerar gráfico.")
        return

    plt.figure(figsize=(12, 6))
    # Desenhando as linhas
    plt.plot(df['timestamp'], df['announcements'], label='Anúncios (Novas Rotas / Updates)', color='blue', alpha=0.7, linewidth=2)
    plt.plot(df['timestamp'], df['withdrawals'], label='Withdrawals (Quedas / Retiradas)', color='red', alpha=0.9, linewidth=2)
    
    plt.title(f'Métrica 1: BGP Churn e Instabilidade - Prefixo {prefixo}\n(Crise no Mar Vermelho - Set. 2025)')
    plt.xlabel('Data/Hora')
    plt.ylabel('Volume de Mensagens BGP por Hora')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Salva o gráfico
    nome_arquivo = prefixo.replace('/', '_')
    plt.savefig(f'bgp_churn_{nome_arquivo}.png')
    print(f"Gráfico gerado com sucesso na pasta: bgp_churn_{nome_arquivo}.png")

if __name__ == "__main__":
    # Usando o prefixo da BSNL
    alvo = "61.2.224.0/20" 
    inicio = "2025-09-04T00:00:00"
    fim = "2025-09-07T00:00:00"
    
    df_updates = coletar_bgp_churn(alvo, inicio, fim)
    gerar_grafico_churn(df_updates, alvo)

