import logging
from pathlib import Path

logger = logging.getLogger('main_logger')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
current_path: str = str(Path.cwd())

script_logger = logging.FileHandler(f'{current_path}/script_log.log')
script_logger.setLevel(logging.INFO)
script_logger.setFormatter(formatter)
