import requests

from auth import authenticate, simple_authenticate
from database_handler import Database, Table

db = Database('spotify_scraped.db')


def main():
    """
    This function is the main function that will be executed when the script is run
    """
    global db

    scope = "user-read-recently-played"
    bearer_token = authenticate(scope)

    # Once each 30 mins
    _read_recently_played_page_and_add_to_db(bearer_token=bearer_token)

    # Once a day
    all_track_ids = db.read_all_rows(Table.RECENTLY_PLAYED, 'track_id')
    bearer_toke_simple = simple_authenticate()
    for track_id in all_track_ids:
        response = _get_track_information(track_id=track_id[0], bearer_token=bearer_toke_simple)
        print(response)

    # Close the database connection
    db.close()


def _read_recently_played_page_and_add_to_db(bearer_token: str):
    """
    """
    global db

    last_played_track = _get_last_played_track(bearer_token=bearer_token)

    for track in last_played_track['items']:
        track_id = track['track']['id']
        played_at = track['played_at']
        album_id = track['track']['album']['id']
        artist_id = track['track']['artists'][0]['id']
        db.add_row(Table.RECENTLY_PLAYED, (played_at, track_id, artist_id, album_id))


def _get_last_played_track(url: str = "https://api.spotify.com/v1/me/player/recently-played?limit=50", bearer_token: str = "") -> dict:
    """
    This function returns the last played track based on the limit size

    :param limit: str
    :param bearer_token: str
    :return: dict
    """

    header = {
        'Authorization': f'Bearer {bearer_token}'
    }

    response = requests.get(url, headers=header)
    response_json = response.json()
    return response_json


def _get_track_information(track_id: str, bearer_token: str) -> dict:
    """
    This function returns the track information based on the track id

    :param track_id: str
    :param bearer_token: str
    :return: dict
    """

    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    header = {
        'Authorization': f'Bearer {bearer_token}'
    }

    response = requests.get(url, headers=header)
    response_json = response.json()
    return response_json


if __name__ == '__main__':
    main()
