import pandas as pd

def csv_to_parquet(csv_path: str, parquet_path: str) -> None:
    """
    Parameters
    ----------
    csv_path : str
        _description_
    parquet_path : str
        _description_
    """
    
    df_violbr = pd.read_csv(csv_path)

    COLUNAS_VIOLBR = [
        # Identificação e data
        "DT_NOTIFIC", "ID_MUNICIP",
        # Dados demográficos
        "NU_IDADE_N", "CS_SEXO", "CS_RACA", "ORIENT_SEX", "IDENT_GEN",
        # Tipos de violência
        "VIOL_FISIC", "VIOL_PSICO", "VIOL_TORT", "VIOL_SEXU", "VIOL_TRAF",
        "VIOL_FINAN", "VIOL_NEGLI", "VIOL_INFAN", "VIOL_LEGAL", "VIOL_OUTR",
        # Violência sexual
        "SEX_ASSEDI", "SEX_ESTUPR", "SEX_PORNO", "SEX_EXPLO", "SEX_OUTRO",
    ]

    MAPA_SEXO = {
        "F": "Feminino",
        "M": "Masculino",
        "I": "Ignorado",
        "": "Em branco",
        None: "Em branco",
    }

    MAPA_ORIENTACAO = {
        1: "Heterossexual",
        2: "Homossexual (Gay/Lésbica)",
        3: "Bissexual",
        8: "Não se aplica",
        9: "Ignorado",
    }

    MAPA_IDENTIDADE = {
        1: "Travesti",
        2: "Transexual Mulher",
        3: "Transexual Homem",
        8: "Não se aplica",
        9: "Ignorado",
    }

    MAPA_RACA = {
        1: "Branca",
        2: "Preta",
        3: "Amarela",
        4: "Parda",
        5: "Indígena",
        6: "Ignorado",
        None: "Em branco",
        "": "Em branco",
    }

    MAPA_VIOLENCIAS = {
        "VIOL_FISIC": "Física",
        "VIOL_PSICO": "Psicológica",
        "VIOL_TORT": "Tortura",
        "VIOL_SEXU": "Sexual",
        "VIOL_TRAF": "Tráfico de seres humanos",
        "VIOL_FINAN": "Financeira",
        "VIOL_NEGLI": "Negligência",
        "VIOL_INFAN": "Trabalho infantil",
        "VIOL_LEGAL": "Intervenção legal",
        "VIOL_OUTR": "Outras violências",
    }

    MAPA_VIOLENCIA_SEXUAL = {
        "SEX_ASSEDI": "Assédio sexual",
        "SEX_ESTUPR": "Estupro",
        "SEX_PORNO": "Pornografia infantil",
        "SEX_EXPLO": "Exploração sexual",
        "SEX_OUTRO": "Outro tipo de violência sexual",
    }

    df_violbr = df_violbr[COLUNAS_VIOLBR]


    df_violbr['CS_SEXO'] = df_violbr['CS_SEXO'].map(MAPA_SEXO)
    df_violbr['ORIENT_SEX'] = df_violbr['ORIENT_SEX'].map(MAPA_ORIENTACAO)
    df_violbr['IDENT_GEN'] = df_violbr['IDENT_GEN'].map(MAPA_IDENTIDADE)
    df_violbr['CS_RACA'] = df_violbr['CS_RACA'].map(MAPA_RACA)

    # Renomear as colunas
    df_violbr = df_violbr.rename(columns=MAPA_VIOLENCIAS)
    df_violbr = df_violbr.rename(columns=MAPA_VIOLENCIA_SEXUAL)


    df_violbr.to_parquet(parquet_path, index=False)