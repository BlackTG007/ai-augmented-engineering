# Lab 3: Build a DE Pipeline Code Review Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** GitHub Copilot in VS Code
**Duration:** 75 minutes
**Day:** Day 2, following Module 4

---

## Prerequisites

- [ ] Modules 3 and 4 lectures completed
- [ ] Chapter 3 scoping exercise completed (or the scope specification template in Task 1.1 reviewed)
- [ ] Lab 2 completed or not; Task 0 loads the Lab 3 starting point either way
- [ ] The repository's `lab-workspace` folder open in VS Code with Copilot signed in, and the venv active in the terminal
- [ ] Git working in the repository; the `pr/001`, `pr/002`, `pr/003` branches present (`git branch -a` lists them under `origin/`)

---

## Lab Overview

Your team reviews dozens of Python pipeline PRs each week. Manual review is inconsistent and depends on who is available. In this lab you build a **custom agent**: a real, reusable agent that lives in a file in the repository, reviews pipeline code against DE-specific criteria, flags issues with severity ratings, and produces a structured review summary ready for human sign-off. Then you compare it with Copilot's built-in Review Changes on the same PR.

Everything you have configured so far has shaped how the agent behaves. A custom agent is the first thing you build that *is* an agent: it has its own name, its own instructions, its own tools, and it appears in the mode picker beside Agent, Ask and Plan.

**What you will produce:**
- `.github/agents/de-pipeline-reviewer.agent.md`: a scoped, read-only review agent you select from the mode picker
- A quality rubric score across two iteration cycles
- A written comparison of your custom agent versus Review Changes on the same PR

**Copilot notes for this lab:** modes are on the **Agent ▾** pill at the bottom left of the chat input, and your custom agent joins that list once the file exists. A new chat (**+** at the top of the panel) keeps the previous chat's mode, so check the pill every time. Terminal commands the agent wants to run appear as an **Allow ▾** / **Skip** card; your agent runs `git diff` itself, so expect one on every review.

**How this lab is written:** each Task has numbered steps. A numbered step is something you do. Text between steps explains what you are looking at; the boxes marked "What you should see" tell you what a correct result looks like. The agent's behaviour varies from run to run: it may ask questions before acting, act at once, or describe a change and wait for your go-ahead. If it asks, answer; if it waits, reply `Go ahead`. The steps describe the end state, not every turn of the conversation.

---

## Task 0: Load the starter files and check out the first PR

Do this whether or not you completed Lab 2. It resets the workspace to a known state, then moves you onto the first of three pull-request branches that ship with the repository.

1. Open a terminal inside VS Code: menu **Terminal → New Terminal**. It opens in `lab-workspace/`; every command in this lab runs from there.

2. Make sure the prompt starts with `(venv)`. If it does not, run `source venv/bin/activate` (Windows: `venv\Scripts\activate`).

3. Put away any unfinished Lab 2 work. Run `git status --short`; if it prints anything, commit on the branch you are on:

   ```bash
   git add -A
   git commit -m "Lab 2 checkpoint"
   ```

4. Go back to `main`, which is still exactly what you cloned:

   ```bash
   git checkout main
   ```

5. Load the Lab 3 starter files:

   ```bash
   python lab.py start 3
   ```

   If the loader refuses because of uncommitted changes, repeat step 3.

6. Confirm the load:

   ```bash
   python lab.py status
   ```

<details open>
<summary>What you should see</summary>

```
Workspace: .../ai-augmented-engineering/lab-workspace
  lab1       ...
  lab2       ...
  lab3       17/17 files identical, 0 extra lab file(s) present  <- matches
  lab4       ...
  solution   ...
git: uncommitted changes present
```

Only the **lab3** line matters: `17/17 files identical` and `<- matches`. `git: uncommitted changes present` is normal here; step 7 clears it.
</details>

7. Create the branch this lab's own commits go on, then commit the starting state:

   ```bash
   git checkout -b lab3
   git add -A
   git commit -m "Lab 3 start state"
   ```

8. Switch to the first review branch:

   ```bash
   git checkout pr/001
   git branch --show-current
   ```

   The three `pr/` branches are shared with everyone in the room. You review them; you do not commit to them. Task 5.4 puts your own work back on `lab3` at the end.

9. Look at what the PR changes:

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

10. Confirm the tests pass:

    ```bash
    pytest tests/ -q
    ```

    Expect `42 passed`. The planted issues are review issues, not test failures.

11. Pin the model. Open the chat panel (menu **View → Chat**), click the model pill (**Auto ▾**) and choose a **named** model.

    This is not optional in this lab. Auto can route consecutive chats to different models, which makes the Consistency score in Task 2 meaningless. Leave the same model selected for the whole lab.

---

## Task 1: Scope the agent and build it

### Task 1.1: Review your scope specification

1. Open your Chapter 3 scope specification document, or use the template below if you did not complete the exercise.

2. Confirm it covers all five components. Add any that are missing, using these definitions:

| Component | Definition |
|---|---|
| **Tools** | The branch diff against `main` for context. Read-only: the agent must not edit any files. |
| **Instructions** | Review against `.github/copilot-instructions.md` plus five DE criteria: schema drift handling, null safety, idempotency, logging completeness, type hint coverage. |
| **Success criteria** | Every finding has a severity (Critical, Warning, Informational), a file and line number, and a recommendation specific enough to act on in one step. |
| **Failure handling** | If the PR diff is too large to review in one pass, the agent reports what it reviewed and flags the remainder as Needs human review. |
| **Escalation path** | Any credential, secret, or key literal in source is escalated regardless of confidence and reported separately. Any finding where agent confidence is Low is also escalated. |

<details open>
<summary>Scope specification template (use if you did not complete the Chapter 3 exercise)</summary>

```
Tools: the branch diff against main for context. Read-only file access.
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

3. **Before you continue, note:**

   > Which of the five components can be enforced by the tool itself, and which can only be asked for in words? You check your answer in Task 1.3.

---

### Task 1.2: Create the custom agent

A custom agent is a Markdown file under `.github/agents/`, named `<name>.agent.md`. It has a name, a description, its own instructions and its own tool list, and it appears in the agent picker for anyone who opens this folder. You do not have to write the file by hand: `/create-agent` writes it from a description, the same way `/create-skill` wrote your skill in Lab 1.

Copilot has a second, related thing called a **subagent**, written in the same `.agent.md` format but marked `user-invocable: false`: the main agent starts it on its own, in an isolated context, when a job suits it. You are building the user-invocable kind, because this one you want to run deliberately and compare across three PRs.

1. Click **+** (New Chat) and set the mode pill to **Agent**.

2. Type `/` and choose **create-agent** ("Create a custom agent for a specific job") from the list. It becomes a highlighted tag. A pasted `/create-agent` is just text and does nothing; type the slash.

3. After the tag, paste the following and press Enter:

   ```
   Could you create a custom agent for me that acts as a DE pipeline code review agent.
   Context: the branch diff with main.
   The agent should review (no code changes) the changes against our defined standards.
   Additionally, check for:
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
   Name it de-pipeline-reviewer.
   ```

4. Wait for it to finish, then click **Keep** in the change summary above the chat input.

<details open>
<summary>What you should see</summary>

One new file, `.github/agents/de-pipeline-reviewer.agent.md`, listed in the change summary. The `.github/agents/` folder ships with the starter files and was empty until now.

If the agent says it is "recovering" or "rebuilding" an earlier agent, it found one in the repository's history. Let it finish; the next Task checks the file it produced.
</details>

---

### Task 1.3: Read the file and finish the scoping

The generated file is a first draft of your scope specification, written by an agent that read your project. Now you make it match the specification from Task 1.1.

1. Read the **Description** field. It is not documentation: Cursor reads it to decide when to hand work to this agent on its own, without you naming it. A description that says "use proactively after any change to `src/`" is asking for exactly that.

2. Read the body below the frontmatter. Find the step where the agent collects the diff (`git diff main...HEAD`) and the step where it reads `.github/copilot-instructions.md` and `.github/instructions/perl-conversion.instructions.md`.

   Those reads are in the instructions on purpose. A custom agent runs with its own instructions, so do not assume it inherits everything that applies to your ordinary chats. Telling it which files to read is what makes it reliable.

3. Check the tools it gave itself. Just above the `tools:` line in the frontmatter there is a **Configure Tools…** link; click it. A picker opens listing the built-in capability groups: **agent**, **browser**, **edit**, **execute**, **read**, **search**, **todo**, **vscode** and **web**.

   Confirm **edit** is unticked and **read**, **search** and **execute** are ticked, then click **OK**. Your prompt said "no code changes", so `/create-agent` has usually left `edit` off already; the point of this step is that you looked and decided, rather than trusting it.

<details open>
<summary>What you should see</summary>

```yaml
tools: [read, search, execute]
user-invocable: true
```

These are capability groups, not individual functions: `read` is every file-reading tool, `execute` is every way of running something on your machine. The count in the corner of the picker ("23 Selected") is the individual tools inside the groups you ticked.

This is the Tools line of your scope specification, and it is the answer to the note in Task 1.1. Every other component is words the agent can ignore; the tool list is enforced — with `edit` unticked there is no editing tool for the agent to reach for, whatever its instructions say.

Look at what `execute` means, though. It is how the agent runs `git diff`, and it is equally how something could run `git reset`. The generated instructions narrow it, usually with a line like "ONLY use `execute` to run read-only git commands." That is the honest shape of scoping an agent: the tool list is the fence, the instructions are the rules inside the fence, and only the fence is enforced.

`user-invocable: true` is what puts the agent in the picker. The same file marked `false` becomes a subagent the main agent starts on its own.
</details>

4. Leave **Model** unset so the agent uses the model you pinned in Task 0 step 11.

5. Check the body against the five components from Task 1.1 and add anything missing, in the agent's own voice. In particular, confirm that it covers:

   - [ ] Review only changed lines; do not comment on code outside the diff
   - [ ] The five DE criteria
   - [ ] The output fields: criterion, file and line, severity, confidence, recommendation
   - [ ] Failure handling for a diff too large to review in one pass
   - [ ] The escalation path, including Low confidence

6. Confirm the file is saved (no dot on the tab).

<details open>
<summary>What the file should look like</summary>

```markdown
---
description: "Reviews the current branch diff against main for DE pipeline code changes.
  Use when the user asks to review, audit, or check a pipeline PR/branch/diff for schema
  drift, null safety, idempotency, logging completeness, or type hint coverage before
  merging. Read-only, does not modify code."
tools: [read, search, execute]
user-invocable: true
---

You are a Data Engineering pipeline code reviewer for this market-data batch pipeline
(ingest -> transform -> validate). You produce review findings only.
You never modify files, never commit, and never apply fixes.

## When invoked

1. Determine the review scope: the git diff of the current branch versus main.
2. Collect `git diff main...HEAD` and `git diff` (unstaged and staged working tree).
3. Read the changed Python files at the versions on disk so line numbers match.
4. Read DE standards in `.github/copilot-instructions.md`, Perl-to-Python rules in
   `.github/instructions/perl-conversion.instructions.md`,
   and the registered schema under `schemas/`.
5. Begin the review immediately. Do not implement, patch, or rewrite code.

... (criteria, output format and escalation path follow)
```

The exact wording will differ from your neighbour's; the frontmatter and the five criteria should not.
</details>

7. **Do not commit the agent file yet.** It is untracked, which is what you want: untracked files stay put when you switch branches, so the same agent follows you onto `pr/002` and `pr/003` without ever landing on a shared branch. Task 5.4 commits it to your `lab3` branch at the end.

---

### Task 1.4: Run it on PR 001

1. Click **+** (New Chat). Confirm you are still on `pr/001` (`git branch --show-current`).

2. Click the mode pill and choose **de-pipeline-reviewer** from the list, then send:

   ```
   Review the changes on this branch.
   ```

   Your agent is now in the mode picker beside Agent, Ask and Plan, because it lives in this folder.

3. Click **Allow** on the command card when it runs `git diff`.

4. Read every finding before going on. Expect somewhere between eight and fifteen. Some are issues your instructor planted; some are real issues nobody planted. Both are legitimate.

5. Expand the **Completed N steps** line above the findings. It shows the agent fetching the diff itself and reading the instruction files it was told to read.

<details open>
<summary>What you should see</summary>

Findings grouped by severity, each citing a file and a line, each with a confidence level and a one-sentence recommendation, and a closing `Overall recommendation: APPROVE / REQUEST CHANGES / ESCALATE`.

No change summary above the input: with no edit tool in its list there is nothing to keep or undo. If a change summary appears anyway, the `tools:` line is missing or misspelled; fix it in the agent file and run again.

If the agent reports that it has no diff to review, you are on `main` rather than `pr/001`. Check with `git branch --show-current`.
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

2. For the Consistency row, click **+** for a **fresh** chat, set the mode pill to **de-pipeline-reviewer** and send the same message. In the same chat the agent sees its first answer and repeats it, which inflates the score. Compare the two outputs.

<details open>
<summary>Scoring guidance</summary>

**Coverage (false negatives):** compare the findings against the instructor's list. Each missed issue costs one point. Score 5 only if every known issue was found.

**Accuracy (false positives):** count findings that describe something not in the code. Each costs one point. A real issue that is not on the instructor's list is **not** a false positive; note it and move on.

**Clarity (actionability):** could you act on each recommendation without a follow-up question? "Consider improving null handling" is not actionable. "Add an explicit None check on `instrument_id` at line 47 before passing it to `transform_record()`" is. Score 5 only if every recommendation is immediately actionable.

**Consistency (determinism):** score 5 if the two runs' findings are identical, 1 if the severity ratings or the finding list differ significantly. Both runs used the same agent file and the same model, so what varies here is the model, not your instructions. That is the floor you are working against.

**Production threshold:** 16 out of 20 with no dimension below 3. First-run scores vary widely by model; Consistency is usually the lowest dimension.
</details>

3. **Before you continue, note:**

   > Your total, and the single lowest-scoring dimension. That dimension is your improvement target for Task 3.

---

## Task 3: First iteration cycle

### Task 3.1: Save a copy, then make one targeted change

From here on, iterating means editing the agent file. That is the point: the thing you are improving is a file in the repository, not a message in a chat window.

1. Copy the whole contents of `.github/agents/de-pipeline-reviewer.agent.md` into a scratch file outside the repository. That is your Version 1, and your way back.

2. Based on your lowest-scoring dimension, make exactly one change to the agent file. Do not change more than one thing.

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

3. Save the file, then click **+** for a fresh chat, set the mode pill to **de-pipeline-reviewer** and send `Review the changes on this branch.` again.

   You pick a mode instead of re-pasting an instruction set, and every chat in the folder picks the change up automatically. That is the difference between a prompt you keep and an agent you own.

---

### Task 3.2: Re-score

1. Score all four dimensions again and record the new total.

2. Decide what to keep:

| Result | Action |
|---|---|
| Target dimension improved | Keep the change. Record the new total. |
| Target dimension unchanged or worse | Put the Version 1 text back from your scratch copy. Try a different change for the same dimension. |
| Another dimension dropped significantly | Go back and try a narrower change. Adding an output template *and* a scope restriction in one step is the classic way to fix Consistency and lose Coverage. |

---

## Task 4: Second iteration and generalization test

### Task 4.1: Second iteration

1. Identify the new lowest-scoring dimension from Task 3.2. Make one more targeted change to the agent file, the same way as Task 3.1, and re-score.

   If you have already reached 16 out of 20 with no dimension below 3, skip to Task 4.2. Do not force a change.

---

### Task 4.2: Generalization test on PR 002

1. Switch branches:

   ```bash
   git checkout pr/002
   git status --short
   ```

   `git status` shows your agent file as untracked (`?? .github/agents/`). It came with you: workspace configuration is not branch content.

2. Click **+** for a fresh chat, set the mode pill to **de-pipeline-reviewer** and send `Review the changes on this branch.`

3. Score the pr/002 output on all four dimensions and compare with your pr/001 score. Two planted issues to check for: one needs reasoning across files (an append-mode write with no de-duplication); the other is a narrowed `except` clause.

4. **Before you continue, note:**

   > Did your agent catch both? If pr/002 scored much lower than pr/001, which change over-fitted to pr/001's issues? Broaden or remove it.

---

### Task 4.3: Hard PR test on PR 003

1. Switch branches:

   ```bash
   git checkout pr/003
   ```

2. Click **+** for a fresh chat, set the mode pill to **de-pipeline-reviewer** and send `Review the changes on this branch.`

3. PR 003 contains a hard-coded credential. Check the output for all three:

   - [ ] The credential finding is marked ESCALATE
   - [ ] It is reported in a separate ESCALATED section, not in the main list
   - [ ] The overall recommendation is ESCALATE, not REQUEST CHANGES or APPROVE

4. If any box is unchecked, your escalation path is confidence-based rather than risk-based: the agent is *sure* the key is a bug, so "escalate when confidence is Low" never fires. Add this to the agent file and run again:

   ```
   Any credential, secret, token, or API key literal in source code is a security finding:
   mark it ESCALATE regardless of confidence, report it in a separate ESCALATED section
   before the other findings, and set the overall recommendation to ESCALATE.
   ```

   Escalate-when-unsure is not the same as escalate-when-dangerous. Ship the version that has both.

---

## Task 5: The shipped rubric and Review Changes

### Task 5.1: Understand what you are comparing

Three distinct things review code in this project. Keep them separate:

| System | What it is | What it reads |
|---|---|---|
| **Your custom agent** | The file you just built; runs when you select it in the mode picker | Whatever its instructions tell it to read |
| **Review Changes** | Local in-editor review from the Source Control panel, no PR needed | `.github/copilot-instructions.md` and the file's diff |
| **Copilot code review on GitHub.com** | PR automation: Copilot as a reviewer on pull requests | `.github/copilot-instructions.md` in the repository |

One file, three readers: the instructions you wrote in Lab 1 are what the local review and the GitHub review both use, so anything you want enforced on PRs belongs there. The Cursor track ships a separate rubric file, `.cursor/BUGBOT.md`, for its own review tooling; in Task 5.2 you read it as an example rubric. Your custom agent is the third reader, and it is the only one you control completely.

---

### Task 5.2: Read the shipped review rubric

1. In the Explorer, open `.cursor/BUGBOT.md`. Copilot does not read this file; it is the Cursor track's review rubric, and it is a good example of one. Where a Copilot team would put these rules is a `## Code Review Rules` section of `.github/copilot-instructions.md`.

2. Read the Security, Critical, Warning and Informational sections and compare them with your agent's five criteria.

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

   > One thing the file has that your agent does not (the exception-narrowing rule and the append-mode rule are candidates), and one thing it lacks.

   Do not add it to `copilot-instructions.md` in this lab; the `pr/` branches are shared, and Task 5.3 needs the shipped instructions so everyone compares the same thing.

---

### Task 5.3: Run Review Changes on PR 001

Review Changes works on files the Source Control panel shows as changed. PR 001's changes are committed on `pr/001`, so first put them into the working tree on a scratch branch.

1. Switch back to the first PR and stage its changes:

   ```bash
   git checkout pr/001
   git checkout -b review-001
   git reset --soft main
   git status --short
   ```

   Status lists the three `src/` files as staged (`M`). The code is unchanged; only the bookkeeping moved.

2. Open the **Source Control** panel (the branch icon in the left bar). The three files appear under Staged Changes.

3. Right-click `src/ingest.py` and choose **Review Changes**. Copilot reviews that file's diff and posts its comments inline in the editor. Repeat for `src/transform.py` and `src/validate.py`.

4. Read the comments. Each has an action next to it; do not apply anything, you are comparing, not fixing. If a file comes back with no comments at all, run **Review Changes** on it again; an empty first pass happens.

5. Put the branch back the way you found it:

   ```bash
   git reset --hard pr/001
   git checkout pr/001
   git branch -D review-001
   git status --short
   ```

   Status shows only your untracked agent file, and you are on `pr/001`.

<details open>
<summary>What you should see</summary>

A handful of inline comments per file, some naming a `copilot-instructions.md` standard as the reason. Expect it to find some but not all of the three planted pr/001 issues, plus a real issue nobody planted. That is not a failure; it is the data point for Task 5.4.
</details>

---

### Task 5.4: Compare, then keep your agent

1. Fill in this table from the Review Changes comments and your best custom-agent output on pr/001:

| | Your custom agent | Review Changes |
|---|---|---|
| Known pr/001 issues found | /3 (a tuned agent typically finds all three) | /3 |
| False positives | | |
| Most actionable finding | | |
| Time to produce output | | |
| Runs on someone else's machine after a clone | | |

2. **Before you continue, note:**

   > When would you use Review Changes instead of your custom agent in your daily work, and when the custom agent instead?

<details open>
<summary>Typical answer pattern</summary>

Review Changes is a right-click and needs no setup; use it for a quick sanity check on a file before committing. Your custom agent produces more structured output with severity ratings, confidence levels and DE-specific criteria, and it is a file in the repository: a teammate who clones the repo has your reviewer, at your standard, without being told. Use it before raising a PR, or in an asynchronous review where the output must be actionable by someone who was not present. On GitHub, Copilot code review on the PR reads the same `copilot-instructions.md`, so the standards travel with the repository.

Neither replaces the other. The professional workflow is: Review Changes before committing, your agent before raising the PR.
</details>

3. Leave the `pr/` branches as you found them. If you changed a tracked file on one, put it back:

   ```bash
   git checkout -- .
   ```

4. Commit your agent on your own branch, where it belongs:

   ```bash
   git checkout lab3
   git add .github/agents/
   git commit -m "Add DE pipeline reviewer agent"
   git --no-pager log --oneline -2
   ```

   That is the deliverable of this lab: not a review, but a reviewer, versioned with the code it reviews.

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

What was your baseline score and your final score after two iteration cycles? What single change to the agent file made the biggest difference?

---

**Question 2**

In Task 4.2, did your agent score similarly on pr/002 as on pr/001? If the score dropped, what caused the over-fitting?

---

**Question 3**

In Task 1.3 you restricted the agent's `tools:` list rather than writing "do not modify any files" in the instructions. Name one thing that protects you from that the instruction does not. Why is "escalate when unsure" not the same as "escalate when dangerous"?

---

**Question 4**

Write one new rule for a `## Code Review Rules` section of `.github/copilot-instructions.md`, based on an issue your agent found in pr/003 that the shipped rubric does not cover. Would you rather put that rule in the instructions file or in your agent file, and why?
