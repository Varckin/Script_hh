import logging
import requests

from json_work import current_path, json_reader
from logger import script_logger


logger = logging.getLogger('Script')
logger.setLevel(logging.INFO)
logger.addHandler(script_logger)

api_token: str = json_reader(file_name=f"{current_path}/resources/api_token.json").get("apiToken")

request = requests.Session()
request.headers.update({'Authorization': f'Bearer {api_token}'})


def get_resume_list() -> list:
    url: str = f'https://api.hh.ru/resumes/mine'
    result = request.get(url=url)

    if result.status_code == 200:
        data: dict = result.json()
        resume_ids: list = [resume['id'] for resume in data['items']]

        logger.info('Loaded resume list: {0} items)'.format(len(resume_ids)))
        return resume_ids
    else:
        logger.error(msg="Can't get resume list from hh.ru!")


def update_resume(resume_id: str) -> None:
    url: str = f'https://api.hh.ru/resumes/{resume_id}/publish'
    request.post(url=url)

    if request.status_code == 204:
        logger.info(f'{resume_id}: updated')
    elif request.status_code == 429:
        logger.info(f'{resume_id}: too many requests')
    elif request.status_code == 400:
        logger.info(f'{resume_id}: can\'t update because resume is incorrect')
    elif request.status_code == 403:
        logger.error(f'{resume_id}: auth required')
    else:
        logger.error(f'{resume_id}: unknown status')


def check_variables() -> None:
    if json_reader(file_name=f"{current_path}/resources/api_token.json")["apiToken"] != "":
        users: dict = json_reader(file_name=f"{current_path}/resources/users.json")
        for key, item in users.items(users):
            if item["resume_list"] != []:
                logger.info(msg=f"{key} not empty")
            else:
                logger.error(msg=f"{key} empty")
    else:
        logger.error(msg="Api token empty")
        exit()
