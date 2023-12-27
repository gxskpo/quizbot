import sqlite3
import typing as t


class DataBase:
    def __init__(self, connection_or_path: t.Union[sqlite3.Connection, str], **kwargs):
        if isinstance(connection_or_path, sqlite3.Connection):
            self.connection = connection_or_path
        elif isinstance(connection_or_path, str):
            self.connection = sqlite3.connect(connection_or_path, **kwargs)
        else:
            raise ValueError("Invalid connection or path")

    def read(self, query):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            return "Error: {}".format(e)

    def execute(self, query, *args, **kwargs) -> int:
        cursor = self.connection.cursor()
        cursor.execute(query, *args, **kwargs)
        self.connection.commit()
        inserted_id = cursor.lastrowid
        return inserted_id
