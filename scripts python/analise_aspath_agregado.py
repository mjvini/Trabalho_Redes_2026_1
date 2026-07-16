import requests
import numpy as np
import matplotlib.pyplot as plt
import time

def obter_tamanho_medio_aspath(prefixo, timestamp):
    """Consulta a API do RIPE para pegar a tabela de roteamento de um prefixo num momento exato."""
    url = "https://stat.ripe.net/data/bgp-state/data.json"
    params = {"resource": prefixo, "timestamp": timestamp}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            bgp_state = response.json().get('data', {}).get('bgp_state', [])
            
            tamanhos = []
            for rota in bgp_state:
                caminho = rota.get('path', [])
                if caminho:
                    tamanhos.append(len(caminho))
            
            # Retorna a média de saltos para este prefixo. Se estiver offline, retorna NaN.
            return np.mean(tamanhos) if tamanhos else np.nan
    except Exception as e:
        print(f"Erro ao consultar {prefixo}: {e}")
    return np.nan

if __name__ == "__main__":
    # LISTA DE PREFIXOS:
    prefixos = [
    # Índia
    "106.200.156.0/22",   # Bharti Airtel
    "59.144.97.0/24",     # Bharti Airtel
    "47.15.64.0/20",      # Reliance Jio
    "115.240.82.0/24",    # Reliance Jio
    "210.210.1.0/24",     # Sify (já existente)
    "2400:d280:8000::/36",# Bell Teleservices (IPv6)
    # Arábia Saudita
    "37.217.240.0/20",    # Etihad Etisalat
    "95.177.192.0/19",    # Arabian Internet
    "212.138.64.0/24",    # KACST-ISU
    # Emirados Árabes
    "2.48.0.0/18",        # Etisalat Group
    ]
    
    # Os quatro dias do evento (Setembro de 2025)
    datas = [
        "2025-09-04T12:00:00",
        "2025-09-05T12:00:00", # Antes do corte
        "2025-09-06T12:00:00", # O Caos consolidado
        "2025-09-07T12:00:00"  # Pós-evento
    ]
    rotulos_dias = ['04/Set', '05/Set', '06/Set', '07/Set']
    
    medias_diarias_globais = []
    
    print(f"Iniciando análise macroscópica de {len(prefixos)} prefixos em {len(datas)} dias...")
    
    for data in datas:
        print(f"\n--- Coletando dados globais para o dia {data[:10]} ---")
        medias_neste_dia = []
        
        for pref in prefixos:
            media_pref = obter_tamanho_medio_aspath(pref, data)
            
            if not np.isnan(media_pref):
                medias_neste_dia.append(media_pref)
                print(f"  {pref}: {media_pref:.2f} saltos")
            else:
                print(f"  {pref}: OFFLINE (Ignorado na média)")
                
            time.sleep(1.5) # Pausa vital para não ser bloqueado pela API (Erro 502)
            
        # Calcula a média agregada de todos os prefixos que sobreviveram naquele dia
        if medias_neste_dia:
            media_global = np.mean(medias_neste_dia)
            medias_diarias_globais.append(media_global)
            print(f">>> MÉDIA GLOBAL DO DIA: {media_global:.2f} saltos")
        else:
            medias_diarias_globais.append(0)
            print(">>> Todas as redes caíram!")

    # ==========================================
    # GERAÇÃO DO GRÁFICO DE LINHA
    # ==========================================
    plt.figure(figsize=(10, 6))
    
    # Desenhando a linha
    plt.plot(rotulos_dias, medias_diarias_globais, marker='o', color='purple', linewidth=3, markersize=8)
    
    plt.title(f'Evolução do AS_PATH Agregado (Amostra de {len(prefixos)} Prefixos)\nImpacto dos Cortes no Mar Vermelho (Set. 2025)', fontsize=14)
    plt.xlabel('Linha do Tempo', fontsize=12)
    plt.ylabel('Média Global de Saltos Administrativos', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Marcador visual do momento do corte
    plt.axvline(x=1.5, color='red', linestyle='--', linewidth=2, label='Rompimento SMW-4/IMEWE')
    plt.legend()
    
    # Adicionando os valores numéricos em cima de cada ponto da linha
    for i, valor in enumerate(medias_diarias_globais):
        if valor > 0:
            plt.text(i, valor + 0.05, f'{valor:.2f}', ha='center', fontweight='bold', fontsize=11)
            
    plt.tight_layout()
    plt.savefig('evolucao_aspath_agregado.png')
    print("\n[SUCESSO] Gráfico gerado e salvo como 'evolucao_aspath_agregado.png'!")

