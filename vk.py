import requests
from requests import HTTPError

def check_error_response(body):
    if body.get('error'):
        msg = body.get('error')['error_msg']
        raise HTTPError(msg)


def get_params_upload_server(access_token):
    params = {
        'access_token': access_token,
        'v': '5.120'
    }
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(url, params=params)
    response.raise_for_status()
    body = response.json()
    check_error_response(body)
    params_server = body.get('response')
    return (params_server.get('upload_url'), params_server.get(
        'album_id'), params_server.get('user_id'))


def download_photo(upload_url, path_file, access_token):
    params = {
        'access_token': access_token,
        'v': '5.120'
    }

    with open(path_file, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url,
                                 files=files,
                                 params=params)
        response.raise_for_status()
        body = response.json()
        check_error_response(body)
        if not body.get('photo'):
            raise requests.RequestException(
                'Неудачная попытка загрузить файл на сервер')
        return body


def save_photo(params_photo, access_token):
    params = {
        'access_token': access_token,
        'v': '5.120'
    }
    url = f'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.post(url, data=params_photo, params=params)
    response.raise_for_status()
    body = response.json()
    check_error_response(body)
    owner_id = body.get('response')[0]['owner_id']
    photo_id = body.get('response')[0]['id']
    return owner_id, photo_id


def create_post_on_wall(owner_id, photo_id, message, access_token, public_id):
    params = {
        'access_token': access_token,
        'v': '5.120'
    }
    url = 'https://api.vk.com/method/wall.post'
    response = requests.post(url,
                             params={**params,
                                     'attachments': f"photo{owner_id}_{photo_id}",
                                     'owner_id': f"-{public_id}",
                                     'from_group': 1,
                                     'message': message})
    response.raise_for_status()
    body = response.json()
    check_error_response(body)
    return body


def publish_photo_post(file, title, access_token, public_id):
    url, *_ = get_params_upload_server(access_token)
    params_photo = download_photo(url, file, access_token)
    owner_id, photo_id = save_photo(params_photo, access_token)
    return create_post_on_wall(owner_id, photo_id, title, access_token, public_id)
