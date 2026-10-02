from fastapi import APIRouter

from .key_registry import registry

router = APIRouter(prefix="/keys")


@router.get("/public")
def public_keys() -> dict:
    return registry.public_document()
