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
# COLUNAS DISPONÍVEIS
# --------------------------------------
# Index(['DT_NOTIFIC', 'NU_IDADE_N', 'CS_SEXO', 'CS_RACA', 'ORIENT_SEX',
#        'IDENT_GEN', 'Física', 'Psicológica', 'Tortura', 'Sexual',
#        'Tráfico de seres humanos', 'Financeira', 'Negligência',
#        'Trabalho infantil', 'Intervenção legal', 'Outras violências',
#        'Assédio sexual', 'Estupro', 'Pornografia infantil',
#        'Exploração sexual', 'Outro tipo de violência sexual', 'Ano', 'Mês',
#        'Faixa etária', 'mun_nome', 'uf_sigla', 'uf_nome',
#        'macro_reg_saude_abrv', 'macro_reg_saude_nome', 'reg_integracao_nome'],
#       dtype='object')

# --------------------------------------
# SIDEBAR
# --------------------------------------
# ------------Opções de filtro para a sidebar----------------
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

# ------------Seleção dos filtros na sidebar----------------
with st.sidebar:
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

        submitted_sidebar = st.form_submit_button("Submit")

    if submitted_sidebar:
        st.write("Intervalo de anos:", filtro_tempo)
        st.write("Sexo:", filtro_sexo)
        st.write("Orientação Sexual:", filtro_orientacao)
        st.write("Identidade de Gênero:", filtro_identidade)
        st.write("Raça/Cor:", filtro_raca)
        st.write("Faixa Etária:", filtro_faixa)


# -----------------------
# DIVISÃO POR LOCALIDADE
# -----------------------
col1, col2, col3, col4 = st.columns(4)

with st.form("Localidade"):
    with col1:
        filtro_minicipio = st.multiselect(
            "Município",
            options=df["mun_nome"].unique()
        )
    with col2:
        filtro_uf = st.multiselect(
            "UF",
            options=df["uf_sigla"].unique()
        )
    with col3:
        filtro_macro = st.multiselect(
            "Macro Região de Saúde",
            options=df["macro_reg_saude_nome"].unique()
        )
    with col4:
        filtro_regiao = st.multiselect(
            "Região de Integração",
            options=df["reg_integracao_nome"].unique()
        )
    submitted_localidade = st.form_submit_button("Submit")


# ------------------------------------------
# APLICAÇÃO DOS FILTROS E EXIBIÇÃO DOS DADOS
# ------------------------------------------
def aplicar_filtros(df, filtro, coluna):
    if filtro:
        return df[df[coluna].isin(filtro)]
    return df

if submitted_sidebar:
    df_filtrado = df

    df_filtrado = df_filtrado[(df_filtrado["Ano"] >= filtro_tempo[0]) & (df_filtrado["Ano"] <= filtro_tempo[1])]
    df_filtrado = aplicar_filtros(df_filtrado, filtro_sexo, "CS_SEXO")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_orientacao, "ORIENT_SEX")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_identidade, "IDENT_GEN")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_raca, "CS_RACA")
    df_filtrado = aplicar_filtros(df_filtrado, filtro_faixa, "Faixa etária")

    st.dataframe(df_filtrado)