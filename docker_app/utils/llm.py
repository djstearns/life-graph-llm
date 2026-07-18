import boto3
import json
import requests
from os import getenv


class Llm:

    # def __init__(self, bedrock_region):
    #     # Create Bedrock client
    #     bedrock_client = boto3.client(
    #         'bedrock-runtime',
    #         region_name=bedrock_region,
    #     )
    #     self.bedrock_client = bedrock_client

    def __init__(self, bedrock_region, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None, openai_api_key=None):
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
        
        # Store OpenAI API key for use in invoke_openai method
        self.openai_api_key = openai_api_key or getenv('OPENAI_API_KEY')


    def invoke(self, input_text):
        """
        Make a call to the foundation model through Bedrock using the messages API
        """

        # Prepare a messages-formatted body instead of a single prompt string
        messages = [
            {"role": "user", "content": [{"type": "text", "text": input_text}]}
        ]
        #Too Old
        #OLD "arn:aws:bedrock:us-east-1:414676341887:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        # opus 4.8 not available
        # "arn:aws:bedrock:us-east-1:414676341887:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"
        # "arn:aws:bedrock:us-east-1:414676341887:application-inference-profile/6bh1s4njpoz7" #claude sonnet 4.6 (applicaiton profile doesnt have permissions)
        model_id = "arn:aws:bedrock:us-east-1:414676341887:inference-profile/us.anthropic.claude-sonnet-4-6"  # Use the correct model ID for Claude Opus 4.8
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

    def invoke_openai(self, input_text):
        """
        Make a call to OpenAI's API using the provided API key.
        This method invokes the ChatCompletions endpoint.
        """
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not provided during initialization")
        
        api_endpoint = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": input_text}
            ],
            "max_tokens": 4096,
            "temperature": 0.0,
        }
        
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()  # Raise exception for non-2xx status codes
        
        return response
