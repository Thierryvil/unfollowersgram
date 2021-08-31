import codecs
import json

CREDENTIAL_FILE_NAME = '.session'


def list_dif(list1, list2):
    return set(list1) - set(list2)


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
        with open(CREDENTIAL_FILE_NAME, "w", encoding='UTF-8') as file:
            file.write(json.dumps(data, indent=4, default=to_json))
    except Exception as e:
        exit(f'Fail to create session file!\n {e}')
    finally:
        print(f'{CREDENTIAL_FILE_NAME} file was created!')
