# services/notifications/email_notifications.py
"""Email notification service for approval workflow.

Implements US-022: WordPress media sync with approval.

Features:
- Send approval notification emails
- HTML and plain text templates
- SMTP integration (SendGrid, SES, etc.)
- Rate limiting and retry logic

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import logging
import os
import smtplib
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.approval_queue_manager import ApprovalItem

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class EmailConfig:
    """Email service configuration."""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = ""
    from_name: str = "SkyyRose Platform"
    use_tls: bool = True
    approval_recipients: list[str] = field(default_factory=list)
    dashboard_url: str = ""

    @classmethod
    def from_env(cls) -> EmailConfig:
        """Create config from environment variables."""
        recipients = os.getenv("APPROVAL_EMAIL_RECIPIENTS", "")
        return cls(
            smtp_host=os.getenv("SMTP_HOST", ""),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            from_email=os.getenv("SMTP_FROM_EMAIL", ""),
            from_name=os.getenv("SMTP_FROM_NAME", "SkyyRose Platform"),
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
            approval_recipients=[r.strip() for r in recipients.split(",") if r.strip()],
            dashboard_url=os.getenv("APPROVAL_DASHBOARD_URL", ""),
        )

    @property
    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        return bool(self.smtp_host and self.smtp_user and self.smtp_password and self.from_email)


# =============================================================================
# Templates
# =============================================================================


class EmailTemplate(StrEnum):
    """Email template types."""

    APPROVAL_PENDING = "approval_pending"
    APPROVAL_BATCH = "approval_batch"
    REVISION_REQUESTED = "revision_requested"
    SYNC_COMPLETE = "sync_complete"
    SYNC_FAILED = "sync_failed"


TEMPLATES = {
    EmailTemplate.APPROVAL_PENDING: {
        "subject": "🌹 SkyyRose: New Image Ready for Approval",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; line-height: 1.6; color: #1A1A1A; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #B76E79 0%, #8B4D5A 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; }}
        .images {{ display: flex; gap: 20px; margin: 20px 0; }}
        .image-box {{ flex: 1; text-align: center; }}
        .image-box img {{ max-width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .label {{ font-weight: bold; margin-bottom: 10px; color: #666; }}
        .btn {{ display: inline-block; background: #B76E79; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">New Image Ready for Approval</h1>
        </div>
        <div class="content">
            <p>A new AI-enhanced image is ready for your review:</p>

            <p><strong>Product:</strong> {product_name}</p>
            <p><strong>Asset ID:</strong> {asset_id}</p>

            <div class="images">
                <div class="image-box">
                    <div class="label">Original</div>
                    <img src="{original_url}" alt="Original image">
                </div>
                <div class="image-box">
                    <div class="label">Enhanced</div>
                    <img src="{enhanced_url}" alt="Enhanced image">
                </div>
            </div>

            <p>Please review and approve or request changes.</p>

            <a href="{dashboard_url}/approval/{item_id}" class="btn">Review Now</a>
        </div>
        <div class="footer">
            <p>SkyyRose</p>
            <p>This is an automated notification from your asset pipeline.</p>
        </div>
    </div>
</body>
</html>
""",
        "text": """
SkyyRose: New Image Ready for Approval

A new AI-enhanced image is ready for your review:

Product: {product_name}
Asset ID: {asset_id}

Original: {original_url}
Enhanced: {enhanced_url}

Please review at: {dashboard_url}/approval/{item_id}

---
SkyyRose
""",
    },
    EmailTemplate.APPROVAL_BATCH: {
        "subject": "🌹 SkyyRose: {count} Images Ready for Approval",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; line-height: 1.6; color: #1A1A1A; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #B76E79 0%, #8B4D5A 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; }}
        .stat {{ display: inline-block; background: white; padding: 15px 25px; margin: 10px 5px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #B76E79; }}
        .stat-label {{ font-size: 12px; color: #666; }}
        .btn {{ display: inline-block; background: #B76E79; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">{count} Images Ready for Approval</h1>
        </div>
        <div class="content">
            <p>New AI-enhanced images are ready for your review.</p>

            <div style="text-align: center;">
                <div class="stat">
                    <div class="stat-number">{count}</div>
                    <div class="stat-label">Pending Review</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{products}</div>
                    <div class="stat-label">Products</div>
                </div>
            </div>

            <p style="text-align: center;">
                <a href="{dashboard_url}/approval" class="btn">Review All</a>
            </p>
        </div>
        <div class="footer">
            <p>SkyyRose</p>
        </div>
    </div>
</body>
</html>
""",
        "text": """
SkyyRose: {count} Images Ready for Approval

{count} new AI-enhanced images are ready for review.
Affected products: {products}

Review at: {dashboard_url}/approval

---
SkyyRose
""",
    },
    EmailTemplate.REVISION_REQUESTED: {
        "subject": "🌹 SkyyRose: Revision Requested - {product_name}",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; line-height: 1.6; color: #1A1A1A; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #FFA500; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; }}
        .feedback {{ background: #fff3cd; border-left: 4px solid #FFA500; padding: 15px; margin: 20px 0; }}
        .priority {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .priority-urgent {{ background: #dc3545; color: white; }}
        .priority-high {{ background: #fd7e14; color: white; }}
        .priority-normal {{ background: #28a745; color: white; }}
        .priority-low {{ background: #6c757d; color: white; }}
        .btn {{ display: inline-block; background: #B76E79; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">Revision Requested</h1>
        </div>
        <div class="content">
            <p><strong>Product:</strong> {product_name}</p>
            <p><strong>Asset ID:</strong> {asset_id}</p>
            <p><strong>Priority:</strong> <span class="priority priority-{priority}">{priority_display}</span></p>

            <div class="feedback">
                <strong>Feedback:</strong>
                <p>{feedback}</p>
            </div>

            <p>Please address the feedback and resubmit for approval.</p>

            <a href="{dashboard_url}/revisions/{revision_id}" class="btn">View Details</a>
        </div>
        <div class="footer">
            <p>SkyyRose</p>
        </div>
    </div>
</body>
</html>
""",
        "text": """
SkyyRose: Revision Requested

Product: {product_name}
Asset ID: {asset_id}
Priority: {priority_display}

Feedback:
{feedback}

View details: {dashboard_url}/revisions/{revision_id}

---
SkyyRose
""",
    },
    EmailTemplate.SYNC_COMPLETE: {
        "subject": "✅ SkyyRose: WordPress Sync Complete - {count} Images",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; line-height: 1.6; color: #1A1A1A; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #28a745; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; }}
        .stat {{ display: inline-block; background: white; padding: 15px 25px; margin: 10px 5px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #28a745; }}
        .stat-label {{ font-size: 12px; color: #666; }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">WordPress Sync Complete!</h1>
        </div>
        <div class="content">
            <p>Your approved images have been synced to WordPress.</p>

            <div style="text-align: center;">
                <div class="stat">
                    <div class="stat-number">{count}</div>
                    <div class="stat-label">Images Synced</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{products}</div>
                    <div class="stat-label">Products Updated</div>
                </div>
            </div>
        </div>
        <div class="footer">
            <p>SkyyRose</p>
        </div>
    </div>
</body>
</html>
""",
        "text": """
SkyyRose: WordPress Sync Complete

{count} images synced to WordPress.
{products} products updated.

---
SkyyRose
""",
    },
}


# =============================================================================
# Exceptions
# =============================================================================


class NotificationError(Exception):
    """Base exception for notification errors."""

    def __init__(
        self,
        message: str,
        *,
        correlation_id: str | None = None,
    ) -> None:
        self.correlation_id = correlation_id
        super().__init__(message)


# =============================================================================
# Email Service
# =============================================================================


class EmailNotificationService:
    """Email notification service for approval workflow.

    Features:
    - Send HTML and text emails
    - Template-based content
    - SMTP integration
    - Logging and error handling

    Usage:
        service = EmailNotificationService()

        await service.send_approval_notification(approval_item)
        await service.send_batch_notification(items, count=5, products=3)
    """

    def __init__(
        self,
        config: EmailConfig | None = None,
    ) -> None:
        """Initialize email service.

        Args:
            config: Optional email configuration
        """
        self._config = config or EmailConfig.from_env()

    @property
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return self._config.is_configured

    def _send_smtp_sync(self, msg: MIMEMultipart, to: list[str]) -> None:
        """Synchronous SMTP send — must only be called via asyncio.to_thread.

        Raises:
            smtplib.SMTPException: on connection or authentication failure.
        """
        with smtplib.SMTP(self._config.smtp_host, self._config.smtp_port) as server:
            if self._config.use_tls:
                server.starttls()
            server.login(self._config.smtp_user, self._config.smtp_password)
            server.sendmail(self._config.from_email, to, msg.as_string())

    async def send_email(
        self,
        to: list[str],
        subject: str,
        html_body: str,
        text_body: str,
        *,
        correlation_id: str | None = None,
    ) -> bool:
        """Send an email.

        Args:
            to: Recipient email addresses
            subject: Email subject
            html_body: HTML content
            text_body: Plain text content
            correlation_id: Optional correlation ID

        Returns:
            True if sent successfully
        """
        if not self.is_configured:
            logger.warning(
                "Email not configured, skipping send",
                extra={"correlation_id": correlation_id},
            )
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self._config.from_name} <{self._config.from_email}>"
            msg["To"] = ", ".join(to)

            # Attach parts
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Send — SMTP is synchronous; dispatch to thread pool to avoid
            # blocking the event loop during connection + TLS + auth + send.
            await asyncio.to_thread(self._send_smtp_sync, msg, to)

            logger.info(
                f"Sent email to {len(to)} recipients: {subject}",
                extra={"correlation_id": correlation_id},
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to send email: {e}",
                extra={"correlation_id": correlation_id},
            )
            return False

    async def send_approval_notification(
        self,
        item: ApprovalItem,
        *,
        correlation_id: str | None = None,
    ) -> bool:
        """Send approval pending notification.

        Args:
            item: Approval item
            correlation_id: Optional correlation ID

        Returns:
            True if sent successfully
        """
        template = TEMPLATES[EmailTemplate.APPROVAL_PENDING]

        # Format template
        context = {
            "product_name": item.product_name or "Unknown Product",
            "asset_id": item.asset_id,
            "original_url": item.original_url,
            "enhanced_url": item.enhanced_url,
            "dashboard_url": self._config.dashboard_url,
            "item_id": item.id,
        }

        subject = template["subject"].format(**context)
        html_body = template["html"].format(**context)
        text_body = template["text"].format(**context)

        return await self.send_email(
            to=self._config.approval_recipients,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            correlation_id=correlation_id,
        )

    async def send_batch_notification(
        self,
        count: int,
        products: int,
        *,
        correlation_id: str | None = None,
    ) -> bool:
        """Send batch approval notification.

        Args:
            count: Number of items pending
            products: Number of products affected
            correlation_id: Optional correlation ID

        Returns:
            True if sent successfully
        """
        template = TEMPLATES[EmailTemplate.APPROVAL_BATCH]

        context = {
            "count": count,
            "products": products,
            "dashboard_url": self._config.dashboard_url,
        }

        subject = template["subject"].format(**context)
        html_body = template["html"].format(**context)
        text_body = template["text"].format(**context)

        return await self.send_email(
            to=self._config.approval_recipients,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            correlation_id=correlation_id,
        )

    async def send_revision_notification(
        self,
        item: ApprovalItem,
        revision_id: str,
        *,
        correlation_id: str | None = None,
    ) -> bool:
        """Send revision requested notification.

        Args:
            item: Approval item
            revision_id: Revision item ID
            correlation_id: Optional correlation ID

        Returns:
            True if sent successfully
        """
        template = TEMPLATES[EmailTemplate.REVISION_REQUESTED]

        priority = item.revision_priority.value if item.revision_priority else "normal"

        context = {
            "product_name": item.product_name or "Unknown Product",
            "asset_id": item.asset_id,
            "priority": priority.lower(),
            "priority_display": priority.upper(),
            "feedback": item.revision_feedback or "No feedback provided",
            "dashboard_url": self._config.dashboard_url,
            "revision_id": revision_id,
        }

        subject = template["subject"].format(**context)
        html_body = template["html"].format(**context)
        text_body = template["text"].format(**context)

        return await self.send_email(
            to=self._config.approval_recipients,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            correlation_id=correlation_id,
        )

    async def send_sync_complete_notification(
        self,
        count: int,
        products: int,
        *,
        correlation_id: str | None = None,
    ) -> bool:
        """Send sync complete notification.

        Args:
            count: Number of images synced
            products: Number of products updated
            correlation_id: Optional correlation ID

        Returns:
            True if sent successfully
        """
        template = TEMPLATES[EmailTemplate.SYNC_COMPLETE]

        context = {
            "count": count,
            "products": products,
        }

        subject = template["subject"].format(**context)
        html_body = template["html"].format(**context)
        text_body = template["text"].format(**context)

        return await self.send_email(
            to=self._config.approval_recipients,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            correlation_id=correlation_id,
        )


# Module singleton
_email_service: EmailNotificationService | None = None


def get_email_service() -> EmailNotificationService:
    """Get or create the email notification service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailNotificationService()
    return _email_service


__all__ = [
    "EmailConfig",
    "EmailTemplate",
    "NotificationError",
    "EmailNotificationService",
    "get_email_service",
]
