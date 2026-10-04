from fastapi import FastAPI, Request
from .logging import configure_logging
from .owner_routes import router as owner_router
from .routes import router
from .key_routes import router as key_router
from .receipt_routes import router as receipt_router
from .operations import router as operations_router
from .professional_routes import router as professional_router
from .site_identity import identity_digest, load_site_identity
from .key_registry import load_env_key, registry as key_registry

configure_logging()
load_env_key()

app = FastAPI(
    title="REALITYX Verification API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    return response


app.include_router(router, prefix="/v1")
app.include_router(owner_router, prefix="/v1")
app.include_router(key_router, prefix="/v1")
app.include_router(receipt_router, prefix="/v1")
app.include_router(operations_router, prefix="/v1")
app.include_router(professional_router, prefix="/v1")


@app.get("/.well-known/realityx-identity")
def realityx_identity() -> dict[str, object]:
    """Machine-readable public identity; ownership status is fail-closed by default."""
    identity = load_site_identity()
    return {"identity": identity.public_document(), "identity_digest": identity_digest(identity)}


@app.get("/.well-known/realityx-keys")
def realityx_keys() -> dict[str, object]:
    """Public signing-key document for independent proof verification."""
    document = key_registry.public_document()
    return {**document, "document_digest": key_registry.public_document_digest()}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "realityx-api"}
