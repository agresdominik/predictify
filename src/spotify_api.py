from typing import Union

import requests

from logger import LoggerWrapper

log = LoggerWrapper()


def get_last_played_track(bearer_token: str, url: str = "https://api.spotify.com/v1/me/player/recently-played?limit=50") -> Union[dict, None]:
    """
    This function returns the last played track based on the limit size

    :param limit: str
    :param bearer_token: str
    :return: dict
    """

    header = {
        'Authorization': f'Bearer {bearer_token}'
    }

    try:
        log.debug(f"GET Request: {url}")
        response = requests.get(url, headers=header)
        response_json = response.json()
        return response_json
    except requests.exceptions.RequestException as e:
        log.error(f"Error in get_last_played_track: {e}")
        return None


def get_track_information(track_id: str, bearer_token: str) -> Union[dict, None]:
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

    try:
        log.debug(f"GET Request: {url}")
        response = requests.get(url, headers=header)
        response_json = response.json()
        return response_json
    except requests.exceptions.RequestException as e:
        log.error(f"Error in get_track_information: {e}")
        return None


def get_artist_information(artist_id: str, bearer_token: str) -> Union[dict, None]:
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
    try:
        log.debug(f"GET Request: {url}")
        response = requests.get(url, headers=header)
        response_json = response.json()
        return response_json
    except requests.exceptions.RequestException as e:
        log.error(f"Error in get_artist_information: {e}")
        return None


def get_album_information(album_id: str, bearer_token: str) -> Union[dict, None]:
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

    try:
        log.debug(f"GET Request: {url}")
        response = requests.get(url, headers=header)
        response_json = response.json()
        return response_json
    except requests.exceptions.RequestException as e:
        log.error(f"Error in get_album_information: {e}")
        return None


def get_multiple_field_information(bearer_token: str, api_type: str, limit: int,  *track_ids) -> Union[dict, None]:
    """
    This function returns the track information based on the track id

    :param *track_id: str
    :param bearer_token: str
    :return: dict
    """

    if len(track_ids) > limit:
        log.error(f'exceeding the limit if ids {limit} for endpoint {api_type}')
        return None

    url_suffix = "ids="
    separator = ","
    try:
        for track_id in track_ids:
            url_suffix = url_suffix + track_id + separator
    except Exception as e:
        log.error(f"Failed setting up the url for multiple ids request."
                  f"Error: {e}")
        return None

    url = f"https://api.spotify.com/v1/{api_type}?{url_suffix}"
    url = url[:-len(separator)]
    header = {
        'Authorization': f'Bearer {bearer_token}'
    }

    try:
        log.debug(f"GET Request: {url}")
        response = requests.get(url, headers=header)
        response_json = response.json()
        return response_json
    except requests.exceptions.RequestException as e:
        log.error(f"Error in get_multiple_field_information: {e}")
        return None
