import sqlite3

DB_FILE = "audio_fingerprint.db"

class DbHelper:
    def __init__(self):
        self.conn = self.create_connection(DB_FILE)

        self.songs_table = "songs"
        self.seq_hashes_table = "seq_hashes"
        self.window_hashes = "win_hashes"
        self.anchor_hashes = "anc_hashes"

        self.create_tables()

    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except sqlite3.Error as e:
            print(e)

    def create_tables(self):
        c = self.conn.cursor()

        sql = 'create table if not exists ' + self.songs_table + \
              ' (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)'
        c.execute(sql)

        sql = 'create table if not exists ' + self.seq_hashes_table + \
              ' (song_id INTEGER, hash BLOB, time INTEGER)'
        c.execute(sql)

        sql = 'create table if not exists ' + self.window_hashes + \
              ' (song_id INTEGER, hash BLOB, time INTEGER)'
        c.execute(sql)

        sql = 'create table if not exists ' + self.anchor_hashes + \
              ' (song_id INTEGER, hash BLOB, time INTEGER)'
        c.execute(sql)


        self.conn.commit()

    def insert_song(self, song_name):
        """
        Inserts song to DB
        :param song_name:
        :return: song_id
        """
        c = self.conn.cursor()
        sql = ''' SELECT id FROM songs WHERE name = ?'''
        c.execute(sql, [song_name])
        result = c.fetchone()
        if result:
            return result[0]

        sql = ''' INSERT INTO songs (name) VALUES (?) '''
        c.execute(sql, [song_name])
        self.conn.commit()
        return c.lastrowid

    def count_duplicate_hashes(self, table):
        c = self.conn.cursor()
        sql = '''SELECT SUM(count) FROM (SELECT COUNT(hash) as count 
                  FROM ? GROUP BY hash HAVING COUNT(*) > 1)'''
        c.execute(sql, [table])
        result = c.fetchone()

        if result:
            return result[0]
        else:
            return 0

    def delete_duplicate_hashes(self, table):
        "DELETE FROM " + table + \
        " WHERE hash in (SELECT  hash FROM " + table + \
        " GROUP BY hash HAVING COUNT(*) > 1);"

    def get_seq_hash_count(self, hash):
        c = self.conn.cursor()
        sql = '''SELECT COUNT(*) FROM seq_hashes WHERE hash = ?'''
        c.execute(sql, [hash])

        result = c.fetchone()
        return result[0]

    def get_seq_hash_count_by_song(self, hash, song_id):
        c = self.conn.cursor()
        sql = '''SELECT COUNT(*) FROM seq_hashes WHERE hash = ? and song_id = ?'''
        c.execute(sql, [hash, song_id])

        result = c.fetchone()
        return result[0]

    def get_win_hash_count(self, hash):
        c = self.conn.cursor()
        sql = '''SELECT COUNT(*) FROM win_hashes WHERE hash = ?'''
        c.execute(sql, [hash])

        result = c.fetchone()
        return result[0]

    def get_anc_hash_count(self, hash):
        c = self.conn.cursor()
        sql = '''SELECT COUNT(*) FROM anc_hashes WHERE hash = ?'''
        c.execute(sql, [hash])

        result = c.fetchone()
        return result[0]

    def get_win_hash_count_by_song(self, hash, song_id):
        c = self.conn.cursor()
        sql = '''SELECT COUNT(*) FROM win_hashes WHERE hash = ? and song_id = ?'''
        c.execute(sql, [hash, song_id])

        result = c.fetchone()
        return result[0]

    def get_anc_hash_count_by_song(self, hash, song_id):
        c = self.conn.cursor()
        sql = '''SELECT COUNT(*) FROM anc_hashes WHERE hash = ? and song_id = ?'''
        c.execute(sql, [ hash, song_id])

        result = c.fetchone()
        return result[0]

    def get_song_id(self, song_name):
        c = self.conn.cursor()
        sql = '''SELECT id FROM songs WHERE name = ?'''
        c.execute(sql, [song_name])

        result = c.fetchone()
        return result[0]

    def insert_seq_hash(self, song_id, hash, time):
        c = self.conn.cursor()
        sql = ''' INSERT INTO seq_hashes (song_id, hash, time) VALUES (?, ?, ?) '''
        c.execute(sql, [song_id, hash, time])
        self.conn.commit()
        pass

    def insert_win_hash(self, song_id, hash, time):
        c = self.conn.cursor()
        sql = ''' INSERT INTO win_hashes (song_id, hash, time) VALUES (?, ?, ?) '''
        c.execute(sql, [song_id, hash, time])
        self.conn.commit()
        pass

    def insert_anchor_hash(self, song_id, hash, time):
        c = self.conn.cursor()
        sql = ''' INSERT INTO anc_hashes (song_id, hash, time) VALUES (?, ?, ?) '''
        c.execute(sql, [song_id, hash, time])
        self.conn.commit()
        pass

    def insert_anc_bulk(self, song_id, hashes):
        c = self.conn.cursor()
        sql = ''' INSERT INTO anc_hashes (song_id, hash, time) VALUES (?, ?, ?) '''

        c.execute('BEGIN TRANSACTION')
        for hsh in hashes:
            c.execute(sql, [song_id, hsh[0], hsh[1]])
        c.execute('COMMIT')

    def drop_tables(self):
        c = self.conn.cursor()
        sql = 'drop table ' + self.songs_table
        c.execute(sql)
        sql = 'drop table ' + self.seq_hashes_table
        c.execute(sql)
        sql = 'drop table ' + self.anchor_hashes
        c.execute(sql)
        self.conn.commit()


