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
        placeholders = ', '.join(['?'] * len(values))
        query = f"INSERT INTO {table.value} VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def read_all_rows(self, table: Table, column: str = "*"):
        """Read all rows from the specified table"""
        self.cursor.execute(f"SELECT {column} FROM {table.value}")
        rows = self.cursor.fetchall()
        return rows

    def close(self):
        """Close the database connection"""
        self.conn.close()
