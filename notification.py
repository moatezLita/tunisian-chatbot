import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

class EmailNotifier:
    def __init__(self, 
                 host="smtp.mail.ovh.net", 
                 port=465, 
                 user="contact@yalors.tn", 
                 password="8Y3iXTaGsUgVZeY", 
                 secure=True):
        """
        Initialize email notifier
        
        Args:
            host: SMTP host
            port: SMTP port
            user: Email username
            password: Email password
            secure: Whether to use SSL
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.secure = secure
        
    def send_notification(self, subject, message, to_email=None):
        """
        Send an email notification
        
        Args:
            subject: Email subject
            message: Email message
            to_email: Recipient email (defaults to sender email)
        """
        if to_email is None:
            to_email = self.user
            
        msg = MIMEMultipart()
        msg['From'] = self.user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        try:
            if self.secure:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
                    server.login(self.user, self.password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(self.host, self.port) as server:
                    server.starttls()
                    server.login(self.user, self.password)
                    server.send_message(msg)
                    
            logger.info(f"Email notification sent: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    notifier = EmailNotifier()
    notifier.send_notification(
        "Tunisian Chatbot Status", 
        "The data collection process has completed successfully."
    )