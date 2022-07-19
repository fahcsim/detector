import sqlite3
import os


def create_db():

  if os.path.exists('data.db') == False:
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE DETECTIONS
                   ( label text, confidence integer, y_min integer, y_max integer, x_min integer, x_max integer, camera_id text, timestamp text, filename text)''')             
    con.commit()

  else:
    print("database already exists")
create_db()