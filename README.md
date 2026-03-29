# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Smarter Scheduling

    The apps scheduling (this app is Health class) process is much improved and more efficient for the user. It now sorts tasks based on time, filters by whether or not the task is completed or not. The new scheduler also detects conflicts, if ever a user unintentionally schedules two tasks at the same time the app will warn them.

### Testing PawPal+

    python -m pytest

    This command runs tests that cover whether out-of-order input gets sorted chronologically, covers the enforcement of priority rankings. This test suite also covers whether or not there are conflicts with task times, if there is a message should be displayed showing which times and pets are conflicting.

    Confidence Level: ****

### Features Implemented

Implemented Features
Task Scheduling

Schedule a task to a specific time of day via Task.schedule()
Detect overdue tasks by comparing scheduled_time against the current wall-clock time (Task.is_overdue())
Retrieve all incomplete tasks scheduled within an upcoming time window (Health.get_upcoming_tasks(hours))
Sorting & Prioritization

Sort tasks chronologically by scheduled_time; tasks with no scheduled time always fall last via a "99:99" sentinel (Health.sort_by_time())
Prioritize all pending tasks using a two-key sort — priority tier first (high → medium → low), then scheduled time within each tier (Health.prioritize_tasks())
Filtering

Filter a task list to completed or pending tasks only (Health.filter_by_completion())
Filter a task list to a specific pet by name, case-insensitively (Health.filter_by_pet_name())
Conflict Detection

Detect scheduling conflicts by bucketing all incomplete, scheduled tasks into a time-slot map and flagging any slot with more than one task (User.detect_conflicts(), Health.detect_conflicts())
Conflict detection ignores completed tasks and tasks with no scheduled time
Recurring Tasks

Mark a task complete and automatically clone it as a new pending task when recurrence is "daily" or "weekly" (Health.complete_task())
The cloned task preserves all original fields (type, time, priority, cost) with a fresh task_id and completed=False
Non-recurring tasks and tasks whose animal is not registered return None with no side effects
Health Records

Log vet visits and observed symptoms per pet by animal_id (Health.log_vet_visit(), Health.log_symptom())
Check whether any vaccine for a pet is due today or overdue by comparing next_due_date against today's date (Health.is_vaccine_due())
Retrieve all vaccine records for a specific pet (Health.get_vaccine_record())
Multi-Pet Management

Register multiple pets under a single Health scheduler; get_all_tasks() flattens all pets' task lists in O(n) over total tasks
Add and remove pets from a User; conflict detection and schedule printing span all registered pets

<a href="/course_images/ai110/your_screenshot_name.png" target="_blank"><img src='/image.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>.
