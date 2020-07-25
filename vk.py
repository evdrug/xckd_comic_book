import requests
from environs import Env

env = Env()
env.read_env()

PARAMS_DEFAULT = {
    'access_token': env("VK_ACCESS_TOKEN"),
    'v': '5.120'
}


def check_error_response(body):
    if body.get('error'):
        msg = body.get('error')['error_msg']
        raise requests.RequestException(msg)


def get_params_upload_server():
    url = f'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(url, params=PARAMS_DEFAULT)
    response.raise_for_status()
    body = response.json()
    check_error_response(body)
    params_server = body.get('response')
    return (params_server.get('upload_url'), params_server.get(
        'album_id'), params_server.get('user_id'))


def download_photo(upload_url, path_file):
    url = f'https://api.vk.com/method/photos.saveWallPhoto'
    with open(path_file, 'rb') as file:
        url = upload_url
        files = {
            'photo': file,
        }
        response = requests.post(url,
                                 files=files,
                                 params=PARAMS_DEFAULT)
        response.raise_for_status()
        body = response.json()
        check_error_response(body)
        if not body.get('photo'):
            raise requests.RequestException(
                'Неудачная попытка загрузить файл на сервер')
        return body


def save_photo(params_photo):
    url = f'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.post(url, data=params_photo, params=PARAMS_DEFAULT)
    response.raise_for_status()
    body = response.json()
    check_error_response(body)
    owner_id = body.get('response')[0]['owner_id']
    photo_id = body.get('response')[0]['id']
    return owner_id, photo_id


def create_post_on_wall(owner_id, photo_id, message):
    url = f'https://api.vk.com/method/wall.post'
    response = requests.post(url,
                             params={**PARAMS_DEFAULT,
                                     'attachments': f"photo{owner_id}_{photo_id}",
                                     'owner_id': f"-{env('PUBLIC_ID')}",
                                     'from_group': 1,
                                     'message': message})
    response.raise_for_status()
    body = response.json()
    check_error_response(body)
    return body


def publish_photo_post(file, title):
    url, *_ = get_params_upload_server()
    params_photo = download_photo(url, file)
    owner_id, photo_id = save_photo(params_photo)
    return create_post_on_wall(owner_id, photo_id, title)
