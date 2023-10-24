import mysql.connector

class MySQLCursorDict(mysql.connector.cursor.MySQLCursor):
    def _row_to_python(self, rowdata, desc=None):
        row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
        if row:
            return dict(zip(self.column_names, row))
        return None

class ReplDBSQL(object):
    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
    
    def connect(self):
        conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.db,
            port=3307
        )
        return conn
    def commit(self, conn):
        conn.commit()

    def run(self, query, vals=()):
        conn = self.connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(query, vals)
        try:
            res = cur.fetchall()
        except:
            res = None
        conn.commit()
        conn.close()
        self.commit(conn)
        return res
    
    def clear(self):
        self.run('DROP TABLE views')