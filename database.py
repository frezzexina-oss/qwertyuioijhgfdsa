
import sqlite3


class Database:
    def __init__(self, filename="tasks.db"):
        self.connection = sqlite3.connect(filename)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self):
        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                project_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                deadline TEXT DEFAULT '',
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        """)

        cursor.execute(
            "INSERT OR IGNORE INTO projects (name) VALUES (?)",
            ("Загальний",)
        )

        self.connection.commit()

    def add_project(self, name):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO projects (name) VALUES (?)",
            (name,)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_projects(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name FROM projects ORDER BY name")
        return cursor.fetchall()

    def add_task(self, title, description, project_id, status, deadline):
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO tasks
            (title, description, project_id, status, deadline)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, project_id, status, deadline))
        self.connection.commit()
        return cursor.lastrowid

    def get_tasks(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT tasks.id, tasks.title, tasks.description,
                   tasks.project_id, projects.name,
                   tasks.status, tasks.deadline
            FROM tasks
            JOIN projects ON tasks.project_id = projects.id
            ORDER BY tasks.id DESC
        """)
        return cursor.fetchall()

    def update_task(self, task_id, title, description,
                    project_id, status, deadline):
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE tasks
            SET title = ?, description = ?, project_id = ?,
                status = ?, deadline = ?
            WHERE id = ?
        """, (title, description, project_id, status, deadline, task_id))
        self.connection.commit()

    def delete_task(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.connection.commit()

    def close(self):
        self.connection.close()
