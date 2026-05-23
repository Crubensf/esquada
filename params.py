# -*- coding: utf-8 -*-
"""Carregamento dos parâmetros GRM (a1, d1, d2, d3) do modelo ESQUADA."""

from __future__ import annotations
import os
from typing import Dict, List, Optional

import pandas as pd

from db import BASE_DIR
from items import PARTRUE_RAW


def _to_float(x) -> Optional[float]:
    """Converte um valor para float; retorna None se vazio ou 'NA'."""
    s = str(x).strip()
    if s == "" or s.lower() == "na":
        return None
    return float(s.replace(",", "."))


def _parse_partrue_embedded(raw: str) -> List[Dict[str, Optional[float]]]:
    """Lê os parâmetros embutidos em PARTRUE_RAW e retorna lista de dicts {a1, d1, d2, d3}."""
    rows: List[Dict[str, Optional[float]]] = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.lower().startswith("a1;"):
            continue  # ignora linhas vazias, comentários e cabeçalho
        parts = [p.strip() for p in line.split(";")]
        while len(parts) < 4:
            parts.append("")
        a1 = _to_float(parts[0])
        if a1 is None:
            continue
        rows.append({"a1": a1, "d1": _to_float(parts[1]),
                     "d2": _to_float(parts[2]), "d3": _to_float(parts[3])})
    return rows


def _load_partrue() -> List[Dict[str, Optional[float]]]:
    """
    Carrega os parâmetros GRM:
    - Se data/parTRUE_R.csv existir no disco, lê desse arquivo (aceita ; ou , como separador).
    - Caso contrário, usa PARTRUE_RAW embutido em items.py.
    """
    path = os.path.join(BASE_DIR, "data", "parTRUE_R.csv")
    if not os.path.exists(path):
        return _parse_partrue_embedded(PARTRUE_RAW)

    with open(path, "r", encoding="utf-8") as f:
        sample = f.read(4096)
    sep = ";" if sample.count(";") >= sample.count(",") else ","

    df = pd.read_csv(path, sep=sep, dtype=str).rename(columns=str.lower)
    for col in ["a1", "d1", "d2", "d3"]:
        if col not in df.columns:
            df[col] = None
    df = df[["a1", "d1", "d2", "d3"]].copy()
    for col in df.columns:
        df[col] = df[col].map(_to_float)

    return [
        {k: (None if pd.isna(v) else v) for k, v in row.items()}
        for row in df.to_dict(orient="records")
    ]
