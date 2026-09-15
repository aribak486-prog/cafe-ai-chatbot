from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router
from app.config import get_settings

settings = get_settings()
app = FastAPI(title="CafeAI API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_url], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
