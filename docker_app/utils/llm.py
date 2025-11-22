import boto3
import json


class Llm:

    # def __init__(self, bedrock_region):
    #     # Create Bedrock client
    #     bedrock_client = boto3.client(
    #         'bedrock-runtime',
    #         region_name=bedrock_region,
    #     )
    #     self.bedrock_client = bedrock_client

    def __init__(self, bedrock_region, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None):
        # Create Bedrock client, optionally supplying explicit credentials including a session token
        client_args = {
            'service_name': 'bedrock-runtime',
            'region_name': bedrock_region,
        }
        if aws_access_key_id and aws_secret_access_key:
            # include provided credentials (aws_session_token is optional but used when present)
            client_args.update({
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key,
            })
            if aws_session_token:
                client_args['aws_session_token'] = aws_session_token

        # instantiate client with possible security token
        # note: boto3.client signature expects the service name first; using dict unpack below
        self.bedrock_client = boto3.client('bedrock-runtime',
                                           region_name=client_args.get('region_name'),
                                           aws_access_key_id=client_args.get('aws_access_key_id'),
                                           aws_secret_access_key=client_args.get('aws_secret_access_key'),
                                           aws_session_token=client_args.get('aws_session_token'))


    def invoke(self, input_text):
        """
        Make a call to the foundation model through Bedrock using the messages API
        """

        # Prepare a messages-formatted body instead of a single prompt string
        messages = [
            {"role": "user", "content": [{"type": "text", "text": input_text}]}
        ]

        model_id = "arn:aws:bedrock:us-east-1:414676341887:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        body = {
            "messages": messages,
            "anthropic_version": "bedrock-2023-05-31",
            "system": "",
            "max_tokens": 4096,
            "temperature": 0.0,
        }
        body = json.dumps(body)
        accept = 'application/json'
        contentType = 'application/json'

        # Make the API call to Bedrock using the messages payload
        response = self.bedrock_client.invoke_model(
            body=body, modelId=model_id, accept=accept, contentType=contentType
        )

        return response
