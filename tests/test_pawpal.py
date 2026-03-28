import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Animal


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
