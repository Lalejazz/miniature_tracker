"""Email service for sending password reset emails."""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from decouple import config

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending password reset emails."""
    
    def __init__(self) -> None:
        """Initialize email service."""
        self.frontend_url = config("FRONTEND_URL", default="http://localhost:3001")
        self.email_enabled = config("EMAIL_ENABLED", default=False, cast=bool)
        
        # Email configuration
        self.smtp_server = config("SMTP_SERVER", default="smtp.gmail.com")
        self.smtp_port = config("SMTP_PORT", default=587, cast=int)
        self.smtp_username = config("SMTP_USERNAME", default="")
        self.smtp_password = config("SMTP_PASSWORD", default="")
        self.from_email = config("FROM_EMAIL", default=self.smtp_username)
        self.from_name = config("FROM_NAME", default="Miniature Tracker")
    
    async def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """Send password reset email."""
        try:
            reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"
            
            # For development, just log the reset link
            if not self.email_enabled:
                logger.info(f"""
                ====== PASSWORD RESET EMAIL ======
                To: {email}
                Subject: Password Reset Request
                
                Click the following link to reset your password:
                {reset_url}
                
                This link will expire in 1 hour.
                
                If you didn't request this password reset, please ignore this email.
                ===================================
                """)
                return True
            
            # Send actual email
            return await self._send_smtp_email(email, reset_url)
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")
            return False
    
    async def _send_smtp_email(self, to_email: str, reset_url: str) -> bool:
        """Send email using SMTP."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Reset Your Miniature Tracker Password"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Create HTML and text versions
            text_content = f"""
            Hi there!

            You requested a password reset for your Miniature Tracker account.

            Click the link below to reset your password:
            {reset_url}

            This link will expire in 1 hour.

            If you didn't request this password reset, please ignore this email.

            Happy painting!
            The Miniature Tracker Team
            """
            
            html_content = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <h2 style="color: #2563eb;">🎨 Reset Your Password</h2>
                  
                  <p>Hi there!</p>
                  
                  <p>You requested a password reset for your <strong>Miniature Tracker</strong> account.</p>
                  
                  <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #2563eb; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;
                              font-weight: bold;">
                      Reset Your Password
                    </a>
                  </div>
                  
                  <p style="color: #666; font-size: 14px;">
                    <strong>Note:</strong> This link will expire in 1 hour.
                  </p>
                  
                  <p style="color: #666; font-size: 14px;">
                    If you didn't request this password reset, please ignore this email.
                  </p>
                  
                  <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                  
                  <p style="color: #999; font-size: 12px; text-align: center;">
                    Happy painting!<br>
                    The Miniature Tracker Team
                  </p>
                </div>
              </body>
            </html>
            """
            
            # Attach parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Password reset email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMTP email to {to_email}: {e}")
            return False


# Global email service instance
email_service = EmailService() 