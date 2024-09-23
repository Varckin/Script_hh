import logging
import time
import threading

from updater import Resume_updater
from json_work import json_reader
from logger import script_logger
from json_work import current_path


logger = logging.getLogger('Script')
logger.setLevel(logging.INFO)
logger.addHandler(script_logger)

stop_thread = True


def main(user: str):
    global stop_thread
    while stop_thread:
        updater = Resume_updater(user=user)
        if updater.check_authCode_user():
            if updater.check_token_user():
                if updater.check_list_resume():
                    users: dict = json_reader(file_name=f"{current_path}/resources/data_users.json")
                    for id in users.get(user)["list_resume_ids"]:
                        updater.update_resume(resume_id=id)
                    logger.info("I going sleep...zzzzz")
                    time.sleep(250 * 60)
                else:
                    updater.get_resume_list()
                    users: dict = json_reader(file_name=f"{current_path}/resources/data_users.json")
                    for id in users.get(user)["list_resume_ids"]:
                        updater.update_resume(resume_id=id)
                    logger.info("I going sleep...zzzzz")
                    time.sleep(250 * 60)
            else:
                users: dict = json_reader(file_name=f"{current_path}/resources/data_users.json")
                updater.get_token_user(authorization_code=users.get(user)["authorization_code"])
        else:
            updater.oauth_user()
            stop_thread = False


if __name__ == '__main__':
    thread_1 = threading.Thread(target=main, args=("XYZ",))

    thread_1.start()

    thread_1.join()

    logger.info("Thread stoped")
