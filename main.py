from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import uuid

from database import create_tables, get_db, AnalysisJob
from worker import process_financial_document_task

app = FastAPI(
    title="Financial Document Analyzer",
    description="AI-powered financial document analysis using CrewAI agents, "
                "backed by a Redis/Celery task queue and SQLite database.",
    version="2.0.0",
)


@app.on_event("startup")
async def startup_event():
    """Create database tables on first run."""
    create_tables()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/", summary="Health Check")
async def root():
    """Returns API status."""
    return {"message": "Financial Document Analyzer API is running"}


# ---------------------------------------------------------------------------
# Submit analysis job (async)
# ---------------------------------------------------------------------------
@app.post("/analyze", summary="Submit a financial document for analysis")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(get_db),
):
    """
    Upload a financial PDF and submit it for async analysis.

    Returns a **job_id** immediately. The actual analysis runs in the background
    via a Celery worker. Poll `/status/{job_id}` to track progress, then fetch
    the full report from `/results/{job_id}`.
    """
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        # Save uploaded file to disk
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Normalise empty query
        if not query or query.strip() == "":
            query = "Analyze this financial document for investment insights"

        # Persist job record to DB
        job = AnalysisJob(
            id=file_id,
            filename=file.filename,
            query=query.strip(),
            status="pending",
        )
        db.add(job)
        db.commit()

        # Push task onto Celery queue (non-blocking)
        process_financial_document_task.delay(file_id, query.strip(), file_path)

        return {
            "status": "queued",
            "job_id": file_id,
            "message": "Document submitted for analysis. Poll /status/{job_id} to track progress.",
            "file_processed": file.filename,
        }

    except Exception as e:
        # Clean up file on submission error
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Error queuing financial document: {str(e)}",
        )


# ---------------------------------------------------------------------------
# Job status
# ---------------------------------------------------------------------------
@app.get("/status/{job_id}", summary="Check analysis job status")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Returns the current status of an analysis job.

    **Statuses:** `pending` → `processing` → `completed` | `failed`
    """
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "status": job.status,
        "filename": job.filename,
        "query": job.query,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error": job.error if job.status == "failed" else None,
    }


# ---------------------------------------------------------------------------
# Fetch results
# ---------------------------------------------------------------------------
@app.get("/results/{job_id}", summary="Fetch completed analysis results")
async def get_job_results(job_id: str, db: Session = Depends(get_db)):
    """
    Returns the full multi-agent analysis report once it is complete.
    Returns a 202-style response if the job is still running.
    """
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status in ("pending", "processing"):
        return {
            "job_id": job.id,
            "status": job.status,
            "message": "Analysis is still in progress. Try again shortly.",
        }

    if job.status == "failed":
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {job.error}",
        )

    return {
        "job_id": job.id,
        "status": job.status,
        "filename": job.filename,
        "query": job.query,
        "analysis": job.result,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------
@app.get("/history", summary="List past analysis jobs")
async def get_analysis_history(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Returns the most recent `limit` analysis jobs (default 10), newest first.
    Useful for reviewing past analyses without re-uploading documents.
    """
    jobs = (
        db.query(AnalysisJob)
        .order_by(AnalysisJob.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "total": len(jobs),
        "jobs": [
            {
                "job_id": job.id,
                "filename": job.filename,
                "query": job.query,
                "status": job.status,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            }
            for job in jobs
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)