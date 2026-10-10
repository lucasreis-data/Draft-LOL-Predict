#!/bin/sh
set -e

# Com argumentos (ex.: treino local), executa o comando passado e pronto.
if [ "$#" -gt 0 ]; then
  exec "$@"
fi

# Na nuvem: baixa CSVs + modelos do S3 ANTES de subir a API.
if [ -n "$ARTEFATOS_S3" ]; then
  python baixar_artefatos.py
fi

# WEB_CONCURRENCY = numero de workers (cada um carrega sua copia dos dados/modelos na RAM).
exec uvicorn api:app --host 0.0.0.0 --port 5000 --workers "${WEB_CONCURRENCY:-1}"
