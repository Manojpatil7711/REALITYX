import pytest

from app.premium.private_engine_loader import load_private_engines


def test_private_engine_loader_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("REALITYX_PRIVATE_ENGINE_MODULE", raising=False)
    assert load_private_engines() == ()


def test_private_engine_loader_rejects_untrusted_namespace(monkeypatch):
    monkeypatch.setenv("REALITYX_PRIVATE_ENGINE_MODULE", "os")
    with pytest.raises(RuntimeError):
        load_private_engines()
