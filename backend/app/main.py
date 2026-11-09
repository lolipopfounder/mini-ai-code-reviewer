from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.services import review
from app.schemas import LintResponse, LintRequest, Language
from app.gateway import LLMGateway, OpenAICompatibleGateway
from app.errors import LLMOutputError, error_response
from app.config import settings
from app.cache import make_key, get_cache, save_cache

app = FastAPI(title="Mini AI Code Reviewer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    key = make_key(req.language.value, req.code)
    issues = get_cache(key)
    if issues is not None:
        await gateway.close()
        return LintResponse(issues=issues, cache=True)
    try:
        issues = await review(gateway, req.language.value, req.code)
        save_cache(key, issues)
        return LintResponse(issues=issues, cache=False)
    finally:
        await gateway.close()
        
@app.get("/languages", tags=["LLM"])
def get_supported_languages():
    return {"languages": [lang.value for lang in Language]}



