"""Annual Reports API endpoints."""

import hashlib
import logging
import uuid as uuid_lib
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.annual_report import AnnualReport
from app.models.company import Company
from app.models.user import User
from app.schemas import ReportListResponse, ReportResponse
from app.storage.r2_client import R2Client
from app.utils import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize R2 client
r2_client = R2Client()

# File upload constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_CONTENT_TYPES = ["application/pdf"]
ALLOWED_EXTENSIONS = [".pdf"]


@router.post(
    "/upload",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload annual report PDF",
    description="Upload an annual report PDF file to Cloudflare R2 storage",
)
async def upload_report(
    file: UploadFile = File(..., description="PDF file to upload"),
    company_name: str = Form(..., min_length=1, max_length=255, description="Company name"),
    fiscal_year: int = Form(..., ge=2000, le=2100, description="Fiscal year (e.g., 2023)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Upload an annual report PDF.

    - **file**: PDF file (max 50MB)
    - **company_name**: Name of the company
    - **fiscal_year**: Fiscal year of the report

    Returns the created AnnualReport record with PDF URL.
    """
    try:
        # Validate file type
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Only PDF files are allowed. Received: {file.content_type}",
            )

        # Validate file extension
        if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension. Only .pdf files are allowed.",
            )

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file size
        if file_size > MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large ({size_mb:.1f}MB). Maximum allowed size is 50MB.",
            )

        # Validate non-empty file
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file. Please upload a valid PDF.",
            )

        logger.info(
            f"Uploading report: {company_name}, FY{fiscal_year}, "
            f"Size: {file_size / (1024 * 1024):.2f}MB, User: {current_user.email}"
        )

        # Calculate SHA-256 hash for deduplication
        pdf_hash = hashlib.sha256(file_content).hexdigest()

        # Check if this exact PDF already exists
        existing_report = (
            db.query(AnnualReport)
            .filter(AnnualReport.pdf_hash == pdf_hash)
            .first()
        )

        if existing_report:
            logger.warning(f"Duplicate PDF detected: {pdf_hash}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"This PDF file has already been uploaded (Report ID: {existing_report.id})",
            )

        # Find or create company
        company = (
            db.query(Company)
            .filter(Company.name.ilike(f"%{company_name}%"))
            .first()
        )

        if not company:
            # Create new company if not found
            company = Company(name=company_name, is_active=True)
            db.add(company)
            db.flush()  # Get company ID
            logger.info(f"Created new company: {company_name} (ID: {company.id})")

        # Generate unique object key for R2
        report_uuid = uuid_lib.uuid4()
        # Clean company name for filename
        clean_company_name = "".join(c for c in company_name if c.isalnum() or c in (" ", "-", "_")).strip()
        clean_company_name = clean_company_name.replace(" ", "_")
        object_key = f"reports/{fiscal_year}/{clean_company_name}_{fiscal_year}_{report_uuid}.pdf"

        # Upload to R2
        try:
            pdf_url = r2_client.upload_file(
                file_content=file_content,
                object_key=object_key,
                content_type="application/pdf",
            )
            logger.info(f"Successfully uploaded to R2: {object_key}")
        except Exception as e:
            logger.error(f"R2 upload failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to storage: {str(e)}",
            )

        # Create AnnualReport record
        annual_report = AnnualReport(
            company_id=company.id,
            fiscal_year=fiscal_year,
            pdf_url=pdf_url,
            file_size_bytes=file_size,
            pdf_hash=pdf_hash,
            is_processed="pending",
        )

        db.add(annual_report)
        db.commit()
        db.refresh(annual_report)

        logger.info(f"Created AnnualReport: {annual_report.id}")

        return annual_report

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


@router.get(
    "",
    response_model=ReportListResponse,
    summary="List annual reports",
    description="Get paginated list of user's annual reports",
)
async def list_reports(
    skip: int = Query(0, ge=0, description="Number of reports to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of reports to return"),
    fiscal_year: Optional[int] = Query(None, description="Filter by fiscal year"),
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    is_processed: Optional[str] = Query(None, description="Filter by processing status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get paginated list of annual reports.

    Returns reports accessible by the current user.
    """
    try:
        # Build query
        query = db.query(AnnualReport)

        # Apply filters
        if fiscal_year:
            query = query.filter(AnnualReport.fiscal_year == fiscal_year)

        if company_id:
            query = query.filter(AnnualReport.company_id == company_id)

        if is_processed:
            query = query.filter(AnnualReport.is_processed == is_processed)

        # Get total count
        total = query.count()

        # Get paginated results
        reports = (
            query
            .order_by(AnnualReport.uploaded_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return ReportListResponse(
            total=total,
            skip=skip,
            limit=limit,
            reports=reports,
        )

    except Exception as e:
        logger.error(f"Failed to list reports: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reports: {str(e)}",
        )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get report details",
    description="Get details of a specific annual report",
)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get details of a specific annual report.

    Returns report metadata including PDF URL and processing status.
    """
    try:
        report = db.query(AnnualReport).filter(AnnualReport.id == report_id).first()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report not found: {report_id}",
            )

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report: {str(e)}",
        )


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete report",
    description="Delete an annual report and all associated data",
)
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete an annual report.

    This will also delete:
    - The PDF file from R2 storage
    - All associated analysis results
    - All red flag records
    """
    try:
        report = db.query(AnnualReport).filter(AnnualReport.id == report_id).first()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report not found: {report_id}",
            )

        # Extract object key by stripping the public base URL
        pdf_url = report.pdf_url
        from app.config import settings
        base = settings.r2_public_url.rstrip("/")
        object_key = pdf_url[len(base):].lstrip("/")

        # Delete from R2
        try:
            r2_client.delete_file(object_key)
            logger.info(f"Deleted from R2: {object_key}")
        except Exception as e:
            logger.warning(f"Failed to delete from R2 (continuing): {e}")
            # Continue with database deletion even if R2 deletion fails

        # Delete from database (cascade will handle related records)
        db.delete(report)
        db.commit()

        logger.info(f"Deleted report: {report_id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete report: {str(e)}",
        )
