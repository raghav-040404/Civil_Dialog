import os
from typing import Any, Dict, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv

from backend.utils.json_parser import parse_json_safely

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

def get_prompt_template(filename: str) -> str:
    path = os.path.join(PROMPTS_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        self._client = None
        
        # Validate API key structure (simple check, not empty or default placeholder)
        if not self.api_key or self.api_key.strip() == "" or "your_api_key" in self.api_key:
            self.api_key = None

    @property
    def client(self) -> genai.Client:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set or is invalid in the environment.")
        if self._client is None:
            # Initialize official GenAI client
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate_json_response(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends a request to Gemini API and enforces a structured JSON response.
        """
        if not self.api_key:
            raise ValueError("Gemini API key is not configured.")

        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,  # Low temperature for highly deterministic/logical outputs
            )
            
            if system_instruction:
                config.system_instruction = system_instruction

            # We use models.generate_content API call
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            if not response.text:
                raise ValueError("Received empty response from Gemini API.")
                
            parsed_json = parse_json_safely(response.text)
            if parsed_json is None:
                raise ValueError(f"Failed to parse JSON response. Raw output: {response.text}")
                
            return parsed_json

        except APIError as e:
            # Handle rate limits, network timeouts, invalid keys
            raise RuntimeError(f"Gemini API failure: {str(e)}") from e
        except Exception as e:
            # Catch other unexpected exceptions
            raise RuntimeError(f"Unexpected error in LLM Service: {str(e)}") from e
