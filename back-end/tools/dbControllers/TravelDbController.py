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
        self.c.execute('''CREATE TABLE IF NOT EXISTS TRAVEL_DIARY_SHARE
        (ID         INTEGER  PRIMARY KEY  AUTOINCREMENT,
        DIARY_ID   INTEGER  NOT NULL,
        USERNAME   TEXT     NOT NULL,
        CREATED_AT TEXT     NOT NULL,
        UNIQUE (DIARY_ID, USERNAME),
        FOREIGN KEY (DIARY_ID) REFERENCES TRAVEL_DIARY(ID))''')
        self.ensureDiaryViewColumns()
        self.conn.commit()

    def _base_db_connection(self):
        try:
            return sqlite3.connect('datas/base.sqlite')
        except:
            return sqlite3.connect('back-end/datas/base.sqlite')

    def userExists(self, username):
        if not username:
            return False
        base_conn = self._base_db_connection()
        try:
            cursor = base_conn.cursor()
            row = cursor.execute('SELECT USERNAME FROM USER WHERE USERNAME=(?)', [username]).fetchone()
            return row is not None
        except:
            return False
        finally:
            base_conn.close()

    def getExistingUsers(self, usernames):
        filtered = []
        for username in usernames:
            if isinstance(username, str):
                text = username.strip()
                if text:
                    filtered.append(text)
        if not filtered:
            return []
        base_conn = self._base_db_connection()
        try:
            cursor = base_conn.cursor()
            placeholders = ','.join(['?'] * len(filtered))
            rows = cursor.execute(
                f'SELECT USERNAME FROM USER WHERE USERNAME IN ({placeholders})',
                filtered
            ).fetchall()
            return [row[0] for row in rows]
        except:
            return []
        finally:
            base_conn.close()

    def getAllUsers(self):
        base_conn = self._base_db_connection()
        try:
            cursor = base_conn.cursor()
            rows = cursor.execute('SELECT USERNAME FROM USER ORDER BY USERNAME ASC').fetchall()
            return [row[0] for row in rows]
        except:
            return []
        finally:
            base_conn.close()

    def isDiaryOwner(self, diary_id, username):
        query = '''SELECT ID FROM TRAVEL_DIARY WHERE ID=(?) AND USERNAME=(?)'''
        row = self.c.execute(query, [diary_id, username]).fetchone()
        return row is not None

    def canAccessDiary(self, diary_id, username):
        if self.isDiaryOwner(diary_id, username):
            return True
        query = '''SELECT ID FROM TRAVEL_DIARY_SHARE WHERE DIARY_ID=(?) AND USERNAME=(?)'''
        row = self.c.execute(query, [diary_id, username]).fetchone()
        return row is not None

    def getDiarySharers(self, diary_id):
        query = '''SELECT USERNAME FROM TRAVEL_DIARY_SHARE
                   WHERE DIARY_ID=(?) ORDER BY USERNAME ASC'''
        rows = self.c.execute(query, [diary_id]).fetchall()
        return [row[0] for row in rows]

    def replaceDiarySharers(self, diary_id, owner_username, sharers):
        if not self.isDiaryOwner(diary_id, owner_username):
            return {'ok': False, 'reason': 'forbidden', 'invalid_users': []}

        normalized = []
        for username in sharers:
            if isinstance(username, str):
                name = username.strip()
                if name and name != owner_username and name not in normalized:
                    normalized.append(name)

        existing = self.getExistingUsers(normalized)
        existing_set = set(existing)
        invalid_users = [name for name in normalized if name not in existing_set]
        if invalid_users:
            return {'ok': False, 'reason': 'invalid_users', 'invalid_users': invalid_users}

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute('DELETE FROM TRAVEL_DIARY_SHARE WHERE DIARY_ID=(?)', [diary_id])
        for username in normalized:
            self.c.execute(
                'INSERT INTO TRAVEL_DIARY_SHARE (DIARY_ID, USERNAME, CREATED_AT) VALUES (?, ?, ?)',
                [diary_id, username, now]
            )
        self.c.execute('UPDATE TRAVEL_DIARY SET UPDATED_AT=(?) WHERE ID=(?)', [now, diary_id])
        self.conn.commit()
        return {'ok': True, 'invalid_users': []}

    def ensureDiaryViewColumns(self):
        cursor = self.c.execute('PRAGMA table_info(TRAVEL_DIARY)')
        columns = [row[1] for row in cursor]
        if 'VIEW_LNG' not in columns:
            self.c.execute('ALTER TABLE TRAVEL_DIARY ADD COLUMN VIEW_LNG REAL')
        if 'VIEW_LAT' not in columns:
            self.c.execute('ALTER TABLE TRAVEL_DIARY ADD COLUMN VIEW_LAT REAL')
        if 'VIEW_ZOOM' not in columns:
            self.c.execute('ALTER TABLE TRAVEL_DIARY ADD COLUMN VIEW_ZOOM REAL')
        if 'TRIP_TIME' not in columns:
            self.c.execute('ALTER TABLE TRAVEL_DIARY ADD COLUMN TRIP_TIME TEXT')
        if 'SUMMARY' not in columns:
            self.c.execute('ALTER TABLE TRAVEL_DIARY ADD COLUMN SUMMARY TEXT')

    # ---- TRAVEL_DIARY CRUD ----

    def getDiaries(self, username):
        query = '''SELECT d.ID, d.USERNAME, d.NAME, d.VIEW_LNG, d.VIEW_LAT, d.VIEW_ZOOM, d.TRIP_TIME, d.SUMMARY,
                          d.CREATED_AT, d.UPDATED_AT,
                          CASE WHEN d.USERNAME = ? THEN 1 ELSE 0 END AS IS_OWNER
                   FROM TRAVEL_DIARY d
                   LEFT JOIN TRAVEL_DIARY_SHARE s
                     ON d.ID = s.DIARY_ID AND s.USERNAME = ?
                   WHERE d.USERNAME = ? OR s.USERNAME = ?
                   ORDER BY d.UPDATED_AT DESC'''
        cursor = self.c.execute(query, [username, username, username, username])
        diaries = []
        for row in cursor:
            diary_id = row[0]
            is_owner = bool(row[10])
            diaries.append({
                'id': row[0],
                'username': row[1],
                'name': row[2],
                'view_lng': row[3],
                'view_lat': row[4],
                'view_zoom': row[5],
                'trip_time': row[6],
                'summary': row[7],
                'created_at': row[8],
                'updated_at': row[9],
                'is_owner': is_owner,
                'can_delete': is_owner,
                'can_manage_share': is_owner,
                'sharers': self.getDiarySharers(diary_id)
            })
        return diaries

    def createDiary(self, username, name, trip_time='', summary=''):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = '''INSERT INTO TRAVEL_DIARY (USERNAME, NAME, TRIP_TIME, SUMMARY, CREATED_AT, UPDATED_AT)
                   VALUES (?, ?, ?, ?, ?, ?)'''
        self.c.execute(query, [username, name, trip_time, summary, now, now])
        self.conn.commit()
        return self.c.lastrowid

    def updateDiary(self, diary_id, username, name, trip_time='', summary=''):
        if not self.canAccessDiary(diary_id, username):
            return False
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = '''UPDATE TRAVEL_DIARY SET NAME=(?), TRIP_TIME=(?), SUMMARY=(?), UPDATED_AT=(?) WHERE ID=(?)'''
        self.c.execute(query, [name, trip_time, summary, now, diary_id])
        self.conn.commit()
        return self.c.rowcount > 0

    def getDiaryView(self, diary_id, username):
        query = '''SELECT VIEW_LNG, VIEW_LAT, VIEW_ZOOM FROM TRAVEL_DIARY
                   WHERE ID=(?)'''
        if not self.canAccessDiary(diary_id, username):
            return None
        row = self.c.execute(query, [diary_id]).fetchone()
        if not row:
            return None
        if row[0] is None or row[1] is None or row[2] is None:
            return None
        return {'center': [row[0], row[1]], 'zoom': row[2]}

    def updateDiaryView(self, diary_id, username, lng, lat, zoom):
        if not self.canAccessDiary(diary_id, username):
            return False
        query = '''UPDATE TRAVEL_DIARY
                   SET VIEW_LNG=(?), VIEW_LAT=(?), VIEW_ZOOM=(?)
                   WHERE ID=(?)'''
        self.c.execute(query, [lng, lat, zoom, diary_id])
        self.conn.commit()
        return self.c.rowcount > 0

    def deleteDiary(self, diary_id, username):
        if not self.isDiaryOwner(diary_id, username):
            return False
        self.c.execute('DELETE FROM TRAVEL_PLACE WHERE DIARY_ID=(?)', [diary_id])
        self.c.execute('DELETE FROM TRAVEL_DIARY_SHARE WHERE DIARY_ID=(?)', [diary_id])
        self.c.execute('DELETE FROM TRAVEL_DIARY WHERE ID=(?) AND USERNAME=(?)', [diary_id, username])
        self.conn.commit()
        return self.c.rowcount > 0

    # ---- TRAVEL_PLACE CRUD ----

    def getPlaces(self, diary_id, username):
        if not self.canAccessDiary(diary_id, username):
            return []
        query = '''SELECT p.* FROM TRAVEL_PLACE p
                   WHERE p.DIARY_ID=(?)
                   ORDER BY p.CREATED_AT ASC'''
        cursor = self.c.execute(query, [diary_id])
        return [{'id': row[0], 'diary_id': row[1], 'poi_id': row[2],
                 'name': row[3], 'address': row[4], 'lng': row[5],
                 'lat': row[6], 'tel': row[7], 'type': row[8],
                 'typecode': row[9], 'note': row[10],
                 'created_at': row[11]} for row in cursor]

    def addPlace(self, diary_id, username, place):
        if not self.canAccessDiary(diary_id, username):
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
        if not self.canAccessDiary(diary_id, username):
            return False
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute('DELETE FROM TRAVEL_PLACE WHERE ID=(?) AND DIARY_ID=(?)',
                       [place_id, diary_id])
        self.c.execute('UPDATE TRAVEL_DIARY SET UPDATED_AT=(?) WHERE ID=(?)',
                       [now, diary_id])
        self.conn.commit()
        return True

    def updatePlaceTypecode(self, place_id, diary_id, username, typecode):
        if not self.canAccessDiary(diary_id, username):
            return False
        self.c.execute('UPDATE TRAVEL_PLACE SET TYPECODE=(?) WHERE ID=(?) AND DIARY_ID=(?)',
                       [typecode, place_id, diary_id])
        self.conn.commit()
        return True

    def updatePlaceNote(self, place_id, diary_id, username, note):
        if not self.canAccessDiary(diary_id, username):
            return False
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute('UPDATE TRAVEL_PLACE SET NOTE=(?) WHERE ID=(?) AND DIARY_ID=(?)',
                       [note, place_id, diary_id])
        self.c.execute('UPDATE TRAVEL_DIARY SET UPDATED_AT=(?) WHERE ID=(?)',
                       [now, diary_id])
        self.conn.commit()
        return True
