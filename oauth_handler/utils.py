from twilio.rest import Client
from django.conf import settings

def send_sms(to, message):
    """
    Sends an SMS message using Twilio API.

    Args:
        to (str): Recipient's phone number (e.g., +1234567890).
        message (str): The message content.
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to
        )
        return {"status": "success", "sid": message.sid}
    except Exception as e:
        return {"status": "error", "message": str(e)}
