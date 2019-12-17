import sqlite3
from sqlite3 import Error as sqlError


def create_connection():
    database = r"include/recipebook.db"
    conn = None
    try:
        conn = sqlite3.connect(database)
        return conn
    except sqlError as e:
        print(e)
    return conn


def create_table(conn):
    sql_recipe_table = """ CREATE TABLE IF NOT EXISTS recipes (
                        id integer PRIMARY KEY,
                        name text NOT NULL,
                        description TEXT,
                        tags TEXT,
                        prep_time TEXT,
                        cook_time TEXT,
                        ingredients TEXT,
                        amounts TEXT,
                        instructions TEXT,
                        rating INTEGER,
                        thumb BLOB,
                        image BLOB
                    ); """
    try:
        c = conn.cursor()
        c.execute(sql_recipe_table)
    except sqlError as e:
        print(e)