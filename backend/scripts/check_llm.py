import asyncio
from openai import AsyncOpenAI
from app.config import settings

async def main() -> None:
    client = AsyncOpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)
    r = await client.chat.completions.create(
        model=settings.llm_model,
        temperature=0,
        messages=[{"role": "user", "content": "Reply with exactly one word: pong"}],
    )
    print("base_url:", settings.llm_base_url)
    print("model:   ", settings.llm_model)
    print("reply:   ", r.choices[0].message.content)

asyncio.run(main())