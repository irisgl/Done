# chm_config_loader.py
import json

class Settings:
    def __init__(self, config_path='./config/config_chm.json'):
        self.config = self._load_config(config_path)
        self._load_settings()

    def _load_config(self, file_path):
        try:
            with open(file_path, 'r') as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {file_path} not found.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing the configuration file: {str(e)}")

    def _load_settings(self):
        settings = self.config['settings']
        self.check_user_phone = settings['check_user_phone']
        self.approved_numbers = settings['approved_numbers']
        self.prompt = settings['prompt']
        self.prompt_new_reg = settings['prompt_new_reg']
        self.prompt_new_unreg = settings['prompt_new_unreg']
        self.prompt_returning = settings['prompt_returning']
        self.prompt_help_student = settings['prompt_help_student']
        self.prompt_goodbye = settings['prompt_goodbye']
        self.prompt_static = settings['prompt_static']
        self.save_all_data = settings['save_all_data']
        self.DEBUG_MODE = settings['DEBUG_MODE']
        self.COMPLETION_MESSAGE = settings['COMPLETION_MESSAGE']
        self.BOSS_TRIGER = settings['BOSS_TRIGER']
        self.END_BOSS_TRIGER = settings['END_BOSS_TRIGER']
        self.BOSS_PHONE = settings['manager_phone_number']
        self.TEST_PHONE = settings['user_phone_number']
        self.ANGELINA_LANG = settings['angelina_lang']
        self.ANGELINA_ASSIST = settings['angelina_assistant'] if self.ANGELINA_LANG != "HEB" else settings['angelina_assistant_heb']
        self.username = settings['username']
        self.app_password = settings['app_password']
        self.base_url = settings['base_url']
        self.site_url = settings['site_url']
        self.consumer_key = settings['consumer_key']
        self.consumer_secret = settings['consumer_secret']
        self.PERSONAL_ACCESS_TOKEN = settings['personal_access_token']
        self.WORKSPACE_ID = settings['workspace_id']
        self.PROJECT_ID = settings['project_id']
        self.ASSAGNEE = settings['ASSAGNEE']
        self.account_sid = settings['account_sid']
        self.auth_token = settings['auth_token']
        self.openai_key = settings['openai_key']
        self.from_whatsapp_number = settings['from_whatsapp_number']
        self.to_whatsapp_boss = f'whatsapp:{self.BOSS_PHONE}'
        self.to_whatsapp_from_BOSS_number = f'whatsapp:{self.TEST_PHONE}'
        self.DATABASE_URL = settings['DATABASE_URL']
        self.TASK_READY = settings['TASK_READY']
        self.CLEAR_THREAD = settings['CLEAR_THREAD']
        self.ALWAYS_NEW = settings['ALWAYS_NEW']
        self.chm_api_key = settings["CHESS_MAGIC_API_KEY"]
        self.techer_data_url = settings["techer_data_url"]
