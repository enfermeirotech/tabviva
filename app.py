import streamlit as st
import pandas as pd
import altair as alt

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
CAMINHO_VIOLBR = r"C:\workspace\tabviva\dados\VIOLBR.csv"
CAMINHO_MUNICIPIOS = r"C:\workspace\tabviva\dimensoes\municipios.xlsx"

# --------------------------------------
# CARREGAR DATAFRAMES
# --------------------------------------
st.sidebar.title("Arquivos Carregados")

# Arquivo VIOLBR
try:
    df_violbr = pd.read_csv(CAMINHO_VIOLBR, sep=";", encoding="utf-8")
except:
    df_violbr = pd.read_csv(CAMINHO_VIOLBR)

# Criar coluna Ano com base nos 4 primeiros dígitos de DT_NOTIFIC
df_violbr["ANO_NOTIFIC"] = df_violbr["DT_NOTIFIC"].astype(str).str.slice(0, 4)


# Arquivo de municípios
if CAMINHO_MUNICIPIOS.endswith(".xlsx"):
    df_municipios = pd.read_excel(CAMINHO_MUNICIPIOS)
else:
    df_municipios = pd.read_csv(CAMINHO_MUNICIPIOS)

# --------------------------------------
# MERGE DOS DATAFRAMES
# --------------------------------------
df = df_violbr.merge(
    df_municipios,
    left_on="ID_MUNICIP",
    right_on="mun_cod",
    how="left"
)


st.sidebar.info(f"Total de notificações (VIOLBR): **{len(df)}**")

# --------------------------------------
# FILTRO DE ANO NO MENU LATERAL
# --------------------------------------
anos_disponiveis = sorted(df_violbr["ANO_NOTIFIC"].dropna().unique())

filtro_anos = st.sidebar.multiselect(
    "Ano da Notificação",
    options=anos_disponiveis,
)

# --------------------------------------
# CRIAR COLUNA DE SEXO
# --------------------------------------
df_violbr["SEXO"] = df_violbr["CS_SEXO"].replace({
    "F": "Feminino",
    "M": "Masculino",
    "I": "Ignorado",
    "": "Em branco",
    None: "Em branco"
})

# Adicionar no DF após o merge
df["SEXO"] = df["CS_SEXO"].replace({
    "F": "Feminino",
    "M": "Masculino",
    "I": "Ignorado",
    "": "Em branco",
    None: "Em branco"
})

# --------------------------------------
# CRIAR COLUNA DE ORIENTAÇÃO SEXUAL
# --------------------------------------
mapa_orientacao = {
    1: "Heterossexual",
    2: "Homossexual (Gay/Lésbica)",
    3: "Bissexual",
    8: "Não se aplica",
    9: "Ignorado"
}

df_violbr["ORIENTACAO"] = df_violbr["ORIENT_SEX"].replace(mapa_orientacao)
df["ORIENTACAO"] = df["ORIENT_SEX"].replace(mapa_orientacao)

# --------------------------------------
# CRIAR COLUNA DE IDENTIDADE DE GÊNERO
# --------------------------------------
mapa_identidade = {
    1: "Travesti",
    2: "Transexual Mulher",
    3: "Transexual Homem",
    8: "Não se aplica",
    9: "Ignorado"
}

df_violbr["IDENTIDADE"] = df_violbr["IDENT_GEN"].replace(mapa_identidade)
df["IDENTIDADE"] = df["IDENT_GEN"].replace(mapa_identidade)


# --------------------------------------
# CRIAR COLUNA DE RAÇA/COR
# --------------------------------------

mapa_raca = {
    1: "Branca",
    2: "Preta",
    3: "Amarela",
    4: "Parda",
    5: "Indígena",
    6: "Ignorado",
    None: "Em branco",
    "": "Em branco"
}

df["RACA"] = df["CS_RACA"].replace(mapa_raca)
df_violbr["RACA"] = df_violbr["CS_RACA"].replace(mapa_raca)


# --------------------------------------
# CRIAR COLUNA DE FAIXA ETÁRIA
# --------------------------------------

# Converter NU_IDADE_N em número inteiro seguro
df_violbr["NU_IDADE_N"] = pd.to_numeric(df_violbr["NU_IDADE_N"], errors="coerce")

# Função que converte uma idade codificada para faixa etária
def converter_idade(idade):
    if pd.isna(idade):
        return "IGNORADO"
    idade = int(idade)

    faixas_etarias = {
        (0, 999): 'IGNORADO',
        (1000, 3999): '00 a < 01 ano',
        (4000, 4004): '01 a 04 anos',
        (4005, 4009): '05 a 09 anos',
        (4010, 4014): '10 a 14 anos',
        (4015, 4019): '15 a 19 anos',
        (4020, 4029): '20 a 29 anos',
        (4030, 4039): '30 a 39 anos',
        (4040, 4049): '40 a 49 anos',
        (4050, 4059): '50 a 59 anos',
        (4060, 4069): '60 a 69 anos',
        (4070, 4079): '70 a 79 anos',
        (4080, 4999): 'Mais de 80 anos'
    }

    for (inicio, fim), faixa in faixas_etarias.items():
        if inicio <= idade <= fim:
            return faixa
    return 'IGNORADO'

# Criar coluna final
df_violbr["FAIXA_ETARIA"] = df_violbr["NU_IDADE_N"].apply(converter_idade)


# --------------------------------------
# FILTRO DE SEXO
# --------------------------------------
sexo_disponivel = ["Feminino", "Masculino", "Ignorado", "Em branco"]

filtro_sexo = st.sidebar.multiselect(
    "Sexo",
    options=sexo_disponivel
)

# --------------------------------------
# FILTRO DE ORIENTAÇÃO SEXUAL
# --------------------------------------
orientacoes_disponiveis = list(mapa_orientacao.values())
filtro_orientacao = st.sidebar.multiselect(
    "Orientação Sexual",
    options=orientacoes_disponiveis
)

# --------------------------------------
# FILTRO DE IDENTIDADE DE GÊNERO
# --------------------------------------
identidade_disponiveis = list(mapa_identidade.values())
filtro_identidade = st.sidebar.multiselect(
    "Identidade de gênero",
    options=identidade_disponiveis
)

# --------------------------------------
# FILTRO DE RAÇA/COR
# --------------------------------------
filtro_raca = list(mapa_raca.values())
filtro_raca = st.sidebar.multiselect(
    "Raça/Cor",
    options=filtro_raca
)

df["FAIXA_ETARIA"] = df["NU_IDADE_N"].apply(converter_idade)

# --------------------------------------
# FILTRO DE FAIXA ETÁRIA
# --------------------------------------

faixas_disponiveis = sorted(df["FAIXA_ETARIA"].dropna().unique())

filtro_faixa = st.sidebar.multiselect(
    "Faixa Etária",
    options=faixas_disponiveis
)

# --------------------------------------
# FILTRO DE TIPO DE VIOLÊNCIA
# --------------------------------------

mapa_violencias = {
    "VIOL_FISIC": "Física",
    "VIOL_PSICO": "Psicológica",
    "VIOL_TORT": "Tortura",
    "VIOL_SEXU": "Sexual",
    "VIOL_TRAF": "Tráfico de seres humanos",
    "VIOL_FINAN": "Financeira",
    "VIOL_NEGLI": "Negligência",
    "VIOL_INFAN": "Trabalho infantil",
    "VIOL_LEGAL": "Intervenção legal",
    "VIOL_OUTR": "Outras violências"
}

filtro_violencia = st.sidebar.multiselect(
    "Tipo de Violência",
    options=list(mapa_violencias.values()),
    default=[]
)

# --------------------------------------
# MAPA DE TIPOS DE VIOLÊNCIA SEXUAL
# --------------------------------------
mapa_violencia_sexual = {
    "SEX_ASSEDI": "Assédio sexual",
    "SEX_ESTUPR": "Estupro",
    "SEX_PORNO": "Pornografia infantil",
    "SEX_EXPLO": "Exploração sexual",
    "SEX_OUTRO": "Outro tipo de violência sexual"
}


# --------------------------------------
# FILTRO DE VIOLÊNCIA SEXUAL (MENU LATERAL)
# --------------------------------------
filtro_violencia_sexual = st.sidebar.multiselect(
    "Violência Sexual",
    options=list(mapa_violencia_sexual.values()),
    default=[]
)


# ----------------------------
# FILTROS EM LINHA (HORIZONTAL)
# ----------------------------
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    filtro_macro = st.multiselect(
        "Macrorregião",
        sorted(df["macro_reg_saude_abrv"].dropna().unique())
    )

with col2:
    filtro_reg_saude = st.multiselect(
        "Região de Saúde",
        sorted(df["reg_saude_nome"].dropna().unique())
    )

with col3:
    filtro_reg_integracao = st.multiselect(
        "Região de Integração",
        sorted(df["reg_integracao_nome"].dropna().unique())
    )

with col4:
    filtro_centro = st.multiselect(
        "Centro Regional de Saúde",
        sorted(df["centro_reg_saude_abrv"].dropna().unique())
    )

with col5:
    filtro_dsei = st.multiselect(
        "DSEI",
        sorted(df["dsei_nome"].dropna().unique())
    )

with col6:
    filtro_municipios = st.multiselect(
        "Municípios",
        sorted(df["mun_nome"].dropna().unique())
    )

# --------------------------------------
# APLICAR FILTROS
# --------------------------------------
df_filtrado = df.copy()

# Filtro de ano
if filtro_anos:
    df_filtrado = df_filtrado[df_filtrado["ANO_NOTIFIC"].isin(filtro_anos)]

if filtro_macro:
    df_filtrado = df_filtrado[df_filtrado["macro_reg_saude_abrv"].isin(filtro_macro)]

if filtro_reg_saude:
    df_filtrado = df_filtrado[df_filtrado["reg_saude_nome"].isin(filtro_reg_saude)]

if filtro_reg_integracao:
    df_filtrado = df_filtrado[df_filtrado["reg_integracao_nome"].isin(filtro_reg_integracao)]

if filtro_centro:
    df_filtrado = df_filtrado[df_filtrado["centro_reg_saude_abrv"].isin(filtro_centro)]

if filtro_dsei:
    df_filtrado = df_filtrado[df_filtrado["dsei_nome"].isin(filtro_dsei)]

if filtro_municipios:
    df_filtrado = df_filtrado[df_filtrado["mun_nome"].isin(filtro_municipios)]

if filtro_sexo:
    df_filtrado = df_filtrado[df_filtrado["SEXO"].isin(filtro_sexo)]

if filtro_faixa:
    df_filtrado = df_filtrado[df_filtrado["FAIXA_ETARIA"].isin(filtro_faixa)]

if filtro_faixa:
    df_filtrado = df_filtrado[df_filtrado["FAIXA_ETARIA"].isin(filtro_faixa)]

if filtro_raca:
    df_filtrado = df_filtrado[df_filtrado["RACA"].isin(filtro_raca)]

if filtro_orientacao:
    df_filtrado = df_filtrado[df_filtrado["ORIENTACAO"].isin(filtro_orientacao)]

if filtro_identidade:
    df_filtrado = df_filtrado[df_filtrado["IDENTIDADE"].isin(filtro_identidade)]

if filtro_violencia_sexual:
    colunas_sexuais_selecionadas = [
        col for col, nome in mapa_violencia_sexual.items()
        if nome in filtro_violencia_sexual
    ]
    for col in colunas_sexuais_selecionadas:
        df_filtrado = df_filtrado[df_filtrado[col] == 1]

    
# --------------------------------------
# RESULTADO
# --------------------------------------
st.write(f"Total após filtros: **{len(df_filtrado)}** registros")

# --------------------------------------
# TABELA DE FREQUÊNCIA POR TIPO DE VIOLÊNCIA
# --------------------------------------

# Só mostrar se algum tipo de violência for selecionado
if filtro_violencia:

    st.subheader("Tipos de Violência — Tabela de Frequência")

    # Identificar colunas correspondentes ao filtro selecionado
    colunas_violencia = [
        col for col, nome in mapa_violencias.items()
        if nome in filtro_violencia
    ]

    # Criar tabela apenas com as colunas selecionadas
    tabela_violencia = (
        df_filtrado[colunas_violencia]
        .apply(lambda col: (col == 1).sum())
        .reset_index()
    )

    tabela_violencia.columns = ["Variável", "Total"]

    # Nome legível
    tabela_violencia["Tipo de Violência"] = tabela_violencia["Variável"].map(mapa_violencias)

    # Percentual
    total_geral = tabela_violencia["Total"].sum()
    if total_geral > 0:
        tabela_violencia["Percentual (%)"] = (
            tabela_violencia["Total"] / total_geral * 100
        ).round(2)
    else:
        tabela_violencia["Percentual (%)"] = 0.0

    # Reordenar colunas
    tabela_violencia = tabela_violencia[
        ["Tipo de Violência", "Total", "Percentual (%)"]
    ]

    st.dataframe(tabela_violencia)
    st.markdown("---")

# --------------------------------------
# TABELA DE FREQUÊNCIA — VIOLÊNCIA SEXUAL
# --------------------------------------
if filtro_violencia_sexual:

    st.subheader("Violência Sexual — Tabela de Frequência")

    colunas_sexuais = [
        col for col, nome in mapa_violencia_sexual.items()
        if nome in filtro_violencia_sexual
    ]

    tabela_sexual = (
        df_filtrado[colunas_sexuais]
        .apply(lambda col: (col == 1).sum())
        .reset_index()
    )

    tabela_sexual.columns = ["Variável", "Total"]

    tabela_sexual["Tipo de Violência Sexual"] = tabela_sexual["Variável"].map(mapa_violencia_sexual)

    total_sexual = tabela_sexual["Total"].sum()

    tabela_sexual["Percentual (%)"] = (
        tabela_sexual["Total"] / total_sexual * 100 if total_sexual > 0 else 0
    ).round(2)

    tabela_sexual = tabela_sexual[
        ["Tipo de Violência Sexual", "Total", "Percentual (%)"]
    ]

    st.dataframe(tabela_sexual)
    st.markdown("---")


# --------------------------------------
# MAPA DE TIPOS DE VIOLÊNCIA SEXUAL
# --------------------------------------
mapa_violencia_sexual = {
    "SEX_ASSEDI": "Assédio sexual",
    "SEX_ESTUPR": "Estupro",
    "SEX_PORNO": "Pornografia infantil",
    "SEX_EXPLO": "Exploração sexual",
    "SEX_OUTRO": "Outro tipo de violência sexual"
}

# --------------------------------------
# MOSTRAR TABELAS PARA CADA FILTRO SELECIONADO
# --------------------------------------

# Mapeamento: nome do filtro -> (nome que aparece no cabeçalho, coluna no df_filtrado, variável de controle de seleção)

mapa_filtros = {
    "Sexo": ("Sexo", "SEXO", filtro_sexo),
    "Faixa Etária": ("Faixa Etária", "FAIXA_ETARIA", filtro_faixa),
    "Macrorregião": ("Macrorregião", "macro_reg_saude_abrv", filtro_macro),
    "Região de Saúde": ("Região de Saúde", "reg_saude_nome", filtro_reg_saude),
    "Região de Integração": ("Região de Integração", "reg_integracao_nome", filtro_reg_integracao),
    "Centro Regional de Saúde": ("Centro Regional de Saúde", "centro_reg_saude_abrv", filtro_centro),
    "DSEI": ("DSEI", "dsei_nome", filtro_dsei),
    "Municípios": ("Municípios", "mun_nome", filtro_municipios),
    "Orientação Sexual": ("Orientação Sexual", "ORIENTACAO", filtro_orientacao),
    "Identidade de Gênero": ("Identidade de Gênero", "IDENTIDADE", filtro_identidade),
    "Raça/Cor": ("Raça/Cor", "RACA", filtro_raca)
}

# --------------------------------------
# MOSTRAR TABELAS PARA CADA FILTRO SELECIONADO (LOOP ÚNICO E SEGURO)
# --------------------------------------

# Verifica se pelo menos um filtro foi selecionado
houve_filtro = any(bool(v[2]) for v in mapa_filtros.values())

if not houve_filtro:
    st.info("🛈 A tabela de frequência será exibida quando você selecionar pelo menos um filtro.")
else:
    for chave, (titulo, coluna, selecao) in mapa_filtros.items():
        if not selecao:
            continue  # pula filtros sem seleção

        # --- Tabela principal ---
        # Proteção: checar se coluna existe
        if coluna not in df_filtrado.columns:
            st.warning(f"Coluna '{coluna}' não encontrada nos dados — pulando {titulo}.")
            continue

        st.subheader(f"{titulo} — Tabela de Frequência")

        tabela = (
            df_filtrado[coluna]
            .value_counts(dropna=False)
            .reset_index()
        )
        tabela.columns = [titulo, "Total"]
        tabela["Percentual (%)"] = (
            tabela["Total"] / tabela["Total"].sum() * 100
        ).round(2)

        st.dataframe(tabela)

        # --- Tabela de municípios relacionados ---
        # Só faz sentido mostrar quando o filtro NÃO for 'Municípios'
        if coluna == "mun_nome":
            st.info("Filtro por Município selecionado — tabela de municípios relacionados não é aplicável.")
            st.markdown("---")
            continue

        # Verificar existência da coluna mun_nome
        if "mun_nome" not in df_filtrado.columns:
            st.info("Coluna 'mun_nome' não encontrada — não é possível listar municípios relacionados.")
            st.markdown("---")
            continue

        # Preparar base segura: apenas linhas com valores válidos nas duas colunas
        base = df_filtrado[[ "mun_nome", coluna ]].dropna()
        if base.empty:
            st.info(f"Sem dados suficientes para exibir municípios relacionados a {titulo}.")
            st.markdown("---")
            continue

        st.markdown(f"#### Municípios relacionados a {titulo}")

        municipios_relacionados = (
            base.groupby("mun_nome")
                .size()
                .reset_index(name="Total")
                .sort_values(by="Total", ascending=False)
        )

        # Proteção adicional: evitar divisão por zero
        total_mun = municipios_relacionados["Total"].sum()
        if total_mun > 0:
            municipios_relacionados["Percentual (%)"] = (
                municipios_relacionados["Total"] / total_mun * 100
            ).round(2)
        else:
            municipios_relacionados["Percentual (%)"] = 0.0

        st.dataframe(municipios_relacionados)
        st.markdown("---")


# --------------------------------------
# GRÁFICO DE SÉRIE HISTÓRICA (ÚLTIMOS 10 ANOS)
# --------------------------------------

st.markdown("### Série Histórica de Notificações")

# Garantir que o ano seja numérico
df_filtrado["ANO_NOTIFIC"] = pd.to_numeric(df_filtrado["ANO_NOTIFIC"], errors="coerce")

# Selecionar últimos 10 anos disponíveis
anos_disponiveis = sorted(df_filtrado["ANO_NOTIFIC"].dropna().unique())
ultimos_10 = anos_disponiveis[-10:] if len(anos_disponiveis) > 10 else anos_disponiveis

df_serie = (
    df_filtrado[df_filtrado["ANO_NOTIFIC"].isin(ultimos_10)]
    .groupby("ANO_NOTIFIC")
    .size()
    .reset_index(name="Total_Notificações")
    .sort_values("ANO_NOTIFIC")
)

# Criar gráfico Altair
grafico_serie = (
    alt.Chart(df_serie)
    .mark_line(point=True)
    .encode(
        x=alt.X("ANO_NOTIFIC:O", title="Ano da Notificação"),
        y=alt.Y("Total_Notificações:Q", title="Total de Notificações"),
        tooltip=["ANO_NOTIFIC", "Total_Notificações"]
    )
    .properties(height=350)
)

st.altair_chart(grafico_serie, use_container_width=True)

st.markdown("---")
