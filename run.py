# Standard Library Imports
import json
import os
import sys
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import time
import re
from moviepy.editor import AudioFileClip
from openai import OpenAI  # Import the correct client
#sys.path.append('/home/donehr2ai/.local/lib/python3.11/site-packages')  # Adjust the Python version if needed





# Third-Party Imports
import requests
from requests.auth import HTTPBasicAuth
import twilio
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient
# from sqlalchemy import (
#     create_engine, Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean, event
# )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


# Internal Imports
# from models.asana_task_manager import AsanaTaskManager
from models.assistant import restore, run, run_new, save_txt_in_drct, handle_exception, change_in_file
# new
from models.context_manage import save_context, get_context_field
from models.chm_api_getters import get_teacher_data, check_registration_status, get_student_data
#
from models.chm_config_loader import Settings
from models.db_store import store_user_message, store_asana_task
from models.database import get_session_factory, UserMessage, AsanaTask, UserMedia
from models.html_utils import serve_html
from models.image_handler import process_image
from models.media_handler import process_media
from models.learndash_lead_manager import submit_elementor_form, get_woocommerce_customers_with_phone, get_courses
from models.message_utils import extract_sms_data
from models.send_whatsapp_message import send_whatsapp_message
from models.sms import SmsMessage, convert_phone_number
from models.logging_utils import setup_logger
from models.audio_handler import download_media_convert_to_text


import logging


# Initialize logger
##########################################################################
# Create logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create a single file handler with UTF-8 encoding
file_handler = logging.FileHandler('/home/donehr2ai/logs/debug_chm.log', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(file_handler)

# Test logging
logger.info("\ndebug 01")
logger.info("1. TESTING LOG ENTRY!!")
##########################################################################

## init ## Global Variables
chm_context = {
    'thread_store': "",
    'teacher_name': "",
    'user_phone': "",
    'teacherId': "",
    'user_message': "",
    'classesId': [],
    'teacher_data': {},
    'students_dict': {},
    'status': "new"
}
# user_language = "HEB" - for future use maybe
####################################

conversation_start_time = None
logger.info(f"0 the status is::: {chm_context['status']}")
## config file loading ##
settings = Settings()

## Initialize Twilio Client ##
http_client = TwilioHttpClient(timeout=120)  # Set timeout to 120 seconds
client = Client(settings.account_sid, settings.auth_token, http_client=http_client) # Create a custom HTTP client with a specified timeout 

## Initialize DB ##
new_user_message = None
SessionFactory = get_session_factory(settings.DATABASE_URL) # This is a factory


####################### Handle application helloo!!! ##########################################
# the main function
def application(environ, start_response):


    #logger.info("in the application function:")
    session = SessionFactory()
    path = environ.get('PATH_INFO', '').lstrip('/')
    try:
        ###### 0. HTML frontend
        if path == '':
            return serve_html(start_response)

        ###### Chat API (Internal App Requests) handle all the whatsaap interactions needed ######
        elif path == 'api/chat' and environ['REQUEST_METHOD'] == 'POST':
            logger.info("4. The WhatsApp message was recognized as path == 'api/chat'!!")
            return handle_twilio_request(environ, start_response, session)

        else:
            raise ValueError(f"Unhandled path: {path}")
            
    except Exception as e:
        logger.error(f"Application error: {e}")
        start_response('500 Internal Server Error', [('Content-Type', 'application/json')])
        return [json.dumps({'status': 'error', 'message': 'Server error'}).encode('utf-8')]


##########################################################
# returns: null
# params: time_varuable : number
#         conversation_start_time : number 

# def reset_conversation(time_variable, conversation_start_time):
#     return
##########################################################
def split_message(message, max_length=1600):
    """
    Split a message into smaller parts, ensuring clean breaks.
    """
    parts = []
    while len(message) > max_length:
        split_index = message[:max_length].rfind("\n")  # Find the last line break within max_length
        if split_index == -1:  # If no line break is found, split at max_length
            split_index = max_length
        parts.append(message[:split_index].strip())  # Add the part, stripping extra spaces
        message = message[split_index:].lstrip()  # Remove the used portion and leading whitespace
    parts.append(message.strip())  # Add the remaining part
    return parts

##########################################################
'''
'''
def handle_media_messages(media_type, media_url, sms_sid):
    # Ensure media directory exists
    media_directory = "media"
    os.makedirs(media_directory, exist_ok=True)

    # Download the audio file from Twilio
    response = requests.get(media_url, auth=(settings.account_sid, settings.auth_token))
    if response.status_code != 200:
        raise Exception(f"Failed to download audio. HTTP Status: {response.status_code}")
    logger.info("media has been downloaded")
    # Save the audio file
    file_extension = media_type.split('/')[-1]  # Extract file extension
    file_name = f"{media_directory}/{sms_sid}.{file_extension}"
    with open(file_name, "wb") as audio_file:
        audio_file.write(response.content)

    logger.info(f"Audio file saved: {file_name}")
    # Convert to MP3 if necessary
    mp3_file = f"{media_directory}/{sms_sid}.mp3"
    if file_extension != "mp3":
        try:
            audio_clip = AudioFileClip(file_name, fps=16000)  # Reduce memory usage
            audio_clip.write_audiofile(mp3_file, codec="libmp3lame")
            os.remove(file_name)  # Remove original file after conversion
            logger.info(f"Converted audio to MP3: {mp3_file}")
        except Exception as e:
            raise Exception(f"Error converting audio file: {e}")
    else:
        mp3_file = file_name


    # Transcribe audio using OpenAI Whisper
    client0 = OpenAI(api_key=settings.openai_key)

    with open(mp3_file, "rb") as audio:
        transcription_response = client0.audio.transcriptions.create(
            model="whisper-1", 
            file=audio
        )
    transcribed_text = transcription_response.text.strip()
    logger.info(f"transcribed_text  = {transcribed_text}")
    if not transcribed_text:
        raise Exception("Transcription failed or returned empty text.")

    # Update user_message
    chm_context['user_message'] = transcribed_text
    logger.info(f"from new func - Transcribed audio to text: {chm_context['user_message']}")
    # Delete the MP3 file to clean up
    os.remove(mp3_file)
    logger.info(f"Deleted MP3 file: {mp3_file}")


##########################################################

##########################################################                      ##########################################################
# 1. Handles requests received via WhatsApp: parse the message and print the relevant phone number and the message to the file logs/debug.log
def handle_twilio_request(environ, start_response, session):

    content_type = environ.get('CONTENT_TYPE', '')
    content_length = int(environ.get('CONTENT_LENGTH', 0))
    request_body = environ['wsgi.input'].read(content_length).decode('utf-8') if content_length > 0 else ''

    try:
        # Parse the request data based on content type
        if content_type == 'application/json':
            parsed_data = json.loads(request_body)
            logger.debug(f"json - Parsed data: {parsed_data}")
        elif content_type == 'application/x-www-form-urlencoded':
            # for debug
            #logger.info(f"the content type is: {content_type}")
            parsed_data = {key: value[0] for key, value in parse_qs(request_body).items()}
            logger.debug(f"x-www-form-urlencoded - Parsed data: {parsed_data}")
        else:
            raise ValueError("Unsupported Content-Type")
        # Extract key data
        user_message = parsed_data.get('Body', '').strip()
        chm_context['user_message'] = user_message 
        # debug
        logger.info(f"the message from user: {chm_context['user_message']}")
        user_phone_number = parsed_data.get('From', '').replace('whatsapp:', '').strip()
        #                                       End of the getting the request info part
        user_phone_number = "0" + user_phone_number[4:]
        #user_phone_number = "0524416701" #test iris
        ##########################################################################################################
        ### NEW - handling media
        # Check for media files (audio)
        logger.info("debug1")

        media_type = parsed_data.get('MediaContentType0', '')
        media_url = parsed_data.get('MediaUrl0', '')
        sms_sid = parsed_data.get('MessageSid', '')

        if media_type.startswith('audio/'):  # Ensure we are processing audio media
            try:
                logger.info(f"Audio message detected from {user_phone_number}")
                handle_media_messages(media_type, media_url, sms_sid)
                logger.info(f"the user's message: {user_message} and teh  chm_context['user_message'] = {chm_context['user_message']}")

            except Exception as e:
                logger.error(f"Error processing audio message: {e}")
                chm_context['user_message'] = "I couldn't process your audio message."

        if not chm_context['user_message'] or not user_phone_number:
            logger.warning("Missing user message or phone number.")
            start_response('400 Bad Request', [('Content-Type', 'application/json')])
            return [json.dumps({'status': 'error', 'message': 'Invalid request data'}).encode('utf-8')]
        #############
        # for debug only 
        # 1 Retrieve conversation history
        conversation_history = restore(user_phone_number) #restore(user_phone_number)
        #logger.info("called save_context before the prompts job")
        ##
        is_registered = check_registration_status(user_phone_number, settings)
        #logger.info("before the first call to get_context_field")
        chm_context['status'] = get_context_field(user_phone_number, "status")
        # 3 Update chm_context
        chm_context['user_phone'] = user_phone_number
        chm_context['thread_store'] = conversation_history + f"\nUser: {chm_context['user_message']}"
        
        status = get_context_field(user_phone_number, "status")
        if status is None:
            logger.info(f"No status found for {user_phone_number}. Creating chm_context file.")
            save_context(user_phone_number, chm_context)
        else:
            logger.info(f"Loaded status for {user_phone_number}: {status}")
        # 2. Determine the correct prompt based on the conversation history
        static_prompt = settings.prompt_static 
        prompt = settings.prompt_static
        if is_registered: 
            chm_context["status"] = get_context_field(user_phone_number, "status")
            logger.info("for debug only")
            if chm_context['status'] == "new":
                logger.info(f"the status MUST be new, an it is: {chm_context['status']} ")
                #2
                get_teacher_data(user_phone_number, settings, chm_context) # build the user's special prompt according to the relevant data about them
                logger.info(f"the teacher data: {chm_context['teacher_data']}")
                prompt = settings.prompt_new_reg #"./prompts/chess_magic_promps/prompt_new_reg.txt"
                # ask the user what kind of help of they need
                place_of_text = "start the conversation with a greeting line for the teacher:"
                new_text = chm_context['teacher_name']
                change_in_file(prompt, new_text, place_of_text)
                chm_context['status'] = "returning0"
                save_context(user_phone_number, chm_context) # save chm_context after update

            elif chm_context['status'] == "returning0":
                logger.info(f"the status MUST be returning0, an it is: {chm_context['status']} ")
                #3
                chm_context["classesId"] = get_context_field(user_phone_number, "classesId")
                chm_context["teacherId"] = get_context_field(user_phone_number, "teacherId")
                chm_context["teacher_data"] = get_context_field(user_phone_number,"teacher_data")
                save_context(user_phone_number, chm_context) # save after update
                user_prompt = "./files/data_" + user_phone_number + "/thread_data.txt"
##########################
                prompt = user_prompt
                change_in_file(user_prompt, chm_context['user_message'], ": you got this message from the teacher:") 
                ## NEW 
                #chm_context['status'] = "returning0"
                
                logger.info(f"the status MUST be returning0, an it is: {chm_context['status']} ")
        else:
            #1
            chm_context['status'] = "unreg"
            save_context(user_phone_number, chm_context)
            prompt = settings.prompt_new_unreg
            logger.info(f"1 the status is::::: {chm_context['status']}")
#$%$%$%$$%$%$%$$%$%$%$$%$%$%$$%$%$%$$%$%$%$$%$%$%$      
        ai_response = run(
            thread_store=chm_context['thread_store'],
            openai_key=settings.openai_key,
            assistant_id=settings.ANGELINA_ASSIST,
            prompt=prompt,
            static=static_prompt,
            background_data=chm_context.get('teacher_data', ''),
            message=chm_context['user_message']
        )

        # detect if the ai_response contains the string: "#SENDING_HELP"
        if "#SENDING_HELP" in ai_response:
            logger.info(f"here is the ai response: {ai_response}")
            #get student id
            logger.info("for debug only")
            student_id = re.search(r'\d+', ai_response)
            if student_id:
                student_id = int(student_id.group())
            logger.info(f"id from ai response = {student_id}")
             
             # TODO: go over the students_dict array and get sure that the name is correct and there is a suitable ID for it,
             # and just then send a help
            payload_message = run(
                thread_store="",
                openai_key=settings.openai_key,
                assistant_id=settings.ANGELINA_ASSIST,
                prompt= settings.prompt_help_student,
                static=settings.prompt_help_student,
                background_data=chm_context.get('teacher_data', ''),
                message=""
            )
            # add the payload_message to the conversation history
            chm_context['thread_store'] += f"\n{payload_message}\n"
            save_txt_in_drct(chm_context['thread_store'], chm_context['user_phone'], "thread_conv_history")
            # debug
            logger.info(f"the message to be sent to the student: {payload_message}")
            send_student_help(chm_context['teacherId'], student_id, payload_message)
            # debug
            logger.info(f"--->>> after the ai generated response that should be sent to the student")
        if not ai_response:
            ai_response = "I'm sorry, I couldn't understand your message. Can you rephrase?"

        # 5 Update and save conversation history
        chm_context['thread_store'] += f"\n{ai_response}\n"
        save_txt_in_drct(chm_context['thread_store'], chm_context['user_phone'], "thread_conv_history")
        # 6 Store user message in the database
        store_user_message(session, message_type="NORMAL", context = chm_context, results=ai_response)
        session.commit()
        # 7 Send WhatsApp response
        message_parts = split_message(ai_response)
        send_to = "+972" + user_phone_number[1:]
        for part in message_parts:
            send_whatsapp_message(client, f'whatsapp:{send_to}', part, from_number=settings.from_whatsapp_number)

        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps({'status': 'success', 'message': ai_response}).encode('utf-8')]
    
    except Exception as e:
        response = handle_exception(e, start_response)
        return response

##########################################################


##########################################################


def send_student_help(teacherId, studentId, payload_message):
    url = f"https://api-qa.chess-m.com/angelina/student-help?teacherId={teacherId}&studentId={studentId}"
    headers = {"X-Api-Key": settings.chm_api_key}

    #logger.info(f"Sending student help request. Payload: {payload_message}")
    try:
        # Make the POST request to the API
        response = requests.post(url, json=payload_message, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        # Parse and return the API response
        api_response = response.json()
        logger.info(f"for debug only:: the api_response is: {api_response}")
        return {
            "result": api_response.get("result"),
            "data": api_response.get("data"),
            "error": api_response.get("error"),
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred during student help request: {e}")
        return {
            "result": False,
            "data": None,
            "error": str(e),
        }

##########################################################