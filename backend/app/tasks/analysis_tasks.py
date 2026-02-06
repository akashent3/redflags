"""Celery tasks for annual report analysis."""

import logging
import time
from uuid import UUID

from celery import Task
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.annual_report import AnnualReport
from app.services.analysis_service import analysis_service
from app.storage.r2_client import R2Client

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management."""

    _db: Session = None
    _r2_client: R2Client = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    @property
    def r2_client(self) -> R2Client:
        if self._r2_client is None:
            self._r2_client = R2Client()
        return self._r2_client

    def after_return(self, *args, **kwargs):
        """Close database session after task completion."""
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.analysis_tasks.analyze_report_task",
    max_retries=3,
    default_retry_delay=60,
)
def analyze_report_task(self, report_id: str) -> dict:
    """
    Background task to analyze an annual report.

    Args:
        report_id: UUID of the AnnualReport to analyze

    Returns:
        dict with analysis result information

    Raises:
        Exception: If analysis fails after retries
    """
    try:
        logger.info(f"Starting analysis task for report {report_id}")

        # Update task state to STARTED
        self.update_state(state="STARTED", meta={"status": "Downloading PDF from storage"})

        # Get report from database
        report = self.db.query(AnnualReport).filter(AnnualReport.id == report_id).first()

        if not report:
            raise Exception(f"Report not found: {report_id}")

        # Update report status
        report.is_processed = "processing"
        self.db.commit()

        # Extract object key from PDF URL
        pdf_url = report.pdf_url
        object_key = pdf_url.split("/", 3)[-1]

        # Update state
        self.update_state(state="PROGRESS", meta={"status": "Downloading PDF", "progress": 10})

        # Download PDF from R2
        try:
            pdf_bytes = self.r2_client.download_file(object_key)
            logger.info(f"Downloaded PDF: {len(pdf_bytes)} bytes")
        except Exception as e:
            logger.error(f"Failed to download PDF from R2: {e}")
            report.is_processed = "failed"
            self.db.commit()
            raise Exception(f"Failed to download PDF: {str(e)}")

        # Get company information
        company = report.company
        company_name = company.name if company else "Unknown Company"

        # Update state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Extracting text from PDF", "progress": 20}
        )

        # Run analysis
        start_time = time.time()

        try:
            # Update state before starting analysis
            self.update_state(
                state="PROGRESS",
                meta={"status": "Running forensic analysis (54 red flags)", "progress": 30}
            )

            analysis_result = analysis_service.analyze_report(
                db=self.db,
                report_id=UUID(report_id),
                pdf_bytes=pdf_bytes,
                company_name=company_name,
                fiscal_year=str(report.fiscal_year),
            )

            processing_time = int(time.time() - start_time)
            analysis_result.processing_time_seconds = processing_time

            # Update report status
            report.is_processed = "completed"
            report.processed_at = analysis_result.analyzed_at
            self.db.commit()

            logger.info(
                f"Analysis completed for report {report_id}: "
                f"Risk Score {analysis_result.risk_score} ({analysis_result.risk_level}), "
                f"Flags Triggered: {analysis_result.flags_triggered_count}/54, "
                f"Time: {processing_time}s"
            )

            # Return success result
            return {
                "status": "SUCCESS",
                "analysis_id": str(analysis_result.id),
                "report_id": str(report_id),
                "risk_score": analysis_result.risk_score,
                "risk_level": analysis_result.risk_level,
                "flags_triggered": analysis_result.flags_triggered_count,
                "processing_time": processing_time,
                "message": f"Analysis completed successfully. Risk Score: {analysis_result.risk_score}/100 ({analysis_result.risk_level})",
            }

        except Exception as e:
            logger.error(f"Analysis failed for report {report_id}: {e}", exc_info=True)
            report.is_processed = "failed"
            self.db.commit()

            # Retry the task if retries remaining
            if self.request.retries < self.max_retries:
                logger.warning(f"Retrying analysis task (attempt {self.request.retries + 1}/{self.max_retries})")
                raise self.retry(exc=e)

            raise Exception(f"Analysis failed after {self.max_retries} retries: {str(e)}")

    except Exception as e:
        logger.error(f"Task failed for report {report_id}: {e}", exc_info=True)

        # Update report status to failed
        try:
            report = self.db.query(AnnualReport).filter(AnnualReport.id == report_id).first()
            if report:
                report.is_processed = "failed"
                self.db.commit()
        except:
            pass

        # Return failure result
        return {
            "status": "FAILURE",
            "report_id": str(report_id),
            "error": str(e),
            "message": f"Analysis failed: {str(e)}",
        }
