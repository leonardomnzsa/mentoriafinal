import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random
import os

# Configuração da página
st.set_page_config(
    page_title="Dashboard Informativos STF",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar os dados (corrigida para Streamlit Cloud)
@st.cache_data
def carregar_dados():
    # Caminho relativo para o arquivo de dados
    arquivo_final = 'data/informativos_stf_2021_2025.xlsx'
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(arquivo_final):
            st.error(f"Arquivo de dados não encontrado em: {arquivo_final}")
            return None
            
        # Carregar o arquivo Excel
        df = pd.read_excel(arquivo_final)
        
        # Converter a coluna de data para datetime
        df["Data Julgamento"] = pd.to_datetime(df["Data Julgamento"], format="%d/%m/%Y", errors="coerce")
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        return None

# Estilo CSS personalizado
def aplicar_estilo():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #0e1117;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #0e1117;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .reading-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #4e8cff;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    .reading-card h3 {
        color: #1f1f1f;
        margin-bottom: 15px;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 10px;
    }
    .reading-card-meta {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 15px;
    }
    .reading-card-content {
        color: #333;
    }
    .highlight {
        color: #ff4b4b;
        font-weight: bold;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #888888;
        font-size: 0.8rem;
    }
    .assertiva-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 4px solid #4e8cff;
    }
    .assertiva-card.correct {
        border-left: 4px solid #28a745;
    }
    .assertiva-card.incorrect {
        border-left: 4px solid #dc3545;
    }
    .feedback-correct {
        color: #28a745;
        font-weight: bold;
        padding: 10px;
        border-radius: 5px;
        background-color: rgba(40, 167, 69, 0.1);
    }
    .feedback-incorrect {
        color: #dc3545;
        font-weight: bold;
        padding: 10px;
        border-radius: 5px;
        background-color: rgba(220, 53, 69, 0.1);
    }
    .question-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 4px solid #17a2b8;
    }
    .answer-card {
        background-color: #f0f7ff;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 20px;
        border-left: 4px solid #4e8cff;
    }
    </style>
    """, unsafe_allow_html=True)

# Função para gerar assertivas baseadas nos dados
def gerar_assertivas(df, num_assertivas=5):
    assertivas = []
    
    # Filtrar apenas registros com resumo não nulo
    df_com_resumo = df[df["Resumo"].notna()]
    
    if len(df_com_resumo) < 5:
        return [{"texto": "Não há dados suficientes para gerar assertivas.", "resposta": None}]
    
    # Selecionar registros aleatórios
    indices = random.sample(range(len(df_com_resumo)), min(num_assertivas * 2, len(df_com_resumo)))
    registros_selecionados = df_com_resumo.iloc[indices]
    
    # Tipos de assertivas
    tipos_assertivas = [
        "O STF decidiu que {tese}.",
        "De acordo com o informativo {informativo}, {resumo_parcial}.",
        "No julgamento de {classe} em {data}, o STF entendeu que {resumo_parcial}.",
        "É correto afirmar que, segundo o STF, {tese}.",
        "O {orgao} do STF, ao julgar {classe} em {data}, firmou entendimento de que {resumo_parcial}."
    ]
    
    # Gerar assertivas verdadeiras e falsas
    for i, (_, registro) in enumerate(registros_selecionados.iterrows()):
        if i >= num_assertivas:
            break
            
        # Obter dados do registro
        informativo = registro["Informativo"]
        classe = registro["Classe Processo"]
        data = registro["Data Julgamento"].strftime("%d/%m/%Y") if pd.notna(registro["Data Julgamento"]) else "data não especificada"
        
        # Verificar se há resumo ou tese
        if pd.notna(registro["Resumo"]):
            resumo = registro["Resumo"]
            # Pegar apenas parte do resumo para não ficar muito longo
            palavras = resumo.split()
            if len(palavras) > 15:
                resumo_parcial = " ".join(palavras[:15]) + "..."
            else:
                resumo_parcial = resumo
        else:
            resumo_parcial = "o tema foi objeto de análise pelo tribunal"
        
        tese = registro["Tese Julgado"] if pd.notna(registro["Tese Julgado"]) else resumo_parcial
        
        # Escolher aleatoriamente se a assertiva será verdadeira ou falsa
        e_verdadeira = random.choice([True, False])
        
        # Escolher um tipo de assertiva aleatoriamente
        tipo_assertiva = random.choice(tipos_assertivas)
        
        # Formatar a assertiva
        if e_verdadeira:
            texto_assertiva = tipo_assertiva.format(
                tese=tese,
                informativo=informativo,
                resumo_parcial=resumo_parcial,
                classe=classe,
                data=data,
                orgao="Plenário"
            )
        else:
            # Para assertivas falsas, modificamos algum elemento
            modificadores = [
                lambda t: "Não " + t[0].lower() + t[1:] if t else t,  # Negar a afirmação
                lambda t: t.replace("pode", "não pode") if "pode" in t else t.replace("não pode", "pode"),  # Inverter permissões
                lambda t: t.replace("constitucional", "inconstitucional") if "constitucional" in t else t.replace("inconstitucional", "constitucional"),  # Inverter constitucionalidade
                lambda t: t.replace("direito", "dever") if "direito" in t else t.replace("dever", "direito"),  # Trocar direito por dever
            ]
            
            modificador = random.choice(modificadores)
            texto_modificado = modificador(tese)
            
            texto_assertiva = tipo_assertiva.format(
                tese=texto_modificado,
                informativo=informativo,
                resumo_parcial=modificador(resumo_parcial),
                classe=classe,
                data=data,
                orgao="Plenário"
            )
        
        assertivas.append({
            "texto": texto_assertiva,
            "resposta": e_verdadeira,
            "explicacao": f"Informativo {informativo}: {resumo_parcial}"
        })
    
    return assertivas

# Função para encontrar registros relevantes para a pergunta
def encontrar_registros_relevantes(pergunta, df, max_registros=3):
    # Palavras-chave para buscar nos dados
    palavras_chave = [palavra.lower() for palavra in pergunta.split() if len(palavra) > 3]
    
    # Se não houver palavras-chave significativas, retornar lista vazia
    if not palavras_chave:
        return []
    
    # Buscar registros relevantes
    registros_relevantes = []
    
    for _, row in df.iterrows():
        pontuacao = 0
        
        # Verificar título
        if pd.notna(row["Título"]):
            for palavra in palavras_chave:
                if palavra in row["Título"].lower():
                    pontuacao += 3  # Peso maior para correspondência no título
        
        # Verificar resumo
        if pd.notna(row["Resumo"]):
            for palavra in palavras_chave:
                if palavra in row["Resumo"].lower():
                    pontuacao += 2
        
        # Verificar matéria
        if pd.notna(row["Matéria"]):
            for palavra in palavras_chave:
                if palavra in row["Matéria"].lower():
                    pontuacao += 1
        
        # Verificar ramo do direito
        if pd.notna(row["Ramo Direito"]):
            for palavra in palavras_chave:
                if palavra in row["Ramo Direito"].lower():
                    pontuacao += 1
        
        # Se houver pontuação, adicionar à lista de registros relevantes
        if pontuacao > 0:
            registros_relevantes.append((pontuacao, row))
    
    # Ordenar por relevância (pontuação)
    registros_relevantes.sort(reverse=True, key=lambda x: x[0])
    
    # Retornar apenas os registros mais relevantes
    return [registro for _, registro in registros_relevantes[:max_registros]]

# Função para criar um contexto baseado nos registros relevantes
def criar_contexto(registros_relevantes):
    if not registros_relevantes:
        return ""
    
    contexto = "Contexto dos informativos do STF:\n\n"
    
    for i, registro in enumerate(registros_relevantes):
        informativo = registro["Informativo"]
        data = registro["Data Julgamento"].strftime("%d/%m/%Y") if pd.notna(registro["Data Julgamento"]) else "data não especificada"
        titulo = registro["Título"] if pd.notna(registro["Título"]) else "Título não disponível"
        
        contexto += f"Informativo {informativo} ({data}): {titulo}\n"
        
        if pd.notna(registro["Resumo"]):
            contexto += f"Resumo: {registro["Resumo"]}\n"
        
        if pd.notna(registro["Tese Julgado"]):
            contexto += f"Tese: {registro["Tese Julgado"]}\n"
        
        contexto += "\n"
    
    return contexto

# Função para simular respostas às perguntas
def simular_resposta(pergunta, df):
    # Buscar registros relevantes
    registros_relevantes = encontrar_registros_relevantes(pergunta, df)
    
    # Se não houver registros relevantes, retornar mensagem
    if not registros_relevantes:
        return "Não encontrei informações específicas sobre essa pergunta nos informativos do STF entre 2021 e 2025."
    
    # Construir resposta com base nos registros mais relevantes
    resposta = "Com base nos informativos do STF, posso informar que:\n\n"
    
    for i, registro in enumerate(registros_relevantes):
        informativo = registro["Informativo"]
        data = registro["Data Julgamento"].strftime("%d/%m/%Y") if pd.notna(registro["Data Julgamento"]) else "data não especificada"
        titulo = registro["Título"] if pd.notna(registro["Título"]) else "Título não disponível"
        
        resposta += f"**Informativo {informativo} ({data})**: {titulo}\n\n"
        
        if pd.notna(registro["Resumo"]):
            resposta += f"{registro["Resumo"]}\n\n"
        elif pd.notna(registro["Tese Julgado"]):
            resposta += f"**Tese**: {registro["Tese Julgado"]}\n\n"
        
        if i < len(registros_relevantes) - 1:
            resposta += "---\n\n"
    
    return resposta

# Função principal
def main():
    # Aplicar estilo
    aplicar_estilo()
    
    # Cabeçalho
    st.markdown('<div class="main-header">Dashboard Informativos STF (2021-2025)</div>', unsafe_allow_html=True)
    
    # Carregar dados
    df = carregar_dados()
    
    if df is None:
        st.error("Não foi possível carregar os dados. Por favor, verifique se o arquivo existe.")
        return
    
    # Sidebar para filtros
    with st.sidebar:
        st.header("Filtros")
        
        # Filtro por Informativo
        informativos = sorted(df["Informativo"].unique())
        informativo_selecionado = st.selectbox("Número do Informativo", 
                                              options=["Todos"] + list(informativos))
        
        # Filtro por Ramo do Direito
        ramos_direito = sorted(df["Ramo Direito"].dropna().unique())
        ramo_selecionado = st.selectbox("Ramo do Direito", 
                                       options=["Todos"] + list(ramos_direito))
        
        # Filtro por Classe Processual
        classes_processo = sorted(df["Classe Processo"].unique())
        classe_selecionada = st.selectbox("Classe Processual", 
                                         options=["Todos"] + list(classes_processo))
        
        # Filtro por Repercussão Geral
        repercussoes = sorted(df["Repercussão Geral"].dropna().unique())
        repercussao_selecionada = st.selectbox("Repercussão Geral", 
                                              options=["Todos"] + list(repercussoes))
        
        # Filtro por Data
        min_date = df["Data Julgamento"].min().date()
        max_date = df["Data Julgamento"].max().date()
        
        data_selecionada = st.date_input(
            "Intervalo de Data",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Barra de pesquisa
        termo_pesquisa = st.text_input("Pesquisar termo", "")
        
        # Botão para limpar filtros
        if st.button("Limpar Filtros"):
            informativo_selecionado = "Todos"
            ramo_selecionado = "Todos"
            classe_selecionada = "Todos"
            repercussao_selecionada = "Todos"
            data_selecionada = (min_date, max_date)
            termo_pesquisa = ""
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    # Filtro por Informativo
    if informativo_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Informativo"] == informativo_selecionado]
    
    # Filtro por Ramo do Direito
    if ramo_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Ramo Direito"] == ramo_selecionado]
    
    # Filtro por Classe Processual
    if classe_selecionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Classe Processo"] == classe_selecionada]
    
    # Filtro por Repercussão Geral
    if repercussao_selecionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Repercussão Geral"] == repercussao_selecionada]
    
    # Filtro por Data
    if len(data_selecionada) == 2:
        start_date, end_date = data_selecionada
        df_filtrado = df_filtrado[(df_filtrado["Data Julgamento"].dt.date >= start_date) & 
                                 (df_filtrado["Data Julgamento"].dt.date <= end_date)]
    
    # Filtro por termo de pesquisa
    if termo_pesquisa:
        mask = (
            df_filtrado["Título"].fillna("").str.contains(termo_pesquisa, case=False) |
            df_filtrado["Resumo"].fillna("").str.contains(termo_pesquisa, case=False) |
            df_filtrado["Matéria"].fillna("").str.contains(termo_pesquisa, case=False) |
            df_filtrado["Tese Julgado"].fillna("").str.contains(termo_pesquisa, case=False)
        )
        df_filtrado = df_filtrado[mask]
    
    # Criar abas para as diferentes seções
    tab1, tab2, tab3, tab4 = st.tabs(["Visualização dos Informativos", "Estatísticas Interativas", 
                                      "Assertivas para Estudo", "Pergunte para a Result"])
    
    # Aba 1: Visualização dos Informativos
    with tab1:
        st.markdown('<div class="sub-header">Visualização dos Informativos</div>', unsafe_allow_html=True)
        
        # Mostrar número de resultados
        st.write(f"Exibindo {len(df_filtrado)} de {len(df)} informativos.")
        
        # Opções de visualização
        visualizacao = st.radio(
            "Modo de visualização:",
            ["Tabela", "Cards de Leitura"],
            horizontal=True
        )
        
        if visualizacao == "Tabela":
            # Tabela interativa
            if not df_filtrado.empty:
                # Formatar a data para exibição
                df_exibicao = df_filtrado.copy()
                df_exibicao["Data Julgamento"] = df_exibicao["Data Julgamento"].dt.strftime("%d/%m/%Y")
                
                # Selecionar colunas para exibição
                colunas_exibicao = ["Informativo", "Classe Processo", "Data Julgamento", "Título", "Ramo Direito", "Matéria"]
                st.dataframe(df_exibicao[colunas_exibicao], use_container_width=True)
                
                # Detalhes do informativo selecionado
                st.markdown('<div class="sub-header">Detalhes do Informativo Selecionado</div>', unsafe_allow_html=True)
                
                # Permitir selecionar um informativo para ver detalhes
                indices = df_exibicao.index.tolist()
                if indices:
                    indice_selecionado = st.selectbox("Selecione um informativo para ver detalhes:", indices)
                    informativo_selecionado = df_exibicao.loc[indice_selecionado]
                    
                    # Exibir detalhes em cards
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f"**Informativo:** {informativo_selecionado['Informativo']}")
                        st.markdown(f"**Classe Processo:** {informativo_selecionado['Classe Processo']}")
                        st.markdown(f"**Data Julgamento:** {informativo_selecionado['Data Julgamento']}")
                        st.markdown(f"**Ramo Direito:** {informativo_selecionado['Ramo Direito']}")
                        st.markdown(f"**Matéria:** {informativo_selecionado['Matéria']}")
                        st.markdown(f"**Repercussão Geral:** {informativo_selecionado['Repercussão Geral']}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f"**Título:** {informativo_selecionado['Título']}")
                        
                        # Verificar se há tese julgada
                        if pd.notna(informativo_selecionado["Tese Julgado"]):
                            st.markdown("**Tese Julgada:**")
                            st.markdown(f"{informativo_selecionado['Tese Julgado']}")
                        
                        # Verificar se há resumo
                        if pd.notna(informativo_selecionado["Resumo"]):
                            st.markdown("**Resumo:**")
                            st.markdown(f"{informativo_selecionado['Resumo']}")
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Nenhum informativo encontrado com os filtros selecionados.")
        
        else:  # Cards de Leitura
            if not df_filtrado.empty:
                # Ordenar por data (mais recente primeiro)
                df_cards = df_filtrado.sort_values(by="Data Julgamento", ascending=False)
                
                # Paginação
                items_por_pagina = 5
                num_paginas = (len(df_cards) + items_por_pagina - 1) // items_por_pagina
                
                if num_paginas > 1:
                    pagina_atual = st.number_input("Página", min_value=1, max_value=num_paginas, value=1) - 1
                    inicio = pagina_atual * items_por_pagina
                    fim = min(inicio + items_por_pagina, len(df_cards))
                    df_pagina = df_cards.iloc[inicio:fim]
                    st.write(f"Mostrando {inicio+1}-{fim} de {len(df_cards)} informativos")
                else:
                    df_pagina = df_cards
                
                # Exibir cards
                for _, row in df_pagina.iterrows():
                    st.markdown(f"""
                    <div class="reading-card">
                        <h3>{row['Título'] if pd.notna(row['Título']) else 'Sem título'}</h3>
                        <div class="reading-card-meta">
                            <strong>Informativo:</strong> {row['Informativo']} | 
                            <strong>Data:</strong> {row['Data Julgamento'].strftime('%d/%m/%Y') if pd.notna(row['Data Julgamento']) else 'Data não disponível'} | 
                            <strong>Classe:</strong> {row['Classe Processo']} | 
                            <strong>Ramo:</strong> {row['Ramo Direito'] if pd.notna(row['Ramo Direito']) else 'Não especificado'}
                        </div>
                        <div class="reading-card-content">
                    """, unsafe_allow_html=True)
                    
                    # Verificar se há tese julgada
                    if pd.notna(row["Tese Julgado"]):
                        st.markdown("<strong>Tese Julgada:</strong>", unsafe_allow_html=True)
                        st.markdown(f"{row['Tese Julgado']}")
                    
                    # Verificar se há resumo
                    if pd.notna(row["Resumo"]):
                        st.markdown("<strong>Resumo:</strong>", unsafe_allow_html=True)
                        st.markdown(f"{row['Resumo']}")
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
            else:
                st.warning("Nenhum informativo encontrado com os filtros selecionados.")
    
    # Aba 2: Estatísticas Interativas
    with tab2:
        st.markdown('<div class="sub-header">Estatísticas Interativas</div>', unsafe_allow_html=True)
        
        # Verificar se há dados suficientes para gerar estatísticas
        if len(df) > 0:
            # Layout em colunas para os gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de distribuição por Ramo do Direito
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Distribuição por Ramo do Direito")
                
                # Contar ocorrências de cada ramo do direito
                ramo_counts = df["Ramo Direito"].value_counts().reset_index()
                ramo_counts.columns = ["Ramo do Direito", "Quantidade"]
                
                # Limitar para os 10 principais ramos
                top_ramos = ramo_counts.head(10)
                
                # Criar gráfico de barras
                fig = px.bar(
                    top_ramos, 
                    x="Quantidade", 
                    y="Ramo do Direito",
                    orientation="h",
                    color="Quantidade",
                    color_continuous_scale="Blues",
                    title="Top 10 Ramos do Direito"
                )
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # Gráfico de distribuição por Repercussão Geral
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Proporção de Casos com Repercussão Geral")
                
                # Contar ocorrências de cada tipo de repercussão geral
                repercussao_counts = df["Repercussão Geral"].value_counts().reset_index()
                repercussao_counts.columns = ["Repercussão Geral", "Quantidade"]
                
                # Criar gráfico de pizza
                fig = px.pie(
                    repercussao_counts, 
                    values="Quantidade", 
                    names="Repercussão Geral",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Gráfico de distribuição por Classe Processual
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Classes Processuais mais Frequentes")
            
            # Contar ocorrências de cada classe processual
            classe_counts = df["Classe Processo"].value_counts().reset_index()
            classe_counts.columns = ["Classe Processual", "Quantidade"]
            
            # Limitar para as 15 principais classes
            top_classes = classe_counts.head(15)
            
            # Criar gráfico de barras
            fig = px.bar(
                top_classes, 
                x="Classe Processual", 
                y="Quantidade",
                color="Quantidade",
                color_continuous_scale="Blues",
                title="Top 15 Classes Processuais"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Gráfico de distribuição por ano
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Distribuição de Informativos por Ano")
            
            # Extrair o ano da data de julgamento
            df["Ano"] = df["Data Julgamento"].dt.year
            
            # Contar ocorrências de cada ano
            ano_counts = df["Ano"].value_counts().sort_index().reset_index()
            ano_counts.columns = ["Ano", "Quantidade"]
            
            # Criar gráfico de linha
            fig = px.line(
                ano_counts, 
                x="Ano", 
                y="Quantidade",
                markers=True,
                line_shape="linear",
                title="Evolução Anual dos Informativos"
            )
            
            fig.update_layout(xaxis=dict(tickmode="linear", dtick=1))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Não há dados suficientes para gerar estatísticas.")
    
    # Aba 3: Assertivas para Estudo
    with tab3:
        st.markdown('<div class="sub-header">Assertivas para Estudo</div>', unsafe_allow_html=True)
        
        # Introdução
        st.markdown("""
        Esta seção apresenta assertivas de verdadeiro ou falso baseadas nos informativos do STF. 
        Teste seus conhecimentos respondendo às questões abaixo.
        """)
        
        # Botão para gerar novas assertivas
        if st.button("Gerar Novas Assertivas"):
            # Limpar estado anterior
            if "assertivas" in st.session_state:
                del st.session_state["assertivas"]
            if "respostas_usuario" in st.session_state:
                del st.session_state["respostas_usuario"]
        
        # Inicializar estado da sessão se necessário
        if "assertivas" not in st.session_state:
            st.session_state.assertivas = gerar_assertivas(df, num_assertivas=5)
        
        if "respostas_usuario" not in st.session_state:
            st.session_state.respostas_usuario = {}
        
        # Exibir assertivas
        for i, assertiva in enumerate(st.session_state.assertivas):
            # Verificar se a assertiva tem resposta (algumas podem ser apenas informativas)
            if assertiva["resposta"] is None:
                st.markdown(f"""
                <div class="assertiva-card">
                    <p>{assertiva['texto']}</p>
                </div>
                """, unsafe_allow_html=True)
                continue
            
            # Determinar a classe CSS com base no estado da resposta
            classe_css = "assertiva-card"
            if i in st.session_state.respostas_usuario:
                if st.session_state.respostas_usuario[i] == assertiva["resposta"]:
                    classe_css += " correct"
                else:
                    classe_css += " incorrect"
            
            st.markdown(f"""
            <div class="{classe_css}">
                <p><strong>Assertiva {i+1}:</strong> {assertiva['texto']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Opções de resposta
            col1, col2, col3 = st.columns([1, 1, 3])
            
            with col1:
                verdadeiro = st.button("Verdadeiro", key=f"v_{i}")
                if verdadeiro:
                    st.session_state.respostas_usuario[i] = True
            
            with col2:
                falso = st.button("Falso", key=f"f_{i}")
                if falso:
                    st.session_state.respostas_usuario[i] = False
            
            # Mostrar feedback se o usuário já respondeu
            if i in st.session_state.respostas_usuario:
                resposta_correta = assertiva["resposta"]
                resposta_usuario = st.session_state.respostas_usuario[i]
                
                if resposta_usuario == resposta_correta:
                    st.markdown(f"""
                    <div class="feedback-correct">
                        ✓ Correto! {assertiva['explicacao']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="feedback-incorrect">
                        ✗ Incorreto. A resposta correta é {"Verdadeiro" if resposta_correta else "Falso"}.
                        {assertiva['explicacao']}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)
        
        # Mostrar pontuação
        if st.session_state.respostas_usuario:
            acertos = sum(1 for i, resposta in st.session_state.respostas_usuario.items() 
                         if resposta == st.session_state.assertivas[i]["resposta"])
            total = len(st.session_state.respostas_usuario)
            
            st.markdown(f"""
            <div class="card">
                <h3>Pontuação Atual</h3>
                <p>Você acertou {acertos} de {total} assertivas ({acertos/total*100:.1f}%).</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Aba 4: Pergunte para a Result
    with tab4:
        st.markdown('<div class="sub-header">Pergunte para a Result</div>', unsafe_allow_html=True)
        
        st.markdown("""
        Nesta seção, você pode fazer perguntas sobre os informativos do STF e receber respostas baseadas nos dados disponíveis.
        
        **Exemplos de perguntas que você pode fazer:**
        - Quais são as principais teses sobre direito tributário julgadas em 2023?
        - Resumir os informativos sobre direito administrativo com repercussão geral reconhecida.
        - Explicar a tese do informativo sobre matéria constitucional.
        """)
        
        # Campo de entrada para a pergunta
        pergunta = st.text_input("Digite sua pergunta sobre os informativos do STF:", placeholder="Ex: Quais são as principais teses sobre direito tributário?")
        
        # Botão para enviar a pergunta
        if st.button("Enviar Pergunta"):
            if pergunta:
                with st.spinner("Analisando sua pergunta..."):
                    # Simular um pequeno atraso para dar a impressão de processamento
                    import time
                    time.sleep(1)
                    
                    # Obter resposta simulada
                    resposta = simular_resposta(pergunta, df)
                    
                    # Exibir a resposta
                    st.markdown(f"""
                    <div class="question-card">
                        <strong>Sua pergunta:</strong> {pergunta}
                    </div>
                    <div class="answer-card">
                        <strong>Resposta:</strong><br>
                        {resposta}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Por favor, digite uma pergunta para continuar.")
    
    # Rodapé
    st.markdown('<div class="footer">Dashboard Informativos STF © 2025</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
