import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

import httpx
from app.core.config import Settings
from app.prompts.dj_persona import DJ_SYSTEM_PROMPT
from app.utils.exceptions import LLMGenerationError
from google import genai

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate text from the LLM provider.

        Raises:
            LLMGenerationError: If generation fails.
        """
        pass


class OpenAIClient(LLMClient):
    """Client for OpenAI Chat Completion API."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.openai.com/v1/chat/completions"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 150,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.url, headers=headers, json=data, timeout=10.0
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                # logger.error is handled inside Exception init but we can pass provider
                raise LLMGenerationError(str(e), provider="OpenAI") from e


class OllamaClient(LLMClient):
    """Client for local Ollama instance."""

    def __init__(self, base_url: str, model: str = "llama2"):
        self.base_url = base_url
        self.model = model

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Ollama often works best with a combined prompt if strictly using the /api/generate endpoint.
        full_prompt = f"System: {system_prompt}\nUser: {user_prompt}\nAssistant:"

        url = f"{self.base_url}/api/generate"
        data = {"model": self.model, "prompt": full_prompt, "stream": False}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=data, timeout=5.0)
                response.raise_for_status()
                return response.json().get("response", "").strip()
            except Exception as e:
                raise LLMGenerationError(str(e), provider="Ollama") from e


class GeminiClient(LLMClient):
    """Client for Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        full_text = f"{system_prompt}\n\n{user_prompt}"

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model, contents=full_text
            )
            return response.text.strip()
        except Exception as e:
            raise LLMGenerationError(str(e), provider="Gemini") from e


def get_llm_client() -> LLMClient:
    """Factory to return the configured LLM client."""
    settings = Settings.get_settings()

    if settings.gemini_api_key:
        return GeminiClient(
            api_key=settings.gemini_api_key, model=settings.gemini_model
        )

    if settings.openai_api_key:
        return OpenAIClient(
            api_key=settings.openai_api_key, model=settings.openai_model
        )

    return OllamaClient(
        base_url=settings.ollama_url,
        model=settings.ollama_model,
    )


async def generate_dj_script(context: Dict[str, Any]) -> str:
    """
    Generate a DJ script using the configured LLM provider.

    Args:
        context: A dictionary containing track and user info for the prompt.

    Returns:
        str: The generated text script.
    """
    client = get_llm_client()
    user_prompt = DJ_SYSTEM_PROMPT.format(**context)
    system_instruction = "You are DJ HAL. Short, punchy, charismatic intros only."

    try:
        return await client.generate(
            system_prompt=system_instruction, user_prompt=user_prompt
        )
    except Exception:
        # Fallback if the provider fails
        logger.warning("LLM generation failed, using fallback.")
        return "Hey everyone, keep the vibe going! Coming up next is a great track."
