import os
import json

'''
CONTEXT MODIFICATIONS:
'''
def save_context(user_phone, context):
    try:
        '''
        os.makedirs("./files"+{user_phone}, exist_ok=True)
        file_path = f"./files/"+{user_phone} + "context.json"
        '''
        # create a new directory
        os.makedirs(f"./files/data_{user_phone}", exist_ok=True)
        file_path = f"./files/data_{user_phone}/context.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving context for {user_phone}: {e}")

###############################
def get_context_field(user_phone, field_name):
    """
    Load a specific field from the user's context JSON file.
    If the file or field does not exist, initialize the file with a default context.
    """
    # file_path = f"./files/context_{user_phone}.json"
    os.makedirs(f"./files/data_{user_phone}", exist_ok=True) # if no such directory exists, creat it
    file_path = f"./files/data_{user_phone}/context.json"
    default_context = {
        'thread_store': "",
       'teacher_name': "",
        'user_phone': user_phone,
        'teacherId': "",
        'user_message': "",
        'classesId': [],
        'teacher_data': {},
        'status': "new"
    }

    if not os.path.exists(file_path):
        print(f"Context file not found for {user_phone}. Creating with default values.")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_context, f, ensure_ascii=False, indent=4)
        return default_context.get(field_name, None)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            context = json.load(f)
        return context.get(field_name, None)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON file for user {user_phone}: {e}")
        return None