import dotenv
import time
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import os

def main():

    recently_played_access_token = authenticate()
    last_played_track = get_last_played_track(limit=1, bearer_token=recently_played_access_token)


def authenticate() -> str:
    """
    This function authenticates the user and returns the access token
    """
    spotify_client_id, spotify_client_secret, spotify_redirect_uri = _read_env_file()

    auth_url = _get_authorization_url(spotify_client_id, spotify_redirect_uri)
    print(f'Please go to the following URL to authorize the app: {auth_url}')

    authorization_code = _start_server_and_wait_for_code()

    access_token, refresh_token = _exchange_code_for_token(authorization_code, redirect_uri=spotify_redirect_uri,
                                                          client_id=spotify_client_id, client_secret=spotify_client_secret)

    return access_token


def get_last_played_track(limit: str = "1", bearer_token: str = "") -> dict:
    """
    This function returns the last played track based on the limit size

    :param limit: str
    :param bearer_token: str
    :return: dict
    """

    header = {
        'Authorization': f'Bearer {bearer_token}'
    }

    response = requests.get(f'https://api.spotify.com/v1/me/player/recently-played?limit={limit}', headers=header)
    response_json = response.json()
    return response_json


def _get_authorization_url(client_id: str, redirect_uri: str) -> str:
    """
    This function generates the URL that the user needs to visit to authorize the app

    :param client_id: str
    :param redirect_uri: str
    :return: str
    """

    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": "user-read-recently-played",
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
    dotenv_folder_path = os.path.join(current_dir, 'env')
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
    print("Starting server to capture the authorization code...")
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
    return access_token, refresh_token


if __name__ == '__main__':
    main()