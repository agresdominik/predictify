import json
import os

from auth import simple_authenticate
from database_handler import Database, Table
from logger import LoggerWrapper
from spotify_api import get_multiple_field_information

# Define the absolute folder path to the folder containing the gdrp retrieved data
folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'gdpr_data')
# Define the db
db = Database()
log = LoggerWrapper()


def _read_gdrp_data() -> list:
    """
    This function reads all .json files in the folder containing the gdpr data.
    This data is then extracted into a dict and sorted by timestamp ascending.

    :return: all_songs_played: A dict with an items field containing all songs played for the user
    """
    all_songs_played = []
    try:
        for filename in os.listdir(folder_path):

            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)

                with open(file_path, 'r') as file:
                    data = json.load(file)

                    for entry in data:
                        # This removes all podcasts from the list
                        if entry['spotify_track_uri'] is None:
                            continue
                        try:
                            track = {
                                'timestamp': entry['ts'],
                                'id': _extract_id(entry['spotify_track_uri']),
                                'track_name': entry['master_metadata_track_name'],
                                'artist_name': entry['master_metadata_album_artist_name'],
                                'album_name': entry['master_metadata_album_album_name'],
                                'conn_country': entry['conn_country'],
                                'ms_played': entry['ms_played']
                                }
                            all_songs_played.append(track)
                        except Exception as e:
                            log.warning(f'Missing field from gdpr data: {e}')
    except Exception as e:
        log.error(f'Failed to read gdpr data: {e}')

    all_songs_played = sorted(all_songs_played, key=lambda x: x['timestamp'])
    return all_songs_played


def _extract_id(spotify_id: str) -> str:
    """
    This function gets a id with extra details and extracts the id from it.

    :param: id a string containing the id
    :return: str the ID
    """
    prefix = "spotify:track:"
    prefix_removed_id = spotify_id[len(prefix):]
    return prefix_removed_id


def _populate_ids(all_songs_played: list):

    track_ids = []
    all_songs_played_info = []
    token = simple_authenticate()

    processed_songs_id = set()

    counter = 0

    for entry in all_songs_played:
        track_id = entry['id']

        if track_id not in processed_songs_id:
            track_ids.append(track_id)
            processed_songs_id.add(track_id)
            counter += 1

        if (counter + 1) % 50 == 0 and len(track_ids) > 0:
            track_ids_tuple = tuple(track_ids)
            track_ids.clear()
            response = get_multiple_field_information(token, 'tracks', 50, *track_ids_tuple)
            all_songs_played_info.extend(_sort_and_create_required_dataset(response))
            counter = 0

    if len(track_ids) > 0:
        track_ids_tuple = tuple(track_ids)
        response = get_multiple_field_information(token, 'tracks', 50, *track_ids_tuple)
        all_songs_played_info.extend(_sort_and_create_required_dataset(response))

    return all_songs_played_info


def _sort_and_create_required_dataset(response) -> dict:

    track_list = []

    for entry in response['tracks']:
        track_data = {
            'track_id': entry['id'],
            'album_id': entry['album']['id'],
            'artist_id': entry['artists'][0]['id']
        }
        track_list.append(track_data)

    return track_list


def _fill_missing_ids(all_songs_played, all_songs_catalogued):

    # Create a dictionary to map track_id to artist_id and album_id
    track_id_to_artist_album = {data['track_id']: {'album_id': data['album_id'], 'artist_id': data['artist_id']} for data in all_songs_catalogued}

    # Now, we will update the original `tracks` list by adding artist_id and album_id
    for track in all_songs_played:
        track_info = track_id_to_artist_album.get(track['id'])
        if track_info:
            track['artist_id'] = track_info['artist_id']
            track['album_id'] = track_info['album_id']

    return all_songs_played


def _insert_data_into_db(all_songs_played: list):
    """
    This function takes a list of all played songs and inserts these into the database.

    :param: all_songs_played list of all songs
    """
    for entry in all_songs_played:
        try:
            db.add_row(Table.RECENTLY_PLAYED, (entry['timestamp'], entry['id'], entry['artist_id'], entry['album_id']))
        except Exception as e:
            log.error(f'Failed adding {entry} to database, error {e}')


def export_gdpr_data(n_limit: int = 100) -> None:
    all_songs_played = _read_gdrp_data()
    all_songs_played = all_songs_played[-n_limit:]
    all_songs_catalogued = _populate_ids(all_songs_played)
    all_songs_played = _fill_missing_ids(all_songs_played, all_songs_catalogued)
    _insert_data_into_db(all_songs_played)
