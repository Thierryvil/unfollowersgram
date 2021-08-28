import json
import os
import codecs
from instagram_private_api import Client, ClientCookieExpiredError, \
    ClientLoginRequiredError


CREDENTIAL_FILE_NAME = '.session'


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {
            '__class__': 'bytes',
            '__value__': codecs.encode(python_object, 'base64').decode()
        }
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def create_session_file(data: dict):
    try:
        with open(CREDENTIAL_FILE_NAME, "w") as file:
            file.write(json.dumps(data, indent=4, default=to_json))
    except Exception as e:
        exit(f'Fail to create session file!\n {e}')


def login_instagram(username: str, password: str):
    try:
        if os.path.isfile(CREDENTIAL_FILE_NAME):
            print('Reusing Credentials')
            device_id = None
            with open(CREDENTIAL_FILE_NAME) as file:
                cached_settings = json.load(file, object_hook=from_json)
                device_id = cached_settings.get('device_id')

            api = Client(username, password, settings=cached_settings)
        else:
            print('Creating Credentials')
            api = Client(username, password)
            create_session_file(api.settings)
    except (ClientCookieExpiredError, ClientLoginRequiredError):
        print('Login Error, trying new credential')
        api = Client(username, password, device_id=device_id)

    return api
    