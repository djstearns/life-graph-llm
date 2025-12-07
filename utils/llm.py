import boto3
import json
import requests

class Llm:
    def __init__(self, openai_api_key=None, bedrock_region=None, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None):
        # Create Bedrock client, optionally supplying explicit credentials including a session token
        if bedrock_region:
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
            print('test')
            # instantiate client with possible security token
            # note: boto3.client signature expects the service name first; using dict unpack below
            self.bedrock_client = boto3.client('bedrock-runtime',
                                            region_name=client_args.get('region_name'),
                                            aws_access_key_id=client_args.get('aws_access_key_id'),
                                            aws_secret_access_key=client_args.get('aws_secret_access_key'),
                                            aws_session_token=client_args.get('aws_session_token'))

        else:
            self.bedrock_client = None
            # OpenAI API key setup
            self.openai_api_key = openai_api_key

    def invoke(self, input_text):
        """
        Make a call to the foundation model through Bedrock
        """
        if not self.bedrock_client:
            raise ValueError("Bedrock client not initialized.")
        prompt = f"\n\nHuman: {input_text}\n\nAssistant:"
        model_id = "anthropic.claude-v2:1"
        body = {
            "prompt": prompt,
            "max_tokens_to_sample": 4096,
            "temperature": 0.,
        }
        body = json.dumps(body)
        accept = 'application/json'
        contentType = 'application/json'
        response = self.bedrock_client.invoke_model(
            body=body, modelId=model_id, accept=accept, contentType=contentType
        )
        return response

    def invoke_openai(self, input_text, model="gpt-3.5-turbo"):
        """
        Make a call to OpenAI API using the provided API key
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not provided.")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": input_text}
            ],
            "max_tokens": 4096,
            "temperature": 0.0
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"OpenAI API error: {response.status_code} {response.text}")
