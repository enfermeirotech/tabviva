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

# Index(['DT_NOTIFIC', 'ID_MUNICIP', 'NU_IDADE_N', 'CS_SEXO', 'CS_RACA',
#        'ORIENT_SEX', 'IDENT_GEN', 'Física', 'Psicológica', 'Tortura', 'Sexual',
#        'Tráfico de seres humanos', 'Financeira', 'Negligência',
#        'Trabalho infantil', 'Intervenção legal', 'Outras violências',
#        'Assédio sexual', 'Estupro', 'Pornografia infantil',
#        'Exploração sexual', 'Outro tipo de violência sexual', 'Ano', 'Mês',
#        'Faixa etária'],
#       dtype='object')

# --------------------------------------
# SIDEBAR
# --------------------------------------
# ------------Opções de filtro para a sidebar----------------
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

        submitted = st.form_submit_button("Submit")

    if submitted:
        st.write("Sexo:", filtro_sexo)
        st.write("Orientação Sexual:", filtro_orientacao)
        st.write("Identidade de Gênero:", filtro_identidade)
        st.write("Raça/Cor:", filtro_raca)
        st.write("Faixa Etária:", filtro_faixa)