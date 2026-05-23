import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def gerar_csv_esquada_compat(n_pessoas: int, seed: int = 42,
                             nome_arquivo: str = "AvaliaoClinicaDoEfei-Michelle_DATA_2025-02-28_0147_aligned.csv"):
    """
    Gera um CSV compatível com o script em R, mantendo:
      1) record_id
      2) dat_sem0
      3) rghc_sem0
      4) peso_sem0
      5) alt_sem0
      6..30) esq_q1_sem0 .. esq_q25_sem0 (inteiros iniciando em 0)
      31) obs_sem0  (que vira a 27ª após o R remover 4 colunas por posição)
    O arquivo é salvo com vírgula como separador (compatível com readr::read_csv).
    """
    np.random.seed(seed)
    random.seed(seed)

    # nº de categorias por item (inferido dos seus parâmetros a1/d1..d3)
    n_categorias = [
        2, 3, 2, 2, 4, 2, 3, 2, 4, 4,
        4, 4, 4, 2, 3, 3, 4, 3, 4, 3,
        3, 3, 3, 4, 4
    ]
    assert len(n_categorias) == 25

    # 1) record_id (coluna 1)
    record_id = np.arange(1, n_pessoas + 1)

    # 2) dat_sem0 (coluna 2): datas aleatórias em 2025
    base_date = datetime(2025, 1, 1)
    dat_sem0 = [(base_date + timedelta(days=int(x))).date().isoformat()
                for x in np.random.randint(0, 180, size=n_pessoas)]

    # 3) rghc_sem0 (coluna 3): string fictícia
    rghc_sem0 = [f"RGHC{100000 + i}" for i in record_id]

    # 4) peso_sem0 (coluna 4): peso em kg (float)
    peso_sem0 = np.round(np.random.normal(loc=70, scale=12, size=n_pessoas), 1)

    # 5) alt_sem0 (coluna 5): altura em cm (int)
    alt_sem0 = np.random.randint(150, 195, size=n_pessoas)

    # 6..30) Itens esq_q1_sem0 .. esq_q25_sem0 (inteiros iniciando em 0)
    itens = {}
    for i, n_cat in enumerate(n_categorias, start=1):
        col = f"esq_q{i}_sem0"
        itens[col] = np.random.randint(0, n_cat, size=n_pessoas)

    # 31) obs_sem0 (texto livre; o R vai removê-la por posição)
    frases = ["", "OK", "sem observações", "revisar", "confirmado", "NA"]
    obs_sem0 = [random.choice(frases) for _ in range(n_pessoas)]

    # Monta DataFrame na ordem EXATA esperada
    cols = (["record_id", "dat_sem0", "rghc_sem0", "peso_sem0", "alt_sem0"] +
            [f"esq_q{i}_sem0" for i in range(1, 26)] +
            ["obs_sem0"])

    df = pd.DataFrame({
        "record_id": record_id,
        "dat_sem0": dat_sem0,
        "rghc_sem0": rghc_sem0,
        "peso_sem0": peso_sem0,
        "alt_sem0": alt_sem0,
        **itens,
        "obs_sem0": obs_sem0,
    })[cols]

    # Salva com separador vírgula (compatível com readr::read_csv)
    df.to_csv(nome_arquivo, index=False)
    print(f"✅ CSV gerado: {nome_arquivo} (linhas: {len(df)}, colunas: {len(df.columns)})")

# Exemplo de uso:
if __name__ == "__main__":
    gerar_csv_esquada_compat(n_pessoas=100)
