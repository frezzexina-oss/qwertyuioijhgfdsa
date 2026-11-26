from database import Database
from models import Project, Task


class TaskManager:
    def __init__(self):
        self.database = Database()

    def get_projects(self):
        rows = self.database.get_projects()
        return [
            Project(id=row[0], name=row[1])
            for row in rows
        ]

    def add_project(self, name):
        return self.database.add_project(name)

    def get_tasks(self):
        rows = self.database.get_tasks()
        return [
            Task(
                id=row[0],
                title=row[1],
                description=row[2],
                project_id=row[3],
                project_name=row[4],
                status=row[5],
                deadline=row[6]
            )
            for row in rows
        ]

    def add_task(self, title, description, project_id, status, deadline):
        return self.database.add_task(
            title, description, project_id, status, deadline
        )

    def update_task(self, task_id, title, description,
                    project_id, status, deadline):
        self.database.update_task(
            task_id, title, description,
            project_id, status, deadline
        )

    def delete_task(self, task_id):
        self.database.delete_task(task_id)

    def close(self):
        self.database.close()
