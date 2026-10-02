from __future__ import annotations

import base64
import hashlib
import os

from .attestation import canonical_json
from .contracts import VerificationArtifact


ALGORITHM = "Ed25519"
KEY_ID_ENV = "REALITYX_SIGNING_KEY_ID"
PRIVATE_KEY_ENV = "REALITYX_SIGNING_PRIVATE_KEY_B64"


def _payload(artifact: VerificationArtifact) -> bytes:
    return canonical_json(artifact.model_dump(mode="json", exclude={"signature", "signature_algorithm"}))


def artifact_digest(artifact: VerificationArtifact) -> str:
    return hashlib.sha256(_payload(artifact)).hexdigest()


def sign_artifact(artifact: VerificationArtifact) -> VerificationArtifact:
    key_b64 = os.getenv(PRIVATE_KEY_ENV)
    key_id = os.getenv(KEY_ID_ENV)
    if not key_b64 or not key_id:
        return artifact

    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        raw = base64.b64decode(key_b64, validate=True)
        private_key = Ed25519PrivateKey.from_private_bytes(raw)
        signature = private_key.sign(_payload(artifact))
    except (ValueError, TypeError) as exc:
        raise RuntimeError("Invalid REALITYX Ed25519 signing key") from exc

    return artifact.model_copy(update={
        "signature_algorithm": f"{ALGORITHM}:{key_id}",
        "signature": base64.b64encode(signature).decode("ascii"),
    })
