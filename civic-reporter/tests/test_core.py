import json

from prompt_engineering import build_civic_analysis_prompt
from civic_analyzer import _generate_with_overload_fallback, get_model_name, validate_analysis_payload


def test_get_model_name_upgrades_retired_model(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")
    assert get_model_name() == "gemini-3.8-flash"


def test_overloaded_primary_model_uses_multimodal_fallback():
    class FakeModels:
        def __init__(self):
            self.calls = []

        def generate_content(self, model, contents):
            self.calls.append(model)
            if model == "gemini-3.8-flash":
                raise RuntimeError("503 UNAVAILABLE: high demand")
            return "fallback response"

    class FakeClient:
        def __init__(self):
            self.models = FakeModels()

    client = FakeClient()
    result = _generate_with_overload_fallback(client, "gemini-3.8-flash", ["image", "prompt"])

    assert result == "fallback response"
    assert client.models.calls == ["gemini-3.8-flash", "gemini-3.5-flash-lite"]


def test_prompt_contains_required_schema_and_civic_guidance():
    prompt = build_civic_analysis_prompt()
    assert "Act as an AI civic issue reporting assistant" in prompt
    assert """{
"is_civic_issue": true""" in prompt or '"is_civic_issue": true' in prompt
    assert "Urgency" in prompt or "urgency" in prompt


def test_validate_analysis_payload_rejects_missing_required_fields():
    invalid = {
        "is_civic_issue": True,
        "category": "Pothole / Road Damage",
        "title": "Visible road surface damage"
    }
    assert validate_analysis_payload(invalid) is False


def test_validate_analysis_payload_accepts_valid_payload():
    valid = {
        "is_civic_issue": True,
        "category": "Pothole / Road Damage",
        "title": "Visible road surface damage",
        "evidence": ["Crack visible on road surface"],
        "urgency": "Medium",
        "urgency_reason": "Road damage may affect pedestrians and vehicles.",
        "potential_impact": "Possible trip hazard and uneven travel surface.",
        "recommended_action": "Inspect and repair the road surface promptly.",
        "confidence_note": "The image clearly shows deterioration but exact extent is limited."
    }
    assert validate_analysis_payload(valid) is True
