# Civic Reporter

Civic Reporter is a beginner-friendly Streamlit web app that helps citizens analyze photos of civic issues and draft a complaint that can be reviewed before submission.

## Problem and solution

Public infrastructure problems such as potholes, garbage accumulation, blocked drains, and damaged streetlights are often reported informally or not reported at all. Civic Reporter uses a vision-capable AI model to inspect a photo, describe visible evidence, identify a likely issue category, estimate preliminary urgency, and generate a complaint draft in clear language.

This project demonstrates how prompt engineering and computer vision can support civic reporting in a practical, approachable way.

## Project objectives

- Let a user upload an image of a civic issue.
- Use a supported vision-capable AI model to identify the visible problem.
- Explain the evidence in the image using structured output.
- Suggest a preliminary urgency level and public impact.
- Generate an English or Tamil complaint draft.
- Allow the user to review, edit, copy, and download the final text.
- Keep the application simple enough for a beginner to run locally.

## Key features

- Photo upload and preview
- Civic issue analysis with a structured JSON response
- Category detection for the supported issue types
- Preliminary urgency rubric and uncertainty notes
- Complaint generation in English and Tamil
- Editable complaint text area
- Download as TXT and optional PDF export
- Prompt Lab for comparing a basic prompt with an engineered prompt
- About and limitations sections

## Technology stack

- Python
- Streamlit
- Pillow
- Python-dotenv
- Google Generative AI official SDK: `google-genai`
- Vision model: `gemini-3.8-flash`
- JSON for structured responses
- ReportLab for PDF export

## How computer vision is used

The app accepts a local image file and sends it to a vision-capable model. The model is prompted to examine only what is visible in the photograph and explain the evidence. It does not claim to verify hidden conditions or infer a location from the image.

## How prompt engineering is used

Prompt engineering is central to the project.

- The system prompt explains the AI role and expected behavior.
- The task instructions ask for evidence-based reasoning and cautious uncertainty.
- The output must follow a strict JSON schema.
- The application includes an urgency rubric and a clear distinction between facts and assumptions.
- Separate prompts are used for complaint drafting in English and Tamil.
- Prompt Lab shows a basic prompt versus a more structured engineering prompt for comparison.

## Application workflow

1. Open the homepage.
2. Upload a JPG, JPEG, or PNG file.
3. Enter optional location and observation notes.
4. Choose English or Tamil complaint language.
5. Click Analyze Civic Issue.
6. Review the detected issue category, evidence, urgency, impact, and recommended action.
7. Review and edit the generated complaint.
8. Copy or download the complaint.

## Project folder structure

```text
civic-reporter/
├── app.py
├── prompt_engineering.py
├── civic_analyzer.py
├── complaint_generator.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── tests/
    └── test_core.py
```

## Installation on Windows

From a terminal in the workspace folder, run:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

To deactivate the virtual environment later, run:

```powershell
deactivate
```

## How to configure the API key

1. Copy `.env.example` to `.env`.
2. Add your Google AI Studio API key.
3. Optionally change the model if needed.

Example:

```env
GEMINI_API_KEY=your_google_ai_studio_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Keep the `.env` file private and do not commit it to version control.

## How to run the application

Once the virtual environment is active and dependencies are installed:

```powershell
streamlit run app.py
```

Then open the local URL shown in the terminal in your browser.

## Example use cases

- A citizen photographs a pothole near a bus stop.
- A resident uploads an image of overflowing waste bins.
- A user reports a blocked drain that causes waterlogging.
- A damaged streetlight is identified from a public photograph.

## Limitations and ethical considerations

- AI results are preliminary and not official government assessments.
- Image analysis can be mistaken, especially with poor lighting or unclear photos.
- A photo may not show hidden hazards or structural conditions.
- The app should help users prepare a complaint, not replace professional inspection.
- Citizens should review the complaint before submitting it to any authority.

## Future enhancements

- Add image-based geotagging or more detailed issue classification.
- Add a richer complaint template for different departments.
- Support more languages and local civic categories.
- Improve UX with better result summaries and issue history.

## License

This project is intended for educational use in a college environment.
