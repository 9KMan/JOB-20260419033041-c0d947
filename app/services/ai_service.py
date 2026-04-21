from flask import request, jsonify
import os
import openai


class AIService:
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('AI_API_KEY', '')
        self.model = os.environ.get('AI_MODEL', 'gpt-4-turbo-preview')
        self.temperature = float(os.environ.get('AI_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.environ.get('AI_MAX_TOKENS', '2000'))
        self.client = None
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)

    def chat(self, messages, model=None, temperature=None, max_tokens=None):
        if not self.client:
            raise Exception("AI service not configured. Please set OPENAI_API_KEY.")

        model = model or self.model
        temperature = temperature or self.temperature
        max_tokens = max_tokens or self.max_tokens

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        content = response.choices[0].message.content
        usage = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }

        return content, usage

    def complete(self, prompt, model=None, temperature=None, max_tokens=None, system_prompt=None):
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        return self.chat(messages, model, temperature, max_tokens)

    def list_available_models(self):
        if not self.client:
            return ['gpt-4-turbo-preview', 'gpt-3.5-turbo']

        try:
            models = self.client.models.list()
            return [m.id for m in models.data if 'gpt' in m.id.lower()]
        except Exception:
            return ['gpt-4-turbo-preview', 'gpt-3.5-turbo']

    def count_tokens(self, text):
        if not self.client:
            return len(text) // 4

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': text}],
                max_tokens=1
            )
            return response.usage.total_tokens
        except Exception:
            return len(text) // 4