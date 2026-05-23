# -*- coding: utf-8 -*-
"""
ESQUADA — Backend Flask.

Define a aplicação Flask, autenticação de usuários e todas as rotas da API.
A lógica de cálculo IRT está em irt.py; a de pontuação em scoring.py.
"""

from __future__ import annotations
import csv
import io
import json
import logging
import os
import random
import secrets
import time
import urllib.request
import base64 as _b64
from functools import wraps

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, send_file, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash

from db import BASE_DIR, get_db, _query_one, init_db
from items import ESQ_ITEMS, ESQ_COLS
from params import _load_partrue
from scoring import (
    _compute_scores,
    _item_category_count,
    _read_csv_flexible,
    _score_dataframe,
    _validate_response_array,
    categorizar_F1,
    categorizar_F1novo,
)

logging.basicConfig(level=logging.ERROR)

RESEND_API_KEY   = os.environ.get("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "ESQUADA <noreply@resend.dev>")


# ─── Chave secreta e autenticação ─────────────────────────────────────────────

def _load_secret_key() -> str:
    """Carrega a chave secreta do Flask: variável de ambiente > arquivo local > gera nova."""
    env_key = os.environ.get("SECRET_KEY")
    if env_key:
        return env_key
    key_file = os.path.join(BASE_DIR, ".flask_secret")
    if os.path.exists(key_file):
        with open(key_file) as f:
            return f.read().strip()
    key = secrets.token_hex(32)
    try:
        with open(key_file, "w") as f:
            f.write(key)
    except OSError:
        pass
    return key


def login_required(f):
    """Decorator: exige sessão autenticada; retorna 401 caso contrário."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify(error="Acesso restrito. Faça login para continuar."), 401
        return f(*args, **kwargs)
    return decorated


# ─── Aplicação Flask ──────────────────────────────────────────────────────────

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key                        = _load_secret_key()
app.config['MAX_CONTENT_LENGTH']      = int(4.5 * 1024 * 1024)  # 4.5 MB
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
# Cookies seguros apenas em produção (Vercel define VERCEL=1)
app.config['SESSION_COOKIE_SECURE']   = os.environ.get('VERCEL') == '1'

try:
    init_db()
except Exception:
    logging.exception("Falha ao inicializar o banco de dados")


@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify(error="O arquivo enviado excede o limite de 4,5 MB."), 413


# ─── Auth ─────────────────────────────────────────────────────────────────────

def _send_verification_email(to_email: str, code: str) -> None:
    """Envia o código de verificação via Resend."""
    html = f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
                max-width:480px;margin:0 auto;padding:40px 32px;color:#0f1c25">
      <h2 style="margin:0 0 8px;font-size:22px">Verifique seu e-mail</h2>
      <p style="margin:0 0 28px;color:#4e5a63;font-size:15px;line-height:1.5">
        Use o código abaixo para concluir seu cadastro no ESQUADA.
        Ele expira em <strong>10 minutos</strong>.
      </p>
      <div style="background:#f3eee5;border-radius:14px;padding:28px;
                  text-align:center;margin-bottom:28px">
        <span style="font-size:42px;font-weight:700;letter-spacing:10px;
                     font-family:monospace;color:#0f1c25">{code}</span>
      </div>
      <p style="margin:0;color:#6b7580;font-size:13px">
        Se você não solicitou esse cadastro, ignore este e-mail.
      </p>
    </div>
    """
    payload = json.dumps({
        "from":    RESEND_FROM_EMAIL,
        "to":      [to_email],
        "subject": f"{code} — código de verificação ESQUADA",
        "html":    html,
    }).encode()
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type":  "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        if resp.status >= 400:
            raise RuntimeError(f"Resend status {resp.status}")


@app.route("/api/auth/send-verification", methods=["POST"])
def send_verification():
    """Gera um código de 6 dígitos, salva no banco e envia por e-mail."""
    data  = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify(error="E-mail obrigatório."), 400

    conn = get_db()
    if _query_one(conn, "SELECT id FROM users WHERE email = ?", (email,)):
        return jsonify(error="Este e-mail já está cadastrado."), 409

    code    = f"{random.randint(0, 999999):06d}"
    expires = int(time.time()) + 600  # 10 minutos
    conn.execute(
        "INSERT OR REPLACE INTO verification_codes (email, code, expires_at) VALUES (?, ?, ?)",
        (email, code, expires),
    )
    conn.commit()

    if not RESEND_API_KEY:
        # Modo desenvolvimento: retorna o código para facilitar testes locais
        return jsonify(ok=True, dev_code=code)

    try:
        _send_verification_email(email, code)
    except Exception:
        logging.exception("Falha ao enviar e-mail de verificação")
        return jsonify(error="Falha ao enviar o e-mail. Tente novamente."), 500

    return jsonify(ok=True)


@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    """Valida o código de verificação e cria o usuário."""
    data        = request.get_json(force=True) or {}
    name        = (data.get("name") or "").strip()
    institution = (data.get("institution") or "").strip()
    email       = (data.get("email") or "").strip().lower()
    password    = (data.get("password") or "")
    code        = (data.get("code") or "").strip()

    if not name or not institution or not email or not password or not code:
        return jsonify(error="Todos os campos obrigatórios devem ser preenchidos."), 400
    if len(password) < 6:
        return jsonify(error="A senha precisa ter pelo menos 6 caracteres."), 400

    conn = get_db()

    # Valida o código de verificação
    row_code = _query_one(
        conn, "SELECT code, expires_at FROM verification_codes WHERE email = ?", (email,)
    )
    if not row_code:
        return jsonify(error="Código inválido. Solicite um novo código."), 400
    stored_code, expires_at = row_code
    if int(time.time()) > expires_at:
        return jsonify(error="Código expirado. Solicite um novo código."), 400
    if code != stored_code:
        return jsonify(error="Código incorreto. Verifique e tente novamente."), 400

    # Cria o usuário
    if _query_one(conn, "SELECT id FROM users WHERE email = ?", (email,)):
        return jsonify(error="Este e-mail já está cadastrado."), 409
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash, institution) VALUES (?, ?, ?, ?)",
            (name, email, generate_password_hash(password), institution),
        )
        conn.execute("DELETE FROM verification_codes WHERE email = ?", (email,))
        conn.commit()
    except Exception as e:
        if "unique" in str(e).lower() or "constraint" in str(e).lower():
            return jsonify(error="Este e-mail já está cadastrado."), 409
        raise
    row = _query_one(conn, "SELECT id, name, email FROM users WHERE email = ?", (email,))
    session["user_id"]    = row[0]
    session["user_name"]  = row[1]
    session["user_email"] = row[2]
    return jsonify(user={"id": row[0], "name": row[1], "email": row[2]}), 201


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    """Autentica usuário e inicia sessão."""
    data     = request.get_json(force=True) or {}
    email    = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "")
    conn = get_db()
    row  = _query_one(
        conn, "SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,)
    )
    if not row or not check_password_hash(row[3], password):
        return jsonify(error="E-mail ou senha incorretos."), 401
    session["user_id"]    = row[0]
    session["user_name"]  = row[1]
    session["user_email"] = row[2]
    return jsonify(user={"id": row[0], "name": row[1], "email": row[2]})


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    """Encerra a sessão do usuário."""
    session.clear()
    return jsonify(ok=True)


@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    """Retorna os dados do usuário autenticado, ou null se não houver sessão."""
    if "user_id" not in session:
        return jsonify(user=None)
    return jsonify(user={
        "id":    session["user_id"],
        "name":  session["user_name"],
        "email": session["user_email"],
    })


# ─── API de pontuação ─────────────────────────────────────────────────────────

@app.route("/api/score_csv", methods=["POST"])
@login_required
def score_csv():
    """Recebe um CSV com respostas ESQUADA e devolve CSV com escores calculados."""
    if "file" not in request.files:
        return jsonify(error="Envie um arquivo CSV em form-data com a chave 'file'."), 400
    try:
        par = _load_partrue()
        if len(par) != 25:
            return jsonify(error=f"Parâmetros do modelo têm {len(par)} itens; precisam ser 25."), 400
        df     = _read_csv_flexible(request.files["file"].read())
        scored = _score_dataframe(df, par)
        buf = io.StringIO()
        scored.to_csv(buf, sep=";", index=False, decimal=",",
                      quoting=csv.QUOTE_NONNUMERIC, quotechar='"')
        mem = io.BytesIO(buf.getvalue().encode("utf-8"))
        mem.seek(0)
        return send_file(mem, mimetype="text/csv", as_attachment=True,
                         download_name="qualidade-da-dieta.csv")
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception:
        logging.exception("Erro interno em /api/score_csv")
        return jsonify(error="Erro interno ao processar o arquivo. Verifique se o CSV está no formato correto."), 500


@app.route("/api/template_csv", methods=["GET"])
def download_template_csv():
    """Devolve o CSV modelo para preenchimento."""
    return send_file(
        os.path.join(BASE_DIR, "data", "modelo_envio_esquada.csv"),
        mimetype="text/csv",
        as_attachment=True,
        download_name="modelo_envio_esquada.csv",
    )


@app.route("/api/score_rows", methods=["POST"])
def score_rows():
    """Pontua respostas enviadas como JSON (sem CSV). Usado pelo questionário online."""
    try:
        data = request.get_json(force=True)
        rows = data.get("rows", [])
        if not rows:
            return jsonify(error="Envie 'rows' como lista de listas com 25 respostas cada."), 400
        arr = np.array(rows, dtype=float)
        if arr.ndim != 2 or arr.shape[1] != 25:
            return jsonify(error=f"Esperava matriz N x 25; recebi shape {arr.shape}"), 400
        par = _load_partrue()
        if len(par) != 25:
            return jsonify(error=f"Parâmetros do modelo têm {len(par)} itens; precisam ser 25."), 400
        _validate_response_array(arr, par)
        F1, SE, F1novo = _compute_scores(arr, par)
        resp = [
            {
                "F1":              None if np.isnan(F1[i])     else float(F1[i]),
                "SE_F1":           None if np.isnan(SE[i])     else float(SE[i]),
                "F1novo":          None if np.isnan(F1novo[i]) else float(F1novo[i]),
                "escore.cat":      None if np.isnan(F1[i])     else categorizar_F1(float(F1[i])),
                "escore.cat.novo": None if np.isnan(F1novo[i]) else categorizar_F1novo(float(F1novo[i])),
            }
            for i in range(len(F1))
        ]
        return jsonify(results=resp)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception:
        logging.exception("Erro interno em /api/score_rows")
        return jsonify(error="Erro interno ao calcular escores. Verifique o formato dos dados enviados."), 500


@app.route("/api/analyze_csv", methods=["POST"])
@login_required
def analyze_csv():
    """Pontua um CSV e retorna estatísticas, gráficos e tabela de resultados para o dashboard."""
    if "file" not in request.files:
        return jsonify(error="Envie um arquivo CSV."), 400
    try:
        par = _load_partrue()
        if len(par) != 25:
            return jsonify(error="Parâmetros inválidos."), 400

        raw       = request.files["file"].read()
        df        = _read_csv_flexible(raw)
        total     = len(df)
        items_arr = df[ESQ_COLS].to_numpy(dtype=float, na_value=np.nan)

        # Coleta problemas: células ausentes e valores fora da faixa permitida
        errors = []
        for i in range(total):
            row_id  = str(df.iloc[i]["ID"])
            missing = [ESQ_COLS[j] for j in range(25) if np.isnan(items_arr[i, j])]
            if missing:
                cols_str = ", ".join(missing[:3]) + ("…" if len(missing) > 3 else "")
                errors.append({"row": i + 1, "id": row_id, "type": "valores_ausentes",
                               "detail": f"{len(missing)} coluna(s) sem resposta: {cols_str}"})
        for j, item_par in enumerate(par):
            max_val = _item_category_count(item_par) - 1
            for i in range(total):
                v = items_arr[i, j]
                if not np.isnan(v) and (v < 0 or v > max_val):
                    errors.append({"row": i + 1, "id": str(df.iloc[i]["ID"]),
                                   "type": "valor_invalido",
                                   "detail": f"{ESQ_COLS[j]}: {int(v)} (esperado 0–{max_val})"})

        scored           = _score_dataframe(df, par)
        f1_ser           = scored["F1novo"].dropna().astype(float)
        valid_count      = int(len(f1_ser))
        rows_any_missing = int(np.isnan(items_arr).any(axis=1).sum())

        # Estatísticas descritivas
        stats = {
            "total":      total,
            "valid":      valid_count,
            "incomplete": rows_any_missing,
            "mean":       round(float(f1_ser.mean()),        2) if valid_count > 0 else None,
            "median":     round(float(f1_ser.median()),      2) if valid_count > 0 else None,
            "min":        round(float(f1_ser.min()),         2) if valid_count > 0 else None,
            "max":        round(float(f1_ser.max()),         2) if valid_count > 0 else None,
            "std":        round(float(f1_ser.std(ddof=1)),   2) if valid_count > 1 else (0.0 if valid_count == 1 else None),
            "top_cat":    str(scored["escore.cat.novo"].value_counts().idxmax()) if valid_count > 0 else None,
        }

        # Distribuição por categoria
        cats_order = ["muito ruim", "ruim", "boa", "muito boa", "excelente"]
        cat_dist   = {c: int((scored["escore.cat.novo"] == c).sum()) for c in cats_order}

        # Histograma com bins de 25 pontos, entre 150 e 425
        bins      = list(range(150, 426, 25))
        hist_data = [
            {"lo": bins[k], "hi": bins[k + 1],
             "count": int(((f1_ser >= bins[k]) & (f1_ser < bins[k + 1])).sum())}
            for k in range(len(bins) - 1)
        ]

        # Média de cada item como % do valor máximo possível
        item_means_list = []
        for j, col in enumerate(ESQ_COLS):
            vals       = items_arr[:, j]
            valid_vals = vals[~np.isnan(vals)]
            max_val    = _item_category_count(par[j]) - 1
            raw_mean   = float(np.mean(valid_vals)) if len(valid_vals) > 0 else 0.0
            pct        = (raw_mean / max_val * 100) if max_val > 0 else 0.0
            item_means_list.append({"label": f"Q{j+1}", "raw_mean": round(raw_mean, 3),
                                    "pct": round(pct, 1), "max": max_val})

        # Resultados individuais para a tabela do dashboard
        results_list = [
            {
                "ID":     str(row["ID"]),
                "F1novo": None if pd.isna(row["F1novo"]) else round(float(row["F1novo"]), 1),
                "F1":     None if pd.isna(row["F1"])     else round(float(row["F1"]),     4),
                "SE_F1":  None if pd.isna(row["SE_F1"])  else round(float(row["SE_F1"]),  4),
                "cat":    None if pd.isna(row["escore.cat.novo"]) else str(row["escore.cat.novo"]),
            }
            for _, row in scored.iterrows()
        ]

        # CSV pontuado em base64 para download no front-end
        buf     = io.StringIO()
        scored.to_csv(buf, sep=";", index=False, decimal=",",
                      quoting=csv.QUOTE_NONNUMERIC, quotechar='"')
        csv_b64 = _b64.b64encode(buf.getvalue().encode("utf-8")).decode("ascii")

        return jsonify({
            "stats":         stats,
            "category_dist": cat_dist,
            "histogram":     hist_data,
            "item_means":    item_means_list,
            "results":       results_list,
            "errors":        errors,
            "csv_b64":       csv_b64,
        })
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception:
        logging.exception("Erro em /api/analyze_csv")
        return jsonify(error="Erro interno ao processar o arquivo."), 500


# ─── Frontend e schema ────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def root():
    """Serve o arquivo HTML principal."""
    return send_from_directory(os.path.join(BASE_DIR, "static"), "index.html")


@app.route("/api/schema", methods=["GET"])
def schema():
    """Retorna a definição dos 25 itens: texto, opções e score_map."""
    try:
        par = _load_partrue()
        if len(par) != 25 or len(ESQ_ITEMS) != 25:
            return jsonify(error="Esperava 25 itens."), 400
        items = []
        for j in range(25):
            m         = _item_category_count(par[j])
            options   = ESQ_ITEMS[j]["options"]
            score_map = ESQ_ITEMS[j]["score_map"]
            if len(options) != len(score_map):
                return jsonify(error=f"Item {j+1} com número diferente de opções e score_map."), 400
            if any(score < 0 or score >= m for score in score_map):
                return jsonify(error=f"Item {j+1} tem score_map fora da faixa 0..{m-1}."), 400
            items.append({
                "index":            j + 1,
                "name":             ESQ_ITEMS[j]["name"],
                "text":             ESQ_ITEMS[j]["text"],
                "categories":       len(options),
                "score_categories": m,
                "options":          options,
                "score_map":        score_map,
            })
        return jsonify(items=items)
    except Exception as e:
        return jsonify(error=str(e)), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
