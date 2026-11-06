from typing import Protocol
import openai
from openai import AsyncOpenAI
from .config import settings
from .errors import LLMError

class LLMGateway(Protocol):
    model: str
    async def complete(self, messages: list[dict]) -> str: ...

class OpenAICompatibleGateway: # work with OpenAI, OpenRouter, LiteLLM and Ollama
    def __init__(self) -> None:
        self.model = settings.llm_model
        self._client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            timeout=settings.llm_timeout_s,
            max_retries=0
        )

    async def complete(self, messages: list[dict]) -> str:
        try:
            r = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,
                max_tokens=settings.llm_max_tokens,
                # response_format={"type": "json_object"}
            )

        except openai.APITimeoutError as e:
            raise LLMError("The LLM request timed out.", status_code=504) from e
        except (openai.APIConnectionError, openai.RateLimitError) as e:
            raise LLMError("The LLM service is unavailable. Try again later.", status_code=503) from e
        except openai.APIStatusError as e:
            raise LLMError("The LLM provider could not complete the request.", status_code=503) from e

        choice = r.choices[0]
        if choice.finish_reason == "length":
            raise LLMError("The LLM output was cut off. Try a smaller code sample.")
        if choice.message.refusal or choice.finish_reason == "content_filter":
            raise LLMError("The LLM declined the request.")
        if choice.finish_reason != "stop":
            raise LLMError("The LLM did not return a complete reply.")
        if not choice.message.content or not choice.message.content.strip():
            raise LLMError("The LLM returned empty output.")
        return choice.message.content

    async def close(self) -> None:
        await self._client.close()
