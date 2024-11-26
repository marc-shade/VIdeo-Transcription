import requests
import streamlit as st
from typing import Dict, Optional, Tuple, List

class PersonaAnalyzer:
    def __init__(self, model: str = "mistral:instruct", api_base: str = "http://localhost:11434", **kwargs):
        """Initialize the PersonaAnalyzer with Ollama configuration."""
        self.model = model
        self.api_base = api_base
        self.options = kwargs.get('options', {})

    @staticmethod
    def get_available_models(api_base: str = "http://localhost:11434") -> List[str]:
        """Get list of available models from Ollama."""
        try:
            response = requests.get(f"{api_base}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        except Exception as e:
            print(f"Error fetching models: {str(e)}")
            return ["mistral:instruct"]  # Fallback to default model

    def _generate_ollama_completion(self, system: str, user: str) -> str:
        """
        Generate completion using Ollama API with current settings.
        """
        try:
            response = requests.post(
                f"{self.api_base}/api/generate",
                json={
                    "model": self.model,
                    "system": system,
                    "prompt": user,
                    "stream": False,
                    "options": self.options
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Error generating completion: {str(e)}")
            return ""

    def analyze_transcript(self, transcript: str) -> Tuple[str, str]:
        """
        Analyze a transcript and generate a persona prompt that captures the speaking style,
        personality traits, and characteristics of the speaker.
        
        Args:
            transcript (str): The transcribed text to analyze
            
        Returns:
            Tuple[str, str]: (persona_name, system_prompt)
        """
        # System message to guide the analysis
        system_message = """You are an expert in analyzing speech patterns, communication styles, and personality traits.
        Given a transcript, create:
        1. A name for the speaker based on their characteristics (e.g., "Tech Enthusiast Sarah", "Professor James", etc.)
        2. A detailed system prompt that captures:
           - Speaking style and patterns
           - Vocabulary and language choices
           - Personality traits and characteristics
           - Expertise and knowledge areas
           - Common phrases and expressions
           - Tone and emotional patterns
        
        Format your response exactly as follows:
        NAME: [speaker name]
        PROMPT: [detailed system prompt]"""

        # User message template
        user_message = f"""Analyze this transcript and create a persona:

        {transcript}

        Remember to format your response with NAME: and PROMPT: sections."""

        try:
            # Get the generated analysis from Ollama
            response = self._generate_ollama_completion(system_message, user_message)
            
            # Parse the response to extract name and prompt
            try:
                name_part = response.split("NAME:")[1].split("PROMPT:")[0].strip()
                prompt_part = response.split("PROMPT:")[1].strip()
            except:
                # Fallback if parsing fails
                name_part = "AI Assistant"
                prompt_part = response

            return name_part, prompt_part

        except Exception as e:
            print(f"Error analyzing transcript: {str(e)}")
            return "AI Assistant", "You are a helpful AI assistant."

    def generate_response(self, system_prompt: str, user_input: str) -> str:
        """
        Generate a response using the persona prompt and user input.
        
        Args:
            system_prompt (str): The system prompt that defines the AI's personality
            user_input (str): The user's input/question
            
        Returns:
            str: The generated response in the style of the persona
        """
        try:
            return self._generate_ollama_completion(system_prompt, user_input)
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now."
