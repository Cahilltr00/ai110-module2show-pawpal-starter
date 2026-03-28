from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from typing import Optional
import uuid


# ---------------------------------------------------------------------------
# Task — represents a single pet care activity
# ---------------------------------------------------------------------------

@dataclass
class Task:
    type: str               # e.g. "feeding", "park", "vet_visit"
    duration: int           # minutes
    cost: float
    priority: str           # "low", "medium", "high"
    animal_id: str          # links task to an Animal
    scheduled_time: Optional[time] = None   # time of day this task should happen
    completed: bool = False
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def schedule(self, scheduled_time: time) -> None:
        """Set the time of day this task should happen."""
        self.scheduled_time = scheduled_time

    def is_overdue(self) -> bool:
        """Return True if the scheduled time has passed today and task is not complete."""
        if self.completed or self.scheduled_time is None:
            return False
        return datetime.now().time() > self.scheduled_time

    def complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


# ---------------------------------------------------------------------------
# Animal (Pet) — stores pet details and its own task list
# ---------------------------------------------------------------------------

@dataclass
class Animal:
    type: str               # e.g. "dog", "cat"
    name: str
    age: int                # years
    animal_id: int = field(default_factory=lambda: str(uuid.uuid4()))
    _tasks: list[Task] = field(default_factory=list, repr=False)
    _health_records: list[Health] = field(default_factory=list, repr=False)

    def get_profile(self) -> dict:
        """Return a summary of this pet's details."""
        return {
            "animal_id": self.animal_id,
            "type": self.type,
            "name": self.name,
            "age": self.age,
            "task_count": len(self._tasks),
        }

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self._tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self._tasks)

    def add_health_record(self, record: Health) -> None:
        """Attach a health record to this pet."""
        self._health_records.append(record)

    def get_health_record(self) -> list[Health]:
        """Return all health records for this pet."""
        return list(self._health_records)


# ---------------------------------------------------------------------------
# User (Owner) — manages multiple pets and provides access to their tasks
# ---------------------------------------------------------------------------

class User:
    def __init__(self, name: str, age: int) -> None:
        """Initialize a User with a name, age, and an empty pet list."""
        self.user_id: str = str(uuid.uuid4())
        self.name = name
        self.age = age
        self._pets: list[Animal] = []

    def add_pet(self, animal: Animal) -> None:
        """Register a new pet under this owner."""
        self._pets.append(animal)

    def remove_pet(self, animal: Animal) -> None:
        """Remove a pet from this owner's list."""
        self._pets.remove(animal)

    def get_pets(self) -> list[Animal]:
        """Return all pets owned by this user."""
        return list(self._pets)

    def print_daily_schedule(self) -> None:
        """Print today's schedule for all pets, grouped by pet and sorted by time."""
        today_str = datetime.now().strftime("%A, %B %d %Y")
        order = {"high": 0, "medium": 1, "low": 2}

        # Gather all incomplete tasks across every pet
        all_tasks = [
            t for animal in self._pets
            for t in animal.get_tasks()
            if not t.completed
        ]

        print(f"\n{'=' * 48}")
        print(f"  PawPal+ Daily Schedule — {today_str}")
        print(f"{'=' * 48}")

        if not all_tasks:
            print("  No tasks scheduled for today.")
            print(f"{'=' * 48}\n")
            return

        # Group by animal
        grouped: dict[str, list[Task]] = {}
        for task in all_tasks:
            grouped.setdefault(task.animal_id, []).append(task)

        animal_map = {a.animal_id: a for a in self._pets}

        for animal_id, tasks in grouped.items():
            animal = animal_map.get(animal_id)
            pet_label = f"{animal.name} ({animal.type})" if animal else animal_id
            print(f"\n  {pet_label}")
            print(f"  {'-' * (len(pet_label) + 2)}")

            # Sort by scheduled_time (None = no time set, shown last), then priority
            sorted_tasks = sorted(
                tasks,
                key=lambda t: (
                    t.scheduled_time or time.max,
                    order.get(t.priority, 9),
                ),
            )

            for task in sorted_tasks:
                overdue_flag = " [OVERDUE]" if task.is_overdue() else ""
                time_str = task.scheduled_time.strftime("%I:%M %p") if task.scheduled_time else "anytime"
                print(
                    f"    {time_str} [{task.priority.upper()}] {task.type}"
                    f" | {task.duration} min | ${task.cost:.2f}{overdue_flag}"
                )

        print(f"\n{'=' * 48}\n")


# ---------------------------------------------------------------------------
# Health (Scheduler) — the brain that organizes and manages tasks across pets
# ---------------------------------------------------------------------------

class Health:
    """
    Acts as the central scheduler for a user's pets.
    Logs health records per animal and surfaces task management
    methods that work across every animal in the roster.
    """

    def __init__(self) -> None:
        """Initialize the Health scheduler with an empty animal roster and record list."""
        self.health_id: str = str(uuid.uuid4())
        self._animals: list[Animal] = []
        # Each record: {health_id, animal_id, record_type, notes,
        #               vaccine_type, next_due_date, created_at}
        self._records: list[dict] = []

    # --- animal roster ---

    def register_animal(self, animal: Animal) -> None:
        """Add a pet to the scheduler's roster."""
        if animal not in self._animals:
            self._animals.append(animal)

    # --- health record methods ---

    def log_vet_visit(self, animal_id: str, notes: str) -> None:
        """Record a vet visit for a pet."""
        self._records.append({
            "health_id": str(uuid.uuid4()),
            "animal_id": animal_id,
            "record_type": "vet_visit",
            "notes": notes,
            "vaccine_type": None,
            "next_due_date": None,
            "created_at": date.today(),
        })

    def log_symptom(self, animal_id: str, symptom: str) -> None:
        """Log a symptom observed for a pet."""
        self._records.append({
            "health_id": str(uuid.uuid4()),
            "animal_id": animal_id,
            "record_type": "symptom",
            "notes": symptom,
            "vaccine_type": None,
            "next_due_date": None,
            "created_at": date.today(),
        })

    def get_vaccine_record(self, animal_id: str) -> list[dict]:
        """Return all vaccine records for a specific pet."""
        return [
            r for r in self._records
            if r["animal_id"] == animal_id and r["record_type"] == "vaccine"
        ]

    def is_vaccine_due(self, animal_id: str) -> bool:
        """Return True if any vaccine for this pet is due today or overdue."""
        for record in self.get_vaccine_record(animal_id):
            if record["next_due_date"] and date.today() >= record["next_due_date"]:
                return True
        return False

    # --- scheduler / brain methods ---

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all registered pets."""
        tasks = []
        for animal in self._animals:
            tasks.extend(animal.get_tasks())
        return tasks

    def get_overdue_tasks(self) -> list[Task]:
        """Return all incomplete tasks whose scheduled time has passed today."""
        return [t for t in self.get_all_tasks() if t.is_overdue()]

    def get_upcoming_tasks(self, hours: int = 2) -> list[Task]:
        """Return incomplete tasks scheduled within the next `hours` hours."""
        now = datetime.now().time()
        cutoff = (datetime.now() + timedelta(hours=hours)).time()
        return [
            t for t in self.get_all_tasks()
            if not t.completed and t.scheduled_time and now <= t.scheduled_time <= cutoff
        ]

    def prioritize_tasks(self) -> list[Task]:
        """Return all incomplete tasks sorted by priority then by earliest scheduled time."""
        order = {"high": 0, "medium": 1, "low": 2}
        pending = [t for t in self.get_all_tasks() if not t.completed]
        return sorted(
            pending,
            key=lambda t: (order.get(t.priority, 9), t.scheduled_time or time.max),
        )
