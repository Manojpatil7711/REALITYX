from __future__ import annotations

import base64
import os

from .attestation import artifact_payload
from .contracts import VerificationArtifact
from .key_registry import registry


ALGORITHM = "Ed25519"
KEY_ID_ENV = "REALITYX_SIGNING_KEY_ID"
PRIVATE_KEY_ENV = "REALITYX_SIGNING_PRIVATE_KEY_B64"
REQUIRE_SIGNING_ENV = "REALITYX_REQUIRE_SIGNING"


def _payload(artifact: VerificationArtifact) -> bytes:
    return artifact_payload(artifact)


def _signing_required() -> bool:
    return os.getenv(REQUIRE_SIGNING_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def sign_artifact(artifact: VerificationArtifact) -> VerificationArtifact:
    key_b64 = os.getenv(PRIVATE_KEY_ENV)
    key_id = os.getenv(KEY_ID_ENV)

    if not key_b64 or not key_id:
        if _signing_required():
            raise RuntimeError("REALITYX signing is required but signing credentials are not configured")
        return artifact

    record = registry.require_active(key_id)
    if not record.public_key:
        raise RuntimeError("Registered signing key has no public key")

    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        raw = base64.b64decode(key_b64, validate=True)
        private_key = Ed25519PrivateKey.from_private_bytes(raw)
        derived_public = private_key.public_key().public_bytes_raw()
        registered_public = base64.b64decode(record.public_key, validate=True)
        if derived_public != registered_public:
            raise RuntimeError("Signing private key does not match registered public key")
        signature = private_key.sign(_payload(artifact))
    except (ValueError, TypeError) as exc:
        raise RuntimeError("Invalid REALITYX Ed25519 signing key") from exc

    return artifact.model_copy(update={
        "signature_algorithm": f"{ALGORITHM}:{key_id}",
        "signature": base64.b64encode(signature).decode("ascii"),
    })
