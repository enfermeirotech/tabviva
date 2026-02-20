import pandas as pd

def violbr_to_parquet(csv_path: str, parquet_path: str) -> None:
    """
    Parameters
    ----------
    csv_path : str
        _description_
    parquet_path : str
        _description_
    """
    
    df_violbr = pd.read_csv(csv_path, low_memory=False)

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
    
    COLUNAS_BOOLEANAS = [
        'Física', 'Psicológica', 'Tortura', 'Sexual',
        'Tráfico de seres humanos', 'Financeira', 'Negligência',
        'Trabalho infantil', 'Intervenção legal', 'Outras violências',
        'Assédio sexual', 'Estupro', 'Pornografia infantil',
        'Exploração sexual', 'Outro tipo de violência sexual'
    ]
    
    FAIXAS_ETARIAS = {
        (0, 999): "IGNORADO",
        (1000, 3999): "00 a < 01 ano",
        (4000, 4004): "01 a 04 anos",
        (4005, 4009): "05 a 09 anos",
        (4010, 4014): "10 a 14 anos",
        (4015, 4019): "15 a 19 anos",
        (4020, 4029): "20 a 29 anos",
        (4030, 4039): "30 a 39 anos",
        (4040, 4049): "40 a 49 anos",
        (4050, 4059): "50 a 59 anos",
        (4060, 4069): "60 a 69 anos",
        (4070, 4079): "70 a 79 anos",
        (4080, 4999): "Mais de 80 anos",
    }
    
    def converter_idade(idade: float) -> str:
        """
            Converte código de idade do 
            SINAN para faixa etária legível.
        """
        if pd.isna(idade):
            return "IGNORADO"
        idade = int(idade)
        for (inicio, fim), faixa in FAIXAS_ETARIAS.items():
            if inicio <= idade <= fim:
                return faixa
        return "IGNORADO"
        
    df_violbr = df_violbr[COLUNAS_VIOLBR]
    
    # Converter a coluna de data para o formato datetime
    df_violbr['DT_NOTIFIC'] = pd.to_datetime(df_violbr['DT_NOTIFIC'], format='%Y%m%d')
    
    # Extrair ano e mês da data de notificação
    df_violbr['Ano'] = df_violbr['DT_NOTIFIC'].dt.year
    df_violbr['Mês'] = df_violbr['DT_NOTIFIC'].dt.month

    # Aplicar os mapeamentos
    df_violbr['CS_SEXO'] = df_violbr['CS_SEXO'].map(MAPA_SEXO)
    df_violbr['ORIENT_SEX'] = df_violbr['ORIENT_SEX'].map(MAPA_ORIENTACAO)
    df_violbr['IDENT_GEN'] = df_violbr['IDENT_GEN'].map(MAPA_IDENTIDADE)
    df_violbr['CS_RACA'] = df_violbr['CS_RACA'].map(MAPA_RACA)

    # Converter a coluna de idade para faixas etárias
    df_violbr["FAIXA_ETARIA"] = df_violbr["NU_IDADE_N"].apply(converter_idade)


    # Renomear as colunas
    df_violbr = df_violbr.rename(columns=MAPA_VIOLENCIAS)
    df_violbr = df_violbr.rename(columns=MAPA_VIOLENCIA_SEXUAL)
    
    # Converter as colunas de violência para booleanas
    df_violbr[COLUNAS_BOOLEANAS] = df_violbr[COLUNAS_BOOLEANAS] == 1
    
    df_violbr.to_parquet(parquet_path, index=False)



def regiao_to_parquet(csv_path: str, parquet_path: str) -> None:
    """
    Parameters
    ----------
    csv_path : str
        _description_
    parquet_path : str
        _description_
    """
    
    df_municipios = pd.read_csv(csv_path, sep=';', encoding='latin-1')
    
    COLUNAS_MUNICIPIOS = [
    "mun_cod", "mun_nome", 
    "uf_sigla", "uf_nome", 
    "macro_reg_saude_abrv", "macro_reg_saude_nome",
    "reg_saude_nome", "reg_integracao_nome",
    # "dsei", "dsei_nome",
    # "mun_mapa"
    ]
    
    df_municipios = df_municipios[COLUNAS_MUNICIPIOS]
    
    df_municipios.to_parquet(parquet_path, index=False)