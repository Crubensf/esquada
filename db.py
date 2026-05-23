# -*- coding: utf-8 -*-
"""Conexão com o banco de dados (SQLite local em desenvolvimento, Turso em produção)."""

from __future__ import annotations
import os
import sqlite3

try:
    import libsql  # cliente Turso (libSQL) — disponível apenas em produção
except ImportError:
    libsql = None

# Diretório raiz do projeto (onde este arquivo está)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "esquada.db")

# Variáveis de ambiente para conexão com Turso (definidas apenas em produção)
TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN   = os.environ.get("TURSO_AUTH_TOKEN")


def get_db():
    """Retorna uma conexão ativa: Turso em produção, SQLite em desenvolvimento."""
    if TURSO_DATABASE_URL:
        if libsql is None:
            raise RuntimeError("Pacote 'libsql' ausente — rode: pip install libsql")
        return libsql.connect(database=TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)
    return sqlite3.connect(DB_PATH)


def _query_one(conn, sql: str, params: tuple = ()):
    """Executa um SELECT e retorna a primeira linha como tupla, ou None."""
    rows = conn.execute(sql, params).fetchall()
    return rows[0] if rows else None


def init_db() -> None:
    """Cria as tabelas necessárias se ainda não existirem."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            institution   TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Migração: adiciona coluna institution em bancos existentes sem ela
    try:
        conn.execute("ALTER TABLE users ADD COLUMN institution TEXT")
    except Exception:
        pass
    conn.execute("""
        CREATE TABLE IF NOT EXISTS verification_codes (
            email      TEXT PRIMARY KEY,
            code       TEXT NOT NULL,
            expires_at INTEGER NOT NULL
        )
    """)
    conn.commit()
