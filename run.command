#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Criando ambiente virtual..."
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

echo "Iniciando ESQUADA em http://localhost:5001"
open "http://localhost:5001"
.venv/bin/python app.py
