from auth import authenticate, simple_authenticate
from database_handler import Database, Table
from spotify_api import (
    get_album_information,
    get_artist_information,
    get_last_played_track,
    get_track_information,
)


def scraping():
    """
    This function is the main function that will be executed when the script is run
    """

    scope = "user-read-recently-played"
    bearer_token = authenticate(scope)

    # Once each 30 mins
    _read_recently_played_page_and_add_to_db(bearer_token=bearer_token)
    scrape_missing_infos()



def _read_recently_played_page_and_add_to_db(bearer_token: str):
    """
    This function gets a list of song play history and adds it into the database.
    """

    last_played_track = get_last_played_track(bearer_token=bearer_token)

    db = Database()
    for track in reversed(last_played_track['items']):
        track_id = track['track']['id']
        played_at = track['played_at']
        album_id = track['track']['album']['id']
        artist_id = track['track']['artists'][0]['id']
        db.add_row(Table.RECENTLY_PLAYED, (played_at, track_id, artist_id, album_id))
    db.close()

def scrape_missing_infos():
    """

    """

    bearer_token_simple = simple_authenticate()

    db = Database()
    # Track Info
    all_track_ids_recently_played = db.read_all_rows(Table.RECENTLY_PLAYED, 'track_id')
    all_track_ids_saved = db.read_all_rows(Table.TRACK_INFORMATION, 'track_id')
    all_track_ids_missing = list(set(all_track_ids_recently_played) - set(all_track_ids_saved))
    for track_id in all_track_ids_missing:
        response = get_track_information(track_id=track_id[0], bearer_token=bearer_token_simple)
        db.add_row(Table.TRACK_INFORMATION, (response['id'], response['name'], response['duration_ms'], response['explicit'], response['popularity']))
    # Album Info
    all_album_ids_recently_played = db.read_all_rows(Table.RECENTLY_PLAYED, 'album_id')
    all_album_ids_saved = db.read_all_rows(Table.ALBUM_INFORMATION, 'album_id')
    all_album_ids_missing = list(set(all_album_ids_recently_played) - set(all_album_ids_saved))
    for album_id in all_album_ids_missing:
        response = get_album_information(album_id=album_id[0], bearer_token=bearer_token_simple)
        try:
            release_year = response['release_date'][:4]
        except Exception:
            release_year = ""
        db.add_row(Table.ALBUM_INFORMATION, (response['id'], response['name'], response['album_type'], response['total_tracks'], release_year, response['label']))
    # Artist Info
    all_artist_ids_recently_played = db.read_all_rows(Table.RECENTLY_PLAYED, 'artist_id')
    all_artist_ids_saved = db.read_all_rows(Table.ARTIST_INFORMATION, 'artist_id')
    all_artist_ids_missing = list(set(all_artist_ids_recently_played) - set(all_artist_ids_saved))
    for artist_id in all_artist_ids_missing:
        response = get_artist_information(artist_id=artist_id[0], bearer_token=bearer_token_simple)
        try:
            genre = response['genres'][0]
        except IndexError:
            genre = ""
        db.add_row(Table.ARTIST_INFORMATION, (response['id'], response['name'], response['followers']['total'], genre, response['popularity']))
    db.close()
