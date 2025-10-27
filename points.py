import sqlite3

class PointsDB:
    def __init__(self, db_path="points.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS points (
                    username TEXT PRIMARY KEY,
                    points INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def addPoints(self, user, amount):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO points (username, points) VALUES (?, 0)", (user,))
            cursor.execute("UPDATE points SET points = points + ? WHERE username = ?", (amount, user))
            conn.commit()

    def removePoints(self, user, amount):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE points SET points = points - ? WHERE username = ?", (amount, user))
            conn.commit()

    def getPoints(self, user):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT points FROM points WHERE username = ?", (user,))
            row = cursor.fetchone()
            return row[0] if row else 0
