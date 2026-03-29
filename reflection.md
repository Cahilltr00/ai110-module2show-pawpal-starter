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
  ->I used Claude for most of my brainstorming and helping with going through the codebase and making the changes that I saw fit. It's nice to use Claude as an agent of going through everything and making the changes (you approve) cause it can become a spider web of concepts. Using Claude to test and debug was also very helpful and efficient.

- What kinds of prompts or questions were most helpful?

  ->The question on which part of the codebase can be streamlined/made more efficient as well as readable helped me understand more what was going on.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  -> Claude tried to suggest changing something to do with the completed/overdue flags and I didn't think it was necessary. It was going to make it too complicated.

- How did you evaluate or verify what the AI suggested?
  -> When I looked at the suggestion it just didn't sit right in my brain, maybe because it was going to make it more confusing to look at and understand immediately.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  -> I tested the apps ability to sort the tasks by time as well as the conflict resolution functionality. I also tested how the program handles marking tasks completed and whether or not it inputs a new occurence if it is a recurring task that is marked complete.

- Why were these tests important?
  -> I thought these were going to be the features that would affect the UX the most. When I use an application I always assume it is going to be sorted in a way that is inline with my own daily schedule. Testing to see how tasks were marked complete and recurring tests were handled allowed me to verify that the application will handle things I expect without even thinking about them.

**b. Confidence**

- How confident are you that your scheduler works correctly?
  -> I would rate my confidence a 7 out of 10.

- What edge cases would you test next if you had more time?
  -> Just the non-functional aspects mostly, such as uptime and how the program handles a loss of user data and how secure the application is. These are just things that would be an iteration of the program I suppose.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  -> The outcome, and my ability to write a prompt that let Claude know "exactly" what I would like to be implemented. This of course was anchored in the given questions in the instructions but those questions allowed me to know what a good prompting question should look like. Before this I would just talk to the agent like I would talk to a coworker, but it takes a little more specific details like #file: and #codebase, those helped get things more concise.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

  -> The UI has a lot of clicking going on, maybe redesign that into a more streamlined process and simpler to look at.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

  -> How quickly you can get in the "weeds" when doing something like this. Before I knew it there was a lot going on in the #codebase and that overwhelmed me quite a bit. This is something I need to keep in mind for next time and maybe tailor my prompts more toward simplicity to begin with.
