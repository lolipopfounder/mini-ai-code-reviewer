from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    # LLM gateway
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_model: str = "qwen3.5:9b"
    llm_timeout_s: float = 60
    llm_max_tokens: int = 5000
    llm_json_mode: bool = False
    llm_prompt_version: str = "v2"
    
    # Cache
    cache_ttl_s: int = 3600
    cache_max_items: int = 1000
    
    # HTTP
    cors_origins: list[str] = ["http://localhost:5173"]

settings = Settings()