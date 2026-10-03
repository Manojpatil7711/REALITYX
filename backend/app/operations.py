from fastapi import APIRouter

from .capability_watch import snapshot
from .contracts import PROTOCOL_VERSION
from .engines import ENGINE_REGISTRY

router = APIRouter(prefix="/operations", tags=["operations"])


WORKFLOW_PROFILES = (
    {
        "id": "government",
        "label": "Government & public administration",
        "purpose": "Evidence-first checking of submitted digital material before an official workflow decision.",
        "flow": ("ingest", "integrity", "forensics", "evidence", "human review"),
    },
    {
        "id": "legal",
        "label": "Legal & investigation",
        "purpose": "Preserve hashes, evidence and limitations for a defensible review trail.",
        "flow": ("ingest", "preserve", "analyze", "attest", "review"),
    },
    {
        "id": "media",
        "label": "News & media",
        "purpose": "Screen images, video and audio for manipulation or synthetic signals before publication.",
        "flow": ("ingest", "fast checks", "deep checks", "evidence", "editor review"),
    },
    {
        "id": "business",
        "label": "Business & platforms",
        "purpose": "Automate trust checks while escalating ambiguous cases instead of forcing a verdict.",
        "flow": ("ingest", "policy", "parallel checks", "fusion", "escalate if uncertain"),
    },
    {
        "id": "public",
        "label": "Public verification",
        "purpose": "Give people a simple result with the supporting evidence and clear limitations.",
        "flow": ("upload", "verify", "result", "evidence"),
    },
)


@router.get("/profiles")
def profiles() -> dict[str, object]:
    return {"profiles": WORKFLOW_PROFILES}


@router.get("/capability-watch")
def capability_watch() -> dict[str, object]:
    """Safe operational signal for detecting runtime capability drift.

    Only aggregate data is returned; private engine module names and secrets are
    never exposed by this endpoint.
    """
    current = snapshot(ENGINE_REGISTRY, PROTOCOL_VERSION)
    return {
        "status": "ok",
        "protocol_version": current.protocol_version,
        "engine_count": len(current.engines),
        "capability_fingerprint": current.fingerprint,
        "tracking": (
            "engine identity, engine version, protocol version and capability "
            "fingerprint; benchmark/model adapters can be added later"
        ),
    }
