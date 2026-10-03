from fastapi import FastAPI
from .logging import configure_logging
from .owner_routes import router as owner_router
from .routes import router
from .key_routes import router as key_router
from .receipt_routes import router as receipt_router
from .key_registry import load_env_key

configure_logging()
load_env_key()

app = FastAPI(
    title="REALITYX Verification API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(router, prefix="/v1")
app.include_router(owner_router, prefix="/v1")
app.include_router(key_router, prefix="/v1")
app.include_router(receipt_router, prefix="/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "realityx-api"}
