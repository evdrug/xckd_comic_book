from pathlib import Path
from random import randint

import requests

from vk import publish_photo_post


class ErrorFileException(Exception):
    pass


def download_random_comics():
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status()
    page_count = response.json().get('num')

    random_page = randint(1, page_count)
    response = requests.get(f'https://xkcd.com/{random_page}/info.0.json')
    response.raise_for_status()
    body = response.json()
    img_link = body.get('img')
    title_comic_book = body.get('alt')
    file_name = img_link.split('/')[-1]
    path = Path(file_name)
    load_image(img_link, path.name)
    if not path.is_file():
        raise ErrorFileException('Неудалось скачать файл')
    return path.name, title_comic_book


def load_image(url, path_file):
    response = requests.get(url)
    response.raise_for_status()
    path = Path(path_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'bw') as file:
        file.write(response.content)


if __name__ == '__main__':
    file_name, title_comic_book = download_random_comics()
    path = Path(file_name)
    publish_photo_post(path.name, title_comic_book)
    path.unlink()
