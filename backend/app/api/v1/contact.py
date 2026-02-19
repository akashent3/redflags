"""Contact form endpoint — sends enquiry email via Brevo."""

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.services.email_service import send_email

logger = logging.getLogger(__name__)

router = APIRouter()

CONTACT_RECIPIENT_EMAIL = "info@stockforensics.com"
CONTACT_RECIPIENT_NAME = "StockForensics Support"


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


@router.post("/contact", status_code=status.HTTP_200_OK)
async def submit_contact_form(payload: ContactRequest):
    """
    Receive a contact form submission and forward it to the support inbox.
    No authentication required — public endpoint.
    """
    subject = f"[StockForensics Contact] {payload.subject}"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background: #1d4ed8; padding: 24px; border-radius: 8px 8px 0 0;">
        <h2 style="color: white; margin: 0;">New Contact Form Submission</h2>
        <p style="color: #bfdbfe; margin: 4px 0 0;">StockForensics</p>
      </div>
      <div style="background: #f8fafc; padding: 24px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 8px 8px;">
        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <td style="padding: 8px 0; font-weight: bold; color: #374151; width: 100px;">Name:</td>
            <td style="padding: 8px 0; color: #111827;">{payload.name}</td>
          </tr>
          <tr>
            <td style="padding: 8px 0; font-weight: bold; color: #374151;">Email:</td>
            <td style="padding: 8px 0; color: #111827;">
              <a href="mailto:{payload.email}" style="color: #1d4ed8;">{payload.email}</a>
            </td>
          </tr>
          <tr>
            <td style="padding: 8px 0; font-weight: bold; color: #374151;">Subject:</td>
            <td style="padding: 8px 0; color: #111827;">{payload.subject}</td>
          </tr>
        </table>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 16px 0;" />
        <p style="font-weight: bold; color: #374151; margin: 0 0 8px;">Message:</p>
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; color: #111827; white-space: pre-wrap;">{payload.message}</div>
        <p style="font-size: 12px; color: #9ca3af; margin-top: 24px;">
          Reply directly to <a href="mailto:{payload.email}" style="color: #1d4ed8;">{payload.email}</a> to respond to this enquiry.
        </p>
      </div>
    </div>
    """

    try:
        send_email(
            to_email=CONTACT_RECIPIENT_EMAIL,
            to_name=CONTACT_RECIPIENT_NAME,
            subject=subject,
            html_content=html_content,
        )
        logger.info(f"Contact form submitted by {payload.email} — forwarded to support inbox.")
        return {"success": True, "message": "Your message has been sent. We'll get back to you soon."}
    except Exception as e:
        logger.error(f"Failed to forward contact form from {payload.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message. Please email us directly at info@stockforensics.com.",
        )
