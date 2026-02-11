from script.csv_to_parquet import violbr_to_parquet
from script.csv_to_parquet import regiao_to_parquet

if __name__ == "__main__":
    violbr_to_parquet("dados/VIOLBR.csv", "dados/VIOLBR.parquet")
    regiao_to_parquet("dimensoes/dim_regiao.csv", "dimensoes/dim_regiao.parquet")