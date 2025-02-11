import requests
from PIL import Image
from io import BytesIO
from moviepy.editor import AudioFileClip
import os
from requests.auth import HTTPBasicAuth

def process_image(url, save_path, account_sid, auth_token):
    try:

        url = f"https://api.twilio.com{url}"
    
        response = requests.get(url, auth=HTTPBasicAuth(account_sid, auth_token))
            
        media_info = {}
        if response.status_code == 200:
            media_info = response.json()
    
        media_directory = 'media'
    
        # Ensure the media directory exists, create it if it does not
        if not os.path.exists(media_directory):
            os.makedirs(media_directory)
    
        #### Download audio file from Twillio MediaURL #####
        media_url = url.replace('.json','')
        response = requests.get(media_url, auth=HTTPBasicAuth(account_sid, auth_token))
        
        if response.status_code == 200:
            
            extension = media_info["content_type"].split('/')[-1]  # Extract file extension from content type
            message_sid = media_info["sid"]
    
            file_name = f'media/{message_sid}.{extension}'
            output_file = f"media/{message_sid}.jpeg"
    
            with open(file_name, 'wb') as f:
                f.write(response.content)
            print("iris11")
            '''##### Convert OGG file into jpg file ##### 
            audio_clip = AudioFileClip(file_name)
            
            audio_clip.write_audiofile(output_file, codec='libmp3lame')
    
            # Delete ogg file
            os.remove(file_name)'''
            
            return output_file
            
        else:
            print("iris")
            return ""

    except Exception as e:
        print(f'Error: {e}')
        return ""