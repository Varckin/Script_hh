import logging
import requests
import webbrowser
from urllib.parse import urlencode

from json_work import current_path, json_reader, json_write
from logger import script_logger


logger = logging.getLogger('Script')
logger.setLevel(logging.INFO)
logger.addHandler(script_logger)


class Resume_updater():
    def __init__(self, user: str) -> None:
        app_config: dict = json_reader(file_name=f"{current_path}/resources/app_config.json")
        self.user: str = user
        self.redirect_url: str = app_config.get("Redirect_URI")
        self.client_id: str = app_config.get("Client_ID")
        self.client_secret:str = app_config.get("Client_Secret")

    def oauth_user(self) -> None:
        url: str = f"https://hh.ru/oauth/authorize?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_url}"

        users: dict = json_reader(file_name=f"{current_path}/resources/data_users.json")
        user: dict = {
            self.user : {
                "authorization_code": ""
            }
        }
        users.update(user)
        json_write(file_name=f"{current_path}/resources/data_users.json", data_to_write=users)
        logger.info(f"create dict of {self.user} and open browser")
        webbrowser.open(url=url)

    def check_authCode_user(self) -> bool:
        users: dict = json_reader(file_name=f"{current_path}/resources/data_users.json")
        user_data: dict = users.get(self.user)
        if user_data is not None:
            if user_data.get("authorization_code") is not None:
                logger.info(f"{self.user} and authorization_code in base yes")
                return True
            else:
                logger.error("authorization_code no base")
                return False
        else:
            logger.error(f"{self.user} no base")
            return False
    
    def get_token_user(self, authorization_code: str) -> None:
        url = "https://hh.ru/oauth/token"
        parm_post = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'redirect_uri': self.redirect_url
        }
        response = requests.post(url, data=urlencode(parm_post), headers={'Content-Type': 'application/x-www-form-urlencoded'})

        if response.status_code == 200:
            data_response: dict = response.json()
            users: dict = json_reader(file_name=f"{current_path}/resources/data_users.json")
            user_data: dict = {
                self.user: {
                    "access_token": data_response.get("access_token"),
                    "refresh_token": data_response.get("refresh_token"),
                    "expires_in": data_response.get("expires_in"),
                    "authorization_code": authorization_code
                }
            }
            users.update(user_data)
            json_write(file_name=f"{current_path}/resources/data_users.json", data_to_write=users)
            logger.info("token geted")
        else:
            logger.error(f"Error in get_token_user:, {response.status_code}, {response.text}")

    def check_token_user(self) -> bool:
        users: dict = json_reader(file_name=f"{current_path}/resources/data_users.json")
        user_data: dict = users.get(self.user)
        if user_data.get("access_token") is not None:
            logger.info("access_token in base yes")
            return True
        else:
            logger.error("access_token no base")
            return False

    def check_list_resume(self) -> bool:
        users: dict = json_reader(file_name=f"{current_path}/resources/data_users.json")
        if "list_resume_ids" in users[self.user]:
            logger.info("resume list yes")
            return True
        else:
            logger.info("resume list no")
            return False

    def get_resume_list(self) -> None:
        users: dict = json_reader(file_name=f"{current_path}/resources/data_users.json")
        api_token: str = users.get(self.user)["access_token"]
        url: str = f'https://api.hh.ru/resumes/mine'
        header = {
            "Authorization": f"Bearer {api_token}"
        }
        request = requests.get(url=url, headers=header)

        if request.status_code == 200:
            data_list_resume: dict = request.json()
            resume_ids: list = [resume['id'] for resume in data_list_resume['items']]
            users.get(self.user)["list_resume_ids"] = resume_ids
            json_write(file_name=f"{current_path}/resources/data_users.json", data_to_write=users)
            logger.info("Loaded resume list: {0} items)".format(len(resume_ids)))
        else:
            logger.error("Can't get resume list from hh.ru!")

    def update_resume(self, resume_id: str) -> None:
        users: dict = json_reader(file_name=f"{current_path}/resources/data_users.json")
        api_token: str = users.get(self.user)["access_token"]
        url: str = f'https://api.hh.ru/resumes/{resume_id}/publish'
        header = {
            "Authorization": f"Bearer {api_token}"
        }
        result = requests.post(url=url, headers=header)

        if result.status_code == 204:
            logger.info(f"{resume_id}: updated")
        elif result.status_code == 429:
            logger.info(f"{resume_id}: too many requests")
        elif result.status_code == 400:
            logger.info(f"{resume_id}: can't update because resume is incorrect")
        elif result.status_code == 403:
            logger.error(f"{resume_id}: auth required")
        else:
            logger.error(f"{resume_id}: unknown status")
