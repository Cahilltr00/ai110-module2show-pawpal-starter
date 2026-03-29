import streamlit as st
from datetime import time
from pawpal_system import User, Animal, Task, Health

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

if "user" not in st.session_state:
    st.session_state.user = None
if "animal" not in st.session_state:
    st.session_state.animal = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ---------------------------------------------------------------------------
# Pet & Owner setup
# ---------------------------------------------------------------------------

st.subheader("Owner & Pet Profile")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    owner_age = st.number_input("Owner age", min_value=1, max_value=120, value=30)
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    pet_age = st.number_input("Pet age (years)", min_value=0, max_value=30, value=3)

species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add / Update Pet"):
    scheduler = Health()
    animal = Animal(species, pet_name, pet_age)
    user = User(owner_name, owner_age)
    user.add_pet(animal)
    scheduler.register_animal(animal)
    st.session_state.user = user
    st.session_state.animal = animal
    st.session_state.scheduler = scheduler
    st.success(f"Profile saved — {owner_name}'s pet {pet_name} ({species}) is ready.")

if st.session_state.animal:
    st.caption(f"Active pet: **{st.session_state.animal.name}** (id: `{st.session_state.animal.animal_id[:8]}…`)")

st.divider()

# ---------------------------------------------------------------------------
# Task entry
# ---------------------------------------------------------------------------

st.subheader("Tasks")
st.caption("Add care tasks for the active pet. Set a scheduled time to flag overdue tasks.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    cost = st.number_input("Cost ($)", min_value=0.0, value=0.0, step=0.5, format="%.2f")

col_time, col_recur = st.columns(2)
with col_time:
    use_time = st.checkbox("Set a scheduled time")
    scheduled_time = None
    if use_time:
        scheduled_time = st.time_input("Scheduled time", value=time(8, 0))
with col_recur:
    recurrence_choice = st.selectbox("Recurrence", ["none", "daily", "weekly"])
    recurrence = None if recurrence_choice == "none" else recurrence_choice

if st.button("Add task"):
    if st.session_state.animal is None:
        st.error("Please add a pet first using the 'Add / Update Pet' button.")
    else:
        task = Task(
            type=task_title,
            duration=int(duration),
            cost=float(cost),
            priority=priority,
            animal_id=st.session_state.animal.animal_id,
            scheduled_time=scheduled_time,
            recurrence=recurrence,
        )
        st.session_state.animal.add_task(task)
        st.success(f"Task '{task_title}' added to {st.session_state.animal.name}.")

# Display tasks directly from the animal — single source of truth
if st.session_state.animal:
    current_tasks = st.session_state.animal.get_tasks()
    if current_tasks:
        st.write("Current tasks:")
        st.table([
            {
                "title": t.type,
                "time": t.scheduled_time.strftime("%I:%M %p") if t.scheduled_time else "anytime",
                "priority": t.priority,
                "duration (min)": t.duration,
                "cost ($)": f"{t.cost:.2f}",
                "recurrence": t.recurrence or "—",
                "done": "✓" if t.completed else "",
            }
            for t in current_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Complete a task  (uses Health.complete_task for recurrence spawning)
# ---------------------------------------------------------------------------

st.subheader("Complete a Task")

if st.session_state.scheduler and st.session_state.animal:
    scheduler: Health = st.session_state.scheduler
    pending = [t for t in st.session_state.animal.get_tasks() if not t.completed]

    if pending:
        task_labels = [
            f"{t.type} @ {t.scheduled_time.strftime('%I:%M %p') if t.scheduled_time else 'anytime'}"
            f" [{t.priority}]{' (repeats ' + t.recurrence + ')' if t.recurrence else ''}"
            for t in pending
        ]
        selected_label = st.selectbox("Select task to complete", task_labels)
        selected_task = pending[task_labels.index(selected_label)]

        if st.button("Mark complete"):
            next_task = scheduler.complete_task(selected_task)
            if next_task:
                st.success(
                    f"'{selected_task.type}' done. Next {selected_task.recurrence} "
                    f"occurrence added to the schedule."
                )
            else:
                st.success(f"'{selected_task.type}' marked complete.")
            st.rerun()
    else:
        st.info("No pending tasks to complete.")
else:
    st.info("Add a pet and tasks to use this section.")

st.divider()

# ---------------------------------------------------------------------------
# Schedule generation  (uses Health.prioritize_tasks / detect_conflicts)
# ---------------------------------------------------------------------------

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.scheduler is None or st.session_state.animal is None:
        st.error("Please add a pet first using the 'Add / Update Pet' button.")
    else:
        scheduler: Health = st.session_state.scheduler

        # Conflict warnings via Health.detect_conflicts
        for warning in scheduler.detect_conflicts():
            st.warning(f"Scheduling conflict: {warning}")

        # Overdue banner via Health.get_overdue_tasks
        overdue = scheduler.get_overdue_tasks()
        if overdue:
            st.error(
                f"{len(overdue)} overdue task(s): "
                + ", ".join(t.type for t in overdue)
            )

        # Priority-sorted pending tasks via Health.prioritize_tasks
        sorted_tasks = scheduler.prioritize_tasks()

        if not sorted_tasks:
            st.warning("No pending tasks. Add some tasks above.")
        else:
            st.success(
                f"Schedule for {st.session_state.animal.name} "
                f"({st.session_state.animal.type})"
            )
            st.table([
                {
                    "time": t.scheduled_time.strftime("%I:%M %p") if t.scheduled_time else "anytime",
                    "priority": t.priority.upper(),
                    "task": t.type + (" OVERDUE" if t.is_overdue() else ""),
                    "duration (min)": t.duration,
                    "cost ($)": f"{t.cost:.2f}",
                    "recurrence": t.recurrence or "—",
                }
                for t in sorted_tasks
            ])
