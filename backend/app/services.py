from pydantic import ValidationError
from .errors import LLMOutputError
from .gateway import LLMGateway
from .prompts import build_messages
from .schemas import Issue, LLMReview

MAX_RETRY_ATTEMPTS = 3

def sanitize(issues: list[Issue], n_lines: int) -> list[Issue]:
    for issue in issues:
        issue.line_start = min(max(issue.line_start, 1), n_lines)
        issue.line_end = min(max(issue.line_end, issue.line_start), n_lines)
    return sorted(issues, key=lambda i: i.line_start)

async def review(gateway: LLMGateway, language: str, code: str) -> list[Issue]:
    messages = build_messages(language, code)
    n_lines = len(code.splitlines())

    for _ in range(MAX_RETRY_ATTEMPTS):
        raw = await gateway.complete(messages)
        try:
            parsed = LLMReview.model_validate_json(raw)
        except ValidationError:
            continue  # retry
        return sanitize(parsed.issues, n_lines)

    raise LLMOutputError(f"invalid output after {MAX_RETRY_ATTEMPTS} attempts")