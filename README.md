# Financial Document Analyzer

A comprehensive financial document analysis system that processes corporate reports, financial statements, and investment documents using AI-powered analysis agents built with **CrewAI**.

## Features

- **PDF Upload & Analysis** — Upload any financial PDF and get AI-powered insights
- **Multi-Agent Pipeline** — 4 specialized agents work sequentially:
  1. **Document Verifier** — Validates the document is a legitimate financial report
  2. **Financial Analyst** — Deep-dives into financial metrics and trends
  3. **Investment Advisor** — Provides data-driven investment recommendations
  4. **Risk Assessor** — Evaluates market, credit, liquidity, and operational risks
- **Internet-Augmented Analysis** — Agents search the web for current market context
- **REST API** — Simple FastAPI endpoints for integration

---

## Setup & Installation

### 1. Clone the Repository
```sh
git clone <your-repo-url>
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
Copy the example env file and add your API keys:
```sh
cp .env.example .env
```

Edit `.env` and fill in:
```
GOOGLE_API_KEY=your_google_gemini_api_key_here
SERPER_API_KEY=your_serper_dev_api_key_here
```

- **GOOGLE_API_KEY** — Get from [Google AI Studio](https://aistudio.google.com/apikey) (required)
- **SERPER_API_KEY** — Get from [Serper.dev](https://serper.dev/) (optional, for web search)

### 5. Add a Sample Financial Document
Download a financial PDF (e.g., [Tesla Q2 2025 Update](https://www.tesla.com/sites/default/files/downloads/TSLA-Q2-2025-Update.pdf)) and save it as `data/sample.pdf`.

---

## Usage

### Start the Server
```sh
python main.py
```
The API will be available at `http://localhost:8000`.

### API Endpoints

#### `GET /` — Health Check
```sh
curl http://localhost:8000/
```
**Response:**
```json
{"message": "Financial Document Analyzer API is running"}
```

#### `POST /analyze` — Analyze a Financial Document
Upload a PDF and optionally provide a custom query.

```sh
curl -X POST http://localhost:8000/analyze \
  -F "file=@data/sample.pdf" \
  -F "query=What are the key revenue trends and investment risks?"
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File (PDF) | Yes | The financial document to analyze |
| `query` | String | No | Custom analysis query (default: "Analyze this financial document for investment insights") |

**Response:**
```json
{
  "status": "success",
  "query": "What are the key revenue trends and investment risks?",
  "analysis": "...(comprehensive multi-agent analysis)...",
  "file_processed": "sample.pdf"
}
```

### Interactive API Docs
Visit `http://localhost:8000/docs` for the Swagger UI where you can test the API interactively.

---

## Project Structure
```
financial-document-analyzer-debug/
├── main.py            # FastAPI app, crew orchestration, API endpoints
├── agents.py          # CrewAI agent definitions (4 agents)
├── task.py            # CrewAI task definitions (4 tasks)
├── tools.py           # Custom tools (PDF reader, search)
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variable template
├── fixes_done.md      # Detailed log of all bugs found and fixed
├── data/
│   └── sample.pdf     # Sample financial document (Tesla Q2 2025)
└── outputs/           # Output directory
```

---

## Bugs Found & Fixed

See [fixes_done.md](fixes_done.md) for a comprehensive list of all bugs identified and how they were resolved.

---

## Tech Stack

- **CrewAI 0.130.0** — Multi-agent orchestration framework
- **Google Gemini 2.0 Flash** — LLM backbone
- **FastAPI** — REST API framework
- **LangChain Community** — PDF document loading
- **Serper.dev** — Web search integration
