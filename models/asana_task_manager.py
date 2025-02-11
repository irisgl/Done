import asana
import requests

class AsanaTaskManager:
    def __init__(self, personal_access_token):
        self.client = asana.Client.access_token(personal_access_token)
    
    def create_task(self, workspace_id, project_id, task_name, due_date, assignee, task_notes=''):
        """Create a task in Asana."""
        task_data = {
            "name": task_name,
            "notes": task_notes,
            "projects": [project_id],
            "workspace": workspace_id,
            "assignee": assignee,
            "due_on": due_date,
        }
        result = self.client.tasks.create_task(task_data, opt_pretty=True)
        return result
    
    def attach_file_to_task(self, task_id, file_path):
        url = f'https://app.asana.com/api/1.0/tasks/{task_id}/attachments'
        headers = {'Authorization': f'Bearer {self.client.access_token}'}

        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(url, headers=headers, files=files)
                response.raise_for_status()
                print(f"File successfully attached to task {task_id}")
                return response.json()
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except requests.RequestException as e:
            if e.response is not None:
                print(f"Failed to attach file: {e.response.status_code} {e.response.text}")
            else:
                print(f"Failed to attach file: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            
            
    def test_auth(self):
        url = 'https://app.asana.com/api/1.0/users/me'
        headers = {'Authorization': f'Bearer {self.client.access_token}'}
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    
        return None