#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


SCORE_COLUMNS = ["F1", "F1novo", "escore.cat", "escore.cat.novo"]
NUMERIC_SCORE_COLUMNS = ["F1", "F1novo"]
CATEGORY_SCORE_COLUMNS = ["escore.cat", "escore.cat.novo"]


def detect_separator(path: Path) -> str:
    sample = path.read_text(encoding="utf-8")[:4096]
    return ";" if sample.count(";") >= sample.count(",") else ","


def load_result_csv(path: Path) -> pd.DataFrame:
    sep = detect_separator(path)
    df = pd.read_csv(path, sep=sep, dtype=str)
    df.columns = [str(col).strip() for col in df.columns]
    unnamed = [col for col in df.columns if col.lower().startswith("unnamed") or col == ""]
    if unnamed:
        df = df.drop(columns=unnamed)

    for col in ["F1", "F1novo"]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", ".", regex=False),
                errors="coerce",
            )

    for col in ["ID", "record_id"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def choose_join_key(df_a: pd.DataFrame, df_b: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, str, str]:
    options = [
        ("ID", "ID"),
        ("record_id", "record_id"),
        ("ID", "record_id"),
        ("record_id", "ID"),
    ]
    for key_a, key_b in options:
        if key_a in df_a.columns and key_b in df_b.columns:
            return df_a.copy(), df_b.copy(), key_a, key_b

    tmp_a = df_a.copy()
    tmp_b = df_b.copy()
    tmp_a["linha"] = [str(i) for i in range(1, len(tmp_a) + 1)]
    tmp_b["linha"] = [str(i) for i in range(1, len(tmp_b) + 1)]
    return tmp_a, tmp_b, "linha", "linha"


def available_score_columns(df_a: pd.DataFrame, df_b: pd.DataFrame) -> List[str]:
    common = [col for col in SCORE_COLUMNS if col in df_a.columns and col in df_b.columns]
    if not common:
        raise ValueError(
            "Nao encontrei colunas de score em comum entre os dois arquivos. "
            "Esperava pelo menos uma entre: F1, F1novo, escore.cat, escore.cat.novo."
        )
    return common


def build_comparison(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    label_a: str,
    label_b: str,
) -> Tuple[pd.DataFrame, Dict[str, object]]:
    df_a, df_b, key_a, key_b = choose_join_key(df_a, df_b)
    common_scores = available_score_columns(df_a, df_b)
    metadata = {
        "join_key_a": key_a,
        "join_key_b": key_b,
        "duplicated_keys_a": int(df_a[key_a].duplicated().sum()),
        "duplicated_keys_b": int(df_b[key_b].duplicated().sum()),
    }

    cols_a = [key_a] + common_scores
    cols_b = [key_b] + common_scores
    merged = df_a[cols_a].merge(
        df_b[cols_b],
        left_on=key_a,
        right_on=key_b,
        how="outer",
        indicator=True,
        suffixes=(f"_{label_a}", f"_{label_b}"),
    )

    merged["chave"] = merged[key_a].fillna(merged[key_b])

    ordered_cols: List[str] = ["chave", "_merge"]

    if "F1" in common_scores:
        merged["delta_F1"] = merged[f"F1_{label_a}"] - merged[f"F1_{label_b}"]
        merged["abs_delta_F1"] = merged["delta_F1"].abs()
        ordered_cols.extend([
            f"F1_{label_a}",
            f"F1_{label_b}",
            "delta_F1",
            "abs_delta_F1",
        ])

    if "F1novo" in common_scores:
        merged["delta_F1novo"] = merged[f"F1novo_{label_a}"] - merged[f"F1novo_{label_b}"]
        merged["abs_delta_F1novo"] = merged["delta_F1novo"].abs()
        ordered_cols.extend([
            f"F1novo_{label_a}",
            f"F1novo_{label_b}",
            "delta_F1novo",
            "abs_delta_F1novo",
        ])

    if "escore.cat" in common_scores:
        merged["escore.cat_igual"] = merged[f"escore.cat_{label_a}"] == merged[f"escore.cat_{label_b}"]
        ordered_cols.extend([
            f"escore.cat_{label_a}",
            f"escore.cat_{label_b}",
            "escore.cat_igual",
        ])

    if "escore.cat.novo" in common_scores:
        merged["escore.cat.novo_igual"] = (
            merged[f"escore.cat.novo_{label_a}"] == merged[f"escore.cat.novo_{label_b}"]
        )
        ordered_cols.extend([
            f"escore.cat.novo_{label_a}",
            f"escore.cat.novo_{label_b}",
            "escore.cat.novo_igual",
        ])

    sort_col = "abs_delta_F1" if "abs_delta_F1" in merged.columns else "abs_delta_F1novo"
    if sort_col in merged.columns:
        merged = merged.sort_values(by=[sort_col, "chave"], ascending=[False, True], na_position="last")
    else:
        merged = merged.sort_values(by=["chave"], ascending=[True], na_position="last")

    return merged[ordered_cols].reset_index(drop=True), metadata


def _safe_float(value: float | int | np.floating | np.integer | None) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def analyze_numeric_column(matched: pd.DataFrame, label_a: str, label_b: str, col: str) -> Dict[str, object]:
    delta_col = f"delta_{col}"
    abs_col = f"abs_delta_{col}"
    valid = matched[[f"{col}_{label_a}", f"{col}_{label_b}", delta_col, abs_col]].dropna()
    if valid.empty:
        return {"comparacoes_validas": 0}

    delta = valid[delta_col]
    abs_delta = valid[abs_col]
    return {
        "comparacoes_validas": int(len(valid)),
        "max_abs": _safe_float(abs_delta.max()),
        "media_abs": _safe_float(abs_delta.mean()),
        "mediana_abs": _safe_float(abs_delta.median()),
        "p90_abs": _safe_float(abs_delta.quantile(0.90)),
        "p95_abs": _safe_float(abs_delta.quantile(0.95)),
        "rmse": _safe_float(np.sqrt(np.mean(np.square(delta)))),
        "dentro_1e-06": int((abs_delta <= 1e-6).sum()),
        "dentro_1e-04": int((abs_delta <= 1e-4).sum()),
        "dentro_1e-03": int((abs_delta <= 1e-3).sum()),
        "dentro_1e-02": int((abs_delta <= 1e-2).sum()),
    }


def analyze_category_column(matched: pd.DataFrame, label_a: str, label_b: str, col: str) -> Dict[str, object]:
    eq_col = f"{col}_igual"
    valid = matched[[f"{col}_{label_a}", f"{col}_{label_b}", eq_col]].dropna(subset=[f"{col}_{label_a}", f"{col}_{label_b}"])
    if valid.empty:
        return {"comparacoes_validas": 0}

    iguais = int(valid[eq_col].sum())
    diferentes = int((~valid[eq_col]).sum())
    taxa = float(iguais / len(valid))
    pares_diferentes = (
        valid.loc[~valid[eq_col], [f"{col}_{label_a}", f"{col}_{label_b}"]]
        .value_counts()
        .head(5)
        .reset_index(name="frequencia")
    )
    exemplos = []
    for _, row in pares_diferentes.iterrows():
        exemplos.append(
            f"{row[f'{col}_{label_a}']} x {row[f'{col}_{label_b}']}: {int(row['frequencia'])}"
        )

    return {
        "comparacoes_validas": int(len(valid)),
        "iguais": iguais,
        "diferentes": diferentes,
        "taxa_concordancia": taxa,
        "pares_diferentes_mais_comuns": exemplos,
    }


def build_assessment(summary: Dict[str, object]) -> str:
    cat_diff = int(summary.get("categorias_diferentes", 0))
    cat_novo_diff = int(summary.get("categorias_novas_diferentes", 0))
    max_f1 = summary.get("max_abs_delta_F1")
    max_f1novo = summary.get("max_abs_delta_F1novo")

    if cat_diff > 0 or cat_novo_diff > 0:
        return "Ha divergencias nas categorias finais; vale revisar o alinhamento entre os calculos."
    if max_f1 is None or max_f1novo is None:
        return "Nao foi possivel calcular a margem numerica completa."
    if max_f1 <= 0.001 and max_f1novo <= 0.05:
        return "Os resultados estao praticamente identicos, inclusive nos scores numericos."
    if max_f1 <= 0.01 and max_f1novo <= 0.5:
        return "As categorias finais batem 100% e a diferenca numerica dos scores e pequena."
    if max_f1 <= 0.05 and max_f1novo <= 2.5:
        return "As categorias podem continuar estaveis, mas a diferenca numerica dos scores ja merece atencao."
    return "A margem numerica esta relevante; vale revisar quadratura, parametros e alinhamento do processamento."


def summarize(
    comparison: pd.DataFrame,
    metadata: Dict[str, object],
    label_a: str,
    label_b: str,
    top_n: int,
) -> Dict[str, object]:
    matched = comparison[comparison["_merge"] == "both"].copy()
    summary: Dict[str, object] = {
        "linhas_arquivo_a": int((comparison["_merge"] != "right_only").sum()),
        "linhas_arquivo_b": int((comparison["_merge"] != "left_only").sum()),
        "linhas_comparadas": int((comparison["_merge"] == "both").sum()),
        "apenas_no_arquivo_a": int((comparison["_merge"] == "left_only").sum()),
        "apenas_no_arquivo_b": int((comparison["_merge"] == "right_only").sum()),
        "chave_usada_arquivo_a": metadata["join_key_a"],
        "chave_usada_arquivo_b": metadata["join_key_b"],
        "chaves_duplicadas_arquivo_a": metadata["duplicated_keys_a"],
        "chaves_duplicadas_arquivo_b": metadata["duplicated_keys_b"],
    }

    numeric_analysis: Dict[str, Dict[str, object]] = {}
    for col in NUMERIC_SCORE_COLUMNS:
        if f"abs_delta_{col}" in matched.columns:
            info = analyze_numeric_column(matched, label_a, label_b, col)
            numeric_analysis[col] = info
            if info.get("comparacoes_validas", 0):
                summary[f"max_abs_delta_{col}"] = info["max_abs"]
                summary[f"media_abs_delta_{col}"] = info["media_abs"]
                summary[f"mediana_abs_delta_{col}"] = info["mediana_abs"]
                summary[f"p95_abs_delta_{col}"] = info["p95_abs"]
                summary[f"rmse_delta_{col}"] = info["rmse"]

    category_analysis: Dict[str, Dict[str, object]] = {}
    for col in CATEGORY_SCORE_COLUMNS:
        eq_col = f"{col}_igual"
        if eq_col in matched.columns:
            info = analyze_category_column(matched, label_a, label_b, col)
            category_analysis[col] = info
            if info.get("comparacoes_validas", 0):
                if col == "escore.cat":
                    summary["categorias_iguais"] = info["iguais"]
                    summary["categorias_diferentes"] = info["diferentes"]
                    summary["taxa_concordancia_categorias"] = info["taxa_concordancia"]
                if col == "escore.cat.novo":
                    summary["categorias_novas_iguais"] = info["iguais"]
                    summary["categorias_novas_diferentes"] = info["diferentes"]
                    summary["taxa_concordancia_categorias_novas"] = info["taxa_concordancia"]

    top_col = "abs_delta_F1" if "abs_delta_F1" in matched.columns else "abs_delta_F1novo"
    top_diffs = []
    if top_col in matched.columns:
        top = matched.sort_values(top_col, ascending=False).head(top_n)
        for _, row in top.iterrows():
            item = {"chave": row["chave"]}
            if "F1" in numeric_analysis:
                item["F1_py_r"] = (
                    f"{row.get(f'F1_{label_a}', np.nan)} x {row.get(f'F1_{label_b}', np.nan)}"
                )
                item["abs_delta_F1"] = _safe_float(row.get("abs_delta_F1"))
            if "F1novo" in numeric_analysis:
                item["F1novo_py_r"] = (
                    f"{row.get(f'F1novo_{label_a}', np.nan)} x {row.get(f'F1novo_{label_b}', np.nan)}"
                )
                item["abs_delta_F1novo"] = _safe_float(row.get("abs_delta_F1novo"))
            if "escore.cat" in category_analysis:
                item["escore.cat"] = (
                    f"{row.get(f'escore.cat_{label_a}', '')} x {row.get(f'escore.cat_{label_b}', '')}"
                )
            if "escore.cat.novo" in category_analysis:
                item["escore.cat.novo"] = (
                    f"{row.get(f'escore.cat.novo_{label_a}', '')} x {row.get(f'escore.cat.novo_{label_b}', '')}"
                )
            top_diffs.append(item)

    summary["analise_numerica"] = numeric_analysis
    summary["analise_categorias"] = category_analysis
    summary["maiores_diferencas"] = top_diffs
    summary["parecer"] = build_assessment(summary)
    return summary


def write_summary(path: Path, summary: Dict[str, object], label_a: str, label_b: str) -> None:
    lines = [
        f"Comparacao entre: {label_a} x {label_b}",
        f"Linhas no arquivo A: {summary['linhas_arquivo_a']}",
        f"Linhas no arquivo B: {summary['linhas_arquivo_b']}",
        f"Linhas comparadas: {summary['linhas_comparadas']}",
        f"So no arquivo A: {summary['apenas_no_arquivo_a']}",
        f"So no arquivo B: {summary['apenas_no_arquivo_b']}",
        f"Chave usada no arquivo A: {summary['chave_usada_arquivo_a']}",
        f"Chave usada no arquivo B: {summary['chave_usada_arquivo_b']}",
        f"Chaves duplicadas no arquivo A: {summary['chaves_duplicadas_arquivo_a']}",
        f"Chaves duplicadas no arquivo B: {summary['chaves_duplicadas_arquivo_b']}",
        "",
        f"Parecer: {summary['parecer']}",
    ]

    analise_numerica = summary.get("analise_numerica", {})
    for col, info in analise_numerica.items():
        lines.extend([
            "",
            f"Analise numerica de {col}:",
            f"Comparacoes validas: {info['comparacoes_validas']}",
            f"Maior diferenca absoluta: {info['max_abs']}",
            f"Media da diferenca absoluta: {info['media_abs']}",
            f"Mediana da diferenca absoluta: {info['mediana_abs']}",
            f"P90 da diferenca absoluta: {info['p90_abs']}",
            f"P95 da diferenca absoluta: {info['p95_abs']}",
            f"RMSE da diferenca: {info['rmse']}",
            f"Dentro de 1e-06: {info['dentro_1e-06']}",
            f"Dentro de 1e-04: {info['dentro_1e-04']}",
            f"Dentro de 1e-03: {info['dentro_1e-03']}",
            f"Dentro de 1e-02: {info['dentro_1e-02']}",
        ])

    analise_categorias = summary.get("analise_categorias", {})
    for col, info in analise_categorias.items():
        lines.extend([
            "",
            f"Analise categorica de {col}:",
            f"Comparacoes validas: {info['comparacoes_validas']}",
            f"Iguais: {info['iguais']}",
            f"Diferentes: {info['diferentes']}",
            f"Taxa de concordancia: {info['taxa_concordancia']}",
        ])
        if info["pares_diferentes_mais_comuns"]:
            lines.append("Pares diferentes mais comuns:")
            for item in info["pares_diferentes_mais_comuns"]:
                lines.append(f"- {item}")

    maiores_diferencas = summary.get("maiores_diferencas", [])
    if maiores_diferencas:
        lines.extend(["", "Maiores diferencas encontradas:"])
        for item in maiores_diferencas:
            detail = [f"chave={item['chave']}"]
            if "abs_delta_F1" in item:
                detail.append(f"abs_delta_F1={item['abs_delta_F1']}")
            if "abs_delta_F1novo" in item:
                detail.append(f"abs_delta_F1novo={item['abs_delta_F1novo']}")
            if "escore.cat" in item:
                detail.append(f"escore.cat={item['escore.cat']}")
            if "escore.cat.novo" in item:
                detail.append(f"escore.cat.novo={item['escore.cat.novo']}")
            lines.append("- " + "; ".join(detail))

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compara os scores finais entre dois CSVs de resultado."
    )
    parser.add_argument("arquivo_a", type=Path, help="Primeiro CSV de resultado.")
    parser.add_argument("arquivo_b", type=Path, help="Segundo CSV de resultado.")
    parser.add_argument(
        "--rotulo-a",
        default="a",
        help="Rotulo curto do primeiro arquivo na saida comparativa.",
    )
    parser.add_argument(
        "--rotulo-b",
        default="b",
        help="Rotulo curto do segundo arquivo na saida comparativa.",
    )
    parser.add_argument(
        "--saida-csv",
        type=Path,
        help="Arquivo CSV com a comparacao linha a linha.",
    )
    parser.add_argument(
        "--saida-resumo",
        type=Path,
        help="Arquivo TXT com o resumo da comparacao.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Quantidade de linhas com maior diferenca para destacar no resumo.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    label_a = str(args.rotulo_a).strip().replace(" ", "_")
    label_b = str(args.rotulo_b).strip().replace(" ", "_")

    df_a = load_result_csv(args.arquivo_a)
    df_b = load_result_csv(args.arquivo_b)
    comparison, metadata = build_comparison(df_a, df_b, label_a, label_b)
    summary = summarize(comparison, metadata, label_a, label_b, top_n=args.top_n)

    base_dir = Path(__file__).resolve().parent / "saida"
    base_dir.mkdir(parents=True, exist_ok=True)
    output_csv = args.saida_csv or (base_dir / f"comparacao_scores_{label_a}_vs_{label_b}.csv")
    output_txt = args.saida_resumo or (base_dir / f"comparacao_scores_{label_a}_vs_{label_b}_resumo.txt")

    comparison.to_csv(output_csv, index=False)
    write_summary(output_txt, summary, label_a, label_b)

    print(f"Comparacao CSV: {output_csv}")
    print(f"Resumo TXT: {output_txt}")
    print(f"Parecer: {summary['parecer']}")
    print(f"Linhas comparadas: {summary['linhas_comparadas']}")
    if "max_abs_delta_F1" in summary:
        print(f"Maior diferenca absoluta em F1: {summary['max_abs_delta_F1']}")
        print(f"Media da diferenca absoluta em F1: {summary['media_abs_delta_F1']}")
    if "max_abs_delta_F1novo" in summary:
        print(f"Maior diferenca absoluta em F1novo: {summary['max_abs_delta_F1novo']}")
        print(f"Media da diferenca absoluta em F1novo: {summary['media_abs_delta_F1novo']}")
    if "categorias_diferentes" in summary:
        print(f"Categorias diferentes: {summary['categorias_diferentes']}")
    if "categorias_novas_diferentes" in summary:
        print(f"Categorias novas diferentes: {summary['categorias_novas_diferentes']}")


if __name__ == "__main__":
    main()
