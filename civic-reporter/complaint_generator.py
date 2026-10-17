import json


def _clean_text(value):
    return (value or "").strip()


def generate_complaint(analysis, location="", observations="", language="English"):
    if not isinstance(analysis, dict):
        raise ValueError("A valid civic analysis payload is required to generate a complaint.")

    category = analysis.get("category", "Unable to determine")
    title = analysis.get("title", "Civic issue noticed")
    urgency = analysis.get("urgency", "Medium")
    evidence = "; ".join(analysis.get("evidence", []))
    recommended_action = analysis.get("recommended_action", "Please inspect this issue promptly.")
    location_text = _clean_text(location)
    observations_text = _clean_text(observations)

    if language.lower() == "tamil":
        location_block = f"இடம்: {location_text}\n" if location_text else ""
        observation_block = f"நிறுவனக் குறிப்புகள்: {observations_text}\n" if observations_text else ""
        complaint = (
            "மதிப்பிற்குரிய அதிகாரிகளுக்கு,\n\n"
            "வணக்கம்.\n\n"
            "பொது சுகாதாரத்திற்கும், பாதுகாப்பிற்கும், சாலைகள் மற்றும் குடியிருப்பாளர்களின் வசதிக்கும் இடையூறாக இருக்கும் ஒரு பொதுக் குறைபாட்டை நான் தெரிவிக்க விரும்புகிறேன். "
            f"கண்டறியப்பட்ட பிரச்சனை: {category}.\n"
            f"விளக்கக்காட்சி: {title}.\n"
            f"கண்ணுக்கு புலப்படும் சான்றுகள்: {evidence}.\n"
            f"முன்னுரிமை நிலை: {urgency}.\n"
            f"பரிந்துரைக்கப்பட்ட நடவடிக்கை: {recommended_action}.\n"
            f"{location_block}"
            f"{observation_block}"
            "இந்த நிலைமை விரைவாக கவனிக்கப்பட வேண்டியது அவசியம்."
            " இதை சீரமைக்க தேவையான நடவடிக்கைகளை எடுக்குமாறு கேட்டுக் கொள்கிறேன்.\n\n"
            "அன்புடன்,\n"
            "ஒரு பொது குடியிருப்பாளர்"
        )
        return complaint.strip()

    location_block = f"Location: {location_text}\n" if location_text else ""
    observation_block = f"Additional observations: {observations_text}\n" if observations_text else ""

    complaint = (
        "To the concerned authority,\n\n"
        "Dear Sir/Madam,\n\n"
        "I am writing to report a visible civic issue affecting public usability and community safety. "
        f"The identified issue is: {category}.\n"
        f"Issue summary: {title}.\n"
        f"Visible evidence: {evidence}.\n"
        f"Preliminary urgency: {urgency}.\n"
        f"Recommended action: {recommended_action}.\n"
        f"{location_block}"
        f"{observation_block}"
        "I request that the relevant inspection and maintenance work be carried out promptly to reduce risk and improve public safety.\n\n"
        "Sincerely,\n"
        "A concerned citizen"
    )
    return complaint.strip()
