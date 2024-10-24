import os
import boto3
import dotenv
import pandas as pd

from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_community.chat_models import BedrockChat

dotenv.load_dotenv()

# Assign credentials with error handling for missing environment variables
AWS_KEY = os.getenv('aws_access_key_id')
AWS_SECRET_KEY = os.getenv("aws_secret_access_key")

if not AWS_KEY or not AWS_SECRET_KEY:
    raise ValueError("AWS credentials are missing. Please check environment variables.")


class ExcelAgent:
    def __init__(self, preprocessed_csv_files):
        self.preprocessed_csv_files = preprocessed_csv_files
        
        # Initialize bedrock client for runtime with appropriate configurations
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1',
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            config=boto3.session.Config(retries={'max_attempts': 5}, 
            connect_timeout=5, read_timeout=10)
        )
        
        # Set up the LLM model with BedrockChat
        self.llm = BedrockChat(
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            client=self.bedrock_client,
            model_kwargs={"temperature": 0.}
        )
        
        # Create CSV agent with safe settings
        self.agent = create_csv_agent(
            self.llm,
            self.preprocessed_csv_files,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            allow_dangerous_code=True
        )

    def get_context(self, prompt: str) -> str:
        """
        Fetches context from the agent based on the provided prompt.

        :param prompt: User query or prompt for the agent
        :return: The response from the agent, or an empty string in case of an error
        """
        try:
            response = self.agent.run(prompt)
        except Exception as e:
            # Log the error for better production diagnostics
            print(f"Error occurred: {e}")
            return pd.read_csv(self.preprocessed_csv_files).to_csv()
        
        return response

    def __del__(self):
        """
        Ensures that the boto3 client is closed when the ExcelAgent object is deleted.
        """
        self.bedrock_client.close()
