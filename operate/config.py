import os
import sys

import google.generativeai as genai
from dotenv import load_dotenv
from ollama import Client
from openai import OpenAI
from huggingface_hub import InferenceClient
from loguru import logger
from prompt_toolkit.shortcuts import input_dialog
import time

class GeminiClient:
    def __init__(self):
        self.api_keys = [
            os.getenv("GEMINI_API_KEY_1"),  # Replace with actual keys
            os.getenv("GEMINI_API_KEY_2"),
            os.getenv("GEMINI_API_KEY_3")
        ]
        self.current_key_index = -1

    def initialize_client(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.success(self.api_keys)
        api_key = self.api_keys[self.current_key_index]
        # Configure the Google Generative AI with the current API key
        genai.configure(api_key=api_key)
        logger.debug(api_key)
        
        # Initialize your model or client here
        model = genai.GenerativeModel('gemini-2.0-flash')  # Adjust model name as needed
        return model


class Config:
    """
    Configuration class for managing settings.

    Attributes:
        verbose (bool): Flag indicating whether verbose mode is enabled.
        openai_api_key (str): API key for OpenAI.
        google_api_key (str): API key for Google.
        ollama_host (str): url to ollama running remotely.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            # Put any initialization here
        return cls._instance

    def __init__(self):
        load_dotenv()
        self.gemini_client = GeminiClient()
        self.verbose = False
        self.openai_api_key = (
            None  # instance variables are backups in case saving to a `.env` fails
        )
        self.google_api_key = (
            None  # instance variables are backups in case saving to a `.env` fails
        )
        self.ollama_host = (
            None  # instance variables are backups in case savint to a `.env` fails
        )
        self.hf_api_key = (
            None  # instance variables are backups in case savint to a `.env` fails
        )

    def initialize_openai(self):
        if self.verbose:
            print("[Config][initialize_openai]")

        if self.openai_api_key:
            if self.verbose:
                print("[Config][initialize_openai] using cached openai_api_key")
            api_key = self.openai_api_key
            logger.debug(f"OPENAI_API_KEY from cache : {api_key}")
        else:
            if self.verbose:
                print(
                    "[Config][initialize_openai] no cached openai_api_key, try to get from env."
                )
            api_key = os.getenv("OPENAI_API_KEY")
            logger.debug(f"OPENAI_API_KEY is : {api_key}")

        client = OpenAI(
            api_key=api_key,
        )
        
        client.api_key = api_key
        client.base_url = os.getenv("OPENAI_API_BASE_URL", client.base_url)
        logger.debug(f"OPENAI_BASE_URL is : {client.base_url}")
        return client

    def initialize_google(self):
        if self.google_api_key:
            logger.success(f"Gemini_API from cache : {self.google_api_key}")
            if self.verbose:
                print("[Config][initialize_google] using cached google_api_key")
            api_key = self.google_api_key
        else:
            if self.verbose:
                print(
                    "[Config][initialize_google] no cached google_api_key, try to get from env."
                ) 
            logger.debug("Model about to initiate")    
            model = self.gemini_client.initialize_client()

        return model

    def initialize_ollama(self):
        if self.ollama_host:
            if self.verbose:
                print("[Config][initialize_ollama] using cached ollama host")
        else:
            if self.verbose:
                print(
                    "[Config][initialize_ollama] no cached ollama host. Assuming ollama running locally."
                )
            self.ollama_host = os.getenv("OLLAMA_HOST", None)
        model = OpenAI(
                base_url = 'http://localhost:11434/v1',
            )
        return model
    
    def initialize_huggingface(self):
        if self.hf_api_key:
            if self.verbose:
                print("[Config][initialize_huggingface] using cached hf_api_key")
            api_key = self.hf_api_key
        else:
            if self.verbose:
                print(
                    "[Config][initialize_huggingface] no cached hf_api_key, try to get from env."
                )
            api_key = os.getenv("HF_API_KEY")
        model = OpenAI(base_url="https://api-inference.huggingface.co/v1/", api_key=api_key)
        return model

    def validation(self, model, voice_mode):
        """
        Validate the input parameters for the dialog operation.
        """
        return (
            self.require_api_key(
                "OPENAI_API_KEY",
                "OpenAI API key",
                model == "gpt-4"
                or voice_mode
                or model == "gpt-4-with-som"
                or model == "gpt-4-with-ocr"
                or model == "custom-gpt"
                or model == "fast-gpt",
            )
            or
            self.require_api_key(
                "GEMINI_API_KEY", 
                "Google API key", 
                model == "gemini-pro-vision"
                or model == "fast-gemini"
                or model == "custom-gemini"   
            )
        )

    def require_api_key(self, key_name, key_description, is_required):
        key_exists = bool(os.environ.get(key_name))
        return (is_required and not key_exists)
            # self.prompt_and_save_api_key(key_name, key_description)

    def save_api_key(self, model, key_value):
        if key_value is None:  # User pressed cancel or closed the dialog
            sys.exit("Operation cancelled by user.")

        if (model == "gpt-4"
            or model == "gpt-4-with-som"
            or model == "gpt-4-with-ocr"
            or model == "custom-gpt"
            or model == "fast-gpt"):
            key_name = "OPENAI_API_KEY"
        elif (model == "gemini-pro-vision"
              or model == "fast-gemini"
              or model == "custom-gemini"):
            key_name = "GEMINI_API_KEY"

        if key_value:
            if key_name == "OPENAI_API_KEY":
                self.openai_api_key = key_value
            elif key_name == "GEMINI_API_KEY":
                self.google_api_key = key_value
            self.save_api_key_to_env(key_name, key_value)
            load_dotenv()  # Reload environment variables
            # Update the instance attribute with the new key

    def prompt_and_save_api_key(self, key_name, key_description):
        key_value = input_dialog(
            title=f"Enter {key_description}",
            text=f"Please enter your {key_description} to continue:",
        ).run()

        if key_value is None:  # User pressed cancel or closed the dialog
            sys.exit("Operation cancelled by user.")

        if key_value:
            if key_name == "OPENAI_API_KEY":
                self.openai_api_key = key_value
            elif key_name == "GEMINI_API_KEY":
                self.google_api_key = key_value
            self.save_api_key_to_env(key_name, key_value)
            load_dotenv()  # Reload environment variables
            # Update the instance attribute with the new key

    @staticmethod
    def save_api_key_to_env(key_name, key_value):
        with open(".env", "a") as file:
            file.write(f"\n{key_name}='{key_value}'")