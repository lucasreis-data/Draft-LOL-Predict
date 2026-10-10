FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# So codigo. CSVs e .joblib NAO entram na imagem: vem do S3 (ou de volume, no treino local).
COPY api.py cblol.py draft.py modelos_cache.py baixar_artefatos.py entrypoint.sh ./
COPY modelos_treinados/treino_ia.py modelos_treinados/treino_ia.py
RUN useradd -r -u 1001 -m app \
 && chmod +x entrypoint.sh \
 && mkdir -p csv modelos_treinados cache_dados \
 && chown -R app:app /app
USER app

EXPOSE 5000

# Start period longo: download do S3 + import do cblol.py (~25 s) + preload dos modelos.
HEALTHCHECK --interval=30s --timeout=5s --start-period=600s --retries=3 \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:5000/',timeout=4)" || exit 1

ENTRYPOINT ["./entrypoint.sh"]
