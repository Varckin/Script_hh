import logging
import requests
import webbrowser
from urllib.parse import urlencode
import time

from json_work import current_path, json_reader, json_write
from logger import script_logger


logger = logging.getLogger('Script')
logger.setLevel(logging.INFO)
logger.addHandler(script_logger)

def oauth_user(user_name: str) -> None:
    app_config = json_reader(file_name=f"{current_path}/resources/app_config.json")
    url = f"https://hh.ru/oauth/authorize?response_type=code&client_id={app_config.get("Client_ID")}&redirect_uri={app_config.get("Redirect_URI")}"

    users: dict = json_reader(file_name=f"{current_path}/resources/token_users.json")
    user: dict = {
        user_name : {
            "authorization_code": ""
        }
    }
    users.update(user)
    
    json_write(file_name=f"{current_path}/resources/token_users.json", data_to_write=users)
    logger.info("dict create user")
    webbrowser.open(url=url)

def check_auth_code_user(user: str) -> bool:
    users: dict = json_reader(file_name=f"{current_path}/resources/token_users.json")
    user_data = users.get(user)
    if user_data is not None:
        if user_data.get("authorization_code") is not None:
            logger.info("user and authorization_code in base yes")
            return True
        else:
            logger.error("authorization_code no base")
            return False
    else:
        logger.error("user no base")
        return False
    
def get_token_user(authorization_code: str, user: str) -> None:
    app_config = json_reader(file_name=f"{current_path}/resources/app_config.json")
    url = "https://hh.ru/oauth/token"
    parm_post = {
        'grant_type': 'authorization_code',
        'client_id': app_config.get("Client_ID"),
        'client_secret': app_config.get("Client_Secret"),
        'code': authorization_code,
        'redirect_uri': app_config.get("Redirect_URI")
    }
    response = requests.post(url, data=urlencode(parm_post), headers={'Content-Type': 'application/x-www-form-urlencoded'})

    if response.status_code == 200:
        access_token: dict = response.json()
        users: dict = json_reader(file_name=f"{current_path}/resources/token_users.json")
        user_data: dict = {
            user: {
                "access_token": access_token.get("access_token"),
                "refresh_token": access_token.get("refresh_token"),
                "expires_in": access_token.get("expires_in"),
                "authorization_code": authorization_code
            }
        }
        users.update(user_data)
        json_write(file_name=f"{current_path}/resources/token_users.json", data_to_write=users)
        logger.info("token geted")
    else:
        logger.error(f"Error in get_token_user:, {response.status_code}, {response.text}")

def check_token_user(user: str) -> bool:
    users: dict = json_reader(file_name=f"{current_path}/resources/token_users.json")
    user_data: dict = users.get(user)
    if user_data.get("access_token") is not None:
        logger.info("access_token in base yes")
        return True
    else:
        logger.error("access_token no base")
        return False

def check_list_resume(user: str) -> bool:
    users: dict = json_reader(file_name=f"{current_path}/resources/token_users.json")
    if "list_resume_ids" in users[user]:
        logger.info("resume list yes")
        return True
    else:
        logger.info("resume list no")
        return False

def get_resume_list(user: str) -> None:
    users: dict = json_reader(file_name=f"{current_path}/resources/token_users.json")
    api_token: str = users.get(user)["access_token"]
    url: str = f'https://api.hh.ru/resumes/mine'

    header = {
        "Authorization": f"Bearer {api_token}"
    }
    request = requests.get(url=url, headers=header)

    if request.status_code == 200:
        data: dict = request.json()
        resume_ids: list = [resume['id'] for resume in data['items']]
        users.get(user)["list_resume_ids"] = resume_ids
        json_write(file_name=f"{current_path}/resources/token_users.json", data_to_write=users)

        logger.info("Loaded resume list: {0} items)".format(len(resume_ids)))
    else:
        logger.error("Can't get resume list from hh.ru!")

def update_resume(resume_id: str, user: str) -> None:
    users: dict = json_reader(file_name=f"{current_path}/resources/token_users.json")
    api_token: str = users.get(user)["access_token"]
    url: str = f'https://api.hh.ru/resumes/{resume_id}/publish'

    header = {
        "Authorization": f"Bearer {api_token}"
    }
    result = requests.post(url=url, headers=header)

    if result.status_code == 204:
        logger.info(f'{resume_id}: updated')
    elif result.status_code == 429:
        logger.info(f'{resume_id}: too many requests')
    elif result.status_code == 400:
        logger.info(f'{resume_id}: can\'t update because resume is incorrect')
    elif result.status_code == 403:
        logger.error(f'{resume_id}: auth required')
    else:
        logger.error(f'{resume_id}: unknown status')

def main(user: str):
    if check_auth_code_user(user):
        if check_token_user(user):
            if check_list_resume(user):
                users: dict = json_reader(file_name=f"{current_path}/resources/token_users.json")
                for id in users.get(user)["list_resume_ids"]:
                    update_resume(resume_id=id, user=user)
                    time.sleep(250 * 60)
            else:
                get_resume_list(user=user)
                users: dict = json_reader(file_name=f"{current_path}/resources/token_users.json")
                for id in users.get(user)["list_resume_ids"]:
                    print(id)
                    update_resume(resume_id=id, user=user)
                    time.sleep(250 * 60)
        else:
            users: dict = json_reader(file_name=f"{current_path}/resources/token_users.json")
            get_token_user(authorization_code=users.get(user)["authorization_code"], user=user)
    else:
        oauth_user(user_name=user)
        exit()


main("XYZ")
