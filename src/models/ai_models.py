# Copyright (c) 2025 Sisodia Bhumca, Inc.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Factory and base class for AI models.
Handles different AI providers and their configurations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import openai
import anthropic
import google.generativeai as genai
import cohere
from transformers import pipeline
from azure.ai.ml import MLClient
import boto3
import json

class AIModel(ABC):
    """Base class for AI models"""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text based on prompt"""
        pass

class OpenAIModel(AIModel):
    """OpenAI model implementation"""
    
    def __init__(self, config: Dict):
        openai.api_key = config['api_key']
        self.model = config['model']
        
    def generate(self, prompt: str) -> str:
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional meeting assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

class AnthropicModel(AIModel):
    """Anthropic model implementation"""
    
    def __init__(self, config: Dict):
        self.client = anthropic.Anthropic(api_key=config['api_key'])
        self.model = config['model']
        
    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content.text

class HuggingFaceModel(AIModel):
    """HuggingFace model implementation"""
    
    def __init__(self, config: Dict):
        self.pipeline = pipeline(
            "text-generation",
            model=config['model'],
            use_auth_token=config['api_key']
        )
        
    def generate(self, prompt: str) -> str:
        response = self.pipeline(
            prompt,
            max_new_tokens=config['max_tokens'],
            temperature=config['temperature'],
            top_p=config['top_p'],
            top_k=config['top_k'],
            do_sample=config['do_sample']
        )
        return response[0]['generated_text']

class AIModelFactory:
    """Factory for creating AI models"""
    
    @staticmethod
    def get_model(model_type: str) -> AIModel:
        """Create an AI model instance based on type"""
        model_type = model_type.lower()
        config = Config().model_config
        
        if model_type == 'openai':
            return OpenAIModel(config)
        elif model_type == 'anthropic':
            return AnthropicModel(config)
        elif model_type == 'huggingface':
            return HuggingFaceModel(config)
        else:
            raise ValueError(f"Unsupported AI model type: {model_type}")
