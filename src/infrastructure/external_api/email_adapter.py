import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.application.interfaces.notification_service import NotificationService

logger = logging.getLogger(__name__)

class EmailNotificationAdapter(NotificationService):
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self._has_credentials = bool(self.sender_email and self.sender_password)

    async def send_summary(self, recipient: str, summary_text: str) -> bool:
        if self.environment == "production" and not self._has_credentials:
            raise ValueError("SMTP credentials missing in production environment")

        if not self._has_credentials:
            logger.info(f"[DEV MODE] Email would be sent to {recipient}")
            logger.info(f"[DEV MODE] Subject: 📰 Tu Resumen Diario de NewsBrief")
            logger.info(f"[DEV MODE] Body:\n{summary_text}")
            return True

        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient
        msg['Subject'] = "📰 Tu Resumen Diario de NewsBrief"

        msg.attach(MIMEText(summary_text, 'plain'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient, msg.as_string())
            server.quit()
            logger.info(f"Email sent to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            if self.environment == "production":
                raise
            return False