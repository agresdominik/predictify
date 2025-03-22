import json
import os

from database_handler import Database, Table

# Define the absolute folder path to the folder containing the gdrp retrieved data
folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'gdpr_data')
# Define the db
db = Database()


def read_gdrp_data() -> dict:
    """
    This function reads all .json files in the folder containing the gdpr data.
    This data is then extracted into a dict and sorted by timestamp ascending.

    :return: all_songs_played: A dict with an items field containing all songs played for the user
    """
    all_songs_played = {
        'items': []
    }

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
                            'id': extract_id(entry['spotify_track_uri']),
                            'track_name': entry['master_metadata_track_name'],
                            'artist_name': entry['master_metadata_album_artist_name'],
                            'album_name': entry['master_metadata_album_album_name'],
                            'conn_country': entry['conn_country'],
                            'ms_played': entry['ms_played']
                            }
                        all_songs_played['items'].append(track)
                    except Exception as e:
                        print(f'Missing field: {e}')

    all_songs_played['items'] = sorted(all_songs_played['items'], key=lambda x: x['timestamp'])
    return all_songs_played


def extract_id(spotify_id: str) -> str:
    """
    This function gets a id with extra details and extracts the id from it.

    :param: id a string containing the id
    :return: str the ID
    """
    prefix = "spotify:track:"
    prefix_removed_id = spotify_id[len(prefix):]
    print(prefix_removed_id)
    return prefix_removed_id


def populate_ids(all_songs_played: dict):
    pass
    # for entry in all_songs_played['items']:
    #   track_id = entry['id']


def insert_data_into_db(all_songs_played: dict):
    """
    This function takes a list of all played songs and inserts these into the database.

    :param: all_songs_played list of all songs
    """

    for entry in all_songs_played['items']:
        db.add_row(Table.RECENTLY_PLAYED, (entry['timestamp'], entry['id'], entry['']))


read_gdrp_data()
