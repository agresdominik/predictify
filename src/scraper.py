import requests

from auth import authenticate


def main():
    """
    This function is the main function that will be executed when the script is run
    """
    scope = "user-read-recently-played"
    bearer_token = authenticate(scope)
    last_played_track = _get_last_played_track(bearer_token=bearer_token)
    print(last_played_track)


def _get_last_played_track(limit: str = "1", bearer_token: str = "") -> dict:
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


if __name__ == '__main__':
    main()
