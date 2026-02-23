## Celery Worker — Financial Document Analyzer
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from celery import Celery
from crewai import Crew, Process

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ---------------------------------------------------------------------------
# Celery app configuration
# ---------------------------------------------------------------------------
celery_app = Celery(
    "financial_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Retry failed tasks up to 3 times with exponential back-off
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)


# ---------------------------------------------------------------------------
# Crew runner (imported by worker tasks; also kept here to avoid circular deps)
# ---------------------------------------------------------------------------
def run_crew(query: str, file_path: str = "data/TSLA-Q2-2025-Update.pdf") -> str:
    """Instantiate and run the full 4-agent financial analysis CrewAI pipeline."""
    # Lazy imports so Celery workers don't load LLM clients on module import
    from agents import financial_analyst, verifier, investment_advisor, risk_assessor
    from task import (
        analyze_financial_document,
        verification,
        investment_analysis,
        risk_assessment,
    )

    financial_crew = Crew(
        agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
        tasks=[verification, analyze_financial_document, investment_analysis, risk_assessment],
        process=Process.sequential,
        verbose=True,
    )

    result = financial_crew.kickoff({"query": query, "file_path": file_path})
    return str(result)


# ---------------------------------------------------------------------------
# Celery task
# ---------------------------------------------------------------------------
@celery_app.task(bind=True, name="process_financial_document", max_retries=3)
def process_financial_document_task(self, job_id: str, query: str, file_path: str):
    """
    Background task that runs the CrewAI pipeline and persists results to DB.

    Args:
        job_id:    UUID of the AnalysisJob record in the database.
        query:     User-provided analysis query.
        file_path: Path to the uploaded PDF file on disk.
    """
    from database import SessionLocal, AnalysisJob

    db = SessionLocal()
    job = None

    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if job:
            job.status = "processing"
            db.commit()

        result = run_crew(query=query, file_path=file_path)

        if job:
            job.status = "completed"
            job.result = result
            job.completed_at = datetime.utcnow()
            db.commit()

        return {"status": "completed", "job_id": job_id}

    except Exception as exc:
        if job:
            job.status = "failed"
            job.error = str(exc)
            job.completed_at = datetime.utcnow()
            db.commit()
        # Retry with exponential back-off (10s, 20s, 40s)
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))

    finally:
        db.close()
        # Clean up the temporary uploaded file
        if os.path.exists(file_path) and "financial_document_" in file_path:
            try:
                os.remove(file_path)
            except Exception:
                pass
