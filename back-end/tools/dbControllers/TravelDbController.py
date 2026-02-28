import sqlite3
from datetime import datetime


class TravelDbController():
    def __init__(self):
        try:
            self.conn = sqlite3.connect('datas/travel.sqlite')
        except:
            self.conn = sqlite3.connect('back-end/datas/travel.sqlite')
        self.c = self.conn.cursor()
        self.initDb()

    def __del__(self):
        self.conn.close()

    def initDb(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS TRAVEL_DIARY
        (ID         INTEGER  PRIMARY KEY  AUTOINCREMENT,
        USERNAME   TEXT     NOT NULL,
        NAME       TEXT     NOT NULL,
        VIEW_LNG   REAL,
        VIEW_LAT   REAL,
        VIEW_ZOOM  REAL,
        CREATED_AT TEXT     NOT NULL,
        UPDATED_AT TEXT     NOT NULL)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS TRAVEL_PLACE
        (ID         INTEGER  PRIMARY KEY  AUTOINCREMENT,
        DIARY_ID   INTEGER  NOT NULL,
        POI_ID     TEXT     NOT NULL,
        NAME       TEXT     NOT NULL,
        ADDRESS    TEXT,
        LNG        REAL     NOT NULL,
        LAT        REAL     NOT NULL,
        TEL        TEXT,
        TYPE       TEXT,
        TYPECODE   TEXT,
        NOTE       TEXT,
        CREATED_AT TEXT     NOT NULL,
        FOREIGN KEY (DIARY_ID) REFERENCES TRAVEL_DIARY(ID))''')
        self.ensureDiaryViewColumns()
        self.conn.commit()

    def ensureDiaryViewColumns(self):
        cursor = self.c.execute('PRAGMA table_info(TRAVEL_DIARY)')
        columns = [row[1] for row in cursor]
        if 'VIEW_LNG' not in columns:
            self.c.execute('ALTER TABLE TRAVEL_DIARY ADD COLUMN VIEW_LNG REAL')
        if 'VIEW_LAT' not in columns:
            self.c.execute('ALTER TABLE TRAVEL_DIARY ADD COLUMN VIEW_LAT REAL')
        if 'VIEW_ZOOM' not in columns:
            self.c.execute('ALTER TABLE TRAVEL_DIARY ADD COLUMN VIEW_ZOOM REAL')

    # ---- TRAVEL_DIARY CRUD ----

    def getDiaries(self, username):
        query = '''SELECT ID, USERNAME, NAME, VIEW_LNG, VIEW_LAT, VIEW_ZOOM, CREATED_AT, UPDATED_AT
                   FROM TRAVEL_DIARY WHERE USERNAME=(?) ORDER BY UPDATED_AT DESC'''
        cursor = self.c.execute(query, [username])
        return [{'id': row[0], 'username': row[1], 'name': row[2],
                 'view_lng': row[3], 'view_lat': row[4], 'view_zoom': row[5],
                 'created_at': row[6], 'updated_at': row[7]} for row in cursor]

    def createDiary(self, username, name):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = '''INSERT INTO TRAVEL_DIARY (USERNAME, NAME, CREATED_AT, UPDATED_AT)
                   VALUES (?, ?, ?, ?)'''
        self.c.execute(query, [username, name, now, now])
        self.conn.commit()
        return self.c.lastrowid

    def updateDiary(self, diary_id, username, name):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = '''UPDATE TRAVEL_DIARY SET NAME=(?), UPDATED_AT=(?)
                   WHERE ID=(?) AND USERNAME=(?)'''
        self.c.execute(query, [name, now, diary_id, username])
        self.conn.commit()

    def getDiaryView(self, diary_id, username):
        query = '''SELECT VIEW_LNG, VIEW_LAT, VIEW_ZOOM FROM TRAVEL_DIARY
                   WHERE ID=(?) AND USERNAME=(?)'''
        row = self.c.execute(query, [diary_id, username]).fetchone()
        if not row:
            return None
        if row[0] is None or row[1] is None or row[2] is None:
            return None
        return {'center': [row[0], row[1]], 'zoom': row[2]}

    def updateDiaryView(self, diary_id, username, lng, lat, zoom):
        query = '''UPDATE TRAVEL_DIARY
                   SET VIEW_LNG=(?), VIEW_LAT=(?), VIEW_ZOOM=(?)
                   WHERE ID=(?) AND USERNAME=(?)'''
        self.c.execute(query, [lng, lat, zoom, diary_id, username])
        self.conn.commit()
        return self.c.rowcount > 0

    def deleteDiary(self, diary_id, username):
        self.c.execute('DELETE FROM TRAVEL_PLACE WHERE DIARY_ID=(?)', [diary_id])
        self.c.execute('DELETE FROM TRAVEL_DIARY WHERE ID=(?) AND USERNAME=(?)',
                       [diary_id, username])
        self.conn.commit()

    # ---- TRAVEL_PLACE CRUD ----

    def getPlaces(self, diary_id, username):
        query = '''SELECT p.* FROM TRAVEL_PLACE p
                   JOIN TRAVEL_DIARY d ON p.DIARY_ID = d.ID
                   WHERE p.DIARY_ID=(?) AND d.USERNAME=(?)
                   ORDER BY p.CREATED_AT ASC'''
        cursor = self.c.execute(query, [diary_id, username])
        return [{'id': row[0], 'diary_id': row[1], 'poi_id': row[2],
                 'name': row[3], 'address': row[4], 'lng': row[5],
                 'lat': row[6], 'tel': row[7], 'type': row[8],
                 'typecode': row[9], 'note': row[10],
                 'created_at': row[11]} for row in cursor]

    def addPlace(self, diary_id, username, place):
        check = '''SELECT d.ID FROM TRAVEL_DIARY d
                   WHERE d.ID=(?) AND d.USERNAME=(?)'''
        if not self.c.execute(check, [diary_id, username]).fetchone():
            return None
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = '''INSERT INTO TRAVEL_PLACE
                   (DIARY_ID, POI_ID, NAME, ADDRESS, LNG, LAT, TEL, TYPE, TYPECODE, NOTE, CREATED_AT)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        self.c.execute(query, [
            diary_id, place.get('poi_id', ''),
            place.get('name', ''), place.get('address', ''),
            place.get('lng', 0), place.get('lat', 0),
            place.get('tel', ''), place.get('type', ''),
            place.get('typecode', ''), place.get('note', ''), now
        ])
        # Update diary's updated_at
        self.c.execute('UPDATE TRAVEL_DIARY SET UPDATED_AT=(?) WHERE ID=(?)',
                       [now, diary_id])
        self.conn.commit()
        return self.c.lastrowid

    def deletePlace(self, place_id, diary_id, username):
        check = '''SELECT d.ID FROM TRAVEL_DIARY d
                   WHERE d.ID=(?) AND d.USERNAME=(?)'''
        if not self.c.execute(check, [diary_id, username]).fetchone():
            return False
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute('DELETE FROM TRAVEL_PLACE WHERE ID=(?) AND DIARY_ID=(?)',
                       [place_id, diary_id])
        self.c.execute('UPDATE TRAVEL_DIARY SET UPDATED_AT=(?) WHERE ID=(?)',
                       [now, diary_id])
        self.conn.commit()
        return True

    def updatePlaceTypecode(self, place_id, diary_id, username, typecode):
        check = '''SELECT d.ID FROM TRAVEL_DIARY d
                   WHERE d.ID=(?) AND d.USERNAME=(?)'''
        if not self.c.execute(check, [diary_id, username]).fetchone():
            return False
        self.c.execute('UPDATE TRAVEL_PLACE SET TYPECODE=(?) WHERE ID=(?) AND DIARY_ID=(?)',
                       [typecode, place_id, diary_id])
        self.conn.commit()
        return True
