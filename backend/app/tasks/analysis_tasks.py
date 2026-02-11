"""Celery tasks for annual report analysis."""

import logging
import time
from uuid import UUID

from celery import Task
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.annual_report import AnnualReport
from app.models.company import Company
from app.services.analysis_service import analysis_service
from app.services.analysis_service_v2 import analysis_service_v2
from app.services.finedge_client import finedge_client
from app.services.nse_client import nse_client
from app.storage.r2_client import R2Client
import tempfile
import os

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


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.analysis_tasks.analyze_company_by_symbol_task",
    max_retries=2,
    default_retry_delay=120,
)
def analyze_company_by_symbol_task(self, symbol: str, user_id: str) -> dict:
    """
    Background task to analyze a company by symbol - auto-fetches from NSE and FinEdge.

    Steps:
    1. Fetch company profile from FinEdge API
    2. Fetch latest annual report from NSE India
    3. Download PDF
    4. Upload to R2 storage
    5. Create/update company record in database
    6. Create annual report record
    7. Trigger analysis using simplified pipeline (FinEdge API + Gemini)

    Args:
        symbol: NSE symbol (e.g., "RELIANCE", "TCS")
        user_id: User ID who triggered the analysis

    Returns:
        dict with analysis result information
    """
    try:
        logger.info(f"Starting analysis task for company symbol: {symbol}")
        self.update_state(state="STARTED", meta={"status": f"Fetching company data for {symbol}"})

        # Step 1: Fetch company profile from FinEdge
        self.update_state(state="PROGRESS", meta={"status": "Fetching company profile from FinEdge", "progress": 10})

        try:
            profile = finedge_client.get_company_profile(symbol)
            logger.info(f"Fetched company profile for {symbol}: {profile.get('companyName', 'Unknown')}")
        except Exception as e:
            logger.error(f"Failed to fetch company profile from FinEdge: {e}")
            profile = {"companyName": symbol, "industry": "Unknown", "sector": "Unknown"}

        company_name = profile.get("companyName", symbol)

        # Step 2: Fetch latest annual report from NSE
        self.update_state(state="PROGRESS", meta={"status": "Fetching latest annual report from NSE", "progress": 20})

        annual_report_info = nse_client.get_latest_annual_report(symbol)

        if not annual_report_info or not annual_report_info.get("pdf_url"):
            raise Exception(f"No annual report found for {symbol} on NSE India")

        pdf_url = annual_report_info["pdf_url"]
        fiscal_year = annual_report_info["year"]

        logger.info(f"Found annual report for {symbol}: Year {fiscal_year}, URL: {pdf_url}")

        # Step 3: Download PDF from NSE
        self.update_state(state="PROGRESS", meta={"status": f"Downloading annual report (FY {fiscal_year})", "progress": 30})

        pdf_bytes = nse_client.download_pdf(pdf_url)

        if not pdf_bytes:
            raise Exception(f"Failed to download PDF from NSE: {pdf_url}")

        logger.info(f"Downloaded PDF: {len(pdf_bytes)} bytes")

        # Step 4: Create/update company record in database
        self.update_state(state="PROGRESS", meta={"status": "Saving company info", "progress": 40})

        # Check if company exists
        company = self.db.query(Company).filter(Company.nse_symbol == symbol).first()

        if not company:
            # Create new company
            company = Company(
                name=company_name,
                nse_symbol=symbol,
                industry=profile.get("industry", "Unknown"),
                sector=profile.get("sector", "Unknown"),
                is_active=True,
            )
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
            logger.info(f"Created new company record: {company.id}")
        else:
            logger.info(f"Using existing company record: {company.id}")

        # Step 5: Upload PDF to R2
        self.update_state(state="PROGRESS", meta={"status": "Uploading PDF to storage", "progress": 50})

        # Save to temp file for analysis
        temp_fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf")
        os.write(temp_fd, pdf_bytes)
        os.close(temp_fd)

        try:
            # Upload to R2
            object_key = f"reports/{company.id}/{fiscal_year}/annual_report.pdf"
            uploaded_url = self.r2_client.upload_file(temp_pdf_path, object_key)
            logger.info(f"Uploaded PDF to R2: {uploaded_url}")

            # Step 6: Create annual report record
            self.update_state(state="PROGRESS", meta={"status": "Creating report record", "progress": 60})

            # Check if report already exists
            existing_report = (
                self.db.query(AnnualReport)
                .filter(AnnualReport.company_id == company.id, AnnualReport.fiscal_year == fiscal_year)
                .first()
            )

            if existing_report:
                report = existing_report
                logger.info(f"Using existing report record: {report.id}")
            else:
                # Get file size and page count
                file_size_mb = len(pdf_bytes) / (1024 * 1024)

                report = AnnualReport(
                    company_id=company.id,
                    fiscal_year=fiscal_year,
                    pdf_url=uploaded_url,
                    file_size_mb=file_size_mb,
                    pages_count=None,  # Will be set during analysis
                    is_processed="processing",
                )
                self.db.add(report)
                self.db.commit()
                self.db.refresh(report)
                logger.info(f"Created new report record: {report.id}")

            # Step 7: Run analysis using simplified pipeline
            self.update_state(state="PROGRESS", meta={"status": "Running red flag analysis", "progress": 70})

            start_time = time.time()

            analysis_result = analysis_service_v2.analyze_report(
                db=self.db,
                report_id=report.id,
                pdf_path=temp_pdf_path,
                company_symbol=symbol,
                company_name=company_name,
                fiscal_year=str(fiscal_year),
            )

            processing_time = int(time.time() - start_time)
            analysis_result.processing_time_seconds = processing_time

            # Update report status
            report.is_processed = "completed"
            report.processed_at = analysis_result.analyzed_at
            self.db.commit()

            logger.info(
                f"Analysis completed for {symbol}: "
                f"Risk Score {analysis_result.risk_score} ({analysis_result.risk_level}), "
                f"Flags Triggered: {analysis_result.flags_triggered_count}, "
                f"Time: {processing_time}s"
            )

            return {
                "status": "SUCCESS",
                "analysis_id": str(analysis_result.id),
                "report_id": str(report.id),
                "company_id": str(company.id),
                "symbol": symbol,
                "company_name": company_name,
                "fiscal_year": fiscal_year,
                "risk_score": analysis_result.risk_score,
                "risk_level": analysis_result.risk_level,
                "flags_triggered": analysis_result.flags_triggered_count,
                "processing_time": processing_time,
                "message": f"Analysis completed for {company_name}. Risk Score: {analysis_result.risk_score}/100 ({analysis_result.risk_level})",
            }

        finally:
            # Clean up temp file
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

    except Exception as e:
        logger.error(f"Task failed for symbol {symbol}: {e}", exc_info=True)

        # Retry if retries remaining
        if self.request.retries < self.max_retries:
            logger.warning(f"Retrying analysis task for {symbol} (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e)

        return {
            "status": "FAILURE",
            "symbol": symbol,
            "error": str(e),
            "message": f"Analysis failed for {symbol}: {str(e)}",
        }
