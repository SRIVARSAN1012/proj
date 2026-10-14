# REHAB-TWIN backend

This backend exposes the patient, assessment, prediction, and reporting APIs for the REHAB-TWIN research prototype.

## Quick start

1. Create a virtual environment and install dependencies.
2. Run `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.
3. Visit `/docs` for the OpenAPI documentation.

## Notes

- Local research mode is enabled when no trained model artifacts are present.
- Local predictions are clearly marked and should not be treated as validated medical data.
