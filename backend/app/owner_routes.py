from fastapi import APIRouter, Depends
from .premium.owner_access import require_owner

router = APIRouter(prefix="/owner", dependencies=[Depends(require_owner)])


@router.get("/status")
def owner_status() -> dict[str, str]:
    return {"access": "owner", "control_plane": "private"}
