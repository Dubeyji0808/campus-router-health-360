# Campus Router Health 360

Campus Router Health 360 is a full-stack dashboard for monitoring campus network health, identifying problematic routers, and getting AI-assisted troubleshooting guidance. It combines a React frontend with a FastAPI backend, real CSV-based telemetry data, and an OpenRouter-powered copilot experience.

The application helps campus IT teams quickly:

- identify the worst-performing routers
- inspect router health scores and historical trends
- filter by building and firmware version
- view detailed router breakdowns, complaints, and telemetry
- ask an AI assistant for diagnosis and recommended fixes

---

## Project Overview

This project is designed as a practical operations dashboard for infrastructure monitoring. It simulates a real campus networking environment where each router emits performance metrics such as latency, packet loss, disconnect counts, and signal strength.

The application is structured in two main parts:

1. Frontend: React + Vite dashboard UI
2. Backend: FastAPI API layer with CSV data ingestion and AI analysis

The product flow is:

- backend reads router datasets from CSV files
- rankings and router details are computed and exposed as API responses
- frontend fetches those APIs and renders the dashboard
- the Copilot assistant uses OpenRouter to analyze a selected router and suggest action

---

## Why This Project Exists

Campus networks often have many routers across multiple buildings, and identifying a failing node manually is time-consuming. This project provides a single operational view that makes it easy to:

- locate weak routers by health score
- compare router performance across buildings
- investigate the root cause using telemetry and complaints
- surface recommended remediation actions

This makes it useful for demo environments, internal tooling prototypes, and operational dashboards for campus networks.

---

## Tech Stack

### Frontend
- React 18
- Vite
- Recharts for charts and metric visualization
- CSS for interface styling

### Backend
- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- Python-dotenv
- Requests
- Pytest

### AI Integration
- OpenRouter API
- environment-based configuration via `.env`

---

## Application Architecture

The project follows a simple layered design:

- Data layer: CSV files under `backend/data/`
- Service layer: router ranking, telemetry processing, health-scoring logic, AI integration
- Route layer: FastAPI endpoints that expose the data
- UI layer: React components and hooks consuming API responses

### High-level flow

```text
CSV Data files
      ↓
FastAPI backend
      ↓
Router service / health scoring
      ↓
REST API endpoints
      ↓
React dashboard
      ↓
User filters + router selection + AI copilot
```

---

## Features

### Dashboard Overview
- ranking table of routers by health score
- building and firmware filtering
- quick visual summary of degraded routers

### Detailed Router View
- router metadata
- room/building context
- health score and breakdown by category
- time series metrics across hours
- complaint history tied to the router

### AI Copilot
- Ask a natural-language question about a router
- backend identifies the router context
- AI uses router metrics and complaints for insight
- returns probable cause, evidence, and recommended fix

### Data resilience
- CSV-backed data is primary source
- fallback mock data can be used only if the CSV dataset is empty

---

## Folder Structure

```text
campus-router-health-360/
├── README.md
├── setup.sh
├── backend/
│   ├── .env
│   ├── .env.example
│   ├── .venv/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── mock_data.py
│   ├── data/
│   │   ├── complaints.csv
│   │   ├── metrics.csv
│   │   ├── routers.csv
│   │   └── ...
│   ├── models/
│   │   └── schemas.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── copilot_route.py
│   │   ├── rankings.py
│   │   └── router_detail.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── copilot.py
│   │   ├── data_loader.py
│   │   ├── health_score.py
│   │   └── router_service.py
│   ├── tests/
│   │   ├── test_health_score.py
│   │   └── test_routes.py
│   └── utils/
│       └── helpers.py
│
├── docs/
│   ├── api-spec.md
│   ├── architecture.md
│   ├── health-score-formula.md
│   └── screenshots/
│
├── frontend/
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.jsx
│       ├── index.css
│       ├── main.jsx
│       ├── components/
│       │   ├── CopilotBox.jsx
│       │   ├── FilterBar.jsx
│       │   ├── MetricChart.jsx
│       │   ├── RankingsTable.jsx
│       │   └── RouterDetailPanel.jsx
│       ├── hooks/
│       │   └── useRouters.js
│       ├── pages/
│       │   └── Dashboard.jsx
│       ├── services/
│       │   └── api.js
│       └── utils/
│           └── formatters.js
└──
```

---

## Backend Structure

### `backend/app.py`
This is the FastAPI application entry point. It registers routes and exposes the API.

Core routes include:
- `/health`
- `/api/rankings`
- `/api/router/{router_id}`
- `/api/copilot`

### `backend/config.py`
Provides environment-based configuration. It loads values such as:
- OpenRouter API key
- OpenRouter base URL
- model name

### `backend/services/data_loader.py`
Loads CSV files and normalizes them into application-friendly structures. It is the main bridge between raw data and runtime logic.

### `backend/services/health_score.py`
Calculates a router health score using a weighted combination of key metrics such as:
- latency
- packet loss
- disconnect rate
- signal quality
- bad hours count

### `backend/services/router_service.py`
Retrieves rankings and detail data for routers in the format expected by the frontend.

### `backend/services/copilot.py`
Handles AI analysis and answer generation for router troubleshooting.

### `backend/routes/`
Contains route files for rankings, router detail, and copilot requests.

### `backend/data/`
This is where the operational data lives.

- `routers.csv`: router inventory and metadata
- `metrics.csv`: telemetry over time
- `complaints.csv`: tickets or issue logs

---

## Frontend Structure

### `frontend/src/App.jsx`
Main app container and entry point for the dashboard.

### `frontend/src/pages/Dashboard.jsx`
The main page layout for the dashboard.

### `frontend/src/components/`
Reusable UI pieces:
- `RankingsTable.jsx`: high-priority routers table
- `FilterBar.jsx`: building and firmware filtering controls
- `RouterDetailPanel.jsx`: router detail view
- `MetricChart.jsx`: metric visualizations
- `CopilotBox.jsx`: AI chat panel

### `frontend/src/hooks/useRouters.js`
Fetches rankings and route details and manages loading state.

### `frontend/src/services/api.js`
Central API wrapper that calls the backend and handles JSON responses.

---

## Data Flow

### 1. Router inventory
The backend loads router metadata from `backend/data/routers.csv`.

### 2. Operational telemetry
Each router has recorded performance metrics in `backend/data/metrics.csv`.

### 3. Complaints
Issue or incident data is loaded from `backend/data/complaints.csv` and attached to the relevant router.

### 4. Rankings calculation
The backend computes which routers are in the worst condition based on health score and bad-hour counts.

### 5. Dashboard rendering
The frontend calls `/api/rankings` and renders a sorted table.

### 6. Detail view
Selecting a router calls `/api/router/{router_id}` and loads historical metrics, complaints, and metadata.

### 7. AI recommendation
The copilot asks `/api/copilot` and receives a diagnosis with probable cause and fix guidance.

---

## Environment Configuration

The backend expects environment variables in a `.env` file inside `backend/`.

Example:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

You can copy from `.env.example`:

```bash
cd backend
cp .env.example .env
```

The app loads these automatically via `python-dotenv` in the configuration layer.

---

## Local Setup

### 1. Backend setup

```bash
cd campus-router-health-360/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start backend

```bash
cd campus-router-health-360/backend
source .venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at:

```text
http://localhost:8000
```

### 3. Frontend setup

```bash
cd campus-router-health-360/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

The frontend will be available at:

```text
http://localhost:5173
```

---

## API Endpoints

### Health
```http
GET /health
```
Returns service health status.

### Rankings
```http
GET /api/rankings
```
Returns a sorted list of routers with health score and metadata.

### Router Details
```http
GET /api/router/{router_id}
```
Returns all information for one router including breakdown, time series, and complaints.

### Copilot
```http
POST /api/copilot
Content-Type: application/json
```
Request body:

```json
{
  "router_id": "R-1010"
}
```

Response includes:
- router id
- probable cause
- evidence
- recommended fix

---

## Testing

The backend includes tests for the health score logic and route behavior.

Run tests with:

```bash
cd campus-router-health-360/backend
source .venv/bin/activate
pytest
```

Typical test files:
- `backend/tests/test_health_score.py`
- `backend/tests/test_routes.py`

---

## Troubleshooting

### Backend port already in use
If port `8000` is already occupied, stop the stale process and retry:

```bash
lsof -i :8000
kill -9 <PID>
```

### Frontend cannot connect to backend
Check that the backend is running on `localhost:8000` and that the frontend `VITE_API_URL` or default base URL points to that address.

### AI not returning a response
Ensure your `.env` file contains a valid OpenRouter API key and that the environment is loaded correctly.

---

## Notes on Data and Mock Fallback

The project is designed to work with real CSV data, but it also includes a mock fallback path in case the CSVs are temporarily empty or missing. This was added primarily to keep the UI usable during development.

The actual production-ish data path is:

```text
backend/data/*.csv -> backend services -> API -> frontend
```

The mock path is only a safe fallback and should not be considered the main data source for real app usage.

---

## Project Summary

Campus Router Health 360 is a campus operations dashboard that helps monitor router health, detect underperforming network equipment, and generate AI-powered troubleshooting guidance. It combines a clean React interface with a structured FastAPI backend and realistic telemetry data, making it suitable for demos, internal tooling, and operational monitoring scenarios.

---

## Suggested Next Enhancements

- add authentication
- support real-time streaming telemetry
- add export to CSV/PDF reporting
- add login and role-based access
- integrate with real campus device APIs
- add scheduled alerts and notifications

---

## Authoring Note

This project is intentionally designed for clarity and maintainability. Each layer has a specific role: CSV ingestion for data, service logic for health analysis, route layer for API exposure, and component layer for interactive UI.
