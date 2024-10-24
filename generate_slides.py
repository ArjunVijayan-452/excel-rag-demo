import os
import dotenv
import boto3
import json

import pandas as pd

from excel_agent import ExcelAgent
from prompts import *

# Load environment variables from the .env file
dotenv.load_dotenv("magicfill.env")

# Assign credentials with error handling for missing environment variables
AWS_KEY = os.getenv('aws_access_key_id')
AWS_SECRET_KEY = os.getenv("aws_secret_access_key")

if not AWS_KEY or not AWS_SECRET_KEY:
    raise ValueError("AWS credentials are missing. Please check environment variables.")

class GenerateSlides:
    """
    A class to generate slide content using AWS Bedrock and the Claude model.
    """

    def __init__(self):

        # Initialize the Bedrock client with retry and timeout settings
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1',
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
        )

        # Define the model ID and parameters for the Claude model
        self.model_id = "anthropic.claude-3-haiku-20240307-v1:0:48k"

        self.model_kwargs = {
            "max_tokens": 2048,
            "temperature": 0,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\n\nHuman"],
        }

    def get_prompts_title_and_desc(self, input_query):
        user_prompt = TITLE_AND_DESCRIPTION_USER.format(input_query)
        # user_prompt = SLIDE_USER_PROMPT.format(input_query, context)
        return TITLE_AND_DESCRIPTION_SYSTEM, user_prompt
        
    def generate_title_and_desc(self, input_query):

        system_prompt, prompt = self.get_prompts_title_and_desc(input_query)

        modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"

        # Define the inference configuration
        inference_config = {
            "temperature": 0.0,  # Set the temperature for generating diverse responses
            "maxTokens": 1000,  # Set the maximum number of tokens to generate
            "topP": 1,  # Set the top_p value for nucleus sampling
        }
        # Create the converse method parameters
        converse_api_params = {
            "modelId": modelId,  # Specify the model ID to use
            "messages": [{"role": "user", "content": [{"text": prompt}]}],  # Provide the user's prompt
            "inferenceConfig": inference_config,  # Pass the inference configuration
        }

        converse_api_params["system"] = [{"text": system_prompt}]

        # Send a request to the Bedrock client to generate a response
        try:
            response = self.bedrock_runtime.converse(**converse_api_params)

            # Extract the generated text content from the response
            text_content = response['output']['message']['content'][0]['text']

            # Return the generated text content
            return text_content

        except Exception as err:
            print(f"A client error occured: {err}")


    def get_prompts(self, input_query, context):
        user_prompt = DECK_USER_PROMPT1.format(input_query, context)
        # user_prompt = SLIDE_USER_PROMPT.format(input_query, context)
        return DECK_SYSTEM_PROMPT1, user_prompt
        
    def generate_slide_content(self, input_query, context):

        system_prompt, prompt = self.get_prompts(input_query, context)

        modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"

        # Define the inference configuration
        inference_config = {
            "temperature": 0.0,  # Set the temperature for generating diverse responses
            "maxTokens": 1000,  # Set the maximum number of tokens to generate
            "topP": 1,  # Set the top_p value for nucleus sampling
        }
        # Create the converse method parameters
        converse_api_params = {
            "modelId": modelId,  # Specify the model ID to use
            "messages": [{"role": "user", "content": [{"text": prompt}]}],  # Provide the user's prompt
            "inferenceConfig": inference_config,  # Pass the inference configuration
        }

        converse_api_params["system"] = [{"text": system_prompt}]

        # Send a request to the Bedrock client to generate a response
        try:
            response = self.bedrock_runtime.converse(**converse_api_params)

            # Extract the generated text content from the response
            text_content = json.loads(response['output']['message']['content'][0]['text'])

            # Return the generated text content
            return text_content

        except Exception as err:
            print(f"A client error occured: {err}")
