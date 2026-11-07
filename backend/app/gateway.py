from typing import Protocol
import openai
from openai import AsyncOpenAI
from .config import settings
from .errors import LLMOutputError

class LLMGateway(Protocol):
    model: str
    async def complete(self, messages: list[dict]) -> str: ...
    async def close(self) -> None: ...

class OpenAICompatibleGateway:
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
                response_format={"type": "json_object"} if settings.llm_json_mode else None,
            )

        except Exception as e:
            raise LLMOutputError("The LLM provider could not complete the request.") from e

        choice = r.choices[0]
        if choice.finish_reason == "length":
            raise LLMOutputError("The LLM output was cut off. Try a smaller code sample.")
        return choice.message.content

    async def close(self) -> None:
        await self._client.close()
