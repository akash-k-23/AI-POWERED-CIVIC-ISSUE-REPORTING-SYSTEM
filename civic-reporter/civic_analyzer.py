import json
import os
import re
from io import BytesIO

from PIL import Image, ImageOps

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover - dependency check handled in app startup
    genai = None
    types = None

from prompt_engineering import SUPPORTED_CATEGORIES, ALLOWED_URGENCY_VALUES, build_civic_analysis_prompt

MAX_IMAGE_BYTES = 8 * 1024 * 1024
VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
OVERLOAD_FALLBACK_MODEL = "gemini-3.5-flash-lite"
RETIRED_MODEL_ALIASES = {
    "gemini-2.5-flash": "gemini-3.8-flash",
    "models/gemini-2.5-flash": "gemini-3.8-flash",
}


def get_model_name():
    configured_model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    return RETIRED_MODEL_ALIASES.get(configured_model, configured_model)


def get_api_key():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No API key configured. Add GEMINI_API_KEY or GOOGLE_API_KEY to your .env file.")
    return api_key


def validate_image_file(file_obj):
    if file_obj is None:
        raise ValueError("Please upload an image file.")

    filename = getattr(file_obj, "name", "")
    extension = os.path.splitext(filename)[1].lower()
    if extension not in VALID_IMAGE_EXTENSIONS:
        raise ValueError("Unsupported file type. Please upload a JPG, JPEG, or PNG image.")

    file_obj.seek(0, os.SEEK_END)
    size = file_obj.tell()
    file_obj.seek(0)
    if size <= 0:
        raise ValueError("The uploaded image is empty.")
    if size > MAX_IMAGE_BYTES:
        raise ValueError("The uploaded image is too large. Please use an image under 8MB.")

    try:
        file_obj.seek(0)
        image = Image.open(file_obj)
        image.verify()
        file_obj.seek(0)
        image = Image.open(file_obj)
        image = ImageOps.exif_transpose(image)
        image.load()
        return image
    except Exception as exc:  # pragma: no cover - depends on corrupt input
        raise ValueError("The uploaded file could not be opened as a valid image.") from exc


def prepare_image_bytes(file_obj):
    image = validate_image_file(file_obj)
    converted = image.convert("RGB")
    buffer = BytesIO()
    image_format = "PNG" if file_obj.name.lower().endswith(".png") else "JPEG"
    converted.save(buffer, format=image_format)
    return buffer.getvalue(), "image/png" if image_format == "PNG" else "image/jpeg"


def extract_response_text(response):
    if response is None:
        return ""
    text = getattr(response, "text", None)
    if text:
        return text

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        if content is None:
            continue
        parts = getattr(content, "parts", None) or []
        for part in parts:
            if hasattr(part, "text") and part.text:
                return part.text
            if isinstance(part, dict) and part.get("text"):
                return part.get("text")
    return ""


def parse_json_response(response_text):
    cleaned = response_text.strip()
    if not cleaned:
        raise ValueError("The model returned an empty response.")
    cleaned = re.sub(r"```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"```\s*", "", cleaned)
    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("The model response was not valid JSON.") from exc
    return payload


def validate_analysis_payload(payload):
    if not isinstance(payload, dict):
        return False

    required_fields = [
        "is_civic_issue",
        "category",
        "title",
        "evidence",
        "urgency",
        "urgency_reason",
        "potential_impact",
        "recommended_action",
        "confidence_note",
    ]

    for field in required_fields:
        if field not in payload:
            return False

    if not isinstance(payload["is_civic_issue"], bool):
        return False

    category = payload.get("category")
    valid_categories = set(SUPPORTED_CATEGORIES)
    if category not in valid_categories:
        return False

    urgency = payload.get("urgency")
    if urgency not in ALLOWED_URGENCY_VALUES:
        return False

    if not isinstance(payload.get("evidence"), list) or not payload["evidence"]:
        return False
    if not all(isinstance(item, str) and item.strip() for item in payload["evidence"]):
        return False

    for field in ["title", "urgency_reason", "potential_impact", "recommended_action", "confidence_note"]:
        if not isinstance(payload.get(field), str) or not payload.get(field, "").strip():
            return False

    if payload["is_civic_issue"] is False and category != "Unable to determine":
        return False

    if payload["is_civic_issue"] is True and category == "Unable to determine":
        return False

    return True


def _is_temporary_api_error(error):
    status_code = getattr(error, "code", None) or getattr(error, "status_code", None)
    if status_code in (429, 503):
        return True

    message = str(error).lower()
    return any(marker in message for marker in ("429", "503", "unavailable", "resource_exhausted", "high demand"))


def _generate_with_overload_fallback(client, model_name, contents):
    try:
        return client.models.generate_content(model=model_name, contents=contents)
    except Exception as primary_error:
        if not _is_temporary_api_error(primary_error) or model_name == OVERLOAD_FALLBACK_MODEL:
            raise

    try:
        return client.models.generate_content(model=OVERLOAD_FALLBACK_MODEL, contents=contents)
    except Exception as fallback_error:
        if _is_temporary_api_error(fallback_error):
            raise RuntimeError(
                "Both Gemini image models are temporarily busy. Please wait a few minutes and retry."
            ) from fallback_error
        raise


def analyze_with_prompt(image_file, prompt, model_name=None):
    if genai is None or types is None:
        raise ImportError("The official google-genai SDK is not installed. Install requirements first.")

    api_key = get_api_key()
    model_name = model_name or get_model_name()
    model_name = RETIRED_MODEL_ALIASES.get(model_name.strip(), model_name.strip())
    image_bytes, mime_type = prepare_image_bytes(image_file)

    client = genai.Client(api_key=api_key)
    contents = [
        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        prompt,
    ]
    response = _generate_with_overload_fallback(client, model_name, contents)

    response_text = extract_response_text(response)
    if not response_text:
        raise ValueError("The model returned no usable text.")

    payload = parse_json_response(response_text)
    if not validate_analysis_payload(payload):
        raise ValueError("The model response did not match the required civic analysis schema.")
    return payload


def analyze_civic_image(image_file, model_name=None):
    prompt = build_civic_analysis_prompt()
    return analyze_with_prompt(image_file, prompt, model_name=model_name)


def compare_prompts(image_file, model_name=None):
    basic_prompt = "Describe the civic problem in this image."
    engineered_prompt = build_civic_analysis_prompt()
    basic_result = analyze_with_prompt(image_file, basic_prompt, model_name=model_name)
    engineered_result = analyze_with_prompt(image_file, engineered_prompt, model_name=model_name)
    return {
        "basic_prompt": basic_prompt,
        "engineered_prompt": engineered_prompt,
        "basic_result": basic_result,
        "engineered_result": engineered_result,
    }
