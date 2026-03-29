import streamlit as st
from datetime import time
from pawpal_system import User, Animal, Task, PRIORITY_ORDER

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

if "user" not in st.session_state:
    st.session_state.user = None
if "animal" not in st.session_state:
    st.session_state.animal = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []

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
    st.session_state.user = User(owner_name, owner_age)
    st.session_state.animal = Animal(species, pet_name, pet_age)
    st.session_state.user.add_pet(st.session_state.animal)
    st.session_state.tasks = []
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

use_time = st.checkbox("Set a scheduled time")
scheduled_time = None
if use_time:
    t = st.time_input("Scheduled time", value=time(8, 0))
    scheduled_time = t

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
        )
        st.session_state.animal.add_task(task)
        st.session_state.tasks.append({
            "title": task_title,
            "duration (min)": int(duration),
            "priority": priority,
            "cost ($)": f"{cost:.2f}",
            "time": scheduled_time.strftime("%I:%M %p") if scheduled_time else "anytime",
        })
        st.success(f"Task '{task_title}' added to {st.session_state.animal.name}.")

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Schedule generation
# ---------------------------------------------------------------------------

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.user is None or st.session_state.animal is None:
        st.error("Please add a pet first using the 'Add / Update Pet' button.")
    else:
        all_tasks = [t for t in st.session_state.animal.get_tasks() if not t.completed]

        if not all_tasks:
            st.warning("No tasks scheduled. Add some tasks above.")
        else:
            sorted_tasks = sorted(
                all_tasks,
                key=lambda t: (PRIORITY_ORDER.get(t.priority, 9), t.scheduled_time or time.max),
            )

            st.success(f"Schedule for {st.session_state.animal.name} ({st.session_state.animal.type})")

            rows = []
            for task in sorted_tasks:
                overdue = " OVERDUE" if task.is_overdue() else ""
                rows.append({
                    "time": task.scheduled_time.strftime("%I:%M %p") if task.scheduled_time else "anytime",
                    "priority": task.priority.upper(),
                    "task": task.type + overdue,
                    "duration (min)": task.duration,
                    "cost ($)": f"{task.cost:.2f}",
                })
            st.table(rows)

            # Also print to terminal via the User method
            st.session_state.user.print_daily_schedule()
