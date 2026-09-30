import pytest

from app.security.resource_limits import (
    ResourceLimits,
    validate_processing_budget,
    validate_upload_size,
)


def test_upload_budget_accepts_boundary_and_rejects_overflow():
    limits = ResourceLimits(max_upload_bytes=10)
    validate_upload_size(10, limits)
    with pytest.raises(ValueError, match="maximum size"):
        validate_upload_size(11, limits)


def test_upload_budget_rejects_negative():
    with pytest.raises(ValueError, match="negative"):
        validate_upload_size(-1)


def test_processing_budget_accepts_boundary_and_times_out_after_budget():
    limits = ResourceLimits(max_processing_seconds=2.0)
    validate_processing_budget(2.0, limits)
    with pytest.raises(TimeoutError, match="budget exceeded"):
        validate_processing_budget(2.001, limits)


def test_processing_budget_rejects_negative():
    with pytest.raises(ValueError, match="negative"):
        validate_processing_budget(-0.1)
