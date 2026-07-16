import requests
import numpy as np
import matplotlib.pyplot as plt
import time

def obter_estado_bgp(prefixo, timestamp):
    print(f"Coletando RIB (estado BGP) para {prefixo} em {timestamp}...")
    url = "https://stat.ripe.net/data/bgp-state/data.json"
    params = {"resource": prefixo, "timestamp": timestamp}
    
    try:
        response = requests.get(url, params=params, timeout=20)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('bgp_state', [])
    except Exception as e:
        print(f"Falha de conexão: {e}")
    return []

def analisar_as_paths(bgp_state):
    tamanhos = []
    ases_intermediarios = set()
    
    for rota in bgp_state:
        caminho = rota.get('path', [])
        if caminho:
            tamanhos.append(len(caminho))
            # Pega o caminho intermediário (ignora os 2 últimos e os primeiros do RIPE)
            for asn in caminho[1:-1]:
                ases_intermediarios.add(asn)
                
    media_path = np.mean(tamanhos) if tamanhos else 0
    return media_path, ases_intermediarios

if __name__ == "__main__":
    # Prefixo: BSNL (AS9829) afetado diretamente pelo corte
    alvo = "61.2.224.0/20" 
    
    # 05 de setembro (12h) foi ANTES do corte; 06 de setembro (12h) foi DEPOIS
    data_antes = "2025-09-05T12:00:00"
    data_depois = "2025-09-06T12:00:00"
    
    estado_antes = obter_estado_bgp(alvo, data_antes)
    media_antes, ases_antes = analisar_as_paths(estado_antes)
    time.sleep(2) # Evita sobrecarga na API
    
    estado_depois = obter_estado_bgp(alvo, data_depois)
    media_depois, ases_depois = analisar_as_paths(estado_depois)
    
    print(f"\n--- Analisando o prefixo: {alvo} ---")
    print("\n--- Métrica 2: Tamanho Médio do AS_PATH ---")
    print(f"Antes da Crise (05 Set): {media_antes:.2f} saltos")
    print(f"Durante a Crise (06 Set): {media_depois:.2f} saltos")
    
    print("\n--- Métrica 3: Diversidade de ASes Intermediários ---")
    novos_ases = ases_depois - ases_antes
    ases_perdidos = ases_antes - ases_depois
    
    print(f"Quantidade de provedores assumindo novas rotas: {len(novos_ases)}")
    print(f"ASes que caíram/foram retirados da rota: {list(ases_perdidos)[:5]}...") 
    print(f"Novos ASes no AS_PATH (Reroteamento): {list(novos_ases)[:5]}...")
    
    # Gera o Gráfico se houver dados
    if media_antes > 0 or media_depois > 0:
        plt.figure(figsize=(8, 5))
        barras = plt.bar(['Antes do Corte\n(05 Set)', 'Após o Corte\n(06 Set)'], [media_antes, media_depois], color=['#2ca02c', '#d62728'])
        plt.title(f'Métrica 2: Alongamento de AS_PATH - Prefixo {alvo}')
        plt.ylabel('Tamanho Médio do Caminho BGP')
        
        # Coloca o valor exato no topo da barra
        plt.text(0, media_antes + 0.05, f'{media_antes:.2f}', ha='center', fontweight='bold')
        plt.text(1, media_depois + 0.05, f'{media_depois:.2f}', ha='center', fontweight='bold')
        
        plt.tight_layout()
        nome_arquivo = alvo.replace('/', '_')
        plt.savefig(f'as_path_length_{nome_arquivo}.png')
        print(f"\nGráfico gerado com sucesso na pasta: as_path_length_{nome_arquivo}.png")
