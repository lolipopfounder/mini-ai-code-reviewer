from fastapi import FastAPI, Request

from .errors import LLMError, error_response

app = FastAPI(title="Mini AI Code Reviewer")


@app.exception_handler(LLMError)
async def handle_llm_error(request: Request, exc: LLMError):
    return error_response(exc.status_code, str(exc))


@app.get("/health", tags=["Health"])
def read_root():
    return {"status": "ok"}




