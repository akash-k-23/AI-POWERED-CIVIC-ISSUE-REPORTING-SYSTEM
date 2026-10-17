import json

SUPPORTED_CATEGORIES = [
    "Pothole / Road Damage",
    "Garbage / Waste Overflow",
    "Blocked Drain / Waterlogging",
    "Damaged Streetlight / Public Lighting",
    "Other",
    "Unable to determine",
]

ALLOWED_URGENCY_VALUES = ["Low", "Medium", "High"]


def build_basic_prompt():
    return "Describe the civic problem in this image."


def build_civic_analysis_prompt():
    schema = {
        "is_civic_issue": True,
        "category": "Pothole / Road Damage",
        "title": "Visible road surface damage",
        "evidence": ["Description of a detail actually visible in the photo"],
        "urgency": "Medium",
        "urgency_reason": "Explanation based on visible evidence",
        "potential_impact": "Possible impact, expressed cautiously",
        "recommended_action": "Suggested inspection or maintenance",
        "confidence_note": "Any uncertainty or limits of the image",
    }

    return f"""
Act as an AI civic issue reporting assistant.

Task:
- Analyze only evidence visible in the supplied photograph.
- Identify the most likely issue category from the supported categories: {', '.join(SUPPORTED_CATEGORIES)}.
- Choose only if the image genuinely supports the conclusion. If not, return 'Unable to determine'.
- Describe the visible details that support your classification.
- Assess preliminary urgency using the rubric below.
- Explain possible public impact without exaggeration.
- Recommend a reasonable next action.
- Never invent an address, date, official, department, or event.
- Distinguish observed facts from assumptions.
- Do not claim hidden conditions can be verified from a photograph.
- Return valid JSON only, with no markdown fences and no explanatory text outside the JSON.

Urgency rubric:
- Low: A visible maintenance issue with no obvious immediate danger.
- Medium: A visible issue that may affect pedestrian movement, accessibility, sanitation, or road use.
- High: Visible evidence suggests a potentially immediate public safety concern requiring prompt attention.

Strict rules:
- If the image is unrelated, unclear, or insufficient, return `"is_civic_issue": false` with category `"Unable to determine"` and explain the uncertainty.
- Do not automatically label an issue High based only on a dramatic appearance.
- If the evidence is weak, say so plainly in `confidence_note`.
- Use the exact output schema below and ensure all required keys exist.

Return JSON in this structure:
{json.dumps(schema, ensure_ascii=False, indent=2)}

Important:
- `evidence` must be an array of strings that describe details visible in the photo.
- `urgency` must be exactly one of: Low, Medium, High.
- `category` must be one of the supported categories.
- `confidence_note` should explain uncertainty or limits of the image.
- Use factual, cautious language and avoid unsupported claims.
""".strip()


def build_complaint_prompt(analysis_payload, user_details, language="English"):
    analysis_json = json.dumps(analysis_payload, ensure_ascii=False, indent=2)
    details_json = json.dumps(user_details, ensure_ascii=False, indent=2)
    return f"""
You are a civic complaint drafting assistant.

Write a clear, professional complaint in {language} using the findings below.
Requirements:
- Keep the complaint polite, formal, and easy to understand.
- Use only the facts provided by the analysis and the user's notes.
- Never invent an address, official, department, or event.
- Do not claim the complaint has already been submitted.
- Preserve the same underlying findings.
- If the user provided a location or landmark, include it as given.
- If the user added observations, incorporate them carefully.
- Keep the complaint ready for a citizen to submit manually.
- Return only the final complaint text, no extra notes or JSON.

Analysis payload:
{analysis_json}

User details:
{details_json}
""".strip()


def build_tamil_complaint_prompt(analysis_payload, user_details):
    return build_complaint_prompt(analysis_payload, user_details, language="Tamil")


def build_prompt_comparison():
    return {
        "basic_prompt": build_basic_prompt(),
        "engineered_prompt": build_civic_analysis_prompt(),
        "comparison_notes": [
            "The basic prompt is short and flexible, but it may return broad or less structured descriptions.",
            "The engineered prompt adds role instructions, a strict schema, urgency criteria, uncertainty handling, and evidence requirements.",
            "The engineered version is more useful for civic reporting because it promotes factual, structured, and actionable output.",
            "This comparison is a qualitative demonstration, not a scientifically validated benchmark.",
        ],
    }
