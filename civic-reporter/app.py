import json
import base64
from io import BytesIO

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

image_dropzone = components.declare_component(
    "civic_image_dropzone",
    path="components/image_dropzone",
)

from civic_analyzer import analyze_civic_image, compare_prompts, get_api_key, validate_analysis_payload
from complaint_generator import generate_complaint
from prompt_engineering import build_prompt_comparison

load_dotenv()

st.set_page_config(page_title="Civic Reporter", page_icon="🏙️", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --bg: #f4f6f9;
        --surface: #ffffff;
        --surface-soft: #f7f9fc;
        --line: #dfe5ee;
        --text: #1f2d3d;
        --muted: #67768d;
        --primary: #2d6df6;
        --primary-soft: #edf4ff;
        --shadow: rgba(25, 46, 78, 0.08);
        --success: #228b6d;
        --success-soft: #eafaf4;
        --warning: #a76b00;
        --warning-soft: #fff5dd;
        --danger: #b43b3b;
        --danger-soft: #fdeaea;
    }

    .main {
        background: var(--bg);
    }
    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    .topbar {
        background: rgba(255,255,255,0.96);
        border-bottom: 1px solid var(--line);
        padding: 0.85rem 0 0.7rem 0;
        margin: -1rem -1.5rem 1.5rem -1.5rem;
        box-shadow: 0 1px 0 rgba(31,45,61,0.03);
    }
    .brand-wrap {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        min-height: 40px;
    }
    .brand-icon {
        width: 30px;
        height: 30px;
        border-radius: 10px;
        background: linear-gradient(135deg, #2d6df6 0%, #1c4ec9 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1rem;
        box-shadow: 0 8px 18px rgba(45,109,246,0.25);
    }
    .brand-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1f2d3d;
        line-height: 1.1;
    }
    .brand-sub {
        display: block;
        font-size: 0.73rem;
        color: var(--muted);
        font-weight: 500;
        letter-spacing: 0.01em;
    }
    .nav-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.4rem;
        padding: 0.7rem 0.95rem;
        border-radius: 12px;
        background: transparent;
        border: 1px solid transparent;
        color: var(--text);
        font-weight: 600;
        font-size: 0.95rem;
    }
    .nav-btn.active {
        background: var(--primary-soft);
        border-color: #d9e8ff;
        color: var(--primary);
    }
    .nav-btn:hover {
        background: #f3f7ff;
    }
    .page-title {
        text-align: center;
        font-size: clamp(2.2rem, 3vw, 3.2rem);
        font-weight: 800;
        color: var(--text);
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
    }
    .page-subtitle {
        text-align: center;
        font-size: 1.05rem;
        color: var(--muted);
        margin-bottom: 1.6rem;
    }

    .panel-box {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1rem 1.2rem;
        box-shadow: 0 8px 18px var(--shadow);
    }
    .uploader-box {
        border: 2px dashed #d7deea;
        border-radius: 18px;
        background: #f9fafc;
        min-height: 260px;
        padding: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .upload-dropzone {
        border: 2px dashed #cfe0ff;
        border-radius: 16px;
        background: linear-gradient(180deg, #f9fbff 0%, #f3f7ff 100%);
        padding: 1rem 1.1rem;
        min-height: 112px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: var(--muted);
        font-weight: 600;
        margin-bottom: 0.8rem;
        transition: all 0.2s ease;
    }
    .upload-dropzone:hover {
        border-color: var(--primary);
        background: #edf4ff;
    }
    .upload-inner {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.8rem;
    }
    .upload-icon {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: var(--primary-soft);
        color: var(--primary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
    }
    .upload-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text);
    }
    .upload-subtitle {
        font-size: 0.93rem;
        color: var(--muted);
    }
    .info-card {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 8px 18px var(--shadow);
        margin-top: 1.1rem;
    }
    .info-header {
        font-weight: 700;
        font-size: 1.08rem;
        color: var(--text);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .result-card {
        background: var(--surface-soft);
        border: 1px solid var(--line);
        border-radius: 18px;
        min-height: 360px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 1.5rem;
    }
    .result-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.9rem;
        color: var(--muted);
    }
    .result-icon {
        width: 68px;
        height: 68px;
        border-radius: 50%;
        background: #edf1f6;
        color: #7c8aa4;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.9rem;
    }
    .result-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text);
    }
    .result-list {
        font-size: 0.96rem;
        color: var(--muted);
        list-style: none;
        padding: 0;
        margin: 0;
        line-height: 1.9;
    }
    .status-pill {
        display: inline-block;
        padding: 0.42rem 0.8rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.82rem;
    }
    .card {
        padding: 1.1rem 1.2rem;
        border-radius: 18px;
        background: var(--surface);
        border: 1px solid var(--line);
        box-shadow: 0 8px 18px var(--shadow);
    }
    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 0.8rem;
    }
    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        padding: 0.8rem 1.2rem;
        background: linear-gradient(180deg, #2d6df6 0%, #1e4fc9 100%);
        border: none;
        color: white;
        box-shadow: 0 10px 20px rgba(45,109,246,0.22);
    }
    .stButton > button:hover {
        background: linear-gradient(180deg, #255fe1 0%, #1843b6 100%);
    }
    .stDownloadButton > button {
        background: var(--primary-soft);
        color: var(--primary);
        border: 1px solid #dbeaff;
        border-radius: 12px;
        font-weight: 700;
    }
    .stFileUploader > div {
        background: rgba(255,255,255,0.7);
        border-radius: 16px;
    }
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stSelectbox > div > div {
        border-radius: 10px !important;
        border: 1px solid #dfe5ee !important;
        background: #ffffff !important;
        color: #1f2d3d !important;
    }
    [data-baseweb="select"] > div {
        background: #ffffff !important;
        border-color: #dfe5ee !important;
    }
    [data-baseweb="select"] *,
    [data-baseweb="menu"] *,
    [role="option"] {
        color: #1f2d3d !important;
    }
    [data-baseweb="select"] svg {
        fill: #67768d !important;
    }
    .stSelectbox [role="group"] {
        background: #ffffff !important;
        border: 1px solid #dfe5ee !important;
        border-radius: 10px !important;
    }
    .stSelectbox [role="combobox"] {
        color: #1f2d3d !important;
        -webkit-text-fill-color: #1f2d3d !important;
        opacity: 1 !important;
        background: #ffffff !important;
    }
    .stSelectbox button[aria-label="Open"] {
        color: #52627a !important;
    }
    .stSelectbox button[aria-label="Open"] svg {
        fill: currentColor !important;
    }
    [role="listbox"],
    [role="option"] {
        color: #1f2d3d !important;
        background: #ffffff !important;
    }
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label {
        color: #26354a !important;
        font-weight: 600 !important;
    }
    [data-testid="stWidgetLabel"] p {
        font-size: 0.94rem !important;
    }
    [data-testid="stTextInputRootElement"] input::placeholder,
    .stTextArea textarea::placeholder {
        color: #758196 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def urgency_style(urgency):
    palette = {
        "Low": "background: #e8f8ef; color: #126b3b;",
        "Medium": "background: #fff4dc; color: #9a6700;",
        "High": "background: #fdeaea; color: #9e2b2b;",
    }
    return palette.get(urgency, "background: #edf2fb; color: #344054;")


def make_uploaded_file_from_payload(payload):
    if not payload:
        return None

    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            return None
    else:
        parsed = payload

    if not isinstance(parsed, dict):
        return None

    data_url = parsed.get("data")
    if not data_url or not isinstance(data_url, str):
        return None

    try:
        header, encoded = data_url.split(",", 1)
        if not encoded:
            return None
        binary = base64.b64decode(encoded)
    except Exception:
        return None

    file_obj = BytesIO(binary)
    file_obj.name = parsed.get("name") or "pasted_image.png"
    file_obj.seek(0)
    return file_obj


def render_result_cards(analysis):
    evidence = analysis.get("evidence", [])
    urgency = analysis.get("urgency", "Medium")
    st.markdown(f'<div class="section-title">Analysis summary</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="card"><strong>Detected issue</strong><br>{analysis.get("category", "Unable to determine")}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(
            f'<div class="card"><strong>Urgency</strong><br><span class="status-pill" style="{urgency_style(urgency)}">{urgency}</span></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(f'<div class="card"><strong>Confidence</strong><br>{analysis.get("confidence_note", "No note available.")}</div>', unsafe_allow_html=True)

    st.markdown("### Evidence and assessment")
    st.write(f"**Title:** {analysis.get('title', 'Not available')}")
    st.write("**Visible evidence**")
    for item in evidence:
        st.write(f"- {item}")
    st.write(f"**Urgency reason:** {analysis.get('urgency_reason', 'Not available')}")
    st.write(f"**Potential impact:** {analysis.get('potential_impact', 'Not available')}")
    st.write(f"**Recommended action:** {analysis.get('recommended_action', 'Not available')}")
    st.caption("Urgency is an AI-generated preliminary suggestion, not an official risk assessment.")


def pdf_from_text(text):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Civic Reporter Complaint")
    pdf.setFont("Helvetica", 12)
    y = 760
    for line in text.splitlines():
        if y < 40:
            pdf.showPage()
            y = 760
        pdf.drawString(60, y, line[:100])
        y -= 18
    pdf.save()
    return buffer.getvalue()


st.markdown(
    """
    <div class="topbar">
        <div style="max-width: 1200px; margin: 0 auto; padding: 0 1.25rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap;">
            <div class="brand-wrap">
                <div class="brand-icon">◈</div>
                <div>
                    <div class="brand-title">CivicFix</div>
                    <span class="brand-sub">AI-Powered City Issue Reporter</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                <div class="nav-btn active">↗ Report</div>
                <div class="nav-btn">🗺 Map</div>
                <div class="nav-btn">📊 Dashboard</div>
                <div class="nav-btn">🛡 Admin</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    configured_api_key = get_api_key()
    api_key_placeholder = any(
        marker in configured_api_key.lower()
        for marker in ("your_", "paste_", "replace_me", "api_key_here")
    )
    api_key_ok = bool(configured_api_key) and not api_key_placeholder
    st.session_state["api_key_ok"] = api_key_ok
    st.session_state["api_key_checked"] = True
except ValueError:
    api_key_placeholder = False
    api_key_ok = False
    st.session_state["api_key_ok"] = False
    st.session_state["api_key_checked"] = True

if not api_key_ok:
    if api_key_placeholder:
        st.warning("Your .env still contains a placeholder API key. Replace it with a valid Google AI Studio key before analyzing images.")
        with st.expander("How to set the API key"):
            st.code("GEMINI_API_KEY=PASTE_YOUR_REAL_KEY_HERE\nGEMINI_MODEL=gemini-3.8-flash", language="dotenv")
            st.caption("Replace the placeholder with your key, save .env, then restart Streamlit. Keep the key private.")
    else:
        st.warning("No API key is configured. Add GEMINI_API_KEY to your .env file before analyzing images.")

report_tab, prompt_lab_tab, about_tab = st.tabs(["Report Issue", "Prompt Lab", "About Project"])

with report_tab:
    st.markdown('<div class="page-title">Report a City Issue</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Upload a photo and our AI will instantly classify the problem</div>', unsafe_allow_html=True)

    paste_zone = image_dropzone(key="issue_image_dropzone", default=None)
    if paste_zone is None:
        st.session_state.pop("pasted_uploaded_file", None)
    else:
        parsed_upload = make_uploaded_file_from_payload(paste_zone)
        if parsed_upload is not None:
            st.session_state["pasted_uploaded_file"] = parsed_upload

    left_col, right_col = st.columns([1.15, 0.9])

    with left_col:
        uploaded_file = st.session_state.get("pasted_uploaded_file")

        if uploaded_file is None:
            st.markdown(
                """
                <div class="upload-inner">
                    <div class="upload-icon">📷</div>
                    <div class="upload-title">Drag, drop, browse, or paste</div>
                    <div class="upload-subtitle">JPG, PNG up to 8MB</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)

        with st.expander("Optional details", expanded=False):
            st.caption("You can create a report using the image alone.")
            location = st.text_input("Location or nearby landmark", placeholder="For example, near the main bus stop")
            observations = st.text_area("Short note", placeholder="Add any detail the image may not show", height=90)
            language = st.selectbox("Report language", ["English", "Tamil"])

        analyze_button = st.button("Upload & Classify with AI", type="primary")

        if analyze_button:
            if uploaded_file is None:
                st.warning("Please upload a JPG, JPEG, or PNG image before analyzing.")
            elif not api_key_ok:
                st.error("Add a valid GEMINI_API_KEY to your .env file, then restart the app and try again.")
            else:
                try:
                    with st.spinner("Analyzing the image with the configured vision model..."):
                        analysis = analyze_civic_image(uploaded_file)
                    if not validate_analysis_payload(analysis):
                        raise ValueError("The model response did not include all required civic analysis fields.")
                    st.session_state["analysis_result"] = analysis
                    st.session_state["complaint_text"] = generate_complaint(analysis, location, observations, language)
                    st.success("Civic issue analysis complete.")
                except Exception as exc:
                    error_text = str(exc).lower()
                    if "api_key_invalid" in error_text or "api key not valid" in error_text:
                        st.error("Gemini rejected the configured API key. Replace GEMINI_API_KEY in .env with a valid Google AI Studio key, then restart the app.")
                    elif "both gemini image models are temporarily busy" in error_text:
                        st.warning(str(exc))
                    else:
                        st.error(f"Analysis failed: {exc}")
                    st.session_state.pop("analysis_result", None)
                    st.session_state.pop("complaint_text", None)

    with right_col:
        if "analysis_result" in st.session_state:
            analysis = st.session_state["analysis_result"]
            st.markdown(
                """
                <div class="result-card">
                    <div>
                        <div class="result-icon">✦</div>
                        <div class="result-title">AI Classification Results</div>
                        <div style="color: var(--muted); margin-top: 0.3rem;">Detected issue: {category}</div>
                    </div>
                </div>
                """.format(category=analysis.get("category", "Unable to determine")),
                unsafe_allow_html=True,
            )
            render_result_cards(analysis)

            st.markdown('''<div class="section-title">Complaint draft</div>''', unsafe_allow_html=True)
            complaint_text = st.session_state.get("complaint_text", "")
            edited_complaint = st.text_area("Edit the complaint before submitting", complaint_text, height=260, key="complaint_box")
            st.session_state["complaint_text"] = edited_complaint

            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                js_code = json.dumps(edited_complaint)
                html = """
                <script>
                function copyComplaint() {
                    const text = %s;
                    navigator.clipboard.writeText(text)
                        .then(() => {
                            const message = document.getElementById('copy-status');
                            message.innerText = 'Copied!';
                        })
                        .catch(() => {
                            const message = document.getElementById('copy-status');
                            message.innerText = 'Copy failed in this browser.';
                        });
                }
                </script>
                <button onclick="copyComplaint()">Copy complaint</button>
                <div id="copy-status" style="margin-top: 0.5rem; color: #0f172a;"></div>
                """ % js_code
                components.html(html, height=100)
            with c2:
                st.download_button(
                    "Download as TXT",
                    data=edited_complaint.encode("utf-8"),
                    file_name="civic_report.txt",
                    mime="text/plain",
                )
            with c3:
                st.download_button(
                    "Download as PDF",
                    data=pdf_from_text(edited_complaint),
                    file_name="civic_report.pdf",
                    mime="application/pdf",
                )
        else:
            st.markdown(
                """
                <div class="result-card">
                    <div class="result-placeholder">
                        <div class="result-icon">✦</div>
                        <div class="result-title">AI Classification Results</div>
                        <div>Upload a photo to see instant analysis</div>
                        <ul class="result-list">
                            <li>› Issue category detection</li>
                            <li>› Confidence scoring</li>
                            <li>› Severity assessment</li>
                            <li>› Repair cost estimate</li>
                        </ul>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

with prompt_lab_tab:
    st.markdown('<div class="section-title">Prompt Lab</div>', unsafe_allow_html=True)
    st.caption("Qualitative demonstration only — not a scientifically validated performance benchmark.")
    lab_upload = st.file_uploader("Upload an image for prompt comparison", type=["jpg", "jpeg", "png"], key="prompt_lab_upload")

    if lab_upload is not None:
        st.image(Image.open(lab_upload), caption="Uploaded image for Prompt Lab", use_container_width=True)

    compare_button = st.button("Run Prompt Comparison")
    if compare_button:
        if lab_upload is None:
            st.warning("Please upload an image before running a prompt comparison.")
        elif not api_key_ok:
            st.error("An API key is required to run Prompt Lab.")
        else:
            try:
                with st.spinner("Running the two prompt variants on the same image..."):
                    comparison = compare_prompts(lab_upload)
                st.session_state["prompt_comparison"] = comparison
                st.success("Prompt comparison complete.")
            except Exception as exc:
                st.error(f"Prompt comparison failed: {exc}")
                st.session_state.pop("prompt_comparison", None)

    if "prompt_comparison" in st.session_state:
        comparison = st.session_state["prompt_comparison"]
        basic_prompt = comparison["basic_prompt"]
        engineered_prompt = comparison["engineered_prompt"]
        basic_output = comparison["basic_result"]
        engineered_output = comparison["engineered_result"]

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### Basic prompt")
            st.code(basic_prompt)
            st.json(basic_output)
        with col_b:
            st.markdown("#### Engineered prompt")
            st.code(engineered_prompt)
            st.json(engineered_output)

        st.markdown("### Why the engineered prompt is more useful")
        notes = build_prompt_comparison()["comparison_notes"]
        for note in notes:
            st.write(f"- {note}")

with about_tab:
    st.markdown("### About the project")
    st.write(
        "Civic Reporter demonstrates how a vision-capable model and carefully designed prompts can help a citizen "
        "describe a visible civic issue and draft a complaint."
    )
    st.markdown("### Limitations")
    st.write("- The model is not an official government inspector.")
    st.write("- The urgency label is a preliminary AI estimate, not a formal risk assessment.")
    st.write("- Poor lighting, obstructed views, or low-image quality can reduce accuracy.")
    st.write("- The app does not automatically submit complaints to any authority.")
    st.write("- The user should review the generated complaint before sending it manually.")
