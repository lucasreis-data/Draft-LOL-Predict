#!/usr/bin/env python3
"""Sobe os artefatos da IA (CSVs + modelos .joblib + encoders) para o S3 e sincroniza updates.

O bucket e criado pela stack CDK "DraftArtefatos"; este script descobre o nome dele sozinho.
Cada versao vive num prefixo:  s3://<bucket>/artefatos/<versao>/{csv,modelos_treinados}/

Uso (a partir da raiz do repositorio ou de infra/):
  python infra/subir_artefatos.py v1                    # versao nova (recusa se v1 ja existir)
  python infra/subir_artefatos.py v1 --atualizar        # sincroniza v1: sobe so o que mudou
  python infra/subir_artefatos.py v1 --atualizar --tudo # idem, mas reenvia tudo
  python infra/subir_artefatos.py v2 --dry-run          # mostra o plano sem enviar nada
  python infra/subir_artefatos.py --listar              # lista as versoes que existem no bucket

Nunca apaga nada no S3. Credenciais: as mesmas do AWS CLI (aws configure / SSO / AWS_PROFILE).
"""
import argparse
import re
import sys
import threading
from pathlib import Path

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

STACK = "DraftArtefatos"  # mesmo nome usado em infra/app.py
OUTPUT = "Bucket"
BASE = "artefatos"
PY = Path(__file__).resolve().parent.parent / "python"

LIGAS = ["CBLOL", "LCK", "LPL", "LEC", "LCS", "LCP", "GERAL"]
OBRIGATORIOS = [f"modelos_treinados/modelo_{l}.joblib" for l in LIGAS] + ["modelos_treinados/encoders.joblib"]
RECOMENDADOS = ["modelos_treinados/dados_draft.joblib"]


def sair(msg: str, codigo: int = 1):
    print(f"\nERRO: {msg}", file=sys.stderr)
    sys.exit(codigo)


def mb(n: int) -> str:
    return f"{n / 1024 / 1024:.1f} MB"


def arquivos_locais() -> dict:
    """chave relativa (ex.: modelos_treinados/modelo_GERAL.joblib) -> Path"""
    achados = {}
    for pasta, padrao in (("csv", "*.csv"), ("modelos_treinados", "*.joblib")):
        for p in sorted((PY / pasta).glob(padrao)):
            achados[f"{pasta}/{p.name}"] = p
    return achados


def validar_locais(locais: dict):
    if not any(k.startswith("csv/") for k in locais):
        sair(f"Nenhum CSV em {PY / 'csv'}.")
    faltando = [k for k in OBRIGATORIOS if k not in locais]
    if faltando:
        sair("Faltam arquivos obrigatorios (rode o treino antes):\n  - " + "\n  - ".join(faltando))
    for k in RECOMENDADOS:
        if k not in locais:
            print(f"AVISO: {k} nao encontrado (a API o recalcula, mas e melhor subir).")


def descobrir_bucket(sessao) -> str:
    try:
        cf = sessao.client("cloudformation")
        stack = cf.describe_stacks(StackName=STACK)["Stacks"][0]
    except NoCredentialsError:
        sair("Sem credenciais AWS. Confira com: aws sts get-caller-identity")
    except ClientError as e:
        if "does not exist" in str(e):
            sair(f"A stack {STACK} nao existe nessa conta/regiao.\n"
                 f"Rode antes, dentro de infra/:  cdk deploy {STACK}\n"
                 f"(ou use --bucket NOME). Regiao atual: {sessao.region_name}")
        sair(f"Falha ao consultar a stack {STACK}: {e}")
    for o in stack.get("Outputs", []):
        if o["OutputKey"] == OUTPUT:
            return o["OutputValue"]
    sair(f"A stack {STACK} nao tem o output '{OUTPUT}'.")


def listar_remoto(s3, bucket: str, prefixo: str) -> dict:
    itens = {}
    for pag in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefixo):
        for o in pag.get("Contents", []):
            if not o["Key"].endswith("/"):
                itens[o["Key"][len(prefixo):]] = o["Size"]
    return itens


class Progresso:
    def __init__(self, nome: str, total: int):
        self.nome, self.total, self.feito = nome, total, 0
        self.lock, self.ultimo = threading.Lock(), -1

    def __call__(self, n: int):
        with self.lock:
            self.feito += n
            pct = int(self.feito * 100 / self.total) if self.total else 100
            if pct != self.ultimo and (pct % 5 == 0 or pct == 100):
                self.ultimo = pct
                print(f"\r  {self.nome}: {pct:3d}%", end="", flush=True)


def cmd_listar(s3, bucket: str):
    resp = s3.list_objects_v2(Bucket=bucket, Prefix=f"{BASE}/", Delimiter="/")
    versoes = [p["Prefix"] for p in resp.get("CommonPrefixes", [])]
    if not versoes:
        print(f"Nenhuma versao em s3://{bucket}/{BASE}/")
        return
    print(f"Versoes em s3://{bucket}/{BASE}/")
    for v in versoes:
        itens = listar_remoto(s3, bucket, v)
        print(f"  {v[len(BASE) + 1:-1]:<12} {len(itens):>3} arquivos  {mb(sum(itens.values()))}")


def main():
    ap = argparse.ArgumentParser(description="Sobe/sincroniza artefatos da IA no S3.")
    ap.add_argument("versao", nargs="?", help="nome da versao, ex.: v1")
    ap.add_argument("--atualizar", action="store_true", help="permite sincronizar uma versao que ja existe")
    ap.add_argument("--tudo", action="store_true", help="com --atualizar, reenvia tudo (nao so o que mudou)")
    ap.add_argument("--dry-run", action="store_true", help="mostra o plano e nao envia nada")
    ap.add_argument("--listar", action="store_true", help="lista as versoes existentes no bucket")
    ap.add_argument("--bucket", help="usa este bucket em vez de descobrir pela stack")
    a = ap.parse_args()

    sessao = boto3.session.Session()
    bucket = a.bucket or descobrir_bucket(sessao)
    s3 = sessao.client("s3")

    if a.listar:
        return cmd_listar(s3, bucket)
    if not a.versao:
        ap.error("informe a versao (ex.: v1) ou use --listar")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", a.versao):
        sair("Nome de versao invalido: use so letras, numeros, ponto, hifen e underline.")

    locais = arquivos_locais()
    validar_locais(locais)

    prefixo = f"{BASE}/{a.versao}/"
    remoto = listar_remoto(s3, bucket, prefixo)

    if remoto and not a.atualizar:
        sair(f"A versao '{a.versao}' ja existe em s3://{bucket}/{prefixo} ({len(remoto)} arquivos).\n"
             f"Use outro nome (ex.: v2) para manter a antiga como volta atras,\n"
             f"ou --atualizar para sincronizar esta mesma versao.")

    enviar = {k: p for k, p in locais.items()
              if a.tudo or remoto.get(k) != p.stat().st_size}
    iguais = len(locais) - len(enviar)

    print(f"Bucket : {bucket}\nDestino: s3://{bucket}/{prefixo}")
    print(f"Plano  : enviar {len(enviar)} arquivo(s), {iguais} ja igual(is) no S3\n")
    for k, p in enviar.items():
        print(f"  + {k:<55} {mb(p.stat().st_size):>10}")
    extras = sorted(set(remoto) - set(locais))
    for k in extras:
        print(f"  ! {k} existe no S3 mas nao localmente (nao sera apagado)")

    if a.dry_run or not enviar:
        print("\n(dry-run: nada enviado)" if a.dry_run else "\nNada a enviar. S3 ja esta sincronizado.")
    else:
        print()
        cfg = TransferConfig(multipart_threshold=64 * 1024 * 1024,
                             multipart_chunksize=64 * 1024 * 1024, max_concurrency=10)
        for k, p in enviar.items():
            tam = p.stat().st_size
            s3.upload_file(str(p), bucket, prefixo + k, Config=cfg, Callback=Progresso(k, tam))
            print()
        # confere os tamanhos no S3 depois do envio
        depois = listar_remoto(s3, bucket, prefixo)
        ruins = [k for k, p in enviar.items() if depois.get(k) != p.stat().st_size]
        if ruins:
            sair("Tamanho diferente no S3 apos o envio: " + ", ".join(ruins))
        print(f"\nOK: {len(enviar)} arquivo(s) enviado(s) e conferido(s).")

    print(f"\nARTEFATOS_S3=s3://{bucket}/{prefixo.rstrip('/')}")


if __name__ == "__main__":
    try:
        main()
    except NoCredentialsError:
        sair("Sem credenciais AWS. Confira com: aws sts get-caller-identity")
    except (BotoCoreError, ClientError) as e:
        sair(f"Falha na chamada a AWS: {e}")
