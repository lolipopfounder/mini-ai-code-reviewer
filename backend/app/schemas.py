from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, field_validator

MAX_CODE_CHARS = 20000

class Language(str, Enum):
    python = "python"
    javascript = "javascript"
    typescript = "typescript"

class LintRequest(BaseModel):
    language: Language
    code: str = Field(min_length=1, max_length=MAX_CODE_CHARS)
    
class Issue(BaseModel):
    line_start: int = Field(ge=1, description="The starting line number of the issue, must be >= 1")
    line_end: int = Field(ge=1, description="The ending line number of the issue, must be >= 1")
    severity: Literal["high", "medium", "low"] = Field(description="The severity of the issue, must be one of 'high', 'medium', or 'low'")
    explanation: str = Field(description="A concise explanation of Why is this a logic error")
    fix: str = Field(description="A code suggestion to resolve the issue")

class LLMReview(BaseModel):
    issues: list[Issue]

class LintResponse(BaseModel):
    issues: list[Issue]
    cache: bool
