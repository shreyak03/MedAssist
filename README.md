# MedAssist AI — Assignment 10 (Medical Healthcare Agents)

A coursework prototype using FastAPI, Agno's three-member coordinated team, Groq, PubMed literature lookup, Streamlit, Docker Compose, Kubernetes manifests, and pytest.

## Safety boundary
This is an educational demonstration, not a medical device or diagnostic service. It must not be used to diagnose, triage, or make treatment decisions. The model may be wrong. A qualified radiologist/clinician must interpret the complete study and clinical history. The application accepts common raster images only (PNG/JPEG/BMP); it does not parse DICOM series or guarantee correct modality/sequence identification.

## Architecture
- Medical Image Analyzer: vision-capable Groq model describes only visible features and limitations.
- Medical Research Agent: searches PubMed via NCBI E-utilities and summarizes returned metadata/abstracts.
- Medical Report Reviewer: checks unsupported claims and creates a cautious educational summary.
- Agno Team: `TeamMode.coordinate` delegates and synthesizes across exactly these three agents.
- FastAPI backend: `GET /`, `GET /health`, `POST /analyze`, `POST /ask`.
- Streamlit frontend: uploads an image and displays the API response.

## Local setup (Windows PowerShell)
Use Python 3.11 (recommended):
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```
Put your own Groq key in `.env`. Never commit or share it.

Run backend (terminal 1):
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Check `http://127.0.0.1:8000/health` and API docs at `http://127.0.0.1:8000/docs`.

Run frontend (terminal 2, same venv):
```powershell
python -m streamlit run frontend/streamlit_app.py
```
Open `http://localhost:8501`. If using two terminals, activate `.venv` in each.

## Tests
```powershell
python -m pytest -v
```
Tests mock the AI workflow and do not consume Groq tokens.

## Docker
Build backend image:
```powershell
docker build -t medassist-api:1.0 .
```
Run compose (backend + frontend):
```powershell
docker compose up --build
```
Frontend: http://localhost:8501; API docs: http://localhost:8000/docs.
Stop:
```powershell
docker compose down
```
Do not put the API key in the Dockerfile. Compose reads `.env`.

## Kubernetes (local cluster such as Docker Desktop Kubernetes or Minikube)
Create a namespace and secret from the local `.env` value (replace the placeholder locally):
```powershell
kubectl create namespace medassist
kubectl -n medassist create secret generic medassist-secrets --from-literal=GROQ_API_KEY='YOUR_KEY' --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f k8s/
kubectl -n medassist get pods,svc,ingress
```
The manifests assume the `medassist` namespace. The API Service is ClusterIP. For local access:
```powershell
kubectl -n medassist port-forward svc/medassist-api 8000:8000
```
The frontend Service is NodePort 30085; access depends on your Kubernetes distribution. Ingress requires an ingress controller and a configured hostname; it is optional for local demo.

## Jenkins
Create a Pipeline job pointing to this repository. Ensure the Jenkins agent has Python 3.11+, Docker CLI with access to a Docker daemon, and Git. Configure `GROQ_API_KEY` as a Jenkins Secret Text credential with ID `groq-api-key`. The Jenkinsfile runs tests and builds the image. Push/deploy stages are intentionally not automatic because registry credentials and a target cluster are environment-specific.

## API examples
Health:
```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```
Question:
```powershell
$body = @{ question = "Explain what diffusion-weighted MRI is, at a high level." } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/ask -Method Post -ContentType "application/json" -Body $body
```
Image upload:
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/analyze -Method Post -Form @{ file = Get-Item ".\sample.png"; question = "Describe the visible image cautiously." }
```
