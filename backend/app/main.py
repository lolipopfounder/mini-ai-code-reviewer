from fastapi import FastAPI

app = FastAPI(title="Mini AI Code Reviewer")

@app.get("/health", tags=["Health"])
def read_root():
    return {"status": "ok"}




