# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  - Three actions this app will include are:
    -> Track feeding time
    -> Schedule time at the park
    -> Keep track of Vet visits (annual checkup, unplanned visits)

- What classes did you include, and what responsibilities did you assign to each?
  1. User: - name - age - addPet() - removePet() - getPets()

  2. Animal - type - name - age - getProfile() - addTask() - getTasks() - addHealthRecord() - getHealthRecord()
  3. Task - type - duration - cost - priority - create() - schedule() - isOverdue() - complete()
  4. Health - healthId - animalId - recordType - createdAt - updatedAt - logVetVisit() - logSymptom() - getVaccineRecord() - isVaccineDue()

  **b. Design changes**
  - Claude found a few high severity issues, a few medium and one low:
    -> High severity: - No animal.id in Animal class - Task class wasn't linked to Animal class - There wasn't a due_date attribute for is_overdue() in Task class
    -> Medium severity: - No user_id on User class - No data field for vaccine in Health class - No next_due_date field for is_vaccine_due() in Health class
    -> Low: - Task.create() was redundant

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    -> In the Health(scheduler) class, all records are stored as dictionaries in a list, everytime something needs to be looked up the entire list is iterated over.
- Why is that tradeoff reasonable for this scenario?
    -> The list isn't going to be extremely long (i.e. 1000's of items) so the searching doesn't take an unreasonable amount of time

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
