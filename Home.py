import streamlit as st

# --------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------
st.set_page_config(
    page_title="TABVIVA - Tabulador de Notificação de Violência Interpessoal",
    page_icon="🩺",
    layout="wide"
)

# --------------------------------------
# CABEÇALHO
# --------------------------------------
st.title("🩺 TABVIVA")
st.subheader("Tabulador de Notificação de Violência Interpessoal e Mortalidade")
st.markdown("---")

# --------------------------------------
# APRESENTAÇÃO
# --------------------------------------
st.markdown(
    """
    ### Bem-vindo(a) ao **TABVIVA**

    O **TABVIVA** é uma ferramenta interativa desenvolvida para facilitar a
    **consulta, visualização e análise** de dados públicos de saúde relacionados
    à **violência interpessoal** e à **mortalidade** no Brasil.

    A proposta é aproximar profissionais de saúde, pesquisadores, estudantes e
    gestores dos dados provenientes dos sistemas oficiais (como **SINAN** e **SIM**),
    oferecendo tabulações dinâmicas e gráficos intuitivos — sem precisar lidar com
    planilhas brutas ou softwares complexos.
    """
)

st.markdown("---")

# --------------------------------------
# NAVEGAÇÃO / PÁGINAS
# --------------------------------------
st.markdown("### 📂 Navegue pelas análises")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        #### ❕ Notificação
        Explore as **notificações de violência interpessoal** registradas no
        SINAN. Visualize distribuições por faixa etária, sexo, tipo de violência,
        município e período.
        """
    )
    st.page_link(
        "pages/1_❕_Noficação.py",
        label="Acessar Notificações",
        icon="➡️",
    )

with col2:
    st.markdown(
        """
        #### 💀 Mortalidade
        Consulte os dados de **mortalidade** provenientes do SIM (Sistema de
        Informações sobre Mortalidade), com recortes demográficos e temporais
        para apoiar análises epidemiológicas.
        """
    )
    st.page_link(
        "pages/2_🔺_Mortalidade.py",
        label="Acessar Mortalidade",
        icon="➡️",
    )

st.markdown("---")

# --------------------------------------
# COMO USAR
# --------------------------------------
with st.expander("ℹ️ Como utilizar o TABVIVA"):
    st.markdown(
        """
        1. Escolha uma das análises disponíveis acima ou pelo **menu lateral**.
        2. Aplique os **filtros** (ano, região, sexo, faixa etária, etc.) de
            acordo com o recorte desejado.
        3. Explore os **gráficos e tabelas** gerados dinamicamente.
        4. Os dados exibidos têm origem em bases públicas do **DATASUS**.
        """
    )

# --------------------------------------
# RODAPÉ
# --------------------------------------
st.markdown("---")
st.caption(
    "Projeto desenvolvido no âmbito do **PET-Saúde** · "
    "Dados: DATASUS (SINAN e SIM)."
)
