from datetime import time
from pawpal_system import User, Task, Animal, Health

trevor = User("trevor", 34)
duke = Animal("dog", "Duke", 8, 1)
millie = Animal("dog", "Millie", 9, 2)


duke.add_task(Task("eat",   3,   0.50, "HIGH",   1, time(7, 0)))
duke.add_task(Task("walk",  10,  0.0,  "MEDIUM",  1, time(8, 30)))
duke.add_task(Task("sleep", 350, 0.0,  "HIGH",   1, time(21, 0)))

millie.add_task(Task("walk",  10,  0.0,  "MEDIUM",  2, time(8, 30)))
millie.add_task(Task("eat",   5,   0.50, "HIGH",   2, time(8, 30)))
millie.add_task(Task("sleep", 300, 0.0,  "HIGH",   2, time(21, 0)))
millie.add_task(Task("poop", 2, 0.0, "HIGH", 2, time(4, 30)))

trevor.add_pet(duke)
trevor.add_pet(millie)

trevor.print_daily_schedule()
