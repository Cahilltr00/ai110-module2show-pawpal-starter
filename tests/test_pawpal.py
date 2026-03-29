import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import time
from pawpal_system import Task, Animal, Health, User


# ---------------------------------------------------------------------------
# Original tests (kept intact)
# ---------------------------------------------------------------------------

def test_task_completion():
    """Calling complete() should mark the task as completed."""
    task = Task("eat", 5, 0.50, "HIGH", "animal-1")
    assert task.completed is False
    task.complete()
    assert task.completed is True


def test_task_addition_increases_count():
    """Adding a task to an Animal should increase its task count by 1."""
    dog = Animal("dog", "Duke", 8, 1)
    assert len(dog.get_tasks()) == 0
    dog.add_task(Task("walk", 10, 0.0, "MEDIUM", 1))
    assert len(dog.get_tasks()) == 1


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

class TestSortByTime:
    """Health.sort_by_time — chronological ordering by scheduled_time."""

    def _scheduler(self):
        return Health()

    def test_sorts_tasks_chronologically(self):
        """Tasks out of order should come back sorted earliest-first."""
        scheduler = self._scheduler()
        t1 = Task("walk", 30, 0.0, "low", "a1", scheduled_time=time(10, 0))
        t2 = Task("eat",  10, 1.0, "low", "a1", scheduled_time=time(8,  0))
        t3 = Task("vet",  60, 50.0, "low", "a1", scheduled_time=time(14, 30))
        result = scheduler.sort_by_time([t1, t2, t3])
        assert result == [t2, t1, t3]

    def test_unscheduled_tasks_sort_last(self):
        """A task with scheduled_time=None must appear after any timed task."""
        scheduler = self._scheduler()
        t_none  = Task("bath", 20, 5.0, "high", "a1", scheduled_time=None)
        t_early = Task("eat",   5, 0.5, "high", "a1", scheduled_time=time(7, 0))
        result = scheduler.sort_by_time([t_none, t_early])
        assert result == [t_early, t_none]

    def test_multiple_unscheduled_tasks_all_go_last(self):
        """Multiple unscheduled tasks all follow every timed task."""
        scheduler = self._scheduler()
        t_none1 = Task("a", 5, 0, "low", "a1", scheduled_time=None)
        t_timed = Task("b", 5, 0, "low", "a1", scheduled_time=time(9, 0))
        t_none2 = Task("c", 5, 0, "low", "a1", scheduled_time=None)
        result = scheduler.sort_by_time([t_none1, t_timed, t_none2])
        assert result[0] is t_timed
        assert t_none1 in result[1:]
        assert t_none2 in result[1:]

    def test_already_sorted_input_is_unchanged(self):
        """A list already in chronological order should be returned as-is."""
        scheduler = self._scheduler()
        t1 = Task("eat",  5,  0, "low", "a1", scheduled_time=time(6, 0))
        t2 = Task("walk", 30, 0, "low", "a1", scheduled_time=time(8, 0))
        assert scheduler.sort_by_time([t1, t2]) == [t1, t2]

    def test_single_task_list_returns_same_task(self):
        """sort_by_time on a one-element list should return that same task."""
        scheduler = self._scheduler()
        t = Task("eat", 5, 0, "low", "a1", scheduled_time=time(9, 0))
        assert scheduler.sort_by_time([t]) == [t]

    def test_empty_list_returns_empty(self):
        """sort_by_time on an empty list should return an empty list."""
        assert self._scheduler().sort_by_time([]) == []


class TestPrioritizeTasks:
    """Health.prioritize_tasks — priority-first, then time, excluding completed."""

    def _setup(self):
        dog = Animal("dog", "Rex", 3, "dog-1")
        scheduler = Health()
        scheduler.register_animal(dog)
        return dog, scheduler

    def test_high_before_medium_before_low(self):
        """Output order must be high → medium → low regardless of insertion order."""
        dog, scheduler = self._setup()
        t_low  = Task("bath", 20, 5.0, "low",    dog.animal_id, scheduled_time=time(9, 0))
        t_med  = Task("walk", 30, 0.0, "medium",  dog.animal_id, scheduled_time=time(9, 0))
        t_high = Task("eat",   5, 1.0, "high",    dog.animal_id, scheduled_time=time(9, 0))
        for t in [t_low, t_med, t_high]:
            dog.add_task(t)
        result = scheduler.prioritize_tasks()
        assert result[0] is t_high
        assert result[1] is t_med
        assert result[2] is t_low

    def test_within_same_priority_earlier_time_first(self):
        """Ties in priority are broken by scheduled_time ascending."""
        dog, scheduler = self._setup()
        t_late  = Task("walk", 30, 0.0, "medium", dog.animal_id, scheduled_time=time(14, 0))
        t_early = Task("eat",   5, 1.0, "medium", dog.animal_id, scheduled_time=time(8,  0))
        dog.add_task(t_late)
        dog.add_task(t_early)
        result = scheduler.prioritize_tasks()
        assert result[0] is t_early
        assert result[1] is t_late

    def test_unscheduled_tasks_last_within_priority_tier(self):
        """Within a priority tier, tasks without a time sort after timed ones."""
        dog, scheduler = self._setup()
        t_none  = Task("bath", 20, 5.0, "high", dog.animal_id, scheduled_time=None)
        t_timed = Task("eat",   5, 1.0, "high", dog.animal_id, scheduled_time=time(7, 0))
        dog.add_task(t_none)
        dog.add_task(t_timed)
        result = scheduler.prioritize_tasks()
        assert result[0] is t_timed
        assert result[1] is t_none

    def test_completed_tasks_excluded(self):
        """prioritize_tasks must not return any completed tasks."""
        dog, scheduler = self._setup()
        t_done    = Task("walk", 30, 0.0, "high", dog.animal_id, scheduled_time=time(9, 0))
        t_pending = Task("eat",   5, 1.0, "low",  dog.animal_id, scheduled_time=time(10, 0))
        t_done.complete()
        dog.add_task(t_done)
        dog.add_task(t_pending)
        result = scheduler.prioritize_tasks()
        assert t_done not in result
        assert t_pending in result

    def test_empty_roster_returns_empty(self):
        """No registered animals means no tasks to prioritize."""
        assert Health().prioritize_tasks() == []


# ---------------------------------------------------------------------------
# Recurrence
# ---------------------------------------------------------------------------

class TestRecurrence:
    """Health.complete_task — daily/weekly cloning and edge cases."""

    def _setup(self):
        dog = Animal("dog", "Buddy", 4, "buddy-1")
        scheduler = Health()
        scheduler.register_animal(dog)
        return dog, scheduler

    def test_daily_recurrence_spawns_clone(self):
        """Completing a daily task adds a new task to the same animal."""
        dog, scheduler = self._setup()
        task = Task("eat", 5, 1.0, "high", dog.animal_id,
                    scheduled_time=time(8, 0), recurrence="daily")
        dog.add_task(task)

        next_task = scheduler.complete_task(task)

        assert next_task is not None
        assert len(dog.get_tasks()) == 2

    def test_weekly_recurrence_spawns_clone(self):
        """Completing a weekly task also produces a clone."""
        dog, scheduler = self._setup()
        task = Task("vet", 60, 50.0, "high", dog.animal_id,
                    scheduled_time=time(10, 0), recurrence="weekly")
        dog.add_task(task)

        next_task = scheduler.complete_task(task)

        assert next_task is not None
        assert len(dog.get_tasks()) == 2

    def test_clone_is_incomplete_with_new_id(self):
        """The spawned task must be incomplete and have a different task_id."""
        dog, scheduler = self._setup()
        task = Task("eat", 5, 1.0, "high", dog.animal_id,
                    scheduled_time=time(8, 0), recurrence="daily")
        dog.add_task(task)
        original_id = task.task_id

        next_task = scheduler.complete_task(task)

        assert next_task.completed is False
        assert next_task.task_id != original_id

    def test_clone_inherits_scheduled_time(self):
        """The spawned task must keep the same scheduled_time as the original."""
        dog, scheduler = self._setup()
        task = Task("eat", 5, 1.0, "high", dog.animal_id,
                    scheduled_time=time(8, 30), recurrence="daily")
        dog.add_task(task)

        next_task = scheduler.complete_task(task)

        assert next_task.scheduled_time == time(8, 30)

    def test_original_task_marked_complete(self):
        """complete_task must mark the original task done, not just the clone."""
        dog, scheduler = self._setup()
        task = Task("eat", 5, 1.0, "high", dog.animal_id,
                    scheduled_time=time(8, 0), recurrence="daily")
        dog.add_task(task)

        scheduler.complete_task(task)

        assert task.completed is True

    def test_no_recurrence_returns_none_and_no_clone(self):
        """complete_task returns None and adds no extra task when recurrence=None."""
        dog, scheduler = self._setup()
        task = Task("bath", 20, 5.0, "low", dog.animal_id, recurrence=None)
        dog.add_task(task)

        result = scheduler.complete_task(task)

        assert result is None
        assert len(dog.get_tasks()) == 1

    def test_orphan_task_returns_none(self):
        """complete_task returns None when the task's animal isn't registered."""
        scheduler = Health()  # empty roster
        task = Task("walk", 30, 0.0, "medium", "ghost-pet-id",
                    scheduled_time=time(9, 0), recurrence="daily")

        result = scheduler.complete_task(task)

        assert result is None


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

class TestHealthConflictDetection:
    """Health.detect_conflicts — time-slot collision logic."""

    def _two_pet_scheduler(self):
        dog = Animal("dog", "Duke",   5, "duke-1")
        cat = Animal("cat", "Millie", 3, "millie-1")
        scheduler = Health()
        scheduler.register_animal(dog)
        scheduler.register_animal(cat)
        return dog, cat, scheduler

    def test_same_time_two_pets_flagged(self):
        """Two tasks at the same time for different pets must produce one conflict."""
        dog, cat, scheduler = self._two_pet_scheduler()
        dog.add_task(Task("walk", 30, 0.0, "high", dog.animal_id, scheduled_time=time(8, 0)))
        cat.add_task(Task("eat",   5, 1.0, "high", cat.animal_id, scheduled_time=time(8, 0)))

        conflicts = scheduler.detect_conflicts()

        assert len(conflicts) == 1
        assert "08:00 AM" in conflicts[0]

    def test_conflict_message_names_both_pets(self):
        """The conflict string should include both pet names."""
        dog, cat, scheduler = self._two_pet_scheduler()
        dog.add_task(Task("walk", 30, 0.0, "high", dog.animal_id, scheduled_time=time(8, 0)))
        cat.add_task(Task("eat",   5, 1.0, "high", cat.animal_id, scheduled_time=time(8, 0)))

        conflicts = scheduler.detect_conflicts()

        assert "Duke"   in conflicts[0]
        assert "Millie" in conflicts[0]

    def test_different_times_no_conflict(self):
        """Tasks at distinct times should not generate any conflicts."""
        dog, cat, scheduler = self._two_pet_scheduler()
        dog.add_task(Task("walk", 30, 0.0, "medium", dog.animal_id, scheduled_time=time(8,  0)))
        cat.add_task(Task("eat",   5, 1.0, "medium", cat.animal_id, scheduled_time=time(9,  0)))

        assert scheduler.detect_conflicts() == []

    def test_three_tasks_same_slot_one_warning(self):
        """Three tasks in the same slot should produce exactly one conflict entry."""
        dog, cat, scheduler = self._two_pet_scheduler()
        dog.add_task(Task("walk", 30, 0.0, "high", dog.animal_id, scheduled_time=time(8, 0)))
        cat.add_task(Task("eat",   5, 1.0, "high", cat.animal_id, scheduled_time=time(8, 0)))
        cat.add_task(Task("play", 15, 0.0, "low",  cat.animal_id, scheduled_time=time(8, 0)))

        conflicts = scheduler.detect_conflicts()

        assert len(conflicts) == 1

    def test_completed_tasks_not_counted_as_conflicts(self):
        """A completed task sharing a time slot must not trigger a conflict."""
        dog, cat, scheduler = self._two_pet_scheduler()
        t_done = Task("walk", 30, 0.0, "high", dog.animal_id, scheduled_time=time(8, 0))
        t_done.complete()
        dog.add_task(t_done)
        cat.add_task(Task("eat", 5, 1.0, "high", cat.animal_id, scheduled_time=time(8, 0)))

        assert scheduler.detect_conflicts() == []

    def test_unscheduled_tasks_never_conflict(self):
        """Tasks without a scheduled_time must not be flagged as conflicts."""
        dog, cat, scheduler = self._two_pet_scheduler()
        dog.add_task(Task("walk", 30, 0.0, "high", dog.animal_id, scheduled_time=None))
        cat.add_task(Task("eat",   5, 1.0, "high", cat.animal_id, scheduled_time=None))

        assert scheduler.detect_conflicts() == []

    def test_no_tasks_returns_empty_list(self):
        """A scheduler with no tasks should return an empty list."""
        _, _, scheduler = self._two_pet_scheduler()
        assert scheduler.detect_conflicts() == []

    def test_two_separate_conflicts_reported_independently(self):
        """Conflicts at two different times should each produce their own warning."""
        dog, cat, scheduler = self._two_pet_scheduler()
        dog.add_task(Task("walk", 30, 0.0, "high", dog.animal_id, scheduled_time=time(8,  0)))
        cat.add_task(Task("eat",   5, 1.0, "high", cat.animal_id, scheduled_time=time(8,  0)))
        dog.add_task(Task("play", 15, 0.0, "low",  dog.animal_id, scheduled_time=time(14, 0)))
        cat.add_task(Task("vet",  60, 50.0, "low", cat.animal_id, scheduled_time=time(14, 0)))

        conflicts = scheduler.detect_conflicts()

        assert len(conflicts) == 2


class TestUserConflictDetection:
    """User.detect_conflicts — same logic via the User facade."""

    def _setup(self):
        user = User("Alex", 30)
        dog  = Animal("dog", "Duke",   5, "duke-1")
        cat  = Animal("cat", "Millie", 3, "millie-1")
        user.add_pet(dog)
        user.add_pet(cat)
        return user, dog, cat

    def test_cross_pet_conflict_detected(self):
        """User.detect_conflicts should catch a collision between two pets."""
        user, dog, cat = self._setup()
        dog.add_task(Task("walk", 30, 0.0, "high", dog.animal_id, scheduled_time=time(8, 0)))
        cat.add_task(Task("eat",   5, 1.0, "high", cat.animal_id, scheduled_time=time(8, 0)))

        conflicts = user.detect_conflicts()

        assert len(conflicts) == 1
        assert "Duke"   in conflicts[0]
        assert "Millie" in conflicts[0]

    def test_clean_schedule_returns_empty(self):
        """No conflict when every pet's tasks are at different times."""
        user, dog, _ = self._setup()
        dog.add_task(Task("walk", 30, 0.0, "medium", dog.animal_id, scheduled_time=time(8,  0)))
        dog.add_task(Task("eat",   5, 1.0, "low",    dog.animal_id, scheduled_time=time(12, 0)))

        assert user.detect_conflicts() == []
