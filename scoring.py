# -*- coding: utf-8 -*-
"""Pontuação e categorização dos respondentes usando o modelo GRM."""

from __future__ import annotations
import csv
import io
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from items import ESQ_COLS
from irt import eap_grm


# ─── Categorização ────────────────────────────────────────────────────────────

def categorizar_F1(F1: float) -> str:
    """Converte o escore F1 (escala IRT, média 0 DP 1) em categoria textual."""
    if F1 <= -2.0: return "muito ruim"
    if F1 <= -1.0: return "ruim"
    if F1 <=  0.5: return "boa"
    if F1 <=  2.5: return "muito boa"
    return "excelente"


def categorizar_F1novo(F1novo: float) -> str:
    """Converte o escore F1novo (escala 250/50) em categoria textual."""
    if F1novo <= 150: return "muito ruim"
    if F1novo <= 200: return "ruim"
    if F1novo <= 275: return "boa"
    if F1novo <= 375: return "muito boa"
    return "excelente"


# ─── Utilitários de itens ─────────────────────────────────────────────────────

def _item_category_count(item_par: Dict[str, Optional[float]]) -> int:
    """Retorna o número de categorias de resposta de um item (mínimo 2)."""
    ds = [item_par["d1"], item_par["d2"], item_par["d3"]]
    m  = len([d for d in ds if d is not None and not pd.isna(d)]) + 1
    return max(m, 2)


def _validate_response_array(responses: np.ndarray,
                              par: List[Dict[str, Optional[float]]]) -> None:
    """Levanta ValueError se alguma célula não-NaN estiver fora da faixa válida do item."""
    problems = []
    for j, item_par in enumerate(par):
        max_val      = _item_category_count(item_par) - 1
        col          = responses[:, j]
        invalid_rows = np.where(~np.isnan(col) & ((col < 0) | (col > max_val)))[0]
        if invalid_rows.size:
            lines = ", ".join(str(i + 1) for i in invalid_rows[:5])
            # Mensagem na codificação do usuário (base-1): 1 = primeira opção.
            problems.append(f"{ESQ_COLS[j]} aceita valores de 1 a {max_val + 1} (linhas: {lines})")
    if problems:
        raise ValueError("Foram encontradas respostas fora da faixa esperada: " + "; ".join(problems))


# ─── Leitura de CSV ───────────────────────────────────────────────────────────

def _read_csv_flexible(raw: bytes) -> pd.DataFrame:
    """
    Lê um CSV ESQUADA a partir de bytes brutos.

    Detecta automaticamente o separador (; ou ,) e retorna um DataFrame
    com as colunas [ID, esq_q1_sem0, …, esq_q25_sem0].

    As respostas são fornecidas em base-1 (1 = primeira opção) e convertidas
    para a base-0 interna. Aceita bases parciais: perguntas ausentes viram
    omissões. Cabeçalhos podem vir como esq_qN ou esq_qN_sem0.
    """
    sample = raw[:4096].decode("utf-8", errors="ignore")
    sep    = ";" if sample.count(";") >= sample.count(",") else ","
    df     = pd.read_csv(io.BytesIO(raw), sep=sep)
    df.rename(columns=str.lower, inplace=True)

    # Localiza as 25 colunas de item no CSV enviado.
    # Aceita os nomes canônicos (esq_q1_sem0 … esq_q25_sem0) e também a forma
    # curta usada por pesquisadores (esq_q1 … esq_q25), renomeando para o padrão.
    for i in range(1, 26):
        canonical = f"esq_q{i}_sem0"
        if canonical not in df.columns and f"esq_q{i}" in df.columns:
            df.rename(columns={f"esq_q{i}": canonical}, inplace=True)

    # Aceita bases parciais: o pesquisador pode enviar apenas as perguntas que usou.
    found = [c for c in ESQ_COLS if c in df.columns]
    if len(found) == 0:
        raise ValueError(
            "Nenhuma coluna ESQUADA (esq_q1 … esq_q25) foi encontrada. "
            "Verifique se os cabeçalhos seguem o modelo e se o separador é vírgula ou ponto e vírgula."
        )

    # Converte os itens enviados de base-1 (codificação do usuário) para base-0 (interna).
    for c in found:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if df[found].isna().all(axis=1).all():
        raise ValueError("O CSV não possui nenhuma linha com ao menos uma resposta ESQUADA preenchida.")
    for c in found:
        df[c] = (df[c] - 1).astype("Int64")

    # Itens não enviados na base parcial entram como ausentes (omissão), sem afetar o EAP.
    for c in ESQ_COLS:
        if c not in df.columns:
            df[c] = pd.Series(pd.NA, index=df.index, dtype="Int64")

    # Gera a coluna ID: usa a coluna existente (com fallback numérico) ou cria sequencial
    if "id" in df.columns:
        fallback_ids = pd.Series(np.arange(1, len(df) + 1, dtype=int), index=df.index)
        ids          = df["id"].copy()
        missing_ids  = ids.isna() | ids.astype(str).str.strip().eq("")
        ids          = ids.where(~missing_ids, fallback_ids)
        df["ID"]     = ids.astype(str)
    else:
        df["ID"] = np.arange(1, len(df) + 1, dtype=int)

    return df[["ID"] + ESQ_COLS]


# ─── Pontuação ────────────────────────────────────────────────────────────────

def _compute_scores(arr: np.ndarray,
                    par: List[Dict[str, Optional[float]]]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Executa o EAP e calcula F1, SE_F1 e F1novo para uma matriz de respostas.

    Linhas completamente vazias (todos NaN) recebem NaN nos três escores.
    F1novo = 250 + 50 * F1.
    """
    answered_mask = ~np.isnan(arr).all(axis=1)
    F1 = np.full(arr.shape[0], np.nan, dtype=float)
    SE = np.full(arr.shape[0], np.nan, dtype=float)
    if np.any(answered_mask):
        F1[answered_mask], SE[answered_mask] = eap_grm(arr[answered_mask], par, n_quad=61)
    F1novo = np.where(np.isnan(F1), np.nan, 250.0 + 50.0 * F1)
    return F1, SE, F1novo


def _score_dataframe(df_items: pd.DataFrame,
                     par: List[Dict[str, Optional[float]]]) -> pd.DataFrame:
    """
    Pontua um DataFrame com colunas [ID, esq_q1_sem0, …, esq_q25_sem0].

    Retorna o mesmo DataFrame acrescido de F1, SE_F1, escore.cat, F1novo e escore.cat.novo.
    """
    base       = df_items.reset_index(drop=True).copy()
    items_only = base[ESQ_COLS].to_numpy(dtype=float, na_value=np.nan)
    _validate_response_array(items_only, par)

    F1, SE, F1novo = _compute_scores(items_only, par)

    scores = pd.DataFrame({
        "F1":              F1,
        "SE_F1":           SE,
        "escore.cat":      [categorizar_F1(x)     if not np.isnan(x) else pd.NA for x in F1],
        "F1novo":          F1novo,
        "escore.cat.novo": [categorizar_F1novo(x) if not np.isnan(x) else pd.NA for x in F1novo],
    })

    joined = pd.concat([base, scores], axis=1)
    return joined[["ID"] + ESQ_COLS + ["F1", "SE_F1", "escore.cat", "F1novo", "escore.cat.novo"]]
