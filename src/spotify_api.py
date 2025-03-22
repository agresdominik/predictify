import logging as log

import requests


def get_last_played_track(bearer_token: str, url: str = "https://api.spotify.com/v1/me/player/recently-played?limit=50") -> dict:
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


def get_track_information(track_id: str, bearer_token: str) -> dict:
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


def get_multiple_tracks_information(bearer_token: str, *track_ids: str) -> dict:
    """
    This function returns the track information based on the track id

    :param *track_id: str
    :param bearer_token: str
    :return: dict
    """
    if len(track_ids) > 50:
        log.error('Passed more than 50 track ids to get_multiple_tracks_information')
        return None

    url_suffix = "ids="
    separator = ","

    for track_id in track_ids:
        url_suffix = url_suffix + track_id + separator

    url = f"https://api.spotify.com/v1/tracks?{url_suffix}"
    url = url[:-len(separator)]
    header = {
        'Authorization': f'Bearer {bearer_token}'
    }

    response = requests.get(url, headers=header)
    response_json = response.json()
    return response_json


def get_artist_information(artist_id: str, bearer_token: str) -> dict:
    """
    This function returns the artist information based on the artist id

    :param artist_id: str
    :param bearer_token: str
    :return: dict
    """

    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    header = {
        'Authorization': f'Bearer {bearer_token}'
    }

    response = requests.get(url, headers=header)
    response_json = response.json()
    return response_json


def get_album_information(album_id: str, bearer_token: str) -> dict:
    """
    This function returns the album information based on the album id

    :param album_id: str
    :param bearer_token: str
    :return: dict
    """

    url = f"https://api.spotify.com/v1/albums/{album_id}"
    header = {
        'Authorization': f'Bearer {bearer_token}'
    }

    response = requests.get(url, headers=header)
    response_json = response.json()
    return response_json
