import os

import aws_cdk as cdk

from stacks.app_stack import AppStack
from stacks.artefatos_stack import ArtefatosStack

app = cdk.App()

# Usa a conta/regiao da credencial ativa (a mesma do `cdk bootstrap`).
env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION"),
)

# Parametros (cdk deploy DraftApp -c versao=v2 -c waf=block):
versao = app.node.try_get_context("versao") or "v1"   # pasta de modelos no S3
waf_modo = app.node.try_get_context("waf") or "count"  # count | block | off

# O nome "DraftArtefatos" e usado pelo subir_artefatos.py. Se mudar aqui, mude la.
artefatos = ArtefatosStack(app, "DraftArtefatos", env=env)
AppStack(app, "DraftApp", env=env, artefatos_bucket=artefatos.bucket, versao=versao, waf_modo=waf_modo)

cdk.Tags.of(app).add("projeto", "draft-lol")

app.synth()
