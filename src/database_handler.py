import sqlite3
from enum import Enum


class Table(Enum):
    TRACK_INFORMATION = "track_information"
    ARTIST_INFORMATION = "artist_information"
    ALBUM_INFORMATION = "album_information"
    TRACK_ATTRIBUTES = "track_attributes"
    RECENTLY_PLAYED = "recently_played"


class Database:
    """
    A class to handle the database connection and operations
    """

    def __init__(self, db_name):
        """Initialize the connection to the database"""
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create the tables in the database"""

        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {Table.TRACK_INFORMATION.value} (
            track_id TEXT PRIMARY KEY,
            title TEXT
        );
        ''')

        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {Table.ARTIST_INFORMATION.value} (
            artist_id TEXT PRIMARY KEY,
            artist_name TEXT
        );
        ''')

        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {Table.ALBUM_INFORMATION.value} (
            album_id TEXT PRIMARY KEY,
            album_name TEXT
        );
        ''')

        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {Table.TRACK_ATTRIBUTES.value} (
            track_id TEXT PRIMARY KEY,
            attribute_name TEXT,
            attribute_value TEXT
        );
        ''')

        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {Table.RECENTLY_PLAYED.value} (
            played_at TIMESTAMP PRIMARY KEY,
            track_id TEXT,
            artist_id TEXT,
            album_id TEXT,
            FOREIGN KEY (track_id) REFERENCES {Table.TRACK_INFORMATION.value}(track_id),
            FOREIGN KEY (artist_id) REFERENCES {Table.ARTIST_INFORMATION.value}(artist_id),
            FOREIGN KEY (album_id) REFERENCES {Table.ALBUM_INFORMATION.value}(album_id)
        );
        ''')

        # Commit the changes
        self.conn.commit()

    def add_row(self, table: Table, values):
        """Add a new row into the specified table"""
        try:
            placeholders = ', '.join(['?'] * len(values))
            query = f"INSERT INTO {table.value} VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.conn.commit()
        except Exception as e:
            print(f"Error: {e}")

    def read_all_rows(self, table: Table, column: str = "*"):
        """Read all rows from the specified table"""
        self.cursor.execute(f"SELECT {column} FROM {table.value}")
        rows = self.cursor.fetchall()
        return rows

    def close(self):
        """Close the database connection"""
        self.conn.close()

    def get_total_overview(self) -> list:
        """Retrieve a total overview of all recently played songs with full details"""
        try:
            # Join recently_played with track_information, artist_information, and album_information
            query = f'''
            SELECT rp.played_at,
                   ti.track_id,
                   ti.title,
                   ai.artist_id,
                   ai.artist_name,
                   al.album_id,
                   al.album_name
            FROM {Table.RECENTLY_PLAYED.value} rp
            JOIN {Table.TRACK_INFORMATION.value} ti ON rp.track_id = ti.track_id
            JOIN {Table.ARTIST_INFORMATION.value} ai ON rp.artist_id = ai.artist_id
            JOIN {Table.ALBUM_INFORMATION.value} al ON rp.album_id = al.album_id
            ORDER BY rp.played_at DESC
            '''
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error retrieving total overview: {e}")
            return []

            """
            print(rows)

            if rows:
                print(f"{'Played At':<20} {'Track ID':<20} {'Track Title':<50} {'Artist ID':<20} {'Artist Name':<50} {'Album ID':<20} {'Album Name':<50}")
                print("-" * 160)
                for row in rows:
                    played_at, track_id, title, artist_id, artist_name, album_id, album_name = row
                    print(f"{played_at:<20} {track_id:<20} {title:<50} {artist_id:<20} {artist_name:<50} {album_id:<20} {album_name:<50}")
            else:
                print("No recently played songs found.")
        except Exception as e:
            print(f"Error retrieving total overview: {e}")"""
