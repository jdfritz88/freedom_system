# Questioning Framework

A checklist of questions to ask yourself at each stage of debugging. Go through each group in order. Actually answer every question before moving on.

---

## Group 1: What's broken?
- What is the exact error message?
- What was I trying to do?
- What should have happened instead?
- Can I make it break again on purpose?
- What exact steps caused the error?

## Group 2: Why is it broken?
- What parts of the system are involved?
- Which specific part is actually failing?
- Do multiple systems need to talk to each other here?
- What am I assuming that might be wrong?
- Am I even looking at the right files/logs?
- Is there a similar working system I can compare to?

## Group 3: How do I fix it?
- What are 3 different ways to fix this?
- Which fix hits the root cause vs just the symptom?
- What could go wrong with each fix?
- How will I know the fix actually worked?
- How do I stop this from happening again?

## Group 4: Did it actually work?
- Did the fix solve the original problem?
- Did I break something else?
- Does it work every time, not just once?
- What would I do differently next time?
- How can I catch this faster in the future?
