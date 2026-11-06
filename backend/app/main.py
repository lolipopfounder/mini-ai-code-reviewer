from fastapi import Depends, FastAPI, Request

from app.services import review
from app.schemas import LintResponse, LintRequest
from app.gateway import LLMGateway, OpenAICompatibleGateway
from app.errors import LLMOutputError, error_response

app = FastAPI(title="Mini AI Code Reviewer")

def get_gateway() -> OpenAICompatibleGateway:
    return OpenAICompatibleGateway()

@app.exception_handler(LLMOutputError)
async def handle_llm_error(request: Request, exc: LLMOutputError):
    return error_response(exc.status_code, str(exc))

@app.get("/")
def home():
    return {"message": "Go to /docs for the API documentation."}

@app.get("/health", tags=["Health"])
def read_root():
    return {"status": "ok"}

@app.post("/lint", tags=["LLM"], response_model=LintResponse)
async def lint(req: LintRequest, gateway: LLMGateway = Depends(get_gateway)):
    try:
        issues = await review(gateway, req.language.value, req.code)
        return LintResponse(issues=issues, cache=False)
    finally:
        await gateway.close()


