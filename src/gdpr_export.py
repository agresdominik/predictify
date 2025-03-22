import json
import os
from collections import defaultdict

folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'gdpr_data')

data_dictionary_name = defaultdict(int)
data_dictionary_artist = defaultdict(int)
data_dictionary_album = defaultdict(int)
data_dictionary_conn_country = defaultdict(int)


for filename in os.listdir(folder_path):

    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)

        with open(file_path, 'r') as file:
            data = json.load(file)

            for entry in data:
                try:
                    track_id = entry['spotify_track_uri']
                    name = entry['master_metadata_track_name']
                    artist = entry['master_metadata_album_artist_name']
                    album = entry['master_metadata_album_album_name']
                    conn_country = entry['conn_country']
                    data_dictionary_name[name] += 1
                    data_dictionary_artist[artist] += 1
                    data_dictionary_album[album] += 1
                    data_dictionary_conn_country[conn_country] += 1
                except Exception as e:
                    print(f'Missing field: {e}')

sorted_name_counts_name = sorted(data_dictionary_name.items(), key=lambda x: x[1])
sorted_name_counts_artist = sorted(data_dictionary_artist.items(), key=lambda x: x[1])
sorted_name_counts_album = sorted(data_dictionary_album.items(), key=lambda x: x[1])
sorted_name_counts_conn_country = sorted(data_dictionary_conn_country.items(), key=lambda x: x[1])

for name, count in sorted_name_counts_conn_country:
    print(f"{name}: {count}")
