from importlib import import_module
from .config import settings

PROMPT_VERSION = settings.llm_prompt_version
SYSTEM = import_module(f"app.prompt_versions.{PROMPT_VERSION}").SYSTEM

def add_lines(code: str) -> str:
    lines = code.splitlines()
    return '\n'.join(f"{i+1}| {line}" for i, line in enumerate(lines))

def build_user_prompt(language: str, code: str) -> str:
    code_with_lines = add_lines(code)
    return f'Please review the following {language} code:\n\n{code_with_lines}'

def build_messages(language: str, code: str) -> list[dict]:
    system_message = {"role": "system", "content": SYSTEM.replace("{language}", language)}
    user_prompt = build_user_prompt(language, code)
    user_message = {"role": "user", "content": user_prompt}
    return [system_message, user_message]