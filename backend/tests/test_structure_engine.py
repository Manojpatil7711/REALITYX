import io

from PIL import Image

from app.engines.structure import StructureEngine


def _png(size=(12, 8)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGBA", size).save(buf, format="PNG")
    return buf.getvalue()


def test_structure_engine_reports_decoded_properties():
    result = StructureEngine().analyze(_png(), None)
    assert result["status"] == "available"
    assert result["confidence"] == 1.0
    assert result["format"] == "png"
    assert result["width"] == 12
    assert result["height"] == 8
    assert result["frame_count"] == 1
    assert result["has_alpha"] is True
    assert result["analysis_scope"] == "structural_only"
