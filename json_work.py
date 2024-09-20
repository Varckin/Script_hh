from json import load, dump
from pathlib import Path


current_path: str = str(Path.cwd())


def json_reader(file_name: str) -> dict:
    with open(file=file_name, mode='r', encoding='utf-8') as file:
        return load(fp=file)


def json_write(file_name: str, data_to_write: dict) -> None:
    with open(file=file_name, mode='w', encoding='utf-8') as file:
        dump(obj=data_to_write, fp=file, ensure_ascii=False, indent=4)
