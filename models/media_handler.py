from models import audio_handler
from models.database import UserMedia
from models.image_handler import process_image


import logging
# Initialize logger
##########################################################################
# Create logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create a single file handler with UTF-8 encoding
file_handler = logging.FileHandler('/home/donehr2ai/logs/debug.log', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(file_handler)

def process_media(session, client, sms_sid, context, new_user_message, settings):
    """
    Process all media attached to the Twilio message and update the database.

    :param session: Database session
    :param client: Twilio client
    :param sms_sid: SMS SID from Twilio
    :param context: Context dictionary containing user details
    :param new_user_message: User message as a string (no longer an object)
    :param settings: Configuration settings
    :return: Boolean indicating if media was processed
    """
    media_processed = False  # Flag to check if any media was processed

    try:
        num_media = int(context.get("NumMedia", 0))  # FIXED: Get from `context`, not `smsbody`
        logger.info(f"Number of media files attached: {num_media}")

        if num_media > 0:
            media_list = client.messages(sms_sid).media.list()  # Get media list
            logger.info(f"Media list retrieved: {len(media_list)} files.")

            for media in media_list:
                media_uri = media.uri
                media_type = media.content_type

                logger.info(f"Processing media: {media_uri} | Type: {media_type}")

                if media_type.startswith('audio'):
                    # Handle audio media
                    translation_text, message_sid = audio_handler.download_media_convert_to_text(
                        media_uri, settings.account_sid, settings.auth_token, settings.openai_key, settings.ANGELINA_LANG
                    )

                    if translation_text:
                        logger.info(f"Audio transcription: {translation_text}")
                        context['user_message'] += " " + translation_text  # Append transcription

                        # Store user audio file information
                        user_media = UserMedia(
                            user_message_id=context.get('user_message_id', None),
                            media_url=media_uri,
                            media_location=f"media/{message_sid}.mp3",
                            translation_text=translation_text
                        )
                        session.add(user_media)

                elif media_type.startswith('image'):
                    # Handle image media
                    media_location = f"media/{sms_sid}.jpeg"
                    image = process_image(media_uri, media_location, settings.account_sid, settings.auth_token)

                    logger.info(f"Image processed and saved at: {media_location}")

                    context['user_message'] += f" #Image saved at {media_location}"

                    # Store user image information
                    user_media = UserMedia(
                        user_message_id=context.get('user_message_id', None),
                        media_url=media_uri,
                        media_location=media_location
                    )
                    session.add(user_media)

                media_processed = True  # At least one media was processed

            session.commit()

    except Exception as e:
        logger.error(f"Error processing media: {e}")

    return media_processed
