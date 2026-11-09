import hashlib
import time
from .config import settings

cache = {}

def make_key(language: str, code: str) -> str:
    text = f"{settings.llm_model}|{settings.llm_prompt_version}|{language}|{code}"
    return hashlib.sha256(text.encode()).hexdigest()

def get_cache(key: str):
    if key not in cache:
        return None
    saved_at, issues = cache[key]
    if time.time() - saved_at > settings.cache_ttl_s:
        del cache[key]
        return None
    return issues

def save_cache(key: str, issues) -> None:
    if len(cache) >= settings.cache_max_items:
        oldest = next(iter(cache))
        del cache[oldest]
    cache[key] = (time.time(), issues)
