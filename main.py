from script.csv_to_parquet import csv_to_parquet

if __name__ == "__main__":
    csv_to_parquet("dados/VIOLBR.csv", "dados/VIOLBR.parquet")