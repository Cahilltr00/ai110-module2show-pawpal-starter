from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Task:
    type: str
    duration: int          # minutes
    cost: float
    priority: str          # e.g. "low", "medium", "high"
    scheduled_date: Optional[date] = None
    completed: bool = False

    def create(self) -> None:
        pass

    def schedule(self, scheduled_date: date) -> None:
        pass

    def is_overdue(self) -> bool:
        pass

    def complete(self) -> None:
        pass


@dataclass
class Health:
    health_id: str
    animal_id: str
    record_type: str       # e.g. "vet_visit", "symptom", "vaccine"
    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)

    def log_vet_visit(self, notes: str) -> None:
        pass

    def log_symptom(self, symptom: str) -> None:
        pass

    def get_vaccine_record(self) -> dict:
        pass

    def is_vaccine_due(self) -> bool:
        pass


@dataclass
class Animal:
    type: str
    name: str
    age: int
    _tasks: list[Task] = field(default_factory=list, repr=False)
    _health_records: list[Health] = field(default_factory=list, repr=False)

    def get_profile(self) -> dict:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass

    def add_health_record(self, record: Health) -> None:
        pass

    def get_health_record(self) -> list[Health]:
        pass


class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age
        self._pets: list[Animal] = []

    def add_pet(self, animal: Animal) -> None:
        pass

    def remove_pet(self, animal: Animal) -> None:
        pass

    def get_pets(self) -> list[Animal]:
        pass
