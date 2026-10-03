from app.intelligence_catalog import catalog


def test_intelligence_catalog_covers_requested_domains():
    ids = {item.id for item in catalog()}
    assert {"image", "video", "voice", "document", "ai_tools", "profiles", "social_media", "provenance"} <= ids


def test_intelligence_catalog_has_privacy_boundaries():
    assert all(item.prohibited for item in catalog())
    assert any("private_messages" in item.prohibited for item in catalog())
    assert any("stolen_keys" in item.prohibited for item in catalog())
