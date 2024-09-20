import logging
import requests

from json_work import current_path, json_reader


logger = logging.getLogger("hh resume auto updater")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

hh = logging.StreamHandler()
hh.setFormatter(formatter)
logger.addHandler(hh)


api_token: str = json_reader(file_name=f"{current_path}/users.json").get("apiToken")

request = requests.Session()
request.headers.update({'Authorization': f'Bearer {api_token}'})


def get_resume_list() -> list:
    url = f'https://api.hh.ru/resumes/mine'
    result = request.get(url=url)

    if result.status_code == 200:
        data = result.json()

        resume_ids: list = [resume['id'] for resume in data['items']]

        logger.info('Loaded resume list: {0} items)'.format(len(resume_ids)))

        return resume_ids
    else:
        logger.error(msg="Can't get resume list from hh.ru!")


def update_resume(resume_id):
    url = f'https://api.hh.ru/resumes/{resume_id}/publish'
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


def check_variables():
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
