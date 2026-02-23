# Financial Document Analyzer

A comprehensive financial document analysis system that processes corporate reports, financial statements, and investment documents using AI-powered analysis agents built with **CrewAI**.

## Features

- **PDF Upload & Async Analysis** — Upload any financial PDF and get AI-powered insights without blocking the HTTP request
- **Multi-Agent Pipeline** — 4 specialized agents work sequentially:
  1. **Document Verifier** — Validates the document is a legitimate financial report
  2. **Financial Analyst** — Deep-dives into financial metrics and trends
  3. **Investment Advisor** — Provides data-driven investment recommendations
  4. **Risk Assessor** — Evaluates market, credit, liquidity, and operational risks
- **Internet-Augmented Analysis** — Agents search the web for current market context
- **Async Queue Processing** — Redis + Celery task queue handles concurrent requests without bottlenecks
- **Database Storage** — SQLite (or PostgreSQL) stores all analysis jobs and results for later retrieval
- **REST API** — 6 FastAPI endpoints covering submission, status polling, result fetching, and history

---

## Architecture

```
HTTP Client
    │
    ▼
FastAPI (main.py)          ← Submit job, poll status, fetch results
    │
    ├─── SQLite DB (database.py)   ← Store job records + analysis results
    │
    └─── Redis Queue
              │
              ▼
        Celery Worker (worker.py)  ← Run CrewAI pipeline in background
              │
              ▼
        4 CrewAI Agents (agents.py + task.py + tools.py)
```

---

## Setup & Installation

### 1. Clone the Repository
```sh
git clone https://github.com/VatsalRaina01/financial-document-analyzer-debug.git
cd financial-document-analyzer-debug
```

### 2. Create a Virtual Environment
```sh
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```sh
cp .env.example .env
```

Edit `.env` and fill in:
```
GOOGLE_API_KEY=your_google_gemini_api_key_here
SERPER_API_KEY=your_serper_dev_api_key_here
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///./analysis_results.db
```

- **GOOGLE_API_KEY** — Get from [Google AI Studio](https://aistudio.google.com/apikey) (required)
- **SERPER_API_KEY** — Get from [Serper.dev](https://serper.dev/) (optional, for web search)
- **REDIS_URL** — Redis connection string (required for async job queue)
- **DATABASE_URL** — SQLAlchemy DB URL (defaults to local SQLite file)

### 5. Start Redis
**Option A — Docker (recommended):**
```sh
docker run -d -p 6379:6379 redis
```
**Option B — Windows native:** Download and install from [Redis for Windows](https://github.com/tporadowski/redis/releases), then run `redis-server`.

### 6. Add a Sample Financial Document
Download a financial PDF (e.g., [Tesla Q2 2025 Update](https://www.tesla.com/sites/default/files/downloads/TSLA-Q2-2025-Update.pdf)) and save it as `data/TSLA-Q2-2025-Update.pdf`.

---

## Running the Application

You need **three terminals** running simultaneously:

**Terminal 1 — Redis** (if not using Docker):
```sh
redis-server
```

**Terminal 2 — Celery Worker:**
```sh
celery -A worker worker --loglevel=info
```

**Terminal 3 — FastAPI Server:**
```sh
python main.py
```

The API will be available at `http://localhost:8000`.

---

## API Endpoints

### `GET /` — Health Check
```sh
curl http://localhost:8000/
```
**Response:** `{"message": "Financial Document Analyzer API is running"}`

---

### `POST /analyze` — Submit Document for Analysis
Uploads a PDF and returns a `job_id` immediately (non-blocking).

```sh
curl -X POST http://localhost:8000/analyze \
  -F "file=@data/TSLA-Q2-2025-Update.pdf" \
  -F "query=What are the key revenue trends and investment risks?"
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File (PDF) | Yes | The financial document to analyze |
| `query` | String | No | Custom query (default: "Analyze this financial document for investment insights") |

**Response:**
```json
{
  "status": "queued",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Document submitted for analysis. Poll /status/{job_id} to track progress.",
  "file_processed": "TSLA-Q2-2025-Update.pdf"
}
```

---

### `GET /status/{job_id}` — Check Job Status
```sh
curl http://localhost:8000/status/550e8400-e29b-41d4-a716-446655440000
```
**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "filename": "TSLA-Q2-2025-Update.pdf",
  "query": "What are the key revenue trends?",
  "created_at": "2025-07-23T10:00:00",
  "completed_at": null,
  "error": null
}
```
**Statuses:** `pending` → `processing` → `completed` | `failed`

---

### `GET /results/{job_id}` — Fetch Analysis Results
```sh
curl http://localhost:8000/results/550e8400-e29b-41d4-a716-446655440000
```
**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "filename": "TSLA-Q2-2025-Update.pdf",
  "query": "What are the key revenue trends?",
  "analysis": "...(full multi-agent analysis report)...",
  "created_at": "2025-07-23T10:00:00",
  "completed_at": "2025-07-23T10:05:30"
}
```

---

### `GET /history` — List Past Analyses
```sh
curl "http://localhost:8000/history?limit=5"
```
Returns the most recent `limit` jobs (default 10), newest first.

---

### Interactive API Docs
Visit `http://localhost:8000/docs` for the full Swagger UI.

---

## Project Structure
```
financial-document-analyzer-debug/
├── main.py            # FastAPI app — API endpoints, job submission
├── worker.py          # Celery worker — background task, run_crew()
├── database.py        # SQLAlchemy models and DB session management
├── agents.py          # CrewAI agent definitions (4 agents)
├── task.py            # CrewAI task definitions (4 tasks)
├── tools.py           # Custom tools (PDF reader, Serper search)
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variable template
├── .gitignore         # Git ignore rules
├── fixes_done.md      # Detailed log of all bugs found and fixed
├── data/
│   └── TSLA-Q2-2025-Update.pdf  # Sample financial document
└── outputs/           # Output directory
```

---

## Bugs Found & Fixed

See [fixes_done.md](fixes_done.md) for a complete breakdown of all 27 bugs identified and fixed across `tools.py`, `agents.py`, `main.py`, `task.py`, and `requirements.txt`.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Multi-agent orchestration | CrewAI 0.130.0 |
| LLM | Google Gemini 2.0 Flash |
| API framework | FastAPI + Uvicorn |
| Task queue | Celery + Redis |
| Database | SQLAlchemy + SQLite (or PostgreSQL) |
| PDF parsing | LangChain Community + PyPDF |
| Web search | Serper.dev |
