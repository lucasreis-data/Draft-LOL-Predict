from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_s3 as s3
from constructs import Construct


class ArtefatosStack(Stack):
    """Bucket com os artefatos da IA (CSVs + modelos .joblib + encoders).

    Fica numa stack SEPARADA e com RETAIN de proposito: o `cdk destroy` da stack da
    aplicacao nao apaga os modelos, entao religar o projeto nao exige subir tudo de novo.
    Guardar ~1 GB no S3 custa centavos por mes.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = s3.Bucket(
            self,
            "Artefatos",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                # Upload de arquivo grande interrompido deixa partes invisiveis que
                # continuam sendo cobradas. Isso limpa depois de 7 dias.
                s3.LifecycleRule(
                    id="limpar-uploads-incompletos",
                    abort_incomplete_multipart_upload_after=Duration.days(7),
                ),
            ],
        )

        # O script subir_artefatos.py le este output para descobrir o bucket.
        CfnOutput(self, "Bucket", value=self.bucket.bucket_name)
