from fastapi import FastAPI
from .logging import configure_logging
from .owner_routes import router as owner_router
from .routes import router

configure_logging()

app = FastAPI(
    title="REALITYX Verification API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(router, prefix="/v1")
app.include_router(owner_router, prefix="/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "realityx-api"}
