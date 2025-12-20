

## Hosting on Snowflake Streamlit

You can host this Streamlit app using Snowflake's Streamlit hosting options (often called "Streamlit for Snowflake" or Snowflake Apps). The exact steps depend on your Snowflake edition and configuration; below is a concise guide and recommended checklist to prepare this project for Snowflake hosting.

### Prerequisites

- A Snowflake account with the necessary admin privileges and the Streamlit hosting feature enabled for your organization.
- (Optional) Container registry access if you prefer to deploy a Docker image rather than uploading source.
- Ensure any external services used by the app (AWS Bedrock, Cognito) are reachable and credentials can be provided securely from Snowflake.

### Prepare the app

1. Confirm `docker_app/requirements.txt` contains `streamlit` and any Snowflake packages you need (for example: `snowflake-snowpark-python`, `snowflake-connector-python`) if you plan to interact with Snowflake from the app.
2. Make configuration/environment variables external to the code (for secrets and endpoints). Update `docker_app/config_file.py` to read from environment variables or a secrets store instead of hard-coded values.
3. (Optional) Build and test a Docker image locally using the provided `docker_app/Dockerfile`:

```bash
cd docker_app
docker build -t my-org/life-graph-llm:latest .
docker run --rm -p 8501:8501 -e STREAMLIT_SERVER_PORT=8501 my-org/life-graph-llm:latest
```

### Deploy to Snowflake

- Follow Snowflake's documentation for deploying a Streamlit app. Depending on your Snowflake configuration, you may either:
	- Upload source to Snowflake's Streamlit deployment UI or Git integration, or
	- Point Snowflake to a container image in a registry and deploy the container.
- Configure environment variables and secrets in Snowflake (for AWS credentials, Bedrock model names, Cognito or other auth secrets). Use Snowflake's secrets management or an approved external secrets store.
- Set up network connectivity, roles and permissions so the Streamlit app can access external services it needs (for example, any AWS endpoints the app calls).

### Testing & validation

- After deployment, test the app UI and the authentication flow (Cognito) thoroughly.
- Validate that any Snowflake-specific features (if you added Snowpark or connector usage) work under the Snowflake runtime and that credentials are restricted to the minimum required permissions.

### Notes & security

- Snowflake-hosted Streamlit environments may have network and runtime constraints compared to self-hosted or AWS deployments — review Snowflake docs and test thoroughly.
- Keep secrets out of source control. Use Snowflake's recommended secrets management mechanisms or environment variables set through the Snowflake UI.
- For exact, current Snowflake deployment steps see Snowflake's official documentation: https://docs.snowflake.com

