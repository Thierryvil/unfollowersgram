import os
import json
from sys import argv
from instagram_private_api import Client, ClientCookieExpiredError, \
    ClientLoginRequiredError
from src.util import from_json, create_session_file, list_dif, CREDENTIAL_FILE_NAME


def login_instagram(login_username: str, login_password: str):
    try:
        if os.path.isfile(CREDENTIAL_FILE_NAME):
            print('LOGIN: Reusing Credentials')
            device_id = None
            with open(CREDENTIAL_FILE_NAME, encoding='UTF-8') as file:
                cached_settings = json.load(file, object_hook=from_json)
                device_id = cached_settings.get('device_id')

            api = Client(login_username, login_password,
                         settings=cached_settings)
        else:
            print('LOGIN: Creating Credentials')
            api = Client(login_username, login_password)
            create_session_file(api.settings)
    except (ClientCookieExpiredError, ClientLoginRequiredError):
        print('LOGIN: Trying new credential')
        api = Client(login_username, login_password, device_id=device_id)

    return api


def get_followers(api: Client):
    user_id = api.authenticated_user_id
    uuid = api.generate_uuid()
    results = api.user_followers(user_id, uuid)
    followers = []
    followers.extend(results.get('users', []))
    next_max_id = results.get('next_max_id')

    while next_max_id:
        results = api.user_followers(user_id, uuid, max_id=next_max_id)
        followers.extend(results.get('users', []))
        next_max_id = results.get('next_max_id')

    return [user["username"] for user in followers]


def get_following(api: Client):
    user_id = api.authenticated_user_id
    uuid = api.generate_uuid()
    results = api.user_following(user_id, uuid)
    following = []
    following.extend(results.get('users', []))
    next_max_id = results.get('next_max_id')

    while next_max_id:
        results = api.user_following(user_id, uuid, max_id=next_max_id)
        following.extend(results.get('users', []))
        next_max_id = results.get('next_max_id')

    return [user["username"] for user in following]


if __name__ == '__main__':
    user, password = argv[1:]
    api = login_instagram(user, password)
    unfollow = list_dif(get_following(api), get_followers(api))

    print(f'Currently {len(unfollow)} people are not following you back!. \n')
    for username in unfollow:
        decision = input(
            f'Would you like to stop following @{username} ? (y/n) \n')
        if decision == 'y':
            user_id = api.username_info(username).get('user').get('pk')
            api.friendships_destroy(user_id)
