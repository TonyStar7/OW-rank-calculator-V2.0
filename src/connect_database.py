import sqlite3
import os

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PAR_DIR = os.path.dirname(FILE_DIR)
connection = sqlite3.connect(os.path.join(PAR_DIR, "data", "database.db"))

cursor = connection.cursor()

def create_player_table ():
    database = 'CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY,' \
    ' tag TEXT UNIQUE,' \
    ' username TEXT,' \
    ' tank TEXT,' \
    ' tank_division TEXT,' \
    ' damage TEXT,' \
    ' damage_division TEXT,' \
    ' support TEXT,' \
    ' support_division TEXT,' \
    ' open_queue TEXT,' \
    ' open_queue_division TEXT,' \
    ' owner TEXT,' \
    ' date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP)' \
    
    cursor.execute(database)
    connection.commit()

def add_player(player_data):
    sql = 'INSERT INTO players (tag, username, tank, tank_division, damage, damage_division, support, support_division, open_queue, open_queue_division, owner, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    try:
        cursor.execute(sql, (
            player_data["tag"],
            player_data["username"],
            player_data.get("tank", "Unranked"),
            player_data.get("tank_division", "N/A"),
            player_data.get("damage", "Unranked"),
            player_data.get("damage_division", "N/A"),
            player_data.get("support", "Unranked"),
            player_data.get("support_division", "N/A"),
            player_data.get("open_queue", "Unranked"),
            player_data.get("open_queue_division", "N/A"),
            player_data["owner"],
            player_data["date_added"],
        ))
        connection.commit()
    except sqlite3.IntegrityError as e:
        print(f"Error adding player: {e}")
        return False
    return True

def delete_player(tag):
    sql = 'DELETE FROM players WHERE tag=?'
    cursor.execute(sql, (tag,))
    connection.commit()

def update_player(player_data):
    sql = 'UPDATE players SET username=?, tank=?, tank_division=?, damage=?, damage_division=?, support=?, support_division=?, open_queue=?, open_queue_division=?, date_added=? WHERE tag=?'
    cursor.execute(sql, (
        player_data["username"],
        player_data.get("tank", "Unranked"),
        player_data.get("tank_division", "N/A"),
        player_data.get("damage", "Unranked"),
        player_data.get("damage_division", "N/A"),
        player_data.get("support", "Unranked"),
        player_data.get("support_division", "N/A"),
        player_data.get("open_queue", "Unranked"),
        player_data.get("open_queue_division", "N/A"),
        player_data["date_added"],
        player_data["tag"]
    ))
    connection.commit()

def get_all_players():
    sql = 'SELECT * FROM players ORDER BY id'
    cursor.execute(sql)
    return cursor.fetchall()


# Ensure table exists before any operations
create_player_table()



def print_players(): 
    cursor.execute('SELECT * FROM players')
    print(cursor.fetchall())

def add_column(column_name, column_type):
    sql = f'ALTER TABLE players ADD COLUMN {column_name} {column_type}'
    cursor.execute(sql)
    connection.commit()

def DELETE_TABLE ():
    delete = "DROP TABLE players"
    cursor.execute(delete)
    connection.commit()

#DELETE_TABLE()
