import logging
import time

from updater import update_resume, get_resume_list, check_variables
from logger import script_logger


logger = logging.getLogger('Script')
logger.setLevel(logging.INFO)
logger.addHandler(script_logger)


if __name__ == '__main__':
    while True:
        for id in get_resume_list():
            update_resume(id)
            time.sleep(5)

        logger.info('I going sleep...zzzzz')
        time.sleep(240 * 60)
