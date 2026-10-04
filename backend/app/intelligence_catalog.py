"""Public-source intelligence catalog for verification research.

The catalog describes what REALITYX may study and how. It deliberately excludes
private account data, credential harvesting, hidden profiling, and unauthorized
scraping. Source adapters can be added later without changing verdict policy.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class IntelligenceDomain:
    id: str
    label: str
    signals: tuple[str, ...]
    allowed_sources: tuple[str, ...]
    prohibited: tuple[str, ...]


INTELLIGENCE_DOMAINS = (
    IntelligenceDomain(
        "image",
        "Image intelligence",
        ("pixels", "metadata", "compression", "provenance", "watermark", "edit history"),
        ("user_upload", "documented_public_api", "public_standard"),
        ("private_accounts", "unauthorized_face_identity", "credential_data"),
    ),
    IntelligenceDomain(
        "video",
        "Video intelligence",
        ("frames", "codec", "audio_track", "temporal_consistency", "provenance", "watermark"),
        ("user_upload", "documented_public_api", "public_standard"),
        ("private_accounts", "unauthorized_identity_tracking", "credential_data"),
    ),
    IntelligenceDomain(
        "voice",
        "Voice & audio intelligence",
        ("waveform", "spectral_features", "codec", "watermark", "provenance", "transcript_consistency"),
        ("user_upload", "documented_public_api", "public_standard"),
        ("voiceprint_identity_without_consent", "private_recordings", "credential_data"),
    ),
    IntelligenceDomain(
        "document",
        "Document intelligence",
        ("structure", "metadata", "fonts", "rendering", "signatures", "provenance", "tamper_signals"),
        ("user_upload", "documented_public_api", "public_standard"),
        ("private_records_without_authorization", "credential_data"),
    ),
    IntelligenceDomain(
        "ai_tools",
        "AI tool intelligence",
        ("capability", "model_version", "provenance", "watermark", "known_limitations", "benchmark"),
        ("official_documentation", "public_benchmark", "public_api", "public_release_notes"),
        ("stolen_keys", "private_prompts", "provider_secrets"),
    ),
    IntelligenceDomain(
        "profiles",
        "Public profile verification",
        ("claimed_identity", "account_provenance", "public_metadata", "content_consistency"),
        ("consent", "user_provided_content", "documented_public_api"),
        ("private_profile_data", "passwords", "unauthorized_identity_inference", "doxxing"),
    ),
    IntelligenceDomain(
        "social_media",
        "Social-media content verification",
        ("post_provenance", "media_integrity", "timestamp_consistency", "public_context", "reposts"),
        ("user_provided_url", "documented_public_api", "public_content"),
        ("private_messages", "credential_harvesting", "covert_tracking", "private_social_graph"),
    ),
    IntelligenceDomain(
        "provenance",
        "Provenance & trust standards",
        ("c2pa", "content_credentials", "cryptographic_signature", "key_status", "chain_integrity"),
        ("public_standard", "official_verifier", "signed_artifact"),
        ("trust_claim_without_verification", "certificate_impersonation"),
    ),
)


def catalog() -> tuple[IntelligenceDomain, ...]:
    return INTELLIGENCE_DOMAINS
