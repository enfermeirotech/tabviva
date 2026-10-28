import json

import pandas as pd
import streamlit as st
import plotly.express as px

# --------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------
st.set_page_config(
    page_title="TABVIVA - Tabulador de Notificação de Violência Interpessoal",
    layout="wide"
)

st.title("TABVIVA - Tabulador de Notificação de Violência Interpessoal")
st.markdown("---")

# --------------------------------------
# CAMINHOS DOS ARQUIVOS
# --------------------------------------
CAMINHO_VIOLBR = r"dados/VIOLBR.parquet"
CAMINHO_MUNICIPIOS = r"dimensoes/dim_regiao.parquet"
CAMINHO_GEOJSON = r"dimensoes/geo_pa_municipios.json"
CAMINHO_POPULACAO = r"populacao/pop_svs.csv"

df_violbr = pd.read_parquet(CAMINHO_VIOLBR)
df_municipios = pd.read_parquet(CAMINHO_MUNICIPIOS)

# --------------------------------------
# MERGE DOS DATAFRAMES
# --------------------------------------
df = df_violbr.merge(
    df_municipios,
    left_on="Código do município",
    right_on="mun_cod",
    how="left"
)

# mun_cod é mantido: é a chave de junção com a malha municipal do IBGE no mapa
df = df.drop(columns=["Código do município"])

# --------------------------------------
# OPÇÕES DE FILTRO
# --------------------------------------
TEMPO = [df["Ano"].min(), df["Ano"].max()]

SEXOS = ["Feminino", "Masculino", "Ignorado", "Em branco"]

ORIENTACAO = ["Heterossexual", "Homossexual (Gay/Lésbica)", "Bissexual", "Não se aplica", "Ignorado"]

IDENTIDADE = ["Travesti", "Transexual Mulher", "Transexual Homem", "Não se aplica", "Ignorado"]

RACA = ["Branca", "Preta", "Amarela", "Parda", "Indígena", "Ignorado", "Em branco"]

FAIXA = [
    "IGNORADO", "00 a < 01 ano", "01 a 04 anos", "05 a 09 anos", "10 a 14 anos",
    "15 a 19 anos", "20 a 29 anos", "30 a 39 anos", "40 a 49 anos",
    "50 a 59 anos", "60 a 69 anos", "70 a 79 anos", "Mais de 80 anos"
]

TIPOS_VIOLENCIA = [
    "Física", "Psicológica", "Tortura", "Sexual",
    "Tráfico de seres humanos", "Financeira", "Negligência",
    "Trabalho infantil", "Intervenção legal", "Outras violências"
]

TIPOS_VIOLENCIA_SEXUAL = [
    "Assédio sexual", "Estupro", "Pornografia infantil",
    "Exploração sexual", "Outro tipo de violência sexual"
]

# --------------------------------------
# FUNÇÃO AUXILIAR PARA FILTROS
# --------------------------------------
def aplicar_filtros(df, filtro, coluna):
    if filtro:
        return df[df[coluna].isin(filtro)]
    return df

def aplicar_filtro_booleano(df, filtro_cols):
    if filtro_cols:
        mask = df[filtro_cols].any(axis=1)
        return df[mask]
    return df

# --------------------------------------
# BASES DE APOIO DO MAPA (carregadas sob demanda)
# --------------------------------------
# Faixas etárias em anos completos, para casar a população (que vem em idade
# simples) com a coluna "Faixa etária" das notificações.
FAIXAS_POPULACAO = [
    "00 a < 01 ano", "01 a 04 anos", "05 a 09 anos", "10 a 14 anos",
    "15 a 19 anos", "20 a 29 anos", "30 a 39 anos", "40 a 49 anos",
    "50 a 59 anos", "60 a 69 anos", "70 a 79 anos", "Mais de 80 anos"
]

LIMITES_IDADE = [-1, 0, 4, 9, 14, 19, 29, 39, 49, 59, 69, 79, 10**6]

# Enquadramento do mapa: centro da malha do Pará (lat -9,84 a 2,59 / lon -58,90 a
# -46,06). No zoom 4.7 a altura de 620px cobre ~16,7° de latitude, com folga sobre
# os 12,4° do estado.
CENTRO_PARA = {"lat": -3.63, "lon": -52.48}
ZOOM_PARA = 4.7


@st.cache_data(show_spinner="Carregando malha municipal...")
def carregar_geojson(caminho):
    """Malha municipal do Pará (IBGE). O campo 'id' é o código de 6 dígitos."""
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


@st.cache_data(show_spinner="Carregando base populacional...")
def carregar_populacao(caminho):
    """População por município/ano/sexo/faixa etária, para o cálculo de taxas."""
    pop = pd.read_csv(
        caminho,
        usecols=["mun_cod", "ano", "sexo_sigla", "idade", "qtd_pop"]
    )
    pop["Faixa etária"] = pd.cut(
        pop["idade"],
        bins=LIMITES_IDADE,
        labels=FAIXAS_POPULACAO,
        ordered=False
    )
    pop["Sexo"] = pop["sexo_sigla"].map({"F": "Feminino", "M": "Masculino"})

    return (
        pop.groupby(["mun_cod", "ano", "Sexo", "Faixa etária"], observed=True)["qtd_pop"]
        .sum()
        .reset_index()
    )

# --------------------------------------
# SIDEBAR - FILTROS DEMOGRÁFICOS
# --------------------------------------
with st.sidebar:
    st.header("Filtros Demográficos")
    with st.form("Filtros"):
        filtro_tempo = st.slider(
            "Selecione o intervalo de anos",
            min_value=TEMPO[0],
            max_value=TEMPO[1],
            value=(TEMPO[0], TEMPO[1])
        )

        filtro_sexo = st.multiselect(
            "Sexo",
            options=SEXOS
        )

        filtro_orientacao = st.multiselect(
            "Orientação Sexual",
            options=ORIENTACAO
        )

        filtro_identidade = st.multiselect(
            "Identidade de gênero",
            options=IDENTIDADE
        )

        filtro_raca = st.multiselect(
            "Raça/Cor",
            options=RACA
        )

        filtro_faixa = st.multiselect(
            "Faixa Etária",
            options=FAIXA
        )

        st.divider()
        st.subheader("Tipo de Violência")

        filtro_tipo_violencia = st.multiselect(
            "Tipo de Violência",
            options=TIPOS_VIOLENCIA,
            help="Filtra registros com pelo menos um dos tipos selecionados marcado como verdadeiro."
        )

        filtro_tipo_violencia_sexual = st.multiselect(
            "Tipo de Violência Sexual",
            options=TIPOS_VIOLENCIA_SEXUAL,
            help="Filtra registros com pelo menos um dos subtipos sexuais selecionados marcado como verdadeiro."
        )

        submitted_sidebar = st.form_submit_button("Aplicar Filtros")

# -----------------------
# FILTROS DE LOCALIDADE
# -----------------------
st.header("Filtros de Localidade")

if 'filtros_localidade_aplicados' not in st.session_state:
    st.session_state.filtros_localidade_aplicados = False

with st.form("Localidade"):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filtro_municipio = st.multiselect(
            "Município",
            options=sorted(df["mun_nome"].dropna().unique())
        )
    with col2:
        filtro_uf = st.multiselect(
            "UF",
            options=sorted(df["uf_sigla"].dropna().unique())
        )
    with col3:
        filtro_macro = st.multiselect(
            "Macro Região de Saúde",
            options=sorted(df["macro_reg_saude_nome"].dropna().unique())
        )
    with col4:
        filtro_regiao = st.multiselect(
            "Região de Integração",
            options=sorted(df["reg_integracao_nome"].dropna().unique())
        )
    
    submitted_localidade = st.form_submit_button("Aplicar Filtros")

# --------------------------------------
# APLICAÇÃO DOS FILTROS E EXIBIÇÃO
# --------------------------------------
df_filtrado = df.copy()

# Aplicar filtros demográficos (sidebar)
if submitted_sidebar or st.session_state.get('filtros_demograficos_aplicados', False):
    st.session_state.filtros_demograficos_aplicados = True
    
    df_filtrado = df_filtrado[
        (df_filtrado["Ano"] >= filtro_tempo[0]) & 
        (df_filtrado["Ano"] <= filtro_tempo[1])
    ]
    df_filtrado = aplicar_filtros(df_filtrado, filtro_sexo, "Sexo")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_orientacao, "Orientação sexual")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_identidade, "Identidade de gênero")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_raca, "Raça/Cor")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_faixa, "Faixa etária")

    # Filtros booleanos de violência
    df_filtrado = aplicar_filtro_booleano(df_filtrado, filtro_tipo_violencia)
    df_filtrado = aplicar_filtro_booleano(df_filtrado, filtro_tipo_violencia_sexual)

# Aplicar filtros de localidade
if submitted_localidade or st.session_state.get('filtros_localidade_aplicados', False):
    st.session_state.filtros_localidade_aplicados = True
    
    df_filtrado = aplicar_filtros(df_filtrado, filtro_municipio, "mun_nome")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_uf, "uf_sigla")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_macro, "macro_reg_saude_nome")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_regiao, "reg_integracao_nome")

# --------------------------------------
# EXIBIÇÃO DOS RESULTADOS
# --------------------------------------
st.markdown("---")
st.header("Dados Filtrados")

# Métricas
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("Total de Registros", f"{len(df_filtrado):,}", border=True)
with col_m2:
    st.metric("Registros Originais", f"{len(df):,}", border=True)
with col_m3:
    percentual = (len(df_filtrado) / len(df) * 100) if len(df) > 0 else 0
    st.metric("Percentual Filtrado", f"{percentual:.1f}%", border=True)
with col_m4:
    anos_unicos = df_filtrado["Ano"].nunique() if len(df_filtrado) > 0 else 0
    st.metric("Anos no Filtro", anos_unicos, border=True)

# Exibir o dataframe
st.dataframe(df_filtrado, height=500)

# Botão para limpar filtros
if st.button("Limpar Todos os Filtros"):
    st.session_state.filtros_demograficos_aplicados = False
    st.session_state.filtros_localidade_aplicados = False
    st.rerun()

# --------------------------------------
# MAPA: distribuição geográfica das notificações
# --------------------------------------
st.markdown("---")
st.subheader("Distribuição geográfica das notificações")

if len(df_filtrado) > 0:

    col_metrica, col_visual = st.columns(2)

    with col_metrica:
        metrica_mapa = st.radio(
            "Métrica do mapa",
            options=["Nº de notificações", "Taxa por 100 mil hab."],
            horizontal=True,
            label_visibility="collapsed"
        )

    with col_visual:
        visualizacao_mapa = st.radio(
            "Visualização mapa",
            options=["Coroplético", "Bolhas", "Tabela"],
            horizontal=True,
            label_visibility="collapsed"
        )

    # Códigos negativos são sentinelas da dimensão (Não se aplica / Em branco /
    # Não encontrado) e não possuem geometria.
    df_geo = df_filtrado[df_filtrado["mun_cod"] > 0]

    if len(df_geo) == 0:
        st.info("Nenhum registro com município do Pará identificado nos filtros selecionados.")

    else:
        df_mapa = (
            df_geo.groupby(
                ["mun_cod", "mun_nome", "mun_lat", "mun_lon",
                 "macro_reg_saude_nome", "reg_integracao_nome"],
                observed=True
            )
            .size()
            .reset_index(name="Nº de notificações")
        )

        anos_sem_populacao = []
        colunas_hover = ["macro_reg_saude_nome", "reg_integracao_nome"]

        if metrica_mapa == "Taxa por 100 mil hab.":
            populacao = carregar_populacao(CAMINHO_POPULACAO)

            # O denominador acompanha os filtros de ano, sexo e faixa etária
            anos_notificacao = set(df_geo["Ano"].unique())
            anos_validos = sorted(anos_notificacao & set(populacao["ano"].unique()))
            anos_sem_populacao = sorted(anos_notificacao - set(anos_validos))

            sexos_validos = [
                s for s in df_geo["Sexo"].unique() if s in ("Feminino", "Masculino")
            ] or ["Feminino", "Masculino"]

            faixas_validas = [
                f for f in df_geo["Faixa etária"].unique() if f in FAIXAS_POPULACAO
            ] or FAIXAS_POPULACAO

            denominador = (
                populacao[
                    populacao["ano"].isin(anos_validos)
                    & populacao["Sexo"].isin(sexos_validos)
                    & populacao["Faixa etária"].isin(faixas_validas)
                ]
                .groupby("mun_cod")["qtd_pop"]
                .sum()
                .reset_index(name="Pessoas-ano")
            )

            # Numerador restrito aos mesmos anos cobertos pelo denominador
            numerador = (
                df_geo[df_geo["Ano"].isin(anos_validos)]
                .groupby("mun_cod")
                .size()
                .reset_index(name="Notificações no período")
            )

            df_mapa = df_mapa.merge(numerador, on="mun_cod", how="left")
            df_mapa = df_mapa.merge(denominador, on="mun_cod", how="left")
            df_mapa["Notificações no período"] = df_mapa["Notificações no período"].fillna(0)

            df_mapa = df_mapa[df_mapa["Pessoas-ano"].notna() & (df_mapa["Pessoas-ano"] > 0)]
            df_mapa["Taxa por 100 mil hab."] = (
                df_mapa["Notificações no período"] / df_mapa["Pessoas-ano"] * 100000
            )

            colunas_hover += ["Notificações no período", "Pessoas-ano"]

        coluna_valor = metrica_mapa
        formato_valor = ",.0f" if coluna_valor == "Nº de notificações" else ",.1f"

        if len(df_mapa) == 0:
            st.info("Não há população de referência para o recorte selecionado.")

        elif visualizacao_mapa in ("Coroplético", "Bolhas"):

            hover_extra = (
                "<br>Notificações: %{customdata[2]:,.0f}"
                "<br>População (pessoas-ano): %{customdata[3]:,.0f}"
                if coluna_valor == "Taxa por 100 mil hab." else ""
            )

            hovertemplate = (
                "<b>%{hovertext}</b>"
                "<br>Macro de saúde: %{customdata[0]}"
                "<br>Região de integração: %{customdata[1]}"
                + hover_extra
                + "<extra></extra>"
            )

            if visualizacao_mapa == "Coroplético":
                geojson_pa = carregar_geojson(CAMINHO_GEOJSON)

                fig_mapa = px.choropleth_map(
                    df_mapa,
                    geojson=geojson_pa,
                    locations=df_mapa["mun_cod"].astype(str),
                    featureidkey="id",
                    color=coluna_valor,
                    hover_name="mun_nome",
                    custom_data=colunas_hover,
                    color_continuous_scale="Teal",
                    map_style="carto-positron",
                    center=CENTRO_PARA,
                    zoom=ZOOM_PARA,
                    opacity=0.85
                )
                fig_mapa.update_traces(
                    marker_line_width=0.4,
                    marker_line_color="white",
                    hovertemplate=(
                        f"<b>%{{hovertext}}</b><br>{coluna_valor}: %{{z:{formato_valor}}}"
                        + hovertemplate.split("</b>", 1)[1]
                    )
                )

            else:
                fig_mapa = px.scatter_map(
                    df_mapa,
                    lat="mun_lat",
                    lon="mun_lon",
                    size=coluna_valor,
                    color=coluna_valor,
                    hover_name="mun_nome",
                    custom_data=colunas_hover,
                    color_continuous_scale="Teal",
                    map_style="carto-positron",
                    center=CENTRO_PARA,
                    zoom=ZOOM_PARA,
                    size_max=38
                )
                fig_mapa.update_traces(
                    hovertemplate=(
                        f"<b>%{{hovertext}}</b><br>{coluna_valor}: "
                        f"%{{marker.color:{formato_valor}}}"
                        + hovertemplate.split("</b>", 1)[1]
                    )
                )

            fig_mapa.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=620,
                coloraxis_colorbar=dict(
                    title=coluna_valor.replace(" por ", "<br>por "),
                    tickformat=","
                )
            )
            st.plotly_chart(fig_mapa, width='stretch')

            if coluna_valor == "Taxa por 100 mil hab.":
                legenda = (
                    "Taxa calculada sobre pessoas-ano (população SVS somada nos anos do "
                    "recorte). O denominador acompanha os filtros de ano, sexo e faixa "
                    "etária, mas **não** os de raça/cor, orientação sexual e identidade "
                    "de gênero, que não existem na base populacional."
                )
                if anos_sem_populacao:
                    legenda += (
                        "  \nAnos sem população de referência, excluídos do cálculo: "
                        + ", ".join(str(a) for a in anos_sem_populacao) + "."
                    )
            else:
                legenda = (
                    "Contagem absoluta por município de residência. Municípios populosos "
                    "concentram volume por tamanho — use a taxa por 100 mil habitantes "
                    "para comparar municípios entre si."
                )

            registros_fora = len(df_filtrado) - len(df_geo)
            if registros_fora > 0:
                legenda += (
                    f"  \n{registros_fora:,} registro(s) sem município do Pará "
                    "identificado ficaram fora do mapa."
                )

            st.caption(legenda)

        else:
            df_mapa_tab = (
                df_mapa[["mun_nome", "macro_reg_saude_nome",
                         "reg_integracao_nome", coluna_valor]]
                .sort_values(coluna_valor, ascending=False)
                .rename(columns={
                    "mun_nome": "Município",
                    "macro_reg_saude_nome": "Macro Região de Saúde",
                    "reg_integracao_nome": "Região de Integração"
                })
            )
            casas = 0 if coluna_valor == "Nº de notificações" else 1
            df_mapa_tab[coluna_valor] = df_mapa_tab[coluna_valor].map(
                lambda x: f"{x:,.{casas}f}"
            )
            st.dataframe(df_mapa_tab, hide_index=True, width='stretch')

else:
    st.info("Nenhum dado disponível para os filtros selecionados.")

# --------------------------------------
# GRÁFICO: Ranking de tipos de violência
# --------------------------------------
st.markdown("---")
st.subheader("Ranking de tipos de violência")

if len(df_filtrado) > 0:
    df_ranking = pd.DataFrame({
        "Tipo": TIPOS_VIOLENCIA,
        "Notificações": [int(df_filtrado[t].sum()) for t in TIPOS_VIOLENCIA]
    })
    total_notif = len(df_filtrado)
    df_ranking["% do total"] = df_ranking["Notificações"] / total_notif * 100
    df_ranking = df_ranking.sort_values("Notificações", ascending=True)

    visualizacao_ranking = st.radio(
        "Visualização ranking",
        options=["Gráfico", "Tabela"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if visualizacao_ranking == "Gráfico":
        fig_ranking = px.bar(
            df_ranking,
            x="Notificações",
            y="Tipo",
            orientation="h",
            text="Notificações",
            color="Notificações",
            color_continuous_scale="Teal",
            template="plotly_white",
            labels={"Tipo": "", "Notificações": "Total de notificações"},
            custom_data=["% do total"]
        )
        fig_ranking.update_traces(
            texttemplate="%{x:,.0f}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Notificações: %{x:,.0f}<br>"
                "Participação: %{customdata[0]:.1f}%<extra></extra>"
            )
        )
        fig_ranking.update_layout(
            xaxis=dict(tickformat=",", title="Total de notificações"),
            coloraxis_showscale=False,
            margin=dict(t=40, b=40, l=20, r=60),
            height=460
        )
        st.plotly_chart(fig_ranking, width='stretch')

        st.caption(
            "Cada registro pode ter mais de um tipo marcado, por isso a soma dos "
            "valores pode exceder o total de registros filtrados."
        )

    else:
        df_ranking_tab = df_ranking.sort_values("Notificações", ascending=False).copy()
        df_ranking_tab["% do total"] = df_ranking_tab["% do total"].map(lambda x: f"{x:.1f}%")
        df_ranking_tab["Notificações"] = df_ranking_tab["Notificações"].map(lambda x: f"{x:,}")
        st.dataframe(df_ranking_tab, hide_index=True, width='stretch')

else:
    st.info("Nenhum dado disponível para os filtros selecionados.")


col1, col2 = st.columns(2)

with col1:
    # --------------------------------------
    # GRÁFICO 1: Série temporal por ano
    # --------------------------------------
    st.markdown("---")
    st.subheader("Notificações por ano")

    if len(df_filtrado) > 0:
        df_ano = (
            df_filtrado
            .groupby("Ano")
            .size()
            .reset_index(name="Notificações")
        )
        df_ano["Variação (%)"] = df_ano["Notificações"].pct_change() * 100

        # Seletor de visualização
        visualizacao = st.radio(
            "Visualização",
            options=["Gráfico", "Tabela de variação"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if visualizacao == "Gráfico":
            fig_linha = px.line(
                df_ano,
                x="Ano",
                y="Notificações",
                markers=True,
                labels={"Ano": "Ano", "Notificações": "Total de notificações"},
                template="plotly_white"
            )
            fig_linha.update_traces(
                line=dict(width=2.5, color="#1D9E75"),
                marker=dict(size=8, color="#1D9E75"),
                hovertemplate="<b>Ano: %{x}</b><br>Notificações: %{y:,.0f}<extra></extra>"
            )
            fig_linha.update_layout(
                xaxis=dict(tickmode="linear", dtick=1),
                yaxis=dict(tickformat=","),
                hovermode="x unified",
                margin=dict(t=50, b=40, l=60, r=20)
            )
            st.plotly_chart(fig_linha, width='stretch')

        else:
            df_tabela = df_ano.copy()
            df_tabela["Variação (%)"] = df_tabela["Variação (%)"].map(
                lambda x: f"+{x:.1f}%" if x > 0 else f"{x:.1f}%" if pd.notna(x) else "—"
            )
            df_tabela["Notificações"] = df_tabela["Notificações"].map(lambda x: f"{x:,}")
            st.dataframe(df_tabela, hide_index=True, width='stretch')

    else:
        st.info("Nenhum dado disponível para os filtros selecionados.")

with col2:
    # --------------------------------------
    # GRÁFICO 2: Pirâmide etária por sexo
    # --------------------------------------
    st.markdown("---")
    st.subheader("Pirâmide etária por sexo")

    if len(df_filtrado) > 0:

        # Filtrar apenas Feminino e Masculino
        df_piramide = (
            df_filtrado[df_filtrado["Sexo"].isin(["Feminino", "Masculino"])]
            .groupby(["Faixa etária", "Sexo"])
            .size()
            .reset_index(name="Contagem")
        )

        # Garantir ordem correta das faixas
        df_piramide["Faixa etária"] = pd.Categorical(
            df_piramide["Faixa etária"],
            categories=FAIXA,
            ordered=True
        )
        df_piramide = df_piramide.sort_values("Faixa etária")

        # Masculino vai para o lado negativo (esquerda)
        df_piramide.loc[df_piramide["Sexo"] == "Masculino", "Contagem"] *= -1

        visualizacao_piramide = st.radio(
            "Visualização pirâmide",
            options=["Gráfico", "Tabela"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if visualizacao_piramide == "Gráfico":
            fig_piramide = px.bar(
                df_piramide,
                x="Contagem",
                y="Faixa etária",
                color="Sexo",
                orientation="h",
                color_discrete_map={
                    "Feminino": "#D4537E",
                    "Masculino": "#378ADD"
                },
                template="plotly_white",
                labels={"Faixa etária": "", "Contagem": "Notificações", "Sexo": "Sexo"}
            )

            # Formatar eixo X para mostrar valores absolutos no hover e no eixo
            max_val = df_piramide["Contagem"].abs().max()
            tick_step = max(1, round(max_val / 5, -2))  # ~5 ticks no eixo

            fig_piramide.update_layout(
                xaxis=dict(
                    tickvals=[-4*tick_step, -3*tick_step, -2*tick_step, -tick_step, 0, tick_step, 2*tick_step, 3*tick_step, 4*tick_step],
                    ticktext=[f"{4*tick_step:,.0f}", f"{3*tick_step:,.0f}", f"{2*tick_step:,.0f}", f"{tick_step:,.0f}", "0", f"{tick_step:,.0f}", f"{2*tick_step:,.0f}", f"{3*tick_step:,.0f}", f"{4*tick_step:,.0f}"],
                    title="Notificações"
                ),
                barmode="relative",
                bargap=0.1,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                margin=dict(t=60, b=40, l=120, r=20),
                hovermode="y unified"
            )

            # Hover mostra valor absoluto
            fig_piramide.update_traces(
                hovertemplate="%{customdata[0]}: %{x:,.0f}<extra></extra>",
                customdata=df_piramide[["Sexo"]].values
            )
            fig_piramide.for_each_trace(
                lambda t: t.update(
                    hovertemplate=f"{t.name}: %{{x:,.0f}}<extra></extra>"
                    if t.name == "Feminino"
                    else f"{t.name}: %{{x:,.0f}}<extra></extra>"
                )
            )

            # Corrigir hover do Masculino (valores negativos → mostrar positivo)
            for trace in fig_piramide.data:
                if trace.name == "Masculino":
                    trace.customdata = abs(df_piramide[df_piramide["Sexo"] == "Masculino"]["Contagem"].values).reshape(-1, 1)
                    trace.hovertemplate = "Masculino: %{customdata[0]:,.0f}<extra></extra>"

            st.plotly_chart(fig_piramide, width='stretch')

        else:
            # Tabela com valores absolutos lado a lado
            df_tab_piramide = (
                df_filtrado[df_filtrado["Sexo"].isin(["Feminino", "Masculino"])]
                .groupby(["Faixa etária", "Sexo"])
                .size()
                .unstack(fill_value=0)
                .reindex(FAIXA)
                .reset_index()
            )
            df_tab_piramide.columns.name = None

            # Adicionar total e proporção
            df_tab_piramide["Total"] = df_tab_piramide.get("Feminino", 0) + df_tab_piramide.get("Masculino", 0)
            if "Feminino" in df_tab_piramide.columns:
                df_tab_piramide["% Feminino"] = (df_tab_piramide["Feminino"] / df_tab_piramide["Total"] * 100).map(lambda x: f"{x:.1f}%")
            if "Masculino" in df_tab_piramide.columns:
                df_tab_piramide["% Masculino"] = (df_tab_piramide["Masculino"] / df_tab_piramide["Total"] * 100).map(lambda x: f"{x:.1f}%")

            df_tab_piramide = df_tab_piramide.rename(columns={"Faixa etária": "Faixa Etária"})
            st.dataframe(df_tab_piramide, hide_index=True, width='stretch')

    else:
        st.info("Nenhum dado disponível para os filtros selecionados.")


# --------------------------------------
# GRÁFICO 3: Heatmap de coocorrência entre subtipos de violência sexual
# --------------------------------------
st.markdown("---")
st.subheader("Coocorrência entre subtipos de violência sexual")

if len(df_filtrado) > 0:

    # Nomes curtos para o heatmap (evitar rótulos longos)
    NOMES_CURTOS = {
        "Assédio sexual":                  "Assédio",
        "Estupro":                         "Estupro",
        "Pornografia infantil":            "Pornografia",
        "Exploração sexual":               "Exploração",
        "Outro tipo de violência sexual":  "Outro"
    }

    cols_sexual = list(NOMES_CURTOS.keys())

    # Filtrar apenas registros com pelo menos um subtipo marcado
    df_sexual = df_filtrado[df_filtrado[cols_sexual].any(axis=1)][cols_sexual].copy()

    visualizacao_heat = st.radio(
        "Visualização heatmap",
        options=["Gráfico", "Tabela"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if visualizacao_heat == "Gráfico":
        if len(df_sexual) == 0:
            st.info("Nenhum registro com subtipo de violência sexual nos filtros selecionados.")
        else:
            # Calcular coocorrência relativa: % dos casos de A que também têm B
            n = len(cols_sexual)
            matriz = pd.DataFrame(index=cols_sexual, columns=cols_sexual, dtype=float)

            for col_a in cols_sexual:
                total_a = df_sexual[col_a].sum()
                for col_b in cols_sexual:
                    if total_a == 0:
                        matriz.loc[col_a, col_b] = 0.0
                    else:
                        cooc = (df_sexual[col_a] & df_sexual[col_b]).sum()
                        matriz.loc[col_a, col_b] = round(cooc / total_a * 100, 1)

            # Renomear para nomes curtos
            matriz.index = [NOMES_CURTOS[c] for c in cols_sexual]
            matriz.columns = [NOMES_CURTOS[c] for c in cols_sexual]

            # Texto de anotação dentro de cada célula
            text_matrix = matriz.map(
                lambda v: "100%" if v == 100 else f"{v:.1f}%"
            )

            fig_heat = px.imshow(
                matriz.values,
                x=list(matriz.columns),
                y=list(matriz.index),
                color_continuous_scale="Teal",
                zmin=0,
                zmax=100,
                text_auto=False,
                template="plotly_white",
                labels={"color": "Coocorrência (%)"}
            )

            # Adicionar anotações manuais com % em cada célula
            annotations = []
            for i, row in enumerate(matriz.index):
                for j, col in enumerate(matriz.columns):
                    val = matriz.iloc[i, j]
                    cor_texto = "white" if val > 55 else "black"
                    annotations.append(dict(
                        x=col, y=row,
                        text=f"{val:.1f}%",
                        showarrow=False,
                        font=dict(size=13, color=cor_texto)
                    ))

            fig_heat.update_layout(
                annotations=annotations,
                xaxis=dict(side="bottom", title="Também tem →"),
                yaxis=dict(title="Dado que tem →"),
                coloraxis_colorbar=dict(
                    tickformat=".0f",
                    ticksuffix="%",
                    title="Coocorr. (%)"
                ),
                margin=dict(t=40, b=80, l=100, r=40),
                height=420
            )

            st.plotly_chart(fig_heat, width='stretch')

            st.caption(
                "Leitura: cada célula mostra o % dos casos da linha que também têm o tipo da coluna. "
                "A diagonal sempre vale 100% (um tipo sempre coocorre consigo mesmo)."
            )

    else:
        # Tabela da matriz de coocorrência
        if len(df_sexual) == 0:
            st.info("Nenhum registro com subtipo de violência sexual nos filtros selecionados.")
        else:
            matriz_tab = pd.DataFrame(index=cols_sexual, columns=cols_sexual, dtype=float)
            for col_a in cols_sexual:
                total_a = df_sexual[col_a].sum()
                for col_b in cols_sexual:
                    if total_a == 0:
                        matriz_tab.loc[col_a, col_b] = 0.0
                    else:
                        cooc = (df_sexual[col_a] & df_sexual[col_b]).sum()
                        matriz_tab.loc[col_a, col_b] = round(cooc / total_a * 100, 1)

            matriz_tab.index = [NOMES_CURTOS[c] for c in cols_sexual]
            matriz_tab.columns = [NOMES_CURTOS[c] for c in cols_sexual]
            matriz_tab = matriz_tab.map(lambda v: f"{v:.1f}%")
            matriz_tab.insert(0, "Dado que tem →", matriz_tab.index)

            st.dataframe(matriz_tab, hide_index=True, width='stretch')
            st.caption(
                "Leitura: cada célula mostra o % dos casos da linha que também têm o tipo da coluna."
            )

else:
    st.info("Nenhum dado disponível para os filtros selecionados.")