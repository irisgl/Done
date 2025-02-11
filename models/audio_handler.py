import requests
from requests.auth import HTTPBasicAuth
from moviepy.editor import AudioFileClip
import os
from openai import OpenAI


whisper_model = "whisper-1"

def download_media_convert_to_text(url, account_sid, auth_token, openai_key, ANGELINA_LANG):
    print("GOT AN AUDIO MESSAGE")
    try:
        ###### Download json file information #####
        url = f"https://api.twilio.com{url}"
        response = requests.get(url, auth=HTTPBasicAuth(account_sid, auth_token))
        print(f"Downloading audio from: {url}")
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content[:100]}")  # Print the first 100 bytes

        media_info = {}
        if response.status_code == 200:
            media_info = response.json()

        media_directory = 'media'

        # Ensure the media directory exists, create it if it does not
        if not os.path.exists(media_directory):
            os.makedirs(media_directory)

        #### Download audio file from Twilio MediaURL #####
        media_url = url.replace('.json', '')
        response = requests.get(media_url, auth=HTTPBasicAuth(account_sid, auth_token))

        if response.status_code == 200:
            # Extract file extension from content type
            extension = media_info["content_type"].split('/')[-1]  
            message_sid = media_info["sid"]

            file_name = f'media/{message_sid}.{extension}'
            output_file = f"media/{message_sid}.mp3"

            # Save the media file to disk
            with open(file_name, 'wb') as f:
                f.write(response.content)
            
            print(f"Converting file: {file_name} to MP3")
            print(f"Output file: {output_file}")

            # Convert OGG file into mp3 file
            audio_clip = AudioFileClip(file_name)
            audio_clip.write_audiofile(output_file, codec='libmp3lame')

            # Check if the MP3 file was created
            if not os.path.exists(output_file):
                print(f"Error: {output_file} not created.")
                return "", ""

            # Delete original ogg file after conversion
            os.remove(file_name)

            ##### Configure OpenAI object #####
            print(f"Sending {output_file} to OpenAI Whisper for transcription")
            print(f"File size: {os.path.getsize(output_file)} bytes")

            openai_client = OpenAI(api_key=openai_key)
            audio_file = open(output_file, "rb")

            # Perform transcription via OpenAI Whisper
            translation = openai_client.audio.translations.create(
                model=whisper_model, 
                file=audio_file
            )

            # Check if translation result exists
            if not translation or not hasattr(translation, 'text'):
                print(f"Error: No transcription result returned.")
                return "", ""

            print(f"Transcription result: {translation.text}")

            if ANGELINA_LANG == "HEB":
                # If language is Hebrew, send the translation to GPT-4 for completion
                response = openai_client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[{"role": "system", "content": "Convert text into hebrew"}, 
                              {"role": "user", "content": translation.text}]
                )  
                return response.choices[0].message.content, message_sid
            else:
                return translation.text, message_sid
        else:
            print(f"Error downloading audio file, status code: {response.status_code}")
            return "", ""
    
    except Exception as e:
        print(f'Error: {e}')
        return "", ""



