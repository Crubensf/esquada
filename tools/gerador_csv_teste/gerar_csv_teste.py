#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path
from typing import List, Sequence

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
PARTRUE_PATH = ROOT_DIR / "parTRUE_R.csv"
ESQ_COLS = [f"esq_q{i}_sem0" for i in range(1, 26)]
DEFAULT_CATEGORY_COUNTS = [
    2, 3, 2, 2, 4, 2, 3, 2, 4, 4,
    4, 4, 4, 2, 3, 3, 4, 3, 4, 3,
    3, 3, 3, 4, 4,
]


def _auto_sep(path: Path) -> str:
    sample = path.read_text(encoding="utf-8")[:4096]
    return ";" if sample.count(";") >= sample.count(",") else ","


def load_category_counts() -> List[int]:
    if not PARTRUE_PATH.exists():
        return DEFAULT_CATEGORY_COUNTS
    sep = _auto_sep(PARTRUE_PATH)
    df = pd.read_csv(PARTRUE_PATH, sep=sep, dtype=str).rename(columns=str.lower)
    counts: List[int] = []
    for _, row in df.iterrows():
        d_values = [row.get("d1"), row.get("d2"), row.get("d3")]
        valid = 0
        for value in d_values:
            if value is None:
                continue
            text = str(value).strip()
            if text and text.lower() != "nan":
                valid += 1
        counts.append(valid + 1)
    return counts if len(counts) == 25 else DEFAULT_CATEGORY_COUNTS


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -35.0, 35.0)))


def sample_ordinal(
    rng: np.random.Generator,
    n_categories: int,
    trait: float,
    *,
    bias: float = 0.0,
    slope: float = 1.0,
    noise: float = 0.8,
) -> int:
    if n_categories <= 1:
        return 0
    expected = sigmoid((trait + bias) * slope) * (n_categories - 1)
    draw = expected + float(rng.normal(0.0, noise))
    return int(np.clip(np.rint(draw), 0, n_categories - 1))


def sample_like(
    rng: np.random.Generator,
    source_value: int,
    n_categories: int,
    *,
    noise: float = 0.7,
) -> int:
    draw = source_value + float(rng.normal(0.0, noise))
    return int(np.clip(np.rint(draw), 0, n_categories - 1))


def generate_item_scores(
    rng: np.random.Generator,
    counts: Sequence[int],
    partial_rate: float,
) -> List[int | None]:
    health = float(rng.normal(0.0, 1.0))
    routine = health + float(rng.normal(0.0, 0.55))
    whole_foods = health + float(rng.normal(0.0, 0.60))
    processed_control = health + float(rng.normal(0.0, 0.60))

    values: List[int | None] = [0] * 25

    values[0] = sample_ordinal(rng, counts[0], routine, bias=0.20, slope=1.40, noise=0.35)
    if values[0] == 0:
        values[1] = 0
    else:
        values[1] = 1 + sample_ordinal(
            rng,
            counts[1] - 1,
            routine,
            bias=0.20,
            slope=1.20,
            noise=0.35,
        )

    values[2] = sample_ordinal(rng, counts[2], routine, bias=1.10, slope=1.50, noise=0.25)
    if values[2] == 0:
        values[3] = 0
    else:
        values[3] = sample_ordinal(rng, counts[3], whole_foods, bias=0.25, slope=1.30, noise=0.45)

    values[4] = sample_ordinal(rng, counts[4], routine, bias=0.15, slope=0.95, noise=0.75)
    values[5] = sample_ordinal(rng, counts[5], routine, bias=0.10, slope=1.15, noise=0.40)
    values[6] = sample_ordinal(rng, counts[6], whole_foods, bias=0.05, slope=0.95, noise=0.70)
    values[7] = sample_ordinal(rng, counts[7], health, bias=0.10, slope=1.10, noise=0.40)

    values[8] = sample_ordinal(rng, counts[8], whole_foods, bias=-0.05, slope=1.00, noise=0.70)
    values[9] = sample_ordinal(rng, counts[9], whole_foods, bias=-0.10, slope=1.00, noise=0.75)
    values[10] = sample_ordinal(rng, counts[10], whole_foods, bias=0.00, slope=1.10, noise=0.70)
    values[11] = sample_ordinal(rng, counts[11], whole_foods, bias=0.15, slope=1.10, noise=0.70)
    values[12] = sample_ordinal(rng, counts[12], whole_foods, bias=-0.15, slope=0.95, noise=0.80)
    values[13] = sample_ordinal(rng, counts[13], health, bias=0.10, slope=1.20, noise=0.35)

    values[14] = sample_ordinal(rng, counts[14], processed_control, bias=0.10, slope=1.00, noise=0.65)
    values[15] = sample_ordinal(rng, counts[15], processed_control, bias=0.15, slope=1.00, noise=0.65)
    values[16] = sample_ordinal(rng, counts[16], processed_control, bias=0.00, slope=0.95, noise=0.80)
    values[17] = sample_ordinal(rng, counts[17], processed_control, bias=0.05, slope=1.00, noise=0.70)
    values[18] = sample_like(rng, int(values[16]), counts[18], noise=0.75)
    values[19] = sample_ordinal(rng, counts[19], processed_control, bias=0.00, slope=1.05, noise=0.70)
    values[20] = sample_ordinal(rng, counts[20], processed_control, bias=0.05, slope=1.00, noise=0.70)
    values[21] = sample_ordinal(rng, counts[21], processed_control, bias=0.00, slope=1.00, noise=0.70)
    values[22] = sample_ordinal(rng, counts[22], processed_control, bias=0.10, slope=1.00, noise=0.65)
    values[23] = sample_like(rng, int(values[16]), counts[23], noise=0.65)
    values[24] = sample_like(rng, int(min(values[16], values[23])), counts[24], noise=0.70)

    if partial_rate > 0.0 and rng.random() < partial_rate:
        candidates = list(range(1, 25))
        n_missing = int(rng.integers(1, min(6, len(candidates)) + 1))
        missing_idx = rng.choice(candidates, size=n_missing, replace=False)
        for idx in missing_idx:
            values[int(idx)] = None

    return values


def random_date_iso(rng: np.random.Generator) -> str:
    start = date(2025, 1, 1)
    offset = int(rng.integers(0, 180))
    return (start + timedelta(days=offset)).isoformat()


def random_weight(rng: np.random.Generator) -> float:
    return round(float(np.clip(rng.normal(70.0, 12.0), 38.0, 180.0)), 1)


def random_height_cm(rng: np.random.Generator) -> int:
    return int(rng.integers(145, 196))


def random_obs(rng: np.random.Generator) -> str:
    options = ["", "", "", "OK", "sem observacoes", "revisar", "confirmado"]
    return str(rng.choice(options))


def build_dataframe(
    n_rows: int,
    seed: int,
    output_format: str,
    partial_rate: float,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    counts = load_category_counts()
    rows = []

    for record_id in range(1, n_rows + 1):
        answers = generate_item_scores(rng, counts, partial_rate)
        row = {col: answers[idx] for idx, col in enumerate(ESQ_COLS)}
        if output_format == "modelo":
            row = {"ID": record_id, **row}
        else:
            row = {
                "record_id": record_id,
                "dat_sem0": random_date_iso(rng),
                "rghc_sem0": f"RGHC{100000 + record_id}",
                "peso_sem0": random_weight(rng),
                "alt_sem0": random_height_cm(rng),
                **row,
                "obs_sem0": random_obs(rng),
            }
        rows.append(row)

    return pd.DataFrame(rows)


def default_output_path(output_format: str, n_rows: int) -> Path:
    name = f"csv_teste_esquada_{output_format}_{n_rows}_linhas.csv"
    return ROOT_DIR / "gerador_csv_teste" / "saida" / name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera CSVs de teste para o projeto ESQUADA."
    )
    parser.add_argument(
        "--linhas",
        type=int,
        required=True,
        help="Quantidade de linhas a gerar.",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        help="Caminho do arquivo CSV de saída.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semente aleatória para reproduzir os mesmos dados.",
    )
    parser.add_argument(
        "--formato",
        choices=["completo", "modelo"],
        default="completo",
        help="Formato do CSV gerado.",
    )
    parser.add_argument(
        "--taxa-parciais",
        type=float,
        default=0.0,
        help="Percentual de linhas com alguns itens em branco, de 0 a 1.",
    )
    args = parser.parse_args()
    if args.linhas <= 0:
        parser.error("--linhas deve ser maior que zero.")
    if not 0.0 <= args.taxa_parciais <= 1.0:
        parser.error("--taxa-parciais deve ficar entre 0 e 1.")
    return args


def main() -> None:
    args = parse_args()
    output_path = args.saida or default_output_path(args.formato, args.linhas)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = build_dataframe(
        n_rows=args.linhas,
        seed=args.seed,
        output_format=args.formato,
        partial_rate=args.taxa_parciais,
    )
    df.to_csv(output_path, index=False)

    partial_rows = 0
    if ESQ_COLS[0] in df.columns:
        partial_rows = int(df[ESQ_COLS].isna().any(axis=1).sum())

    print(f"Arquivo gerado: {output_path}")
    print(f"Linhas: {len(df)}")
    print(f"Formato: {args.formato}")
    print(f"Taxa de respostas parciais solicitada: {args.taxa_parciais}")
    print(f"Linhas parciais geradas: {partial_rows}")


if __name__ == "__main__":
    main()
