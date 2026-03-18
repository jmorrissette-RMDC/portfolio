import sqlite3

class TaskManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        self.conn.commit()

    def add_task(self, task_name):
        self.cursor.execute('INSERT INTO tasks (name) VALUES (?)', (task_name,))
        self.conn.commit()

    def delete_task(self, task_name):
        self.cursor.execute('DELETE FROM tasks WHERE name = ?', (task_name,))
        self.conn.commit()

    def get_tasks(self):
        self.cursor.execute('SELECT name FROM tasks ORDER BY id')
        return [row[0] for row in self.cursor.fetchall()]