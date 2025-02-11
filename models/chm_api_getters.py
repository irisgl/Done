import os
import requests
import json
from models.assistant import change_in_file, save_txt_in_drct
from models.chm_config_loader import Settings
from models.context_manage import save_context
import logging


# Initialize logger
##########################################################################
# Create logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('/home/donehr2ai/logs/debug_chm.log', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(file_handler)
##########################################################################



def get_teacher_data(phone, settings, context):
    
    #api_url = f"https://api-qa.chess-m.com/angelina/teacher?phone={phone}"
    logger.info(f"{settings.techer_data_url}{phone} ")
    api_url = f"{settings.techer_data_url}{phone}"
    headers = {"X-Api-Key": settings.chm_api_key}  
    
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        response.encoding = "utf-8" 
        response.raise_for_status()
        # Fetch the teacher data
        teacher_data = response.json().get('data', {})
        
        # Organize the data into a structured format
        formatted_data = {
            "result": True,
            "error": "",
            "data": {
                "id": teacher_data.get("id", 0),
                "fullName": teacher_data.get("fullName", ""),
                "schools": [
                    {
                        "id": school.get("id", 0),
                        "name": school.get("name", ""),
                        "country": school.get("country", ""),
                        "state": school.get("state", ""),
                        "city": school.get("city", ""),
                        "address": school.get("address", ""),
                        "phone": school.get("phone", ""),
                        "classes": [
                            {
                                "id": cls.get("id", 0),
                                "name": cls.get("name", "")
                            } for cls in school.get("classes", [])
                        ]
                    } for school in teacher_data.get("schools", [])
                ]
            }
        }
        ####
        #teacher_data_string = json.dumps(formatted_data["data"], ensure_ascii=False, indent=4)
        # 
        save_txt_in_drct(":", phone, "thread_data")
        file_path_data = './files/data_'+ phone + "/thread_data.txt"
        ### copy the geniric_prompt
        with open(settings.prompt_returning, "r", encoding="utf-8") as file:
            generic_prompt = file.read()
        change_in_file(file_path_data,generic_prompt, ":") # in the file "file_path_data" where you would find ":" paste the content of the file "generic_prompt"

        # Update context variables
        context["teacherId"] = formatted_data["data"]["id"]
        context["teacher_name"] = formatted_data["data"]["fullName"]
        context["classesId"] = [
            cls["id"]
            for school in formatted_data["data"]["schools"]
            for cls in school.get("classes", [])
        ]
        context["teacher_data"] = formatted_data["data"]
        logger.info(f"we are in the 'new' status, so the teacher data is: {context['teacher_data']}")
        save_context(phone, context)

        ## add class data:
######################

        class_data_list = []  # Store the combined class data as a list
##############################
        for cls_id in context['classesId']:
            single_class_data, filtered_data = get_class_data(context['teacherId'], cls_id, settings, phone, context)
            logger.info(f"single_class_data: {single_class_data}")

            if single_class_data['result']:  # Check if the API call was successful
                class_data_list.append(filtered_data['data'])  # Save filtered data for file storage

                # 🔹 Insert class data inside the correct school in `formatted_data`
                class_id = single_class_data["data"]["id"]
                for school in formatted_data["data"]["schools"]:
                    for cls in school["classes"]:
                        if cls["id"] == class_id:  
                            # Found the matching class, add full class data
                            cls["students"] = single_class_data["data"]["students"]  
                            break  # Stop searching once matched

        logger.info(f"Updated formatted_data: {formatted_data['data']}")

        # for cls_id in context['classesId']:
        #     single_class_data, filtered_data = get_class_data(context['teacherId'], cls_id, settings, phone, context)
        #     logger.info(f"single_class_data: {single_class_data}")
        #     if single_class_data['result']:  # Check if the API call was successful
        #         #class_data_list.append(single_class_data['data'])  # Append only the 'data' part
        #         class_data_list.append(filtered_data)  # Append the entire 'single_class_data' dictionary
        #         ######## how to append single_class_data['data'] to formatted_data["data"]??
        
        logger.info(f"the new formated tada: {formatted_data['data']}")
        class_formatted_data = json.dumps(class_data_list, ensure_ascii=False, indent=4)
        # Write it back to the file at the specific location
        change_in_file(file_path_data, class_formatted_data, "class_data:")

######################
        #return {"status": "success", "data": formatted_data["data"]}
        return formatted_data["data"]  #formatted_data

    except requests.RequestException as e:
        logger.error(f"Failed to fetch teacher data: {e}")
        return {'status': 'error', 'message': str(e)}


#######################################################################################
#%%%%%%%%%%%%%%%%%%%%%%%%% helper func #2 - Get Class Data and Save Data to Database (JSON file)
def get_class_data(teacher_id, class_id, settings, phone, context):
    api_url = f"https://api-qa.chess-m.com/angelina/class?teacherId={teacher_id}&classId={class_id}"
    headers = {"X-Api-Key": settings.chm_api_key}  

    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Fetch the class data
        class_data = response.json().get('data', {})
        logger.info(f"the class_data from get classes : {class_data}")
        new_students = {
            student.get("id", 0): student.get("fullName", "").lower()
            for student in class_data.get("students", [])
        }
        #context['students_dict'].update(new_students)
        context['students_dict'] = new_students
        #logger.info(f"the students_dict dedictionary from get classes : {new_students}")
        save_context(phone, context)


        # Format the response
        formatted_data = {
            "result": True,
            "error": "",
            "data": {
                "id": class_data.get("id", 0),
                "name": class_data.get("name", ""),
                "students": [
                    {
                        "id": student.get("id", 0),
                        "fullName": student.get("fullName", ""),
                        "isOnline": student.get("isOnline", False),
                        "lastHeartbeat": student.get("lastHeartbeat", {
                            "year": 0, "month": 0, "day": 0,
                            "hour": 0, "minute": 0, "second": 0
                        }),
                        "helpRequested": student.get("helpRequested", False),
                        "currentLesson": student.get("currentLesson", 0),
                        "currentLessonId": student.get("currentLessonId", 0),
                        "currentChapter": student.get("currentChapter", 0),
                        "currentChapterId": student.get("currentChapterId", 0),
                        "currentChallenge": student.get("currentChallenge", 0),
                        "currentChallengeId": student.get("currentChallengeId", 0),
                        "currentChallengeName": student.get("currentChallengeName", {
                            "additionalProp1": "", 
                            "additionalProp2": "", 
                            "additionalProp3": ""
                        }),
                        "lessonProgress": student.get("lessonProgress", 0),
                        "overallScore": student.get("overallScore", 0),
                        "points": student.get("points", 0),
                        "rankingPoints": student.get("rankingPoints", 0),
                        "coins": student.get("coins", 0),
                        "solutionKeys": student.get("solutionKeys", 0),
                        "currentLessonName": student.get("currentLessonName", {
                            "additionalProp1": "", 
                            "additionalProp2": "", 
                            "additionalProp3": ""
                        }),
                        "currentChapterName": student.get("currentChapterName", {
                            "additionalProp1": "", 
                            "additionalProp2": "", 
                            "additionalProp3": ""
                        }),
                        "maxLesson": student.get("maxLesson", 0),
                        "maxLessonId": student.get("maxLessonId", 0),
                        "maxLessonName": student.get("maxLessonName", {
                            "additionalProp1": "", 
                            "additionalProp2": "", 
                            "additionalProp3": ""
                        }),
                        "maxChapter": student.get("maxChapter", 0),
                        "maxChapterId": student.get("maxChapterId", 0),
                        "maxChapterName": student.get("maxChapterName", {
                            "additionalProp1": "", 
                            "additionalProp2": "", 
                            "additionalProp3": ""
                        }),
                        "maxChallenge": student.get("maxChallenge", 0),
                        "maxChallengeId": student.get("maxChallengeId", 0),
                        "maxChallengeName": student.get("maxChallengeName", {
                            "additionalProp1": "", 
                            "additionalProp2": "", 
                            "additionalProp3": ""
                        })
                    } for student in class_data.get("students", [])
                ]
            }
        }

        # Update context with student IDs
        context['studentsId'] = [student["id"] for student in class_data.get("students", []) if "id" in student]
        save_context(phone, context)

        filtered_data = {
            "result": True,
            "error": "",
            "data": {
                "id": class_data.get("id", 0),
                "name": class_data.get("name", ""),
                "students": [
                    {
                        "id": student.get("id", 0),
                        "fullName": student.get("fullName", ""),
                        "isOnline": student.get("isOnline", False),
                        "lastHeartbeat": student.get("lastHeartbeat", {
                            "year": 0, "month": 0, "day": 0,
                            "hour": 0, "minute": 0, "second": 0
                        }),
                        "helpRequested": student.get("helpRequested", False)
                    } for student in class_data.get("students", [])
                ]
            }
        }

        # Convert to JSON format
        #filtered_data_json = json.dumps(filtered_data, ensure_ascii=False, indent=4)
        logger.info(f"the filtered dta is: {filtered_data}")


    ############################
    # update context:
        context['studentsId'] = [
            int(student.get("id", 0))
            for student in class_data.get("students", [])
            if "id" in student
        ]
        #logger.info(f"the array of context['studentsId']: {context['studentsId']}")
        # TODO go over this again !!!!!!!
        #logger.info(f"students id is: {context['studentsId']}")
    # ############################
        # Build filtered_data_str that contains only the picked parameters for each student.
        # subset_keys = ["id", "fullName", "isOnline", "lastHeartbeat", "helpRequested"]
        # filtered_data_lines = []
        # for student in formatted_data['data']['students']:
        #     subset = {k: student[k] for k in subset_keys if k in student}
        #     filtered_data_lines.append(json.dumps(subset, ensure_ascii=False))
        # filtered_data_str = "\n".join(filtered_data_lines)
        # logger.info(f"New data: {filtered_data_str}")

    # ############################
        logger.info(f"formated data from class {formatted_data['data']}")
        return formatted_data, filtered_data
    except requests.RequestException as e:
        logger.error(f"Failed to fetch class data: {e}")
        return {"result": False, "error": str(e), "data": {}}
    # ############################


#######################################################################################
def get_student_data(teacher_id, student_id, settings):
    api_url = f"https://api-qa.chess-m.com/angelina/student?teacherId={teacher_id}&studentId={student_id}"
    headers = {"X-Api-Key": settings.chm_api_key}
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Extract student data
        student_data = response.json().get('data', {})
        
        # Format the response
        formatted_data = {
            "result": True,
            "data": {
                "id": student_data.get("id", 0),
                "fullName": student_data.get("fullName", ""),
                "isOnline": student_data.get("isOnline", False),
                "lastHeartbeat": student_data.get("lastHeartbeat", {
                    "year": 0, "month": 0, "day": 0,
                    "hour": 0, "minute": 0, "second": 0
                }),
                "helpRequested": student_data.get("helpRequested", False),
                "currentLesson": student_data.get("currentLesson", 0),
                "currentLessonId": student_data.get("currentLessonId", 0),
                "currentLessonName": student_data.get("currentLessonName", {}),
                "currentChapter": student_data.get("currentChapter", 0),
                "currentChapterId": student_data.get("currentChapterId", 0),
                "currentChapterName": student_data.get("currentChapterName", {}),
                "currentChallenge": student_data.get("currentChallenge", 0),
                "currentChallengeId": student_data.get("currentChallengeId", 0),
                "currentChallengeName": student_data.get("currentChallengeName", {}),
                "lessonProgress": student_data.get("lessonProgress", 0),
                "overallScore": student_data.get("overallScore", 0),
                "points": student_data.get("points", 0),
                "rankingPoints": student_data.get("rankingPoints", 0),
                "coins": student_data.get("coins", 0),
                "solutionKeys": student_data.get("solutionKeys", 0),
                "maxLesson": student_data.get("maxLesson", 0),
                "maxLessonId": student_data.get("maxLessonId", 0),
                "maxLessonName": student_data.get("maxLessonName", {}),
                "maxChapter": student_data.get("maxChapter", 0),
                "maxChapterId": student_data.get("maxChapterId", 0),
                "maxChapterName": student_data.get("maxChapterName", {}),
                "maxChallenge": student_data.get("maxChallenge", 0),
                "maxChallengeId": student_data.get("maxChallengeId", 0),
                "maxChallengeName": student_data.get("maxChallengeName", {})
            },
            "error": None
        }
        return {"status": "success", "data": formatted_data}
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch student data: {e}")
        return {
            "status": "error",
            "data": {
                "result": False,
                "data": None,
                "error": str(e)
            }
        }

#######################################################################################
def check_registration_status(phone_number, settings):
    
    #api_key = settings.chm_api_key
    url = f"https://api-qa.chess-m.com/angelina/teacher?phone={phone_number}"
    headers = {"X-Api-Key": settings.chm_api_key}
    params = {"phone": phone_number}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 401:
        logger.error(f"API request failed with status code: 401")
        return None
    if response.status_code != 200:
        logger.error(f"API request failed with status code: {response.status_code}")
        return None
    try:
        data = response.json()
        if data.get("result"):
            return data['data']  # or process the data as needed
        else:
            logger.info(f"No teacher data found for phone number: {phone_number}")
            return None
    except ValueError:
        logger.error(f"Error parsing response: {response.text}")
        return None
    
