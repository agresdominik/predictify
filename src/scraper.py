from auth import authenticate, simple_authenticate
from database_handler import Database, Table
from logger import LoggerWrapper
from spotify_api import get_last_played_track, get_multiple_field_information

# Define DB
db = Database()
log = LoggerWrapper()


def scraping() -> None:
    """
    This function is the main function that will be executed when the script is run
    """

    scope = "user-read-recently-played"
    bearer_token = authenticate(scope)

    _read_recently_played_page_and_add_to_db(bearer_token=bearer_token)
    scrape_missing_infos()


def _read_recently_played_page_and_add_to_db(bearer_token: str) -> None:
    """
    This function gets a list of song play history and adds it into the database.
    """
    global db

    last_played_track = get_last_played_track(bearer_token=bearer_token)

    try:
        for track in reversed(last_played_track['items']):
            track_id = track['track']['id']
            played_at = track['played_at']
            album_id = track['track']['album']['id']
            artist_id = track['track']['artists'][0]['id']
            db.add_row(Table.RECENTLY_PLAYED, (played_at, track_id, artist_id, album_id))
    except Exception as e:
        log.error(f"Failed to add returned play history to database: {e}"
                  f"\nReturned Value: {last_played_track}")


def scrape_missing_infos() -> None:
    """

    """
    bearer_token_simple = simple_authenticate()

    _process_missing_info(bearer_token_simple, Table.TRACK_INFORMATION, 'track_id', 'tracks')
    _process_missing_info(bearer_token_simple, Table.ALBUM_INFORMATION, 'album_id', 'albums')
    _process_missing_info(bearer_token_simple, Table.ARTIST_INFORMATION, 'artist_id', 'artists')


def _process_missing_info(bearer_token_simple: str, table_name: Table, id_field_name: str, endpoint_name: str) -> None:

    if endpoint_name == 'albums':
        limit = 20
    else:
        limit = 50

    all_ids_recently_played = db.read_all_rows(Table.RECENTLY_PLAYED, id_field_name)
    all_ids_saved = db.read_all_rows(table_name, id_field_name)
    all_ids_missing = list(set(all_ids_recently_played) - set(all_ids_saved))

    log.debug(f"Number of missing {table_name.name} entries: {len(all_ids_missing)}. Inserting...")

    ids = []
    processed_ids = set()

    counter = 0

    for id_value in all_ids_missing:

        id_value_str = id_value[0]

        if id_value_str not in processed_ids:
            ids.append(id_value_str)
            processed_ids.add(id_value_str)
            counter += 1

        if (counter + 1) % limit == 0 and len(ids) > 0:
            ids_tuple = tuple(ids)
            ids.clear()
            response = get_multiple_field_information(bearer_token_simple, endpoint_name, limit, *ids_tuple)
            _add_data_to_database(table_name, response)
            counter = 0

    if len(ids) > 0:
        ids_tuple = tuple(ids)
        ids.clear()
        response = get_multiple_field_information(bearer_token_simple, endpoint_name, limit, *ids_tuple)
        _add_data_to_database(table_name, response)


def _add_data_to_database(table_name: Table, response) -> None:

    global db

    if table_name == Table.TRACK_INFORMATION:
        log.debug('Adding track information to database')
        for entry in response['tracks']:
            log.debug(f"Adding track: {entry['name']}")
            db.add_row(table_name, (entry['id'], entry['name'], entry['duration_ms'], entry['explicit'], entry['popularity']))

    elif table_name == Table.ALBUM_INFORMATION:
        log.debug('Adding album information to database')
        for entry in response['albums']:
            log.debug(f"Adding album: {entry['name']}")
            try:
                release_year = entry['release_date'][:4]
            except Exception:
                release_year = ""
            db.add_row(table_name, (entry['id'], entry['name'], entry['album_type'], entry['total_tracks'], release_year, entry['label']))

    elif table_name == Table.ARTIST_INFORMATION:
        log.debug('Adding artist information to database')
        for entry in response['artists']:
            log.debug(f"Adding artist: {entry['name']}")
            try:
                genre = entry['genres'][0]
            except IndexError:
                genre = ""
            db.add_row(Table.ARTIST_INFORMATION, (entry['id'], entry['name'], entry['followers']['total'], genre, entry['popularity']))
