import base64
import json
import logging as log
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import dotenv
import requests

TOKEN_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data', 'tokens.json')


def simple_authenticate(grant_type: str = "client_credentials") -> str:
    """
    This function authenticates the user and returns the access token

    :return: str
    """
    spotify_client_id, spotify_client_secret, spotify_redirect_uri = _read_env_file()
    token_url = "https://accounts.spotify.com/api/token"
    auth_value = f"{spotify_client_id}:{spotify_client_secret}"
    auth_header = base64.b64encode(auth_value.encode('utf-8')).decode('utf-8')

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": f"{grant_type}"
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        access_token = response.json().get('access_token')
        return access_token
    else:
        log.error(f"Error {response.status_code}: {response.text}")


def authenticate(scope: str) -> str:
    """
    This function authenticates the user and returns the access token

    :param scope: str
    :return: str
    """
    spotify_client_id, spotify_client_secret, spotify_redirect_uri = _read_env_file()

    tokens = _load_tokens(scope)
    if tokens:
        access_token, refresh_token, expires_at = tokens
        if time.time() < expires_at:
            return access_token
        else:
            log.info(f"Token for scope {scope} expired, refreshing...")
            access_token, expires_at = _refresh_access_token(refresh_token, spotify_client_id, spotify_client_secret)
            _refresh_tokens_file(access_token, scope, expires_at)
            return access_token

    auth_url = _get_authorization_url(spotify_client_id, spotify_redirect_uri, scope)
    print(f'Please go to the following URL to authorize the app: {auth_url}')

    authorization_code = _start_server_and_wait_for_code()

    access_token, refresh_token, expires_at = _exchange_code_for_token(authorization_code, redirect_uri=spotify_redirect_uri,
                                                                       client_id=spotify_client_id, client_secret=spotify_client_secret)

    _save_tokens(access_token, refresh_token, scope, expires_at)

    return access_token


def _get_authorization_url(client_id: str, redirect_uri: str, scope: str) -> str:
    """
    This function generates the URL that the user needs to visit to authorize the app

    :param client_id: str
    :param redirect_uri: str
    :param scope: str
    :return: str
    """

    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": str(int(time.time()))
    }
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode(auth_params)
    return auth_url


def _read_env_file() -> tuple:
    """
    This function reads the .env file and returns the client_id, client_secret and redirect_uri

    :return: tuple
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dotenv_folder_path = os.path.join(current_dir, '../config')
    dotenv_path = os.path.join(dotenv_folder_path, '.env')
    contents = dotenv.dotenv_values(dotenv_path=dotenv_path)
    spotify_client_id = contents['SPOTIFY_CLIENT_ID']
    spotify_client_secret = contents['SPOTIFY_CLIENT_SECRET']
    spotify_redirect_uri = contents['SPOTIFY_REDIRECT_URI']
    return spotify_client_id, spotify_client_secret, spotify_redirect_uri


def _start_server_and_wait_for_code() -> any:
    """
    This function starts a server and waits for the user to visit the authorization URL
    and get the authorization code

    :return: any
    """
    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            if 'code' in query_params:
                self.server.authorization_code = query_params['code'][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this window.")

    server = HTTPServer(('localhost', 8888), CallbackHandler)
    log.info("Starting server to capture the authorization code...")
    server.handle_request()
    return server.authorization_code


def _exchange_code_for_token(code: str, redirect_uri: str, client_id: str, client_secret: str) -> tuple:
    """
    This function exchanges the authorization code for an access token

    :param code: str
    :param redirect_uri: str
    :param client_id: str
    :param client_secret: str
    :return: tuple
    """

    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }

    response = requests.post(token_url, data=data, headers=headers)
    response_data = response.json()

    if 'access_token' not in response_data:
        raise Exception("Failed to get access token")

    access_token = response_data['access_token']
    refresh_token = response_data.get('refresh_token', None)
    expires_in = response_data['expires_in']
    expires_at = time.time() + expires_in
    return access_token, refresh_token, expires_at


def _refresh_access_token(refresh_token: str, client_id: str, client_secret: str) -> tuple:
    """
    Refreshes the access token using the refresh token.

    :param refresh_token: str
    :param client_id: str
    :param client_secret: str
    :return: tuple
    """
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
    }

    response = requests.post(token_url, data=data, headers=headers)
    response_data = response.json()

    if 'access_token' not in response_data:
        raise Exception("Failed to refresh access token")

    access_token = response_data['access_token']
    expires_in = response_data['expires_in']
    expires_at = time.time() + expires_in
    return access_token, expires_at


def _load_tokens(scope: str) -> tuple:
    """
    Loads the tokens from the local file if they exist and are still valid.

    :return: tuple or None
    """
    if os.path.exists(TOKEN_FILE_PATH):
        with open(TOKEN_FILE_PATH, 'r') as f:
            tokens = json.load(f)
            if scope in tokens:
                if 'access_token' in tokens[scope] and 'expires_at' in tokens[scope] and 'expires_at' in tokens[scope]:
                    return tokens[scope]['access_token'], tokens[scope]['refresh_token'], tokens[scope]['expires_at']
    return None


def _save_tokens(access_token: str, refresh_token: str, scope: str, expires_at) -> None:
    """
    Saves the access and refresh tokens to a local file.

    :param access_token: str
    :param refresh_token: str
    :param scope: str
    """
    tokens = {
        scope: {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at
            },
        }
    with open(TOKEN_FILE_PATH, 'w') as f:
        json.dump(tokens, f)


def _refresh_tokens_file(access_token: str, scope: str, expires_at) -> None:
    """
    Saves the access and refresh tokens to a local file.

    :param access_token: str
    :param scope: str
    """
    with open(TOKEN_FILE_PATH, 'r') as file:
        tokens = json.load(file)

    if scope in tokens and 'refresh_token' in tokens[scope]:
        tokens[scope]['access_token'] = access_token
        tokens[scope]['expires_at'] = expires_at
        with open(TOKEN_FILE_PATH, 'w') as file:
            json.dump(tokens, file, indent=4)
    else:
        log.error(f"Error: Scope '{scope}' or refresh_token not found in the tokens file.")
