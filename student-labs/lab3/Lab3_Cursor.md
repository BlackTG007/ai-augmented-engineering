# Lab 3: Build a DE Pipeline Code Review Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro or Teams plan)
**Duration:** 75 minutes
**Day:** Day 2, following Module 4

---

## Prerequisites

- [ ] Modules 3 and 4 lectures completed
- [ ] Chapter 3 scoping exercise completed (or the scope specification template in Task 1.1 reviewed)
- [ ] Lab 2 completed or not; Task 0 loads the Lab 3 starting point either way
- [ ] The repository's `lab-workspace` folder open in the Cursor IDE, with the venv active in the terminal
- [ ] Git working in the repository; the `pr/001`, `pr/002`, `pr/003` branches present (`git branch -a` lists them under `origin/`)

---

## Lab Overview

Your team reviews dozens of Python pipeline PRs each week. Manual review is inconsistent and depends on who is available. In this lab you build a **subagent**: a real, reusable agent that lives in a file in the repository, reviews pipeline code against DE-specific criteria, flags issues with severity ratings, and produces a structured review summary ready for human sign-off. Then you compare it with Cursor's built-in Agent Review on the same PR.

Everything you have configured so far has shaped how the agent behaves. A subagent is the first thing you build that *is* an agent: it has its own name, its own instructions, its own permissions, and its own model.

**What you will produce:**
- `.cursor/agents/de-pipeline-reviewer.md`: a scoped, read-only review agent you invoke with `/de-pipeline-reviewer`
- Three rules you added yourself, each one closing a gap you found by running the agent
- A written comparison of your subagent versus Agent Review on the same PR

**How this lab is written:** each Task has numbered steps. A numbered step is something you do. Text between steps explains what you are looking at; the boxes marked "What you should see" tell you what a correct result looks like. The agent's behaviour varies from run to run: it may ask questions before acting, act at once, or describe a change and wait for your go-ahead. If it asks, answer; if it waits, reply `Go ahead`. The steps describe the end state, not every turn of the conversation.

---

## Task 0: Load the starter files and check out the first PR

Do this whether or not you completed Lab 2. It resets the workspace to a known state, then moves you onto the first of three pull-request branches that ship with the repository.

1. Open a terminal inside Cursor: menu **Terminal → New Terminal**. It opens in `lab-workspace/`; every command in this lab runs from there.

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

   The three `pr/` branches are shared with everyone in the room. You review them; you do not commit to them. Task 3.4 puts your own work back on `lab3` at the end.

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

11. Check which model you are using. At the bottom of the chat input, click the effort and speed picker (it reads something like **High Fast**). The panel that opens has **Fast**, **Effort** and **Model**; click **Model**.

    Confirm a **named** model is selected rather than **Auto**. The default on a Teams seat is usually Cursor's own Grok, which is exactly what you want; if you want the room on the same footing, pick the latest **Cursor Grok**. Whatever it is, leave it alone for the rest of the lab.

    This matters more than it looks. In Task 2 you change one thing at a time and re-run to see what the change did. If Auto routes consecutive conversations to different models, you are measuring Cursor's routing rather than your edit. On some models, subagent calls do not run at all.

---

## Task 1: Scope the agent and build it

### Task 1.1: Review your scope specification

1. Open your Chapter 3 scope specification document, or use the template below if you did not complete the exercise.

2. Confirm it covers all five components. Add any that are missing, using these definitions:

| Component | Definition |
|---|---|
| **Tools** | The branch diff against `main` for context. Read-only: the agent must not edit any files. |
| **Instructions** | Review against `.cursor/rules/de-standards.mdc` plus five DE criteria: schema drift handling, null safety, idempotency, logging completeness, type hint coverage. |
| **Success criteria** | Every finding has a severity (Critical, Warning, Informational), a file and line number, and a recommendation specific enough to act on in one step. |
| **Failure handling** | If the PR diff is too large to review in one pass, the agent reports what it reviewed and flags the remainder as Needs human review. |
| **Escalation path** | Any credential, secret, or key literal in source is escalated regardless of confidence and reported separately. Any finding where agent confidence is Low is also escalated. |

<details open>
<summary>Scope specification template (use if you did not complete the Chapter 3 exercise)</summary>

```
Tools: the branch diff against main for context. Read-only file access.
The agent must not edit any files.

Instructions: Review changed code against .cursor/rules/de-standards.mdc
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

### Task 1.2: Create the subagent

A subagent is a Markdown file under `.cursor/agents/`. It has a name, a description, its own instructions, and its own permissions, and every conversation in this project can call it. You do not have to write the file by hand: `/create-subagent` writes it from a description, the same way `/create-skill` wrote your skill in Lab 1.

1. Click **+** for a new conversation (Agent mode).

2. Type `/` and choose **create-subagent** from the list. It becomes a highlighted tag. A pasted `/create-subagent` is just text and does nothing; type the slash.

3. After the tag, paste the following and press Enter:

   ```
   Could you create a subagent for me that acts as a DE pipeline code review agent.
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

4. Wait for it to finish, then click **Keep** in the change summary at the bottom of the chat.

<details open>
<summary>What you should see</summary>

One new file, `.cursor/agents/de-pipeline-reviewer.md`, listed in the change summary. The `.cursor/agents/` folder did not exist a moment ago; the command created it.

The file opens in the editor with a form above the text: **Name**, **Model**, **Description**, and two toggles, **Read-only** and **Background**. That form and the text below it are the same thing, the way the rules editor in Lab 1 showed `alwaysApply` as a dropdown: change the form and the frontmatter follows.

If the agent says it is "recovering" or "rebuilding" an earlier agent, it found one in the repository's history. Let it finish; the next Task checks the file it produced.
</details>

---

### Task 1.3: Read the file and finish the scoping

The generated file is a first draft of your scope specification, written by an agent that read your project. Now you make it match the specification from Task 1.1.

1. Read the **Description** field. It is not documentation: Cursor reads it to decide when to hand work to this agent on its own, without you naming it. A description that says "use proactively after any change to `src/`" is asking for exactly that.

2. Read the body below the frontmatter. Find the step where the agent collects the diff (`git diff main...HEAD`) and the step where it reads `.cursor/rules/de-standards.mdc`, `.cursor/rules/perl-to-python.mdc` and `.cursor/BUGBOT.md`.

   Those reads are in the instructions on purpose. A subagent runs in its own context, so do not assume it inherits the rules that apply to your chat. Telling it which files to read is what makes it reliable.

3. Turn **Read-only** on.

   This is the Tools line of your scope specification, and it is the answer to the note in Task 1.1. Every other component is words the agent can ignore. Read-only is enforced: no file edits and no state-changing shell commands. Reading the diff still works, because reading changes nothing.

4. Leave **Background** off. A background subagent returns immediately and works on its own; you want this one to hand its findings back before you do anything else. You turn it on in Lab 4, where it earns its keep.

5. Set the agent's own **Model**. It is created as **Inherit from parent**, which means this agent behaves differently depending on which conversation happens to call it — the opposite of what a file full of fixed instructions is for. Open the dropdown and choose a specific model; the latest **Cursor Grok** is a sensible default and matches what you confirmed in Task 0 step 11.

   Do this yourself, here, rather than asking the chat to do it for you. Cursor writes your choice into the frontmatter as a `model:` line, and from now on the agent runs on that model no matter who calls it.

6. Check the body against the five components from Task 1.1. You are checking for **coverage, not phrasing**: `/create-subagent` writes its own wording, so yours will not match the example below or your neighbour's, and that is fine. Add anything genuinely missing, in the agent's own voice. Confirm it covers:

   - [ ] Review only changed lines; do not comment on code outside the diff
   - [ ] The five DE criteria
   - [ ] The output fields: criterion, file and line, severity, confidence, recommendation
   - [ ] Failure handling for a diff too large to review in one pass
   - [ ] The escalation path, including Low confidence

7. Confirm the file is saved (no dot on the tab).

<details open>
<summary>What the file should look like</summary>

```markdown
---
name: de-pipeline-reviewer
description: DE pipeline code review specialist. Use proactively after any change to
  src/, tests/, schemas/, or Perl-to-Python conversion work. Reviews the current branch
  diff against main with no code changes.
readonly: true
---

You are a Data Engineering pipeline code reviewer for this market-data batch pipeline
(ingest -> transform -> validate). You produce review findings only.
You never modify files, never commit, and never apply fixes.

## When invoked

1. Determine the review scope: the git diff of the current branch versus main.
2. Collect `git diff main...HEAD` and `git diff` (unstaged and staged working tree).
3. Read the changed Python files at the versions on disk so line numbers match.
4. Read DE standards in `.cursor/rules/de-standards.mdc`, Perl-to-Python rules in
   `.cursor/rules/perl-to-python.mdc`, review rules in `.cursor/BUGBOT.md`,
   and the registered schema under `schemas/`.
5. Begin the review immediately. Do not implement, patch, or rewrite code.

... (criteria, output format and escalation path follow)
```

Your wording will differ from this example and from your neighbour's, because the wording is generated. The frontmatter fields and the five criteria are what should match.
</details>

8. **Do not commit the agent file yet.** It is untracked, which is what you want: untracked files stay put when you switch branches, so the same agent follows you onto `pr/002` and `pr/003` without ever landing on a shared branch. Task 3.4 commits it to your `lab3` branch at the end.

---

### Task 1.4: Run it on PR 001

1. Click **+** for a new conversation (Agent mode). Confirm you are still on `pr/001` (`git branch --show-current`).

2. Type `/` and choose **de-pipeline-reviewer** from the list, then press Enter.

   Your agent is now in the list beside Cursor's own commands, because it lives in this project.

   You *could* type extra instructions after the tag — "focus on the transform module", say — and the agent would take them alongside its own. This one does not need any: everything it should do is in the file. Pressing Enter with nothing after the name is the whole invocation, and that is the test of a well-scoped agent.

3. Read every finding before going on. Expect somewhere between eight and fifteen. Some are issues your instructor planted; some are real issues nobody planted. Both are legitimate.

4. Expand the trace above the findings. It shows the agent fetching the diff itself and reading the rules files it was told to read.

<details open>
<summary>What you should see</summary>

Findings grouped by severity, each citing a file and a line, each with a confidence level and a one-sentence recommendation, and a closing `Overall recommendation: APPROVE / REQUEST CHANGES / ESCALATE`.

No change summary at the bottom of the chat: Read-only means there is nothing to keep or undo. If a change summary appears anyway, Read-only is off; turn it on in the agent file and run again.

If the agent reports that it has no diff to review, you are on `main` rather than `pr/001`. Check with `git branch --show-current`.
</details>

---

## Task 2: Iterate on the agent

You are not going to score this agent out of twenty. Scoring needs an answer key you do
not have at review time, and it turns a tuning exercise into a quiz. What you are going
to do instead is what you would actually do at your desk: run the agent against code
whose defects you already know, look at the gap between what it found and what is there,
and close the gap by editing the file.

Three branches, three rounds. The first two hand you the answer key. The third does not,
until you have run it.

One rule for the whole task: **every fix is a change to
`.cursor/agents/de-pipeline-reviewer.md`.** Not a follow-up message in the chat. A message
improves one answer. The file improves every answer, in every conversation, for everyone
who clones the repository.

---

### Task 2.1: PR 001 — find the gap, add your first rule

1. Copy the whole contents of `.cursor/agents/de-pipeline-reviewer.md` into a scratch file
   **outside** the repository. That is your Version 1 and your way back if an edit makes
   things worse.

2. Scroll back to your Task 1.4 output so you can see the findings while you read the list
   below. If you have lost it, click **+** for a fresh conversation, type `/`, choose
   **de-pipeline-reviewer** and press Enter.

3. Open the box below and tick off what your agent found.

<details open>
<summary>Defects planted on pr/001 — read this after your run, not before</summary>

Nine deliberate defects, in three files. The rule each one breaks is named so you can see
where your agent should have got it from.

**`src/ingest.py` — the new `load_supplementary_records()`**

- [ ] No return type declared (`de-standards.mdc`: all return types must be declared)
- [ ] No entry or exit logging (`de-standards.mdc`: every pipeline function must log on entry and exit)
- [ ] Reads a CSV with no schema check against `schemas/` (`BUGBOT.md`, Critical)
- [ ] Appends to the caller's `existing_records` list **and** returns it, so the caller ends
      up with two names for one list and a mutation it did not ask for

**`src/transform.py` — the new `compute_weighted_price()`**

- [ ] No type hints on `prices`, `volumes` or the return value (`de-standards.mdc`)
- [ ] No entry or exit logging (`de-standards.mdc`)

**`src/validate.py` — inside `validate_records()`**

- [ ] `exchange_list` is built and never used (`BUGBOT.md`, Informational: unused variables
      introduced by the change)
- [ ] It is a for-append loop where the house idiom is a comprehension (`BUGBOT.md`, Informational)
- [ ] `r.get("exchange_code") or "UNKNOWN"` silently substitutes a placeholder for a missing
      exchange code — inside the function whose entire job is to *record* violations. Nothing
      downstream will ever know the value was missing.

</details>

4. Count the misses. The standards findings — type hints, logging, unused variables — are
   the ones a competent reviewer gets without help. The last item in each group is the
   interesting one.

5. Pick **one** miss and add **one** rule to the agent file that would have caught it. Write
   it in the agent's own voice, in the Criteria section. Two that work, if you need a
   starting point:

   For the mutation:

   ```
   Flag any function that modifies one of its arguments in place.
   A function that both mutates an argument and returns it is a finding:
   name the argument and say which of the two behaviours the caller is likely to miss.
   ```

   For the placeholder substitution:

   ```
   In validation code, a missing or empty value on a required field must be recorded as a
   violation.
   Substituting a placeholder such as UNKNOWN, N/A or 0 instead of recording the violation
   is a Critical finding.
   ```

   Add one, not both. You want to see what a single change does.

6. Save the file. Click **+** for a **fresh** conversation and run `/de-pipeline-reviewer`
   again. A fresh conversation matters: in the same thread the agent can see its previous
   answer and will tend to repeat it, which tells you nothing about the rule you just added.

<details open>
<summary>What you should see</summary>

The same findings as before, plus the one you wrote the rule for, now reported with the
severity your rule assigned it. You typed four words to get it. You did not re-paste an
instruction set, and neither will anyone else on your team.

If the new finding still does not appear, your rule is probably too abstract. "Check for
side effects" does not work. "Flag any function that modifies one of its arguments in
place" does, because it names the thing to look for rather than the quality to have.
</details>

<details>
<summary>If your agent caught all nine</summary>

That happens on a strong model, and it means the coverage half of the job is already done.
Improve the **output** instead, which is the half that decides whether anyone acts on it.
Add one of these to the agent file and re-run:

```
Every finding must end with a concrete suggested fix: the replacement line or lines,
not a description of what to change.
```

```
Every finding must name the rule it comes from: the file and the line of
.cursor/rules/de-standards.mdc or .cursor/BUGBOT.md that the code violates.
If a finding comes from neither file, say so and mark it as your own judgement.
```

The second one is worth doing even if you do not need it. An agent that cites its source
is an agent whose findings you can argue with.
</details>

7. **Before you continue, note:**

   > Which rule you added, and whether the re-run picked it up.

---

### Task 2.2: PR 002 — a different class of defect

pr/001 was mostly about what the agent does not know to look for. pr/002 is about something
harder: a change that looks like a tidy-up and is actually a regression.

1. Switch branches:

   ```bash
   git checkout pr/002
   git status --short
   ```

   `git status` shows your agent file as untracked (`?? .cursor/agents/`). It came with you:
   untracked files stay put when you switch branches, which is why the same agent follows
   you across all three PRs without ever landing on a shared branch.

2. Click **+** for a fresh conversation and run `/de-pipeline-reviewer`.

3. Open the box below and tick off what it found.

<details open>
<summary>Defects planted on pr/002 — read this after your run</summary>

Seven deliberate defects, in two files.

**`src/transform.py`**

- [ ] `except (ValueError, TypeError)` was narrowed to `except ValueError`. A `None` volume
      now raises `TypeError` and crashes the stage instead of being skipped with a warning
      (`BUGBOT.md`, Critical: do not narrow or remove exception types in existing except clauses)
- [ ] The new `append_to_daily_summary()` opens the file in append mode with no
      de-duplication check, so running the stage twice doubles the rows
      (`BUGBOT.md`, Critical: pipeline steps that write records must be idempotent)
- [ ] It never calls `writeheader()`, and takes its fieldnames from a single record's keys,
      so the column order can differ between calls
- [ ] No entry or exit logging (`de-standards.mdc`)
- [ ] `logger.info("Transform pipeline complete")` was deleted
      (`BUGBOT.md`, Warning: removing an existing log statement is a Warning)

**`src/validate.py`**

- [ ] `import os` sits inside the function body rather than at the top of the file
- [ ] `input_path.exists()` was replaced with `os.path.exists(input_file)`
      (`de-standards.mdc`: use pathlib.Path for all file operations; never use os.path).
      The error message on the next line still interpolates `input_path`, so the check and
      the message now disagree about what was looked at.

</details>

4. The narrowed `except` is the one to watch. It is a two-character deletion that reads like
   a cleanup, it passes every test that does not feed a null volume through the stage, and
   it is the defect most review tools miss — including Cursor's own, as you will see in
   Task 3.

5. Whatever your agent missed, add **one** rule for it. For the narrowed `except`:

   ```
   Treat any change to an existing except clause as a finding in its own right.
   If the change removes an exception type from the tuple, name the input that will now
   crash instead of being handled, and mark the finding Critical.
   ```

6. Save the file, click **+** for a fresh conversation, and run `/de-pipeline-reviewer` again
   on pr/002.

<details open>
<summary>What you should see</summary>

The rule you added in Task 2.1 still firing on pr/002's own instances of the same pattern,
alongside the new one. That is the point of the exercise and it is worth stopping on: you
are not tuning the agent for one diff, you are accumulating a reviewer. Every rule you add
applies to every future PR, which is exactly the property a prompt in a chat window does
not have.
</details>

7. **Before you continue, note:**

   > Whether your Task 2.1 rule fired here as well, and on what.

---

### Task 2.3: PR 003 — no answer key until you have run it

Two rounds of tuning. Now find out whether what you built generalises to code you have not
seen. This round you get no help before the run.

1. Switch branches:

   ```bash
   git checkout pr/003
   ```

2. Click **+** for a fresh conversation and run `/de-pipeline-reviewer`. Do not read ahead.

3. Write down how many findings you got and which files they are in, before you open
   anything below.

4. Now open the box.

<details>
<summary>Defects planted on pr/003</summary>

Nine deliberate defects, in three files.

**`src/figi_client.py`**

- [ ] `or "demo-fallback-key-2026"` — an API key literal in source
      (`BUGBOT.md`, Security: blocking, including "demo" and "fallback" values)
- [ ] Because that fallback always resolves, the `FigiClientError("No API key provided...")`
      branch below it is now unreachable. The guard is still in the file and no longer guards anything
- [ ] A blank line was removed before `self._url`

**`src/ingest.py`**

- [ ] `except FigiClientError` was broadened to a bare `except Exception`
      (`BUGBOT.md`, Critical: do not catch exceptions silently)
- [ ] The `logger.error(f"FigiClient request failed: {exc}")` line inside it was deleted, so
      the failure is now both broader and silent (`BUGBOT.md`, Warning)
- [ ] The new `archive_run()` reads `records[0].keys()`, which raises `IndexError` on an
      empty list
- [ ] `archive_run()` appends with no `writeheader()` and no de-duplication check
      (`BUGBOT.md`, Critical: idempotency)
- [ ] `archive_run()` has no docstring and no logging (`de-standards.mdc`)

**`src/validate.py`**

- [ ] The new `summarise_violations()` returns `by_field` as an empty dict on every call. It
      is a stub that was shipped as though it were finished, and it will report zero for
      every field forever
- [ ] `logger.info(f"Starting validate pipeline for {input_file}")` was deleted (`BUGBOT.md`, Warning)

</details>

5. Compare honestly. Coverage is not the interesting question here — by now your agent
   probably finds most of these. The interesting question is what it did with the credential
   on line 57 of `figi_client.py`. Check all three:

   - [ ] The credential is reported in a separate **ESCALATED** section, before the other findings
   - [ ] It is marked **ESCALATE**, not Critical
   - [ ] The overall recommendation is **ESCALATE**, not REQUEST CHANGES or APPROVE

6. If any of those three is unchecked, you have found something more interesting than a
   missed defect. Your agent almost certainly *found* the key — it is hard to miss. It
   filed it as a Critical bug and moved on.

   The reason is in your escalation path. If it says something like "escalate when
   confidence is Low", it will never fire on a hard-coded credential, because the agent is
   completely confident that a hard-coded credential is a bug. It is right, and it is still
   the wrong call: this is not a thing to fix in a review comment, it is a thing to stop the
   PR for and tell a human about, because the key may already be in the history and in
   everyone's clone.

   Add this to the agent file:

   ```
   Any credential, secret, token or API key literal in source code is a security finding:
   mark it ESCALATE regardless of confidence, report it in a separate ESCALATED section
   before the other findings, and set the overall recommendation to ESCALATE.
   ```

   Run it once more on pr/003 to confirm all three boxes tick.

7. **Before you continue, note:**

   > Escalate-when-unsure is not the same as escalate-when-dangerous. Which one did your
   > agent have before this step, and which categories other than credentials deserve the
   > same treatment on your own team's code?

<details open>
<summary>Why this one is a rule and not a miss</summary>

The rules you added in Tasks 2.1 and 2.2 changed what the agent *looks for*. This one changes
how it *classifies* what it already found — it is a policy, not a detection. Those are the
rules worth writing down, because they are the ones where a reasonable reviewer, human or
not, will make a defensible call that your team has decided against. Risk class, not
confidence, is what should drive escalation: credentials, customer data, money arithmetic,
anything with a regulator attached.
</details>

---

8. Switch back to the first PR and run your finished agent there one last time:

   ```bash
   git checkout pr/001
   ```

   Click **+** for a fresh conversation and run `/de-pipeline-reviewer`.

   Task 2.1's output came from your Version 1. Three rules later you have a different
   reviewer, and Task 3 compares it against Cursor's built-in review on this same branch.
   Keep this output on screen; you will need it.


---

## Task 3: BUGBOT.md and Agent Review

### Task 3.1: Understand what you are comparing

Three distinct things review code in this project. Keep them separate:

| System | What it is | What it reads |
|---|---|---|
| **Your subagent** | The file you just built; runs when you call it, or when Cursor delegates to it | Whatever its instructions tell it to read |
| **Agent Review** | Local in-editor review from the Source Control panel, no GitHub connection needed | `.cursor/rules/*.mdc` **and** `.cursor/BUGBOT.md` |
| **Bugbot** | PR automation on GitHub, configured under Automations in the Agents Window; needs the repo linked in the Cursor dashboard | `.cursor/BUGBOT.md` (whether it also reads rules is unverified) |

Agent Review does read your rules files: on the current build its findings cite `de-standards.mdc` by name. `BUGBOT.md` is the rubric that is *shared* with Bugbot in the cloud, so anything you want enforced on GitHub PRs belongs there too. One sentence to remember: same rubric file, two readers, one in your editor, one on GitHub. Your subagent is the third reader, and it is the only one you control completely.

---

### Task 3.2: Read .cursor/BUGBOT.md

1. In the Explorer, open `.cursor/BUGBOT.md`.

   The path is `.cursor/BUGBOT.md`: not `BUGBOT.md` at the project root, and not `.cursor/rules/BUGBOT.md`. A file at the wrong path is silently ignored.

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

   Do not edit the file in this lab; the `pr/` branches are shared, and Task 3.3 needs the shipped version so everyone compares the same thing.

---

### Task 3.3: Run Agent Review

1. Open Cursor Settings: click the gear icon at the top right of the window. Choose **Git & PRs** in the left list and scroll to the **Agent Review** section. Confirm **Default Approach** is **Quick**. Leave **Start Agent Review on Commit** off; you run the review by hand. Close Settings.

2. Switch back to the first PR:

   ```bash
   git checkout pr/001
   ```

3. Open the **Source Control** panel (third icon in the left bar).

   Look at the **Changes** list at the top before you go further. It shows your untracked
   agent file and nothing else, because everything pr/001 changed is already committed on
   the branch. That list is going to make you think there is nothing here to review. There is.

   **Changes** and **Agent Review** are two sections of one panel with two different scopes:
   Changes is your uncommitted working tree, and Agent Review compares the whole branch
   against `main` — its own tooltip reads "Review diffs vs. main." An empty Changes list says
   nothing about what Agent Review will find.

4. Find the **Agent Review** section below Changes and click **Find Issues**. The button reads
   "Reviewing" with a progress ring for about a minute.

5. A prompt appears offering to **review every commit automatically**, with a button to enable
   it. Dismiss it. Leave it off.

   It is a real feature and a reasonable thing to turn on in your own repository: every commit
   gets reviewed without your asking. We are leaving it off here for two reasons. You are
   working on shared `pr/` branches that the rest of the room is also checking out, and you
   want to run this review by hand so you can see exactly what triggered it and compare it
   against your own agent. Turn it on at your desk next week if you like it.

6. Read the findings in the same panel. Clicking a finding opens a diff view with an explanation card, **Fix with Agent**, and **Dismiss**. Do not click **Fix**, **Fix All Issues**, or **Fix with Agent**: you are comparing, not fixing. If a review comes back with no findings at all, click **Review Again**; an empty first pass happens.

7. Click **Review Again** once. Agent Review varies run to run as well; note whether the second pass finds more.

<details open>
<summary>What you should see</summary>

A short list of findings, each citing a file and line, some of them naming `de-standards.mdc` or a BUGBOT.md rule as the reason. At Quick depth it often finds two to four of the nine planted pr/001 defects, plus a real issue nobody planted. That is not a failure; it is the data point for Task 3.4.
</details>

---

### Task 3.4: Compare, then keep your agent

1. Fill in this table from the Agent Review output and your finished agent's pr/001 output:

| | Your subagent | Agent Review |
|---|---|---|
| Planted pr/001 defects found, out of 9 | | |
| False positives | | |
| Most actionable finding | | |
| Time to produce output | | |
| Runs on someone else's machine after a clone | | |

2. **Before you continue, note:**

   > When would you use Agent Review instead of your subagent in your daily work, and when the subagent instead?

<details open>
<summary>Typical answer pattern</summary>

Agent Review is one click and needs no setup; use it for a quick sanity check before pushing. Your subagent produces more structured output with severity ratings, confidence levels and DE-specific criteria, and it is a file in the repository: a teammate who clones the repo has your reviewer, at your standard, without being told. Use it before raising a PR, or in an asynchronous review where the output must be actionable by someone who was not present.

Neither replaces the other. The professional workflow is: Agent Review before pushing, your agent before raising the PR.
</details>

3. Leave the `pr/` branches as you found them. If you changed a tracked file on one, put it back:

   ```bash
   git checkout -- .
   ```

4. Commit your agent on your own branch, where it belongs:

   ```bash
   git checkout lab3
   git add .cursor/agents/
   git commit -m "Add DE pipeline reviewer subagent"
   git log --no-pager --oneline -2
   ```

   That is the deliverable of this lab: not a review, but a reviewer, versioned with the code it reviews.

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

Which of the three rules you added made the biggest difference, and how did you know? Name one rule you wrote that you would put in your own team's repository on Monday.

---

**Question 2**

Did the rule you added on pr/001 still fire on pr/002 and pr/003? A rule that only ever catches the defect you wrote it for is over-fitted to one diff. Which of yours generalised, and which did not?

---

**Question 3**

In Task 1.3 you turned Read-only on rather than writing "do not modify any files" in the instructions. Name one thing that protects you from that the instruction does not. Why is "escalate when unsure" not the same as "escalate when dangerous"?

---

**Question 4**

Write one new rule for `.cursor/BUGBOT.md` based on an issue your agent found in pr/003 that the current file does not cover. Would you rather put that rule in BUGBOT.md or in your agent file, and why?
