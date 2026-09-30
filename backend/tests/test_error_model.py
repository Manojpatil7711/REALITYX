import pytest

from app.error_model import public_error


def test_public_errors_are_stable_and_safe():
    error = public_error("invalid_upload")
    assert error.code == "INVALID_UPLOAD"
    assert "traceback" not in error.message.lower()
    assert "exception" not in error.message.lower()


def test_unknown_internal_error_is_not_exposed():
    with pytest.raises(ValueError, match="Unknown public error"):
        public_error("internal_database_secret")
