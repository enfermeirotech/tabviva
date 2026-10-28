import json
import os

import requests

URL_MALHA = (
    "https://servicodados.ibge.gov.br/api/v3/malhas/estados/{uf_cod}"
    "?formato=application/vnd.geo+json"
    "&intrarregiao=municipio"
    "&qualidade={qualidade}"
)


def malha_municipal_to_geojson(
    geojson_path: str,
    uf_cod: int = 15,
    qualidade: str = "intermediaria",
    forcar: bool = False,
) -> None:
    """
    Baixa a malha municipal de uma UF na API de malhas do IBGE e grava o
    GeoJSON usado pelo mapa da página de notificação.

    O 'id' de cada feature é gravado como o código IBGE de 6 dígitos, que é
    a chave de junção com a coluna 'mun_cod' de dim_regiao.

    Parameters
    ----------
    geojson_path : str
        Caminho de destino do arquivo GeoJSON.
    uf_cod : int
        Código IBGE da UF (15 = Pará).
    qualidade : str
        Resolução da malha: 'minima', 'intermediaria' ou 'maxima'.
    forcar : bool
        Se False (padrão), não baixa novamente caso o arquivo já exista.
    """

    if os.path.exists(geojson_path) and not forcar:
        print(f"Malha já existe em {geojson_path} (use forcar=True para rebaixar).")
        return

    resposta = requests.get(
        URL_MALHA.format(uf_cod=uf_cod, qualidade=qualidade),
        timeout=60,
    )
    resposta.raise_for_status()
    malha = resposta.json()

    # O IBGE devolve 'codarea' com 7 dígitos (inclui o dígito verificador);
    # dim_regiao usa 6 dígitos.
    for feature in malha["features"]:
        feature["id"] = feature["properties"]["codarea"][:6]

    os.makedirs(os.path.dirname(geojson_path) or ".", exist_ok=True)

    with open(geojson_path, "w", encoding="utf-8") as arquivo:
        json.dump(malha, arquivo, ensure_ascii=False, separators=(",", ":"))

    print(f"Malha salva em {geojson_path} ({len(malha['features'])} municípios).")
