from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_secretsmanager as secretsmanager,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_elasticloadbalancingv2 as elbv2,
    SecretValue,
    CfnOutput,
)
from constructs import Construct
from docker_app.config_file import Config

CUSTOM_HEADER_NAME = "X-Custom-Header"

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define prefix that will be used in some resource names
        prefix = Config.STACK_NAME

        # Create Cognito user pool
        user_pool = cognito.UserPool(self, f"{prefix}UserPool")

        # Create Cognito client
        user_pool_client = cognito.UserPoolClient(self, f"{prefix}UserPoolClient",
                                                  user_pool=user_pool,
                                                  generate_secret=True
                                                  )

        # Store Cognito parameters in a Secrets Manager secret
        secret = secretsmanager.Secret(self, f"{prefix}ParamCognitoSecret",
                                       secret_object_value={
                                           "pool_id": SecretValue.unsafe_plain_text(user_pool.user_pool_id),
                                           "app_client_id": SecretValue.unsafe_plain_text(user_pool_client.user_pool_client_id),
                                           "app_client_secret": user_pool_client.user_pool_client_secret
                                       },
                                       # This secret name should be identical
                                       # to the one defined in the Streamlit
                                       # container
                                       secret_name=Config.SECRETS_MANAGER_ID
                                       )

        # Lambda function definition
        lambda_function = _lambda.Function(
            self,
            f"{prefix}LambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="app.handler",
            code=_lambda.Code.from_asset("lambda_app"),
            environment={
                "COGNITO_POOL_ID": user_pool.user_pool_id,
                "COGNITO_CLIENT_ID": user_pool_client.user_pool_client_id,
                "COGNITO_CLIENT_SECRET": secret.secret_value_from_json("app_client_secret").to_string(),
            }
        )

        # Grant access to Bedrock
        bedrock_policy = iam.Policy(self, f"{prefix}BedrockPolicy",
                                    statements=[
                                        iam.PolicyStatement(
                                            actions=["bedrock:InvokeModel"],
                                            resources=["*"]
                                        )
                                    ]
                                    )
        lambda_function.role.attach_inline_policy(bedrock_policy)

        # Grant access to read the secret in Secrets Manager
        secret.grant_read(lambda_function)

        # ALB to connect to Lambda
        alb = elbv2.ApplicationLoadBalancer(
            self,
            f"{prefix}Alb",
            vpc=None,  # No VPC needed
            internet_facing=True,
            load_balancer_name=f"{prefix}-stl",
        )

        # Add ALB as CloudFront Origin
        origin = origins.LoadBalancerV2Origin(
            alb,
            custom_headers={CUSTOM_HEADER_NAME: Config.CUSTOM_HEADER_VALUE},
            origin_shield_enabled=False,
            protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
        )

        cloudfront_distribution = cloudfront.Distribution(
            self,
            f"{prefix}CfDist",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origin,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
            ),
        )

        # ALB Listener
        http_listener = alb.add_listener(
            f"{prefix}HttpListener",
            port=80,
            open=True,
        )

        http_listener.add_targets(
            f"{prefix}TargetGroup",
            target_group_name=f"{prefix}-tg",
            port=8501,
            priority=1,
            conditions=[
                elbv2.ListenerCondition.http_header(
                    CUSTOM_HEADER_NAME,
                    [Config.CUSTOM_HEADER_VALUE])],
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[elbv2_targets.LambdaTarget(lambda_function)],
        )
        # add a default action to the listener that will deny all requests that
        # do not have the custom header
        http_listener.add_action(
            "default-action",
            action=elbv2.ListenerAction.fixed_response(
                status_code=403,
                content_type="text/plain",
                message_body="Access denied",
            ),
        )

        # Output CloudFront URL
        CfnOutput(self, "CloudFrontDistributionURL",
                  value=cloudfront_distribution.domain_name)
        # Output Cognito pool id
        CfnOutput(self, "CognitoPoolId",
                  value=user_pool.user_pool_id)
