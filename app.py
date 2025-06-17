
import streamlit as st
import requests
import random
from collections import Counter

st.set_page_config(page_title="🔍 Análise e Geração Lotofácil", layout="wide")

API_URL = "https://loteriascaixa-api.herokuapp.com/api/lotofacil/"

def capturar_ultimos_resultados(qtd=5):
    response = requests.get(API_URL)
    if response.status_code != 200:
        st.error("Erro ao acessar a API.")
        return []

    todos = response.json()
    if isinstance(todos, dict):
        todos = [todos]

    concursos = todos[-qtd:]
    resultados = []
    for c in concursos:
        dezenas = c.get('listaDezenas') or c.get('dezenas') or c.get('numeros')
        if not dezenas:
            continue

        resultados.append({
            'concurso': c.get('concurso', 'N/A'),
            'data': c.get('data', 'N/A'),
            'numeros': sorted([int(n) for n in dezenas])
        })

    return resultados

def analisar_concursos(concursos):
    analise = {}
    todos_numeros = [num for c in concursos for num in c['numeros']]
    frequencia = Counter(todos_numeros)
    analise['frequencia'] = dict(frequencia)
    return analise

def gerar_cartoes_inteligentes(analise, qtd_cartoes=10):
    frequencias = Counter(analise['frequencia'])
    dezenas_ordenadas = [num for num, freq in frequencias.most_common(25)]
    cartoes = []
    tentativas_max = 1000
    gerados = 0

    while gerados < qtd_cartoes and tentativas_max > 0:
        dezenas_candidatas = dezenas_ordenadas[:20]
        random.shuffle(dezenas_candidatas)
        cartao = sorted(dezenas_candidatas[:15])

        pares = sum(1 for d in cartao if d % 2 == 0)
        impares = 15 - pares
        soma = sum(cartao)

        linhas = [0]*5
        colunas = [0]*5
        for d in cartao:
            linha = (d - 1) // 5
            coluna = (d - 1) % 5
            linhas[linha] += 1
            colunas[coluna] += 1

        if (
            6 <= pares <= 9 and
            180 <= soma <= 220 and
            max(linhas) <= 5 and min(linhas) >= 1 and
            max(colunas) <= 5 and min(colunas) >= 1
        ):
            if cartao not in cartoes:
                cartoes.append(cartao)
                gerados += 1
        tentativas_max -= 1

    return cartoes

st.title("🎯 Análise Inteligente + Geração de Jogos - Lotofácil")

qtd_concursos = st.slider("Quantos concursos recentes analisar?", min_value=5, max_value=50, value=5)
qtd_cartoes = st.number_input("Quantos cartões deseja gerar?", min_value=1, max_value=500, value=10)

if st.button("🔍 Analisar e Gerar Jogos"):
    concursos = capturar_ultimos_resultados(qtd=qtd_concursos)
    if concursos:
        analise = analisar_concursos(concursos)

        st.subheader("📊 Frequência das Dezenas")
        freq_ordenada = sorted(analise['frequencia'].items(), key=lambda x: (-x[1], x[0]))
        st.write({f"{k:02d}": v for k, v in freq_ordenada})

        cartoes = gerar_cartoes_inteligentes(analise, qtd_cartoes=qtd_cartoes)

        st.subheader("🎟️ Cartões Gerados")
        for i, c in enumerate(cartoes, start=1):
            st.write(f"Cartão {i:03d}: {' - '.join(f'{n:02d}' for n in c)}")

        if st.download_button("⬇️ Baixar Jogos em .TXT", data='\n'.join(
            f"Cartão {i+1:03d}: {' - '.join(f'{n:02d}' for n in cartoes[i])}" for i in range(len(cartoes))),
            file_name="cartoes_lotofacil.txt"
        ):
            st.success("Arquivo exportado com sucesso!")

st.markdown("""
---
🧠 Desenvolvido por **SAM ROCK** com inteligência estatística aplicada à Lotofácil.  
📅 Dados atualizados automaticamente com os concursos mais recentes.  
""")
