# Análise da Topologia Lógica da Internet: Impactos da Crise no Mar Vermelho e a Resiliência de Cabos Submarinos via BGP

Este repositório contém os dados, scripts e resultados práticos desenvolvidos para o Trabalho Final da disciplina de Redes de Computadores do Instituto de Computação da Universidade Federal do Rio de Janeiro (UFRJ).

**Equipe:**
* Richard Dias Amancio Beserra (12324881311)
* Igor Miranda Barbosa (1200608851)
* Marcus Vinicius Torres de Oliveira (1181422231)
* Vitor Ferreira Nunes (1200340701)
* João Victor Borges Nascimento (1210646041)

---

## 📌 Sobre o Projeto

O trabalho investiga os impactos geopolíticos da crise no Mar Vermelho sobre a infraestrutura global da Internet, cruzando a **Dimensão Técnica A3** (Cabos submarinos e infraestrutura física) com a **Questão Geopolítica B4** (Crise no Mar Vermelho e rotas marítimas globais). 

Focamos na disrupção de infraestrutura física (corte dos cabos SMW-4 e IMEWE em setembro de 2025) e analisamos os seus reflexos na Camada 3 através do comportamento do protocolo BGP (Border Gateway Protocol). O objetivo é comprovar com dados empíricos de alcance, anúncios e tamanho de caminho (*Path Hunting*) como a rede adaptou-se a falhas catastróficas L1.

## 📊 Fontes de Dados Públicos

A extração dos metadados para as análises quantitativas foi automatizada utilizando a infraestrutura dos seguintes projetos de monitoramento:
* **RIPE RIS (Routing Information Service):** Fonte primária de telemetria BGP. Os dados de `updates` e tabelas de roteamento (RIBs) foram extraídos diretamente via REST API (`RIPEstat Data API`).
* **RouteViews:** Utilizado para base teórica sobre a visibilidade de tabelas BGP globais.
* **CAIDA AS Relationships & PeeringDB:** Usados para anotações topológicas, relacionamentos comerciais (c2p, p2p) e mapeamento físico/geográfico de Sistemas Autônomos.

## 🛠️ Estrutura dos Scripts (Arquivos em Python)

Os scripts desenvolvidos consultam as tabelas BGP da Internet global em tempo real (para recortes históricos), tratando dados JSON brutos e gerando gráficos e métricas.

1. `analise_churn.py`: 
   * **Objetivo:** Coleta mensagens de *Updates* e *Withdrawals* por hora para o prefixo afetado (ex: `61.2.224.0/20` da BSNL).
   * **Saída:** Gera o gráfico da *Métrica 1* (`bgp_churn_...png`), provando a explosão de instabilidade e reconvergência (BGP Churn) no momento da ruptura do cabo.

2. `analise_aspath.py`: 
   * **Objetivo:** Analisa o estado do roteamento (RIB) antes e depois da crise para o estudo de caso individual.
   * **Saída:** Extrai a variação de Sistemas Autônomos intermediários assumindo tráfego (*Métrica 3*) e gera o gráfico da *Métrica 2* (`as_path_length_...png`), demonstrando a dilatação das rotas (aumento de saltos lógicos).

3. `analise_aspath_agregado.py`: 
   * **Objetivo:** Realiza uma pesquisa macroscópica (*Data Sanitization e Agregação*) sobre uma amostra de 10 prefixos diferentes afetados no Leste Asiático e Oriente Médio ao longo de 4 dias.
   * **Saída:** Gera um gráfico de linha temporal (`evolucao_aspath_agregado.png`), comprovando o alongamento sistêmico e generalizado do AS_PATH na região.

## 🚀 Como Executar o Código Localmente

Os scripts foram desenvolvidos e testados em ambiente Linux (ex: Mint/Ubuntu) rodando `Python 3.12`. Recomenda-se o uso de um ambiente virtual para não gerar conflito de permissões.

### Passo 1: Preparar o ambiente
Abra o seu terminal e clone este repositório (ou acesse a pasta raiz). Em seguida, execute:
```bash
# Cria um ambiente virtual chamado 'env'
python3 -m venv env

# Ativa o ambiente virtual
source env/bin/activate

# Instala as dependências necessárias
pip install requests pandas matplotlib numpy
```
### Passo 2: Rodar as Extrações da API
Com o ambiente ativado, execute os scripts individualmente para consultar a API do RIPEstat e gerar os gráficos na pasta atual:

### Para gerar a Métrica 1 (BGP Churn)
python3 analise_churn.py

### Para gerar o estudo de caso da Métrica 2 e Métrica 3 (Tamanho do AS_PATH)
python3 analise_aspath.py

### Para gerar a evolução macroscópica agregada (Diversos Prefixos)
python3 analise_aspath_agregado.py

#### (Nota: O script de prefixos agregados realiza dezenas de chamadas à API e possui intervalos de time.sleep() para evitar limites de taxa (Erro HTTP 502), podendo levar de 2 a 3 minutos para ser finalizado).
## 📈 Resultados e Entregáveis
#### As imagens geradas pelos scripts (que encontram-se nesta mesma pasta) correspondem diretamente aos entregáveis exigidos para as Métricas Quantitativas e Impactos Topológicos:
   * O protocolo contornou com sucesso a destruição física (marítima), porém sob a penalidade de aumentar em 1 salto global o trânsito da região focal para o Ocidente.
   * Constatou-se uma tormenta de anúncios e retiradas de rotas de magnitudes acima do baseline operacional durante o dia 06 de Setembro.
   * Detectou-se um fluxo denso (mais de 16 novos provedores) assumindo as rotas de trânsito em substituição às rotas que utilizavam a infraestrutura inoperante.
