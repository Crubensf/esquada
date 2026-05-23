# -*- coding: utf-8 -*-
"""
Núcleo IRT — Modelo de Resposta Graduada (GRM) com estimação EAP.

Implementação equivalente à função mirt::fscores() do R.
Nada neste módulo deve ser alterado sem validar contra os resultados do script R de referência.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def logistic(x: np.ndarray) -> np.ndarray:
    """Função logística com clipping para evitar overflow numérico."""
    return 1.0 / (1.0 + np.exp(-np.clip(x, -35, 35)))


def graded_category_probs(a: float,
                          ds: List[Optional[float]],
                          theta: np.ndarray) -> np.ndarray:
    """
    Probabilidades de categoria do GRM para um item em todos os pontos de quadratura.

    Parâmetros
    ----------
    a     : discriminação do item (a1).
    ds    : lista de dificuldades [d1, d2, d3] (None indica categoria inexistente).
    theta : array de pontos de quadratura.

    Retorna
    -------
    P : matriz (m × len(theta)), onde m é o número de categorias do item.
    """
    ds_valid = [d for d in ds if d is not None and not pd.isna(d)]
    m = len(ds_valid) + 1
    if m < 2:
        ds_valid = [0.0]
        m = 2

    # Probabilidades cumulativas P(X >= k | theta)
    Ps = [logistic(a * theta + d) for d in ds_valid]

    # Converte cumulativas em probabilidades de categoria
    probs = [1.0 - Ps[0]]
    for k in range(1, m - 1):
        probs.append(Ps[k - 1] - Ps[k])
    probs.append(Ps[-1])

    P = np.vstack(probs)
    P = np.clip(P, 1e-15, 1.0)
    P = P / P.sum(axis=0, keepdims=True)  # garante que as probabilidades somem 1
    return P


def gh_points(n: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    """
    Pontos e pesos de quadratura de Gauss-Hermite padronizados para N(0,1).

    Usado na integração numérica do EAP.
    """
    nodes, weights = np.polynomial.hermite.hermgauss(n)
    nodes_std   = nodes * np.sqrt(2.0)
    weights_std = weights / np.sqrt(np.pi)
    return nodes_std, weights_std


def eap_grm(responses: np.ndarray,
            par: List[Dict[str, Optional[float]]],
            n_quad: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    """
    Estimação EAP (Expected A Posteriori) para o GRM.

    Parâmetros
    ----------
    responses : ndarray (N × J) — matriz de respostas (inteiros ou NaN para omissões).
    par       : lista de J dicts com chaves a1, d1, d2, d3.
    n_quad    : número de pontos de quadratura de Gauss-Hermite.

    Retorna
    -------
    eap : ndarray (N,) — estimativas do traço latente θ.
    se  : ndarray (N,) — erros padrão das estimativas.
    """
    N, J = responses.shape
    if len(par) != J:
        raise ValueError(f"Nº de itens no CSV ({J}) != nº de parâmetros ({len(par)}).")

    theta, w = gh_points(n_quad)

    # L[n, q] = verossimilhança do respondente n no ponto de quadratura q
    L = np.ones((N, theta.shape[0]), dtype=np.float64)

    for j in range(J):
        a   = par[j]["a1"]
        ds  = [par[j]["d1"], par[j]["d2"], par[j]["d3"]]
        Pjk = graded_category_probs(a, ds, theta)  # (m × Q)

        r          = responses[:, j]
        valid_mask = ~np.isnan(r)
        if not np.any(valid_mask):
            continue  # item inteiramente omitido — não contribui para L

        r_int = r[valid_mask].astype(int)
        m     = Pjk.shape[0]
        r_int = np.clip(r_int, 0, m - 1)

        for cat in range(m):
            mask = (r_int == cat)
            if not np.any(mask):
                continue
            valid_rows = np.where(valid_mask)[0][mask]
            L[valid_rows, :] *= Pjk[cat, :][None, :]

    # Integração numérica: média e variância posteriores
    LW    = L * w[None, :]
    denom = LW.sum(axis=1)
    eap   = (LW * theta[None, :]).sum(axis=1) / denom
    var   = (LW * (theta[None, :] - eap[:, None]) ** 2).sum(axis=1) / denom
    se    = np.sqrt(np.maximum(var, 1e-12))
    return eap, se
