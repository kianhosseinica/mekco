import smtplib
import ssl
import certifi
from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False

        try:
            # Create SSL context with certifi certificates
            context = ssl.create_default_context(cafile=certifi.where())

            # Establish SMTP connection with SSL context
            self.connection = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
            self.connection.ehlo()
            if self.use_tls:
                self.connection.starttls(context=context)
                self.connection.ehlo()

            if self.username and self.password:
                self.connection.login(self.username, self.password)

            return True
        except smtplib.SMTPException as e:
            if not self.fail_silently:
                raise
            # Log the exception if not failing silently
            import logging
            logger = logging.getLogger('django.request')
            logger.exception(f"Error connecting to SMTP server: {e}")
            return False
