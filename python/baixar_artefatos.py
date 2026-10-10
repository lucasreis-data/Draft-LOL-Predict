"""Baixa o pacote de artefatos (CSVs + modelos .joblib + encoders) do S3 para o disco.

Uso:  ARTEFATOS_S3=s3://meu-bucket/artefatos/v1 python baixar_artefatos.py

Estrutura esperada no S3 (mesma estrutura de pastas do projeto):
    <prefixo>/csv/*.csv
    <prefixo>/modelos_treinados/*.joblib
Roda ANTES do uvicorn: o cblol.py le os CSVs no import.
"""
import glob
import os
import sys
from urllib.parse import urlparse

import boto3
from boto3.s3.transfer import TransferConfig

DESTINO = os.environ.get("ARTEFATOS_DESTINO", os.path.dirname(os.path.abspath(__file__)))


def baixar(url_s3: str, destino: str = DESTINO) -> int:
    u = urlparse(url_s3)
    if u.scheme != "s3" or not u.netloc:
        raise ValueError(f"ARTEFATOS_S3 invalido: {url_s3!r} (esperado s3://bucket/prefixo)")
    bucket, prefixo = u.netloc, u.path.strip("/")
    prefixo_busca = prefixo + "/" if prefixo else ""

    s3 = boto3.client("s3")
    cfg = TransferConfig(max_concurrency=16, multipart_chunksize=16 * 1024 * 1024)
    baixados = 0

    for pagina in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefixo_busca):
        for obj in pagina.get("Contents", []):
            chave = obj["Key"]
            if chave.endswith("/"):
                continue
            relativo = chave[len(prefixo_busca):]
            caminho = os.path.join(destino, relativo)
            if os.path.exists(caminho) and os.path.getsize(caminho) == obj["Size"]:
                print(f"[S3] ja existe, pulando: {relativo}", flush=True)
                continue
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            print(f"[S3] baixando {relativo} ({obj['Size'] / 1024 / 1024:.0f} MB)", flush=True)
            s3.download_file(bucket, chave, caminho, Config=cfg)
            baixados += 1

    faltando = []
    if not glob.glob(os.path.join(destino, "csv", "*.csv")):
        faltando.append("csv/*.csv")
    if not os.path.exists(os.path.join(destino, "modelos_treinados", "modelo_GERAL.joblib")):
        faltando.append("modelos_treinados/modelo_GERAL.joblib")
    if faltando:
        raise RuntimeError(f"Artefatos incompletos em {url_s3}; faltam: {', '.join(faltando)}")
    
    print(f"[S3] concluido: {baixados} arquivo(s) baixado(s).", flush=True)
    return baixados


if __name__ == "__main__":
    url = os.environ.get("ARTEFATOS_S3")
    if not url:
        sys.exit("Defina ARTEFATOS_S3=s3://bucket/prefixo")
    baixar(url)
