import json
import os
import time
#from assistant import * 
#ensure_directory_exists

# context_modify.py


# Save context to file
def save_context(user_phone, context):
    file_path = './files/context_'
    file_path = file_path + user_phone + ".json"
    
    #ensure_directory_exists
    #########################
    directory = os.path.dirname(file_path)
   # Check if the directory exists, and create it if it does not
    if not os.path.exists(directory):
        os.makedirs(directory)  # This creates the directory and any intermediate directories
    if not os.path.exists(file_path):
        with open(file_path, 'a') as file:
            pass  # You don't need to do anything, just opening in 'a' mode ensures the file exists.
    #########################
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(context, file)
    return


# Load context from file
def load_context(user_phone):
    file_path = './files/context_'
    file_path = file_path + user_phone + ".json"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return None


# Check if context exists for user
def context_exists(user_phone):
    file_path = './files/context_'
    file_path = file_path + user_phone + ".json"
    return os.path.exists(file_path)

    
def update_context_field(user_phone, field_name, new_value):
    context = load_context(user_phone)
    if context:
        context[field_name] = new_value
        save_json(json.dumps(context), user_phone)
    else:
        print("Context does not exist for user")
    
