import asyncio
from app.gateway import OpenAICompatibleGateway
from app.prompts import PROMPT_VERSION, build_messages

LANGUAGE = "python"
SNIPPET = """
        def last_list(l):
            if not l:
                return None
            else:
                return l[-1]
    """

async def main() -> None:
    messages = build_messages(LANGUAGE, SNIPPET)
    print("=== USER MESSAGE ===")
    print(messages[-1]["content"])
    raw = await OpenAICompatibleGateway().complete(messages)
    print(f"\n=== RAW LLM OUTPUT (prompt {PROMPT_VERSION}) ===")
    # print(raw)
    
    try:
        import json
        parsed = json.loads(raw)
        print(f"\n=== PARSED LLM OUTPUT (prompt {PROMPT_VERSION}) ===")
        # print formatted json
        print(json.dumps(parsed, indent=4))
    except Exception as e:
        print(f"\n=== PARSED LLM OUTPUT (prompt {PROMPT_VERSION}) ===")
        print(f"Failed to parse LLM output as JSON: {e}")
    
asyncio.run(main())