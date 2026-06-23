# -*- coding: utf-8 -*-
"""Núcleo IRT — GRM com estimação EAP (equivalente a mirt::fscores)."""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def logistic(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -35, 35)))


def graded_category_probs(a: float,
                          ds: List[Optional[float]],
                          theta: np.ndarray) -> np.ndarray:
    ds_valid = [d for d in ds if d is not None and not pd.isna(d)]
    m = len(ds_valid) + 1
    if m < 2:
        ds_valid = [0.0]
        m = 2

    Ps = [logistic(a * theta + d) for d in ds_valid]

    probs = [1.0 - Ps[0]]
    for k in range(1, m - 1):
        probs.append(Ps[k - 1] - Ps[k])
    probs.append(Ps[-1])

    P = np.vstack(probs)
    P = np.clip(P, 1e-15, 1.0)
    P = P / P.sum(axis=0, keepdims=True)
    return P


def gh_points(n: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.hermite.hermgauss(n)
    nodes_std   = nodes * np.sqrt(2.0)
    weights_std = weights / np.sqrt(np.pi)
    return nodes_std, weights_std


def eap_grm(responses: np.ndarray,
            par: List[Dict[str, Optional[float]]],
            n_quad: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    N, J = responses.shape
    if len(par) != J:
        raise ValueError(f"Nº de itens no CSV ({J}) != nº de parâmetros ({len(par)}).")

    theta, w = gh_points(n_quad)

    L = np.ones((N, theta.shape[0]), dtype=np.float64)

    for j in range(J):
        a   = par[j]["a1"]
        ds  = [par[j]["d1"], par[j]["d2"], par[j]["d3"]]
        Pjk = graded_category_probs(a, ds, theta)

        r          = responses[:, j]
        valid_mask = ~np.isnan(r)
        if not np.any(valid_mask):
            continue

        r_int = r[valid_mask].astype(int)
        m     = Pjk.shape[0]
        r_int = np.clip(r_int, 0, m - 1)

        for cat in range(m):
            mask = (r_int == cat)
            if not np.any(mask):
                continue
            valid_rows = np.where(valid_mask)[0][mask]
            L[valid_rows, :] *= Pjk[cat, :][None, :]

    LW    = L * w[None, :]
    denom = LW.sum(axis=1)
    eap   = (LW * theta[None, :]).sum(axis=1) / denom
    var   = (LW * (theta[None, :] - eap[:, None]) ** 2).sum(axis=1) / denom
    se    = np.sqrt(np.maximum(var, 1e-12))
    return eap, se
