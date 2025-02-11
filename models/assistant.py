from openai import OpenAI
#import openai.api_requestor as req
import time
import os
import json
from datetime import datetime

import logging

#req.TIMEOUT_SECS=30
# Initialize logger
##########################################################################
# Create logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create a single file handler with UTF-8 encoding
file_handler = logging.FileHandler('/home/donehr2ai/logs/debug1.log', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(file_handler)
##########################################################################



# Ensure the file and directory exists
def ensure_directory_exists(file_path):
       # Extract the directory part from the file_path
       directory = os.path.dirname(file_path)
    
       # Check if the directory exists, and create it if it does not
       if not os.path.exists(directory):
           os.makedirs(directory)  # This creates the directory and any intermediate directories
       if not os.path.exists(file_path):
            with open(file_path, 'a') as file:
                pass  # You don't need to do anything, just opening in 'a' mode ensures the file exists.

# orginal restore           
# # Restore data from file
# def restore(user_phone):
#         file_path = './files/thread_conv_history'
#         file_path=file_path+user_phone+".txt"
#         ensure_directory_exists(file_path)
#         with open(file_path, 'r', encoding='utf-8') as file:
#              thread_store = file.read()
#         return(thread_store)
        
# Restore data from file
def restore(user_phone):
        file_path = './files/data_'+ user_phone + "/thread_conv_history"
        file_path=file_path+".txt"
        ensure_directory_exists(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
             thread_store = file.read()
        return(thread_store)
        
# Save data to file 
def save_txt(thread_store, user_phone, file_path):
        #file_path = './files/thread_conv_history'
        file_path=file_path+user_phone+".txt"
        ensure_directory_exists(file_path)
        with open(file_path, 'w', encoding='utf-8') as file:
             file.write(thread_store)
        return
######### Save data to txt file as file_name
def save_txt_new(thread_store,user_phone, file_name):
        file_path = './files/thread_'
        file_path=file_path + file_name + user_phone + ".txt"
        ensure_directory_exists(file_path)
        with open(file_path, 'w', encoding='utf-8') as file:
             file.write(thread_store)
        return

#########
def save_txt_in_drct(thread_store, user_phone, file_name):
    file_path = f"./files/data_{user_phone}/{file_name}.txt"
    print("in the save in direct")
    ensure_directory_exists(file_path)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(thread_store)


######### Save data to JSON file 
def save_json(thread_store,user_phone):
        file_path = './files/thread_data'
        file_path=file_path + user_phone + ".json"
        ensure_directory_exists(file_path)
        with open(file_path, 'w', encoding='utf-8') as file:
             file.write(thread_store)
        return

######### Save data to JSON file as file_name
def save_json_new(thread_store,user_phone, file_name):
        file_path = './files/thread_'
        file_path=file_path + file_name + user_phone + ".json"
        ensure_directory_exists(file_path)
        with open(file_path, 'w', encoding='utf-8') as file:
             file.write(thread_store)
        return

######### Append data to file 
def update_json(thread_store,user_phone):
        file_path = './files/thread_data'
        file_path=file_path + user_phone + ".json"
        ensure_directory_exists(file_path)
        with open(file_path, 'a', encoding='utf-8') as file:
             file.write("\n" + thread_store)
        return
    
# Read config file
def read_config(file_path):
    ensure_directory_exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config
    
# Read file
def read_file(file_path):
    
    prompt=""
    if file_path != "":
        with open(file_path, 'r', encoding='utf-8') as file:
            prompt = file.read()
    return prompt
    
def add_message(conversation_history, role, content):
    conversation_history.append({"role": role, "content": content})

# Function to start a new conversation session
def start_new_session(assistant):
    current_date = datetime.now().isoformat()[:10]
    # פרומפט הכולל את התאריך הנוכחי
    prompt = f"today is {current_date} give me relevant data acording to this date"
    print(prompt)
    assistant=prompt+assistant
    # Start with a system message that includes the assistant ID
    return [{"role": "system", "content": assistant}]

# Run  
def run(thread_store,openai_key,assistant_id,prompt,static,background_data,message):
    try:

        print("iris")
        client = OpenAI(api_key=openai_key)
        # קבלת התאריך הנוכחי
        if prompt == "NO":
            assistant = client.beta.assistants.retrieve(assistant_id)
            conversation_history = start_new_session(assistant.instructions)
        else:
            prompt = read_file(static) + read_file(prompt)
            #prompt=read_file(static)+prompt
            conversation_history = start_new_session(prompt)

        add_message(conversation_history, "user", json.dumps(background_data))
        add_message(conversation_history, "user", thread_store)
        add_message(conversation_history, "system", message)
        
        #print(f"{message}")
        logger.error("iris0")
        logger.error(f"len: {len (str(conversation_history))} ")
        logger.error(f"history: {str(conversation_history)} ")
        thread = client.chat.completions.create(
        model="gpt-4o-mini",
            messages=conversation_history,
            max_tokens=16000,
            timeout= 120
        )
        string_length = len(thread_store)
        logger.error("iris1")
        # Return result 
        results = thread.choices[0].message.content.strip()
        logger.error(f"result: {results} ")
        print(f"Prompt size: {len(prompt)} characters")

        results = thread.choices[0].message.content.strip()
        return results
    except ValueError as e:
        print(f"ValueError: {e}")
        logger.error(f"ValueError: {e}")
        return "Sorry, I couldn't process your request due to its size. Can you simplify it?"
    except Exception as e:
        print(f"Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}")
        return "An unexpected error occurred. Please try again."

######################################################## NEW Run  
# send string to tha AI
def run_new(thread_store, openai_key, assistant_id, prompt, message):
  try:

    client = OpenAI(api_key=openai_key)
    conversation_history = start_new_session(prompt)

    add_message(conversation_history, "user", thread_store)
    add_message(conversation_history, "system", message)

    thread = client.chat.completions.create(
      model="gpt-4o-mini",
        messages=conversation_history,
        max_tokens=1500,
        timeout=120
    )
    #string_length = len(thread_store)
    # Return result 
    results = thread.choices[0].message.content.strip()
    # Ensure the result is encoded in UTF-8
    results = results.encode('utf-8').decode('utf-8')
    
    return (results)
  except Exception as e:
                    print(f'Error: {e}')
                    return (f'Error: {e}')  
                    
#######################################################################
 #  NEW FUNCTIONS FOR CHESS MAGIC
def handle_exception(e, start_response):
    """Handles different types of exceptions and returns appropriate responses."""
    if isinstance(e, json.JSONDecodeError):
        logger.error(f"JSON decoding failed: {e}")
        status = '400 Bad Request'
        message = 'Invalid JSON'
    elif isinstance(e, ValueError):
        logger.error(f"ValueError: {e}")
        status = '415 Unsupported Media Type'
        message = str(e)
    else:
        logger.error(f"Unexpected error: {e}")
        status = '500 Internal Server Error'
        message = 'Server error'

    start_response(status, [('Content-Type', 'application/json')])
    response_body = json.dumps({'status': 'error', 'message': message}).encode('utf-8')
    return [response_body]
    

######################
def change_in_file(file_name, new_text, place_of_text):
    if not isinstance(place_of_text, str):
        raise TypeError(f"place_of_text must be a string, got {type(place_of_text)} instead")

    # Read the file
    with open(file_name, 'r', encoding='utf-8') as opened_file:
        lines = opened_file.readlines()
    # Replace the line
    for i, line in enumerate(lines):
        if place_of_text in line:
            lines[i] = f"{place_of_text} {new_text}\n"
    # Write the file
    with open(file_name, 'w', encoding='utf-8') as opened_file:
        opened_file.writelines(lines)
######################
def change_in_file_simple(file_name, new_text, place_of_text):
    with open(file_name, 'r') as opened_file:
        lines = opened_file.readlines()
    for i, line in enumerate(lines):
        if place_of_text in line:
            lines[i] = place_of_text + new_text + '\n'
    with open(file_name, 'w') as opened_file:
        opened_file.writelines(lines)




    

    