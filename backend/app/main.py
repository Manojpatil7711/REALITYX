from fastapi import FastAPI
from .routes import router

app = FastAPI(
    title="REALITYX Verification API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(router, prefix="/v1")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "realityx-api"}
