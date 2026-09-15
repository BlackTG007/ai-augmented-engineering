# Lab 3: Build a DE Pipeline Code Review Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** GitHub Copilot in VS Code
**Duration:** 75 minutes
**Day:** Day 2, following Module 4

---

## Prerequisites

- [ ] Modules 3 and 4 lectures completed
- [ ] Chapter 3 scoping exercise completed (or the scope specification template in Task 1.1 reviewed)
- [ ] Lab 2 completed or not; this lab starts from branches that ship with the repository
- [ ] The repository's `lab-workspace` folder open in VS Code with Copilot signed in, and the venv active in the terminal
- [ ] Git working in the repository; the `pr/001`, `pr/002`, `pr/003` branches present (`git branch -a` lists them under `origin/`)

---

## Lab Overview

Your team reviews dozens of Python pipeline PRs each week. Manual review is inconsistent and depends on who is available. Build a Copilot agent instruction set that reviews pipeline code against DE-specific criteria, flags issues with severity ratings, and produces a structured review summary ready for human sign-off. Then read the shipped review rubric and compare Copilot's built-in **Review Changes** with your custom agent on the same PR.

**Copilot notes for this lab:** Cursor attaches a branch diff with `@Branch (Diff with Main)`; in Copilot the agent runs `git diff` itself (you click **Allow** on the command card). Cursor's Agent Review is **Review Changes** in the Source Control panel here. Set the model pill to a named model for the whole lab: **Auto** can route consecutive chats to different models, which wrecks the Consistency score.

**What you will produce:**
- A working code review agent instruction set with all five scope components
- A quality rubric score across two iteration cycles
- A written comparison of your custom agent versus Copilot's Review Changes on the same PR

**How this lab is written:** each Task has numbered steps. A numbered step is something you do. Text between steps explains what you are looking at; the boxes marked "What you should see" tell you what a correct result looks like. The agent's behaviour varies from run to run: it may ask questions before acting, act at once, or describe a change and wait for your go-ahead. If it asks, answer; if it waits, reply `Go ahead`. The steps describe the end state, not every turn of the conversation.

---

## Task 0: Check out the first review branch

This lab reviews three pull-request branches that ship with the repository: `pr/001`, `pr/002` and `pr/003`. Each carries a complete workspace, so there is no loader run in this lab; you only need a clean tree to switch branches.

1. Open a terminal inside VS Code: menu **Terminal → New Terminal**. It opens in `lab-workspace/`; every command in this lab runs from there.

2. Make sure the prompt starts with `(venv)`. If it does not, run `source venv/bin/activate` (Windows: `venv\Scripts\activate`).

3. Put away any unfinished Lab 2 work. Run `git status --short`; if it prints anything, commit on the branch you are on:

   ```bash
   git add -A
   git commit -m "Lab 2 checkpoint"
   ```

4. Switch to the first review branch:

   ```bash
   git checkout pr/001
   git branch --show-current
   ```

   If git says a file "would be overwritten by checkout", step 3 was skipped; do it and try again.

5. Look at what the PR changes:

   ```bash
   git diff --stat main
   ```

<details open>
<summary>What you should see</summary>

```
 src/ingest.py    | 6 ++++++
 src/transform.py | 7 ++++++-
 src/validate.py  | 3 +++
 3 files changed, 15 insertions(+), 1 deletion(-)
```

Three files under `src/`, about fifteen added lines. Those are the changes you will review. If the list is much longer, you are not on `pr/001`, or `main` has commits of your own on it.

`src/ingest.py` on this branch is the complete idiomatic conversion of `perl/ingest.pl` plus the PR's additions; it is the baseline all three sample PRs are built on.
</details>

6. Confirm the tests pass:

   ```bash
   pytest tests/ -q
   ```

   Expect `42 passed`. The planted issues are review issues, not test failures.

7. Open the chat panel (**View → Chat**), click the model pill (**Auto ▾**) and choose a named model (any Claude or GPT entry). Keep it for the whole lab.

---

## Task 1: Scope the agent and build Version 1

### Task 1.1: Review your scope specification

1. Open your Chapter 3 scope specification document, or the template below if you did not complete the exercise.

2. Confirm it covers all five components. Add any that are missing, using these definitions:

| Component | Definition |
|---|---|
| **Tools** | The branch diff (`git diff main...HEAD`, run by the agent) for context. Read-only access only; the agent must not edit any files. |
| **Instructions** | Review against `.github/copilot-instructions.md` plus five DE criteria: schema drift handling, null safety, idempotency, logging completeness, type hint coverage. |
| **Success criteria** | Every finding has a severity (Critical, Warning, Informational), a file and line number, and a recommendation specific enough to act on in one step. |
| **Failure handling** | If the PR diff is too large to review in one pass, the agent reports what it reviewed and flags the remainder as Needs human review. |
| **Escalation path** | Any credential, secret, or key literal in source is escalated regardless of confidence and reported separately. Any finding where agent confidence is Low is also escalated. |

<details open>
<summary>Scope specification template (use if you did not complete the Chapter 3 exercise)</summary>

```
Tools: the branch diff (git diff main...HEAD) for context. Read-only file access.
The agent must not edit any files.

Instructions: Review changed code against .github/copilot-instructions.md
and five DE criteria:
1. Schema drift handling: does the change validate incoming schema?
2. Null safety: are None values handled on all critical fields?
3. Idempotency: can this step run twice without duplicate records?
4. Logging completeness: are pipeline entry, exit, and errors logged?
5. Type hint coverage: do all functions have complete type hints?

Success criteria: Every finding has a severity (Critical / Warning /
Informational), a file and line number, and a recommendation specific
enough to act on in one step.

Failure handling: If the PR diff is too large to review in one pass,
report what was reviewed and flag the remainder as Needs human review.

Escalation path: Any credential, secret, token, or API key literal in
source code is marked ESCALATE regardless of confidence and reported in
a separate ESCALATED section. Any finding where confidence is Low is
also marked ESCALATE rather than included in the summary.

Two failure modes:
1. Non-deterministic output -- same PR produces different findings on
   consecutive runs. Mitigation: explicit output format template.
2. Scope creep -- agent comments on code outside the diff. Mitigation:
   explicit instruction to review only changed lines.
```
</details>

---

### Task 1.2: Build the Version 1 instruction set

You send one message: your instruction set, which tells the agent to fetch the diff itself. This is Version 1; you improve it in Tasks 3 and 4.

1. Click **+** (New Chat) at the top of the chat panel and set the mode pill to **Agent**.

2. Paste this and press Enter:

   ```
   You are a DE pipeline code review agent.
   Context: run git diff main...HEAD to get this branch's changes. Review only changed lines.
   Do NOT modify any files.
   Review the changes against .github/copilot-instructions.md and:
   1. Schema drift handling: does the change validate incoming schema?
   2. Null safety: are None values handled on all critical fields?
   3. Idempotency: can this step run twice without duplicate records?
   4. Logging completeness: are pipeline entry, exit, and errors logged?
   5. Type hint coverage: do all functions have complete type hints?
   For each finding output: criterion violated; file and line number;
   severity: Critical / Warning / Informational; confidence: High / Medium / Low;
   specific recommendation.
   If confidence is Low, mark the finding ESCALATE.
   End with: overall recommendation APPROVE / REQUEST CHANGES / ESCALATE.
   Review the changes on this branch.
   ```

3. A card appears: "Run … command?" with the git command and a one-line explanation. Click **Allow**. (The **Allow ▾** dropdown can allow that command for the session, which saves clicks on the re-runs.)

4. Save a copy of that instruction set somewhere you can paste from (a scratch file outside the repository, or a note). You will send the whole set again, edited, several times in this lab.

---

### Task 1.3: Read the review

1. Read every finding before going on. Expect somewhere between eight and fifteen. Some are issues your instructor planted; some are real issues nobody planted. Both are legitimate. Expand the **Completed N steps** line above the findings: the agent ran the diff, read `copilot-instructions.md`, usually the files the diff touches, and sometimes the pipeline-review skill on its own; that is the evidence its file-and-line citations rest on.

2. Check for a change summary above the input. There should be none: the agent was told not to modify files. If one appears, click **Undo**. If the agent offers to fix the findings, reply `No. Review only.`

<details open>
<summary>If the agent says it has no diff to review</summary>

You clicked **Skip** on the command card, or the diff came back empty. Send `Run git diff main...HEAD and review the changes on this branch.` and click **Allow**. If the diff is empty, confirm `git branch --show-current` prints `pr/001`.
</details>

---

## Task 2: Score the first run

### Task 2.1: Score the output against the rubric

1. Score each dimension from 1 (poor) to 5 (excellent), using the known-issues list your instructor provides to check for misses.

| Dimension | Score (1–5) | Notes |
|---|---|---|
| **Coverage**: did the agent find all known issues in pr/001? | | |
| **Accuracy**: of the issues flagged, how many are real? | | |
| **Clarity**: can you read each recommendation and know exactly what to do next? | | |
| **Consistency**: run the agent on pr/001 a second time (step 2). How similar are the two outputs? | | |
| **Total** | **/20** | |

2. For the Consistency row, click **+** for a **fresh** chat (same named model) and send the identical instruction set. In the same chat the agent sees its first answer and repeats it, which inflates the score. Compare the two outputs.

<details open>
<summary>Scoring guidance</summary>

**Coverage (false negatives):** compare the findings against the instructor's list. Each missed issue costs one point. Score 5 only if every known issue was found.

**Accuracy (false positives):** count findings that describe something not in the code. Each costs one point. A real issue that is not on the instructor's list is **not** a false positive; note it and move on.

**Clarity (actionability):** could you act on each recommendation without a follow-up question? "Consider improving null handling" is not actionable. "Add an explicit None check on `instrument_id` at line 47 before passing it to `transform_record()`" is. Score 5 only if every recommendation is immediately actionable.

**Consistency (determinism):** score 5 if the two runs' findings are identical, 1 if the severity ratings or the finding list differ significantly.

**Production threshold:** 16 out of 20 with no dimension below 3. First-run scores vary widely by model; Consistency is usually the lowest dimension.
</details>

3. **Before you continue, note:**

   > Your total, and the single lowest-scoring dimension. That dimension is your improvement target for Task 3.

---

## Task 3: First iteration cycle

### Task 3.1: Make one targeted change

1. Based on your lowest-scoring dimension, make exactly one change to your saved instruction set. Do not change more than one thing.

<details open>
<summary>Targeted change examples by dimension</summary>

**Coverage low:** add a more specific instruction for the issue type being missed.

```
For null safety: check every .get() call without a default value,
every function that accepts Optional parameters without explicit None handling on critical pipeline fields,
and every changed except clause: narrowing the exception types caught (for example dropping TypeError)
is a null-safety regression.
```

**Accuracy low:** add a constraint against invented findings.

```
Only flag an issue if you can identify the exact file and line number where it occurs.
Do not flag general concerns or patterns you cannot locate in the diff.
```

**Clarity low:** tighten the output format.

```
Each recommendation must be a single actionable sentence starting with a verb.
Example: Add an explicit None check on instrument_id at line 47 before passing it to transform_record().
```

**Consistency low:** add an explicit output template with required field names.

```
For every finding, output exactly these fields in this order:
CRITERION · LOCATION (file:line) · SEVERITY (Critical / Warning / Informational) ·
CONFIDENCE (High / Medium / Low) · RECOMMENDATION (single actionable sentence starting with a verb).
Report each distinct issue once.
After the findings, end with: overall recommendation APPROVE / REQUEST CHANGES / ESCALATE.
```

Do **not** add "only report the five criteria": the `copilot-instructions.md` standards are also in scope, and you would lose findings (a for-append loop, for instance, is a standards finding, not one of the five).
</details>

2. In the same chat as Task 1.2, paste the **whole** updated instruction set, change its last line to `Review the changes on this branch using the updated instructions.` and send it. Click **Allow** when it re-runs the diff.

   Sending the full set each time is what makes versions reversible: to go back to an earlier version, send that version again.

---

### Task 3.2: Re-score

1. Score all four dimensions again and record the new total.

2. Decide what to keep:

| Result | Action |
|---|---|
| Target dimension improved | Keep the change. Record the new total. |
| Target dimension unchanged or worse | Go back to the Version 1 text. Try a different change for the same dimension. |
| Another dimension dropped significantly | Go back and try a narrower change. Adding an output template *and* a scope restriction in one step is the classic way to fix Consistency and lose Coverage. |

---

## Task 4: Second iteration and generalization test

### Task 4.1: Second iteration

1. Identify the new lowest-scoring dimension from Task 3.2. Make one more targeted change, the same way as Task 3.1, and re-score.

   If you have already reached 16 out of 20 with no dimension below 3, skip to Task 4.2. Do not force a change.

---

### Task 4.2: Generalization test on PR 002

1. Switch branches:

   ```bash
   git checkout pr/002
   ```

2. In the same chat, paste your current instruction set, ending with `Review the changes on this branch.`, send it, and click **Allow** on the diff command.

3. Score the pr/002 output on all four dimensions and compare with your pr/001 score. Two planted issues to check for: one needs reasoning across files (an append-mode write with no de-duplication); the other is a narrowed `except` clause.

4. **Before you continue, note:**

   > Did your agent catch both? If pr/002 scored much lower than pr/001, which change over-fitted to pr/001's issues? Broaden or remove it.

---

### Task 4.3: Hard PR test on PR 003

1. Switch branches:

   ```bash
   git checkout pr/003
   ```

2. Same shape: paste the instruction set ending with `Review the changes on this branch.`, send, **Allow**.

3. PR 003 contains a hard-coded credential. Check the output for all three:

   - [ ] The credential finding is marked ESCALATE
   - [ ] It is reported in a separate ESCALATED section, not in the main list
   - [ ] The overall recommendation is ESCALATE, not REQUEST CHANGES or APPROVE

4. If any box is unchecked, your escalation path is confidence-based rather than risk-based: the agent is *sure* the key is a bug, so "escalate when confidence is Low" never fires. Add this sentence to your instruction set and send the set again:

   ```
   Any credential, secret, token, or API key literal in source code is a security finding:
   mark it ESCALATE regardless of confidence, report it in a separate ESCALATED section
   before the other findings, and set the overall recommendation to ESCALATE.
   ```

   Escalate-when-unsure is not the same as escalate-when-dangerous. Ship the version that has both.

---

## Task 5: The shipped rubric and Review Changes

### Task 5.1: Understand what you are comparing

Two distinct systems appear in this Task. Keep them separate:

| System | What it is | What it reads |
|---|---|---|
| **Copilot code review on GitHub.com** | PR automation: Copilot as a reviewer on pull requests in the GitHub repository | `.github/copilot-instructions.md` in the repository |
| **Review Changes** | Local in-editor review from the Source Control panel, no PR needed | `.github/copilot-instructions.md` and the file's diff |
| **Your in-editor agent** | Chat: Agent, Ask, Plan | `.github/copilot-instructions.md`, `.github/instructions/*`, skills when named |

One file, three readers: the instructions you wrote in Lab 1 are what the local review and the GitHub review both use, so anything you want enforced on PRs belongs there. The Cursor track ships a separate rubric file, `.cursor/BUGBOT.md`, for its Bugbot and Agent Review; in this Task you read it as a rubric and compare it with your own instruction set.

---

### Task 5.2: Read the shipped review rubric

1. In the Explorer, open `.cursor/BUGBOT.md`. Copilot does not read this file; it is the Cursor track's review rubric, and it is a good example of one. Where a Copilot team would put these rules is a `## Code Review Rules` section of `.github/copilot-instructions.md`.

2. Read the Security, Critical, Warning and Informational sections and compare them with your custom agent's five criteria.

<details open>
<summary>What the file contains</summary>

```markdown
# DE Pipeline Review Rules

Review only the changed lines. Cite file and line for every finding. Recommendations are one sentence, starting with a verb.

## Security (blocking, always report first)
- Any credential, secret, token, or API key literal in source code, including "demo" or "fallback" values, is a blocking finding regardless of confidence
- Any change that widens network, file, or process access is a blocking finding

## Critical
- Any function reading from an external source (CSV, API response) must validate field names and types against the registered schema in schemas/ before processing records
- Null values on record_id, instrument_id, exchange_code, price, volume, and figi must be handled explicitly; no bare .get() without a default on these fields
- Do not narrow or remove exception types in existing except clauses; do not catch exceptions silently. A swallowed or narrowed handler that lets a None value crash the pipeline is Critical
- Pipeline steps that write records must be idempotent: running twice must not produce duplicate output. Opening a file in append mode without a deduplication check is Critical

## Warning
- All functions must have type hints on all arguments and the return value
- Pipeline entry and exit must be logged with the project logger in the format: Starting {function_name} with {len(records)} records / Completed {function_name} with {len(records)} records
- Removing an existing log statement is a Warning
- All file operations must use pathlib.Path; os.path and raw string paths passed to open() are Warnings

## Informational
- Use collections.Counter for counting and frequency analysis
- Use list comprehensions where they improve readability over for-append loops
- Unused variables or imports introduced by the change
```
</details>

3. **Before you continue, note:**

   > One thing the file has that your instruction set does not (the exception-narrowing rule and the append-mode rule are candidates), and one thing it lacks.

   Do not add it to `copilot-instructions.md` in this lab; the `pr/` branches are shared, and Task 5.3 needs the shipped instructions so everyone compares the same thing.

---

### Task 5.3: Run Review Changes on PR 001

Review Changes works on files that show in the Source Control panel as changed. The PR's changes are committed on `pr/001`, so first make them show as uncommitted changes on a scratch branch.

1. Put PR 001's changes into the working tree as uncommitted changes:

   ```bash
   git checkout -b review-001 pr/001
   git reset --soft main
   git status --short
   ```

   Status lists the three `src/` files as staged (`M`). The code is unchanged; only the bookkeeping moved.

2. Open the **Source Control** panel (the branch icon in the left bar). The three files appear under Staged Changes.

3. Right-click `src/ingest.py` in that list and choose **Review Changes**. Copilot reviews that file's diff and posts its comments inline in the editor (and as a list in the Comments panel). Repeat for `src/transform.py` and `src/validate.py`.

4. Read the comments. Each has an **Apply** or similar action next to it; do not apply anything, you are comparing, not fixing. If a file comes back with no comments at all, run **Review Changes** on it again; an empty first pass happens.

5. Put the branch back the way you found it:

   ```bash
   git reset --hard pr/001
   git checkout pr/001
   git branch -D review-001
   git status --short
   ```

   Status is empty and you are on `pr/001`.

<details open>
<summary>What you should see</summary>

A handful of inline comments per file, some naming a `copilot-instructions.md` standard as the reason. Expect it to find some but not all of the three planted pr/001 issues, plus a real issue nobody planted. That is not a failure; it is the data point for Task 5.4.
</details>

---

### Task 5.4: Compare Review Changes with your custom agent

1. Fill in this table from the Review Changes comments and your best custom-agent output on pr/001:

| | Your custom agent | Review Changes |
|---|---|---|
| Known pr/001 issues found | /3 (a tuned custom agent typically finds all three) | /3 |
| False positives | | |
| Most actionable finding | | |
| Time to produce output | | |

2. **Before you continue, note:**

   > When would you use Review Changes instead of your custom agent in your daily work, and when the custom agent instead?

<details open>
<summary>Typical answer pattern</summary>

Review Changes is a right-click and needs no setup; use it for a quick sanity check on a file before committing. Your custom agent produces more structured output with severity ratings, confidence levels, and DE-specific criteria; use it before raising a PR, or in an asynchronous review where the output must be actionable by someone who was not present. On GitHub, Copilot code review on the PR itself reads the same `copilot-instructions.md`, so the standards travel with the repository.

Neither replaces the other. The professional workflow is: Review Changes before committing, custom agent before raising the PR.
</details>

3. Leave the `pr/` branches as you found them. If you changed anything on one, put it back:

   ```bash
   git checkout -- .
   ```

   Stay on `pr/001`; Lab 4's Task 0 moves you where it needs you.

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

What was your baseline score and your final score after two iteration cycles? What single change made the biggest difference?

---

**Question 2**

In Task 4.2, did your agent score similarly on pr/002 as on pr/001? If the score dropped, what caused the over-fitting?

---

**Question 3**

After Task 5, when would you use your custom agent versus Review Changes for day-to-day code review on your team? Why is "escalate when unsure" not the same as "escalate when dangerous"?

---

**Question 4**

Write one new rule for a `## Code Review Rules` section of `.github/copilot-instructions.md`, based on an issue your agent found in pr/003 that the shipped rubric does not cover.
