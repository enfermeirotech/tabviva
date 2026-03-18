import pandas as pd
import streamlit as st

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

df_violbr = pd.read_parquet(CAMINHO_VIOLBR)
df_municipios = pd.read_parquet(CAMINHO_MUNICIPIOS)

# --------------------------------------
# MERGE DOS DATAFRAMES
# --------------------------------------
df = df_violbr.merge(
    df_municipios,
    left_on="ID_MUNICIP",
    right_on="mun_cod",
    how="left"
)

df = df.drop(columns=["ID_MUNICIP", "mun_cod"])

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
    df_filtrado = aplicar_filtros(df_filtrado, filtro_sexo, "CS_SEXO")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_orientacao, "ORIENT_SEX")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_identidade, "IDENT_GEN")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_raca, "CS_RACA")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_faixa, "FAIXA_ETARIA")

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