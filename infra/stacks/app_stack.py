import os

from aws_cdk import (
    Annotations,
    Aws,
    CfnOutput,
    Duration,
    Fn,
    RemovalPolicy,
    Stack,
    Token,
)
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3deploy
from aws_cdk import aws_wafv2 as wafv2
from constructs import Construct

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ---------------------------------------------------------------------------
# Dimensionamento e TETO DE GASTO. Mexa aqui.
# Modelos ORIGINAIS: ~1,2 GB de RAM por liga carregada (7 ligas ~ 8,4 GB) + dados ~ 1,4 GB => ~10 GB
# por processo. Por isso 1 worker por tarefa de 2 vCPU / 16 GB (a 2a vCPU fica folgada).
# Cada tarefa de Python custa ~US$ 111/mes On-Demand ou ~US$ 33/mes em Spot (us-east-1).
# PY_MAX_TAREFAS e o teto do autoscaling: nem um ataque de bots passa disso.
# Lembre: a quota de vCPUs do Fargate da conta precisa comportar PY_MAX_TAREFAS * 2 + 0,5.
# ---------------------------------------------------------------------------
PY_CPU, PY_MEM = 2048, 16384
PY_WORKERS = "1"            # cada worker carrega TODAS as ligas na RAM (~10 GB): 2 workers nao cabem em 16 GB
PY_MIN_TAREFAS = 2          # 2 tarefas fixas (uma em cada zona)
PY_MAX_TAREFAS = 10         # 10 x 2 vCPU = 20 vCPU (+0,5 do Java): peca quota de ~32 vCPU Fargate
PY_FIXAS_ON_DEMAND = 0      # quantas das tarefas fixas ficam On-Demand (0 = todas em Spot; 1 = ~US$ +78/mes)
JAVA_CPU, JAVA_MEM = 512, 2048   # opcao B: 1 unica copia do Java (sessoes em memoria)

# Limites do WAF por IP em janela de 5 minutos. Comece em modo "count" e ajuste olhando
# as metricas no CloudWatch antes de passar para "block" (IP compartilhado: faculdade, CGNAT).
LIMITE_GERAL = 1000
LIMITE_ROTAS_CARAS = 100    # /draft/Sugestao e /draft/Picks-Bans (chamam o Python)
LIMITE_START = 20           # /draft/Start (cria sessao)

# ECS Exec = shell no container via IAM (util para depurar). DESLIGUE (False) depois dos testes.
ECS_EXEC_LIGADO = True

HEADER_ORIGEM = "X-Origin-Verify"


class AppStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        artefatos_bucket: s3.IBucket,
        versao: str,
        waf_modo: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        if waf_modo not in ("count", "block", "off"):
            raise ValueError("waf deve ser count, block ou off (use: cdk deploy -c waf=block)")
        if (
            waf_modo != "off"
            and not Token.is_unresolved(self.region)
            and self.region != "us-east-1"
        ):
            raise ValueError(
                "O WAF do CloudFront so pode ser criado em us-east-1 e a regiao atual e "
                f"{self.region}. Use us-east-1, ou desligue o WAF com: cdk deploy -c waf=off"
            )

        # ------------------------------------------------------------------ rede
        # Sem NAT Gateway (custo fixo): tarefas em subnet publica com IP publico, e os
        # security groups bloqueiam toda entrada que nao seja a permitida abaixo.
        vpc = ec2.Vpc(
            self,
            "Vpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="publica", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
                )
            ],
        )
        subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)

        alb_sg = ec2.SecurityGroup(self, "AlbSg", vpc=vpc, description="ALB (so CloudFront)")
        java_sg = ec2.SecurityGroup(self, "JavaSg", vpc=vpc, description="Java (so o ALB)")
        py_sg = ec2.SecurityGroup(self, "PythonSg", vpc=vpc, description="Python (so o Java)")

        # O ALB aceita HTTP, mas so ENCAMINHA quem traz o header secreto do CloudFront.
        alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "HTTP; filtrado por header")
        # Python: UNICA entrada permitida e o security group do Java, porta 5000.
        py_sg.add_ingress_rule(java_sg, ec2.Port.tcp(5000), "somente o Java")

        # ----------------------------------------------------------------- cluster
        cluster = ecs.Cluster(
            self,
            "Cluster",
            vpc=vpc,
            enable_fargate_capacity_providers=True,  # Adicione esta linha
            default_cloud_map_namespace=ecs.CloudMapNamespaceOptions(
                name="draft.local", use_for_service_connect=True
            ),
        )

        def logs_de(nome: str) -> ecs.LogDriver:
            grupo = logs.LogGroup(
                self,
                f"Logs{nome}",
                retention=logs.RetentionDays.ONE_WEEK,  # logs sem fim = custo sem fim
                removal_policy=RemovalPolicy.DESTROY,
            )
            return ecs.LogDrivers.aws_logs(stream_prefix=nome.lower(), log_group=grupo)

        x86 = ecs.RuntimePlatform(
            cpu_architecture=ecs.CpuArchitecture.X86_64,
            operating_system_family=ecs.OperatingSystemFamily.LINUX,
        )

        # ------------------------------------------------------------------ Python
        py_task = ecs.FargateTaskDefinition(
            self, "PythonTask", cpu=PY_CPU, memory_limit_mib=PY_MEM, runtime_platform=x86
        )
        py_container = py_task.add_container(
            "python",
            # AMD64 explicito: sem isso, quem builda num Mac M1/M2 sobe imagem ARM e a tarefa nao inicia.
            image=ecs.ContainerImage.from_asset(
                os.path.join(RAIZ, "python"), platform=ecr_assets.Platform.LINUX_AMD64
            ),
            logging=logs_de("Python"),
            environment={
                "ARTEFATOS_S3": f"s3://{artefatos_bucket.bucket_name}/artefatos/{versao}",
                "WEB_CONCURRENCY": PY_WORKERS,
                "AWS_DEFAULT_REGION": self.region,
            },
            health_check=ecs.HealthCheck(
                command=[
                    "CMD-SHELL",
                    "python -c \"import urllib.request;"
                    "urllib.request.urlopen('http://localhost:5000/',timeout=4)\" || exit 1",
                ],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                retries=3,
                # download do S3 + import do cblol.py (~25 s) + preload de 7 modelos + folga
                start_period=Duration.seconds(600),
            ),
        )
        py_container.add_port_mappings(
            ecs.PortMapping(container_port=5000, name="api", app_protocol=ecs.AppProtocol.http)
        )
        artefatos_bucket.grant_read(py_task.task_role)

        estrategia_py = [ecs.CapacityProviderStrategy(capacity_provider="FARGATE_SPOT", weight=1)]
        if PY_FIXAS_ON_DEMAND > 0:
            estrategia_py.insert(
                0,
                ecs.CapacityProviderStrategy(
                    capacity_provider="FARGATE", base=PY_FIXAS_ON_DEMAND, weight=0
                ),
            )

        py_service = ecs.FargateService(
            self,
            "PythonService",
            cluster=cluster,
            task_definition=py_task,
            desired_count=PY_MIN_TAREFAS,
            assign_public_ip=True,
            vpc_subnets=subnets,
            security_groups=[py_sg],
            # Spot (~70% mais barato). PY_FIXAS_ON_DEMAND tarefas ficam On-Demand como base.
            capacity_provider_strategies=estrategia_py,
            # Nome interno: o Java chama http://python-api:5000 (nao ha balanceador do Python).
            service_connect_configuration=ecs.ServiceConnectProps(
                services=[
                    ecs.ServiceConnectService(
                        port_mapping_name="api", dns_name="python-api", port=5000
                    )
                ],
                log_driver=logs_de("PythonProxy"),
            ),
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
            enable_execute_command=ECS_EXEC_LIGADO,  # entrar no container sem abrir porta/SSH
            min_healthy_percent=100,
            max_healthy_percent=200,
        )
        
        py_service.node.add_dependency(cluster)  # Adicione esta linha

        escala = py_service.auto_scale_task_count(
            min_capacity=PY_MIN_TAREFAS, max_capacity=PY_MAX_TAREFAS
        )
        escala.scale_on_cpu_utilization(
            "Cpu",
            target_utilization_percent=55,
            scale_out_cooldown=Duration.minutes(1),
            scale_in_cooldown=Duration.minutes(5),
        )

        # -------------------------------------------------------------------- Java
        java_task = ecs.FargateTaskDefinition(
            self, "JavaTask", cpu=JAVA_CPU, memory_limit_mib=JAVA_MEM, runtime_platform=x86
        )
        java_container = java_task.add_container(
            "java",
            image=ecs.ContainerImage.from_asset(
                os.path.join(RAIZ, "draft-lol"), platform=ecr_assets.Platform.LINUX_AMD64
            ),
            logging=logs_de("Java"),
            environment={
                "PYTHON_API_URL": "http://python-api:5000",
                # Swagger fora do ar em producao (nao expor o contrato da API).
                "SPRINGDOC_SWAGGER_UI_ENABLED": "false",
                "SPRINGDOC_API_DOCS_ENABLED": "false",
            },
        )
        java_container.add_port_mappings(ecs.PortMapping(container_port=8080, name="http"))

        java_service = ecs.FargateService(
            self,
            "JavaService",
            cluster=cluster,
            task_definition=java_task,
            desired_count=1,  # opcao B: sessoes em memoria => UMA copia, sem autoscaling
            assign_public_ip=True,
            vpc_subnets=subnets,
            security_groups=[java_sg],
            # Sempre On-Demand: uma interrupcao Spot apagaria todas as sessoes.
            capacity_provider_strategies=[
                ecs.CapacityProviderStrategy(capacity_provider="FARGATE", weight=1)
            ],
            service_connect_configuration=ecs.ServiceConnectProps(  # so cliente
                log_driver=logs_de("JavaProxy"),
            ),
            health_check_grace_period=Duration.seconds(180),
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
            enable_execute_command=ECS_EXEC_LIGADO,
            min_healthy_percent=100,
            max_healthy_percent=200,
        )
        # O Java le a lista de campeoes/times do Python ao subir. Na primeira criacao, o
        # CloudFormation so cria o Java depois que o Python estiver estavel (saudavel).
        java_service.node.add_dependency(py_service)
        java_service.node.add_dependency(cluster)

        # --------------------------------------------------------------------- ALB
        # Token que so o CloudFront conhece (id unico da stack). Sem ele, o ALB responde 403.
        token = Fn.select(2, Fn.split("/", Aws.STACK_ID))

        alb = elbv2.ApplicationLoadBalancer(
            self,
            "Alb",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_sg,
            vpc_subnets=subnets,
        )
        listener = alb.add_listener(
            "Http",
            port=80,
            open=False,
            default_action=elbv2.ListenerAction.fixed_response(
                403, content_type="text/plain", message_body="Forbidden"
            ),
        )
        listener.add_targets(
            "Java",
            port=8080,
            priority=10,
            conditions=[elbv2.ListenerCondition.http_header(HEADER_ORIGEM, [token])],
            targets=[java_service],
            deregistration_delay=Duration.seconds(30),
            health_check=elbv2.HealthCheck(
                path="/Testar",
                interval=Duration.seconds(30),
                healthy_threshold_count=2,
                unhealthy_threshold_count=3,
                healthy_http_codes="200",
            ),
        )

        # --------------------------------------------------------------------- WAF
        web_acl = None
        if waf_modo != "off":
            web_acl = self._waf(waf_modo)

        # ------------------------------------------------------- front + CloudFront
        site_bucket = s3.Bucket(
            self,
            "Site",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        api_origin = origins.HttpOrigin(
            alb.load_balancer_dns_name,
            protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
            custom_headers={HEADER_ORIGEM: token},
            read_timeout=Duration.seconds(30),
        )

        distribution = cloudfront.Distribution(
            self,
            "Cdn",
            comment="Draft LoL: front (S3) + /draft/* (ALB)",
            default_root_object="index.html",
            web_acl_id=web_acl.attr_arn if web_acl else None,
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(site_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                compress=True,
            ),
            additional_behaviors={
                # O front so chama /draft/* (BASE_URL relativo): mesma origem, sem CORS.
                "/draft/*": cloudfront.BehaviorOptions(
                    origin=api_origin,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
                )
            },
        )

        dist_dir = os.path.join(RAIZ, "frontend", "dist")
        if os.path.isdir(dist_dir):
            s3deploy.BucketDeployment(
                self,
                "DeployFront",
                sources=[s3deploy.Source.asset(dist_dir)],
                destination_bucket=site_bucket,
                distribution=distribution,
                distribution_paths=["/*"],
            )
        else:
            Annotations.of(self).add_warning(
                "frontend/dist nao existe: o site fica vazio. "
                "Rode `npm ci && npm run build` em frontend/ e faca o deploy de novo."
            )

        # ------------------------------------------------------------------ saidas
        CfnOutput(self, "OutSiteUrl", value=f"https://{distribution.distribution_domain_name}")
        CfnOutput(self, "OutAlbDns", value=alb.load_balancer_dns_name)
        CfnOutput(self, "OutCluster", value=cluster.cluster_name)
        CfnOutput(self, "OutPythonService", value=py_service.service_name)
        CfnOutput(self, "OutJavaService", value=java_service.service_name)
        CfnOutput(self, "OutWafModo", value=waf_modo)

    # ---------------------------------------------------------------------- WAF
    def _waf(self, modo: str) -> wafv2.CfnWebACL:
        """Rate limit por IP (janela de 5 min). modo=count so conta; modo=block bloqueia."""
        W = wafv2.CfnWebACL

        def visibilidade(nome: str):
            return W.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name=nome,
                sampled_requests_enabled=True,
            )

        acao = (
            W.RuleActionProperty(block=W.BlockActionProperty())
            if modo == "block"
            else W.RuleActionProperty(count=W.CountActionProperty())
        )

        def comeca_com(caminho: str):
            return W.StatementProperty(
                byte_match_statement=W.ByteMatchStatementProperty(
                    search_string=caminho,  # minusculo: o texto e normalizado abaixo
                    field_to_match=W.FieldToMatchProperty(uri_path={}),
                    text_transformations=[W.TextTransformationProperty(priority=0, type="LOWERCASE")],
                    positional_constraint="STARTS_WITH",
                )
            )

        def regra(nome: str, prioridade: int, limite: int, escopo=None):
            return W.RuleProperty(
                name=nome,
                priority=prioridade,
                action=acao,
                visibility_config=visibilidade(nome),
                statement=W.StatementProperty(
                    rate_based_statement=W.RateBasedStatementProperty(
                        limit=limite,
                        aggregate_key_type="IP",
                        evaluation_window_sec=300,
                        scope_down_statement=escopo,
                    )
                ),
            )

        rotas_caras = W.StatementProperty(
            or_statement=W.OrStatementProperty(
                statements=[comeca_com("/draft/sugestao"), comeca_com("/draft/picks-bans")]
            )
        )

        return wafv2.CfnWebACL(
            self,
            "Waf",
            scope="CLOUDFRONT",
            default_action=W.DefaultActionProperty(allow={}),
            visibility_config=visibilidade("DraftWaf"),
            rules=[
                regra("LimiteStart", 0, LIMITE_START, comeca_com("/draft/start")),
                regra("LimiteRotasCaras", 1, LIMITE_ROTAS_CARAS, rotas_caras),
                regra("LimiteGeral", 2, LIMITE_GERAL),
            ],
        )
