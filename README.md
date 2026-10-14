# REHAB-TWIN

REHAB-TWIN is a local-first academic research prototype for recording lower-limb fracture rehabilitation assessments and exploring a multimodal recovery workflow. It includes a React + TypeScript dashboard, a FastAPI API, SQLite persistence, validated X-ray file upload/preview, follow-up tracking, model estimates, history, and PDF export.

## Safety and limitations

- This workflow is for local research review only and is not medical advice or a validated clinical tool.
- No clinically trained, externally validated model is included. The recovery and delayed-risk values are local research estimates and should not be treated as clinical advice.
- The seeded patient records are fictional and clearly labeled as local sample records.
- Do not upload identifiable patient data to an unsecured deployment. Local upload storage is not a substitute for governed clinical storage, access controls, or audit logging.
- The optional training script evaluates synthetic labels only. Its metrics are software-pipeline demonstrations and not evidence of clinical accuracy.

## Run locally

Requirements: Python 3.11+ and Node.js 20+.

From the repository root:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

In another terminal:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Open the dashboard at http://localhost:5173 and interactive API documentation at http://localhost:8000/docs. The Vite development server proxies `/api` calls to the backend, which also works when the frontend is opened through a forwarded/remote development URL. The backend creates the SQLite schema on startup and seeds two fictional sample patients only once. Records, assessments, predictions, and follow-ups persist in `backend/rehab_twin.db`; uploaded X-rays are stored in `backend/uploads/`.

Set `VITE_API_URL` if the API should be accessed directly at a different URL. To change the local Vite proxy destination, set `VITE_PROXY_TARGET` (default `http://127.0.0.1:8000`). The backend settings and allowed frontend origins are documented in [.env.example](./.env.example).

## Docker

```bash
cp .env.example .env
docker compose up --build
```

The compose setup exposes the UI on port 5173 and API docs on port 8000. Persisted database and X-ray upload data are local application data and should be protected accordingly.

## Deploy on Render

The repository includes a Render Blueprint for a static frontend and a Docker-based API. In Render, create a new Blueprint from this repository and deploy the `render.yaml` configuration. The free API service may spin down when idle, and its SQLite database and uploaded images are ephemeral and may be lost after restarts or redeploys. The public API has no login or access controls: use fictional sample data only, never identifiable patient information.

## Working workflows

1. Select a seeded sample patient or register a fictional patient.
2. Submit a clinical assessment and optionally attach a PNG/JPEG image (maximum 12 MB); the image is validated, stored locally, and attached to that assessment.
3. Generate a local recovery estimate. The assessment and estimate are persisted for review.
4. Enter follow-up measures and review the longitudinal chart and saved prediction history.
5. Download a PDF summary for the selected patient.

All user-facing API writes validate input ranges and missing resources return explicit errors. X-ray uploads accept only decodable PNG/JPEG content; stored filenames are randomized and file paths are not returned to the UI.

## API reference

- `GET /api/health`, `GET /api/model-status`, `GET /api/dashboard/summary`
- `GET/POST /api/patients`, `GET/PATCH/DELETE /api/patients/{patient_id}`
- `GET /api/patients/{patient_id}/history`
- `POST /api/patients/{patient_id}/assessments`, `GET /api/patients/{patient_id}/assessments`
- `POST /api/patients/{patient_id}/followups`
- `POST/GET /api/assessments/{assessment_id}/xray`
- `POST /api/predictions`, `GET /api/patients/{patient_id}/predictions`
- `GET /api/reports/{patient_id}`

See `/docs` for request/response schemas and the full route list.

## Tests and build

```bash
cd backend
. ../.venv/bin/activate
pytest -q

cd ../frontend
npm run build
```

The tests use an isolated in-memory database and cover patient registration, validated assessments, X-ray upload/retrieval, follow-ups, prediction persistence, history, dashboard counts, and PDF report generation.

## ML development boundary

`backend/scripts/train_multimodal.py` and `backend/scripts/evaluate_models.py` demonstrate clinical tabular ML training/evaluation with generated synthetic labels. They do not train a radiology model, DenseNet121, SHAP/LIME explainers, Grad-CAM, or a clinically meaningful fusion model. Local artifacts are reported as research-only by the API. Real model support requires verified, appropriately licensed datasets, real outcome labels, trained artifacts, and independent clinical validation before those capabilities can be represented as available.
