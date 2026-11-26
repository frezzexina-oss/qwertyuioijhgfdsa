from dataclasses import dataclass


@dataclass
class Project:
    id: int
    name: str


@dataclass
class Task:
    id: int
    title: str
    description: str
    project_id: int
    project_name: str
    status: str
    deadline: str
