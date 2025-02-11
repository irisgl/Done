from twilio.rest import Client
import models.logging_utils
from models.logging_utils import setup_logger
import logging

# Setup logger to write to a file with UTF-8 encoding
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('/home/donehr2ai/logs/debug_chm.log', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.info("SEND A WHATSAPP MESSAGE")


def send_whatsapp_message(client, to, body, from_number, media_url=None):
    """
    Send WhatsApp messages via Twilio with UTF-8 encoding.
    """
    try:
        logger.info(f"send_whatsapp_message - Sending WhatsApp message to {to} with body: {body}")
        message_args = {
            'body': body,  # Ensure UTF-8 content
            'from_': from_number,
            'to': to
        }

        if media_url:
            message_args['media_url'] = [media_url]

        client.messages.create(**message_args)
    except Exception as e:
        logger.error(f"Error sending message to {to}: {e}")



# def send_whatsapp_message(client, to, body, from_number, media_url=None):
#     #logger.info("hi from sent whatsapp message")
#     """
#     Send WhatsApp messages via Twilio with UTF-8 encoding.

#     :param client: Twilio client instance
#     :param to: The recipient's WhatsApp number (e.g., 'whatsapp:+1234567890')
#     :param body: The content of the message to be sent, expected to be a Unicode string
#     :param from_number: The sender's WhatsApp number (e.g., 'whatsapp:+0987654321')
#     :param media_url: (Optional) URL of the media to be sent with the message
#     """
#     try:
#         # Ensure strings are UTF-8 encoded if not already
#         if isinstance(body, str):
#             body = body.encode('utf-8').decode('utf-8')
        
#         message_args = {
#             'body': body,
#             'from_': from_number,
#             'to': to
#         }

#         if media_url:
#             message_args['media_url'] = [media_url]
        
#         client.messages.create(**message_args)
#         print(f"Message sent to {to}: {body}")
#     except Exception as e:
#         print(f"Error sending message to {to}: {str(e)}")

        
