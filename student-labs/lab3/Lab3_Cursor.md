# Lab 3: Build a DE Pipeline Code Review Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro or Teams plan)
**Duration:** 75 minutes
**Day:** Day 2, following Module 4

---

## Prerequisites

- [ ] Modules 3 and 4 lectures completed
- [ ] Chapter 3 scoping exercise completed (or scope specification template at end of this document reviewed)
- [ ] Lab 2 completed, or Lab 3 starter files loaded (see Step 0)
- [ ] The repository's `lab-workspace` folder open in the Cursor IDE, with the venv active in the terminal
- [ ] Git working in the repository; the `pr/001`, `pr/002`, `pr/003` branches present (`git branch -a` lists them under `origin/`)

---

## Lab Overview

Your team reviews dozens of Python pipeline PRs each week. Manual review is inconsistent and depends on who is available. Build a Cursor agent that reviews pipeline code against DE-specific criteria, flags issues with severity ratings, and produces a structured review summary ready for human sign-off. Then configure `.cursor/BUGBOT.md` and compare Agent Review output with your custom agent.

**What you will produce:**
- A working code review agent instruction set with all five scope components
- A quality rubric score across two iteration cycles
- `.cursor/BUGBOT.md` configured with DE review rules
- A written comparison of your custom agent versus Agent Review on the same PR

---

## Step 0: Load Starter Files

Run this before anything else, whether or not you completed Lab 2. It resets the workspace to the Lab 3 starting point and moves you onto the first review branch.

Open a terminal inside Cursor (menu **Terminal → New Terminal**; make sure the prompt starts with `(venv)`) and run from `lab-workspace/` (the folder open in the editor; a new terminal starts there). If you are still on `convert-ingest` from Lab 2, commit anything outstanding first (`git add -A && git commit -m "checkpoint"`).

```bash
git checkout main
python lab.py start 3
python lab.py status
git add -A && git commit -m "Lab 3 start state"
git checkout pr/001
git diff --stat main
pytest tests/ -q
```

<details>
<summary>Expected output</summary>

`lab.py status` shows `lab3 … <- matches`. After `git checkout pr/001`, the diff stat lists three files under `src/` (`ingest.py`, `transform.py`, `validate.py`) with about fifteen added lines; those are the changes you will review. All tests pass (the planted issues are review issues, not test failures).

If `git checkout pr/001` says "would be overwritten by checkout", the commit step above was skipped; commit and retry. If the diff lists many more files, you are not on `pr/001`.

`src/ingest.py` on this branch is the complete idiomatic conversion of `perl/ingest.pl` plus the PR's additions. It is the baseline the three sample PRs are built on.
</details>

---

## Part 1: Review Your Scope Specification and Build the Agent

### Step 1.1: Review your scope specification

Open your Chapter 3 scope specification document.

Confirm it covers all five components. If any are missing, add them now using these definitions:

| Component | Definition |
|---|---|
| **Tools** | `@Branch (Diff with Main)` for context. Read-only access only; the agent must not edit any files. |
| **Instructions** | Review against `.cursor/rules/de-standards.mdc` plus five DE criteria: schema drift handling, null safety, idempotency, logging completeness, type hint coverage. |
| **Success criteria** | Every finding has a severity (Critical, Warning, Informational), a file and line number, and a recommendation specific enough to act on in one step. |
| **Failure handling** | If the PR diff is too large to review in one pass, the agent reports what it reviewed and flags the remainder as Needs human review. |
| **Escalation path** | Any credential, secret, or key literal in source is escalated regardless of confidence and reported separately. Any finding where agent confidence is Low is also escalated. |

<details>
<summary>Scope specification template (use if you did not complete the Chapter 3 exercise)</summary>

```
Tools: @Branch (Diff with Main) for context. Read-only file access.
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

---

### Step 1.2: Build the Version 1 instruction set

Open a new Agent mode conversation.

You will send one message: the branch diff as an attachment, then your instruction set. This is your Version 1; you will improve it in Parts 2 and 3.

First, type `@` and select **Branch (Diff with Main)** from the menu. It becomes a tag at the top of the message.

> **Do not put `@Branch` inside pasted text.** Cursor converts an `@` mention as you paste and drops the rest of the text. Attach the diff from the `@` menu first, then paste.

After the tag, paste this and press Enter:

```
You are a DE pipeline code review agent. Context: the attached branch diff. Review only changed lines. Do NOT modify any files. Review the changes against .cursor/rules/de-standards.mdc and: 1. Schema drift handling: does the change validate incoming schema? 2. Null safety: are None values handled on all critical fields? 3. Idempotency: can this step run twice without duplicate records? 4. Logging completeness: are pipeline entry, exit, and errors logged? 5. Type hint coverage: do all functions have complete type hints? For each finding output: criterion violated; file and line number; severity: Critical / Warning / Informational; confidence: High / Medium / Low; specific recommendation. If confidence is Low, mark the finding ESCALATE. End with: overall recommendation APPROVE / REQUEST CHANGES / ESCALATE. Review the changes on this branch.
```

---

### Step 1.3: Read the review

You are already on `pr/001` from Step 0, so the diff the agent reviewed is PR 001.

Read every finding before moving to Part 2. Expect somewhere between eight and fifteen findings. Some will be issues your instructor planted; some will be real issues nobody planted. Both are legitimate.

<details>
<summary>If the agent says it has no diff to review</summary>

The `@Branch` tag was not attached (a pasted "@Branch" in the text does nothing). Type `@`, choose **Branch (Diff with Main)**, and send `Review the changes on this branch.` If the diff is empty, confirm `git branch --show-current` prints `pr/001`.
</details>

---

## Part 2: First Run and Quality Rubric Score

### Step 2.1: Score the output against the rubric

Score each dimension from 1 (poor) to 5 (excellent). Use the known-issues list your instructor provides to check for false negatives.

| Dimension | Score (1--5) | Notes |
|---|---|---|
| **Coverage**—did the agent find all issues in pr_001? | | |
| **Accuracy**—of issues flagged, how many are real? | | |
| **Clarity**—can you read the summary and know exactly what to do next? | | |
| **Consistency**—run the agent on pr_001 a second time. How similar are the two outputs? | | |
| **Total** | **/20** | |

<details>
<summary>Scoring guidance for each dimension</summary>

**Coverage (finding false negatives):** Your instructor has a list of known issues in pr_001. Compare the agent's findings against the list. Each missed issue costs one point. Score 5 only if the agent found every known issue.

**Accuracy (finding false positives):** Count how many agent findings describe issues that do not actually exist in the code. Each false positive costs one point. Score 5 only if every finding is real. A false positive describes something that is not in the code. A real issue that is not on the instructor's list is **not** a false positive; note it and move on.

**Clarity (actionability):** Read each recommendation. Could you act on it immediately without asking a follow-up question? A finding that says "consider improving null handling" is not actionable. A finding that says "add an explicit None check on `instrument_id` at line 47 before passing it to `transform_record()`" is. Score 5 only if every recommendation is immediately actionable.

**Consistency (determinism):** Open a **fresh** conversation and send the identical message (tag plus instruction set). In the same conversation the agent sees its first answer and repeats it, which inflates the score. Compare the two outputs. Score 5 if the findings are identical. Score 1 if the severity ratings or the finding list differs significantly between runs.

**Production threshold:** 16 out of 20 with no dimension below 3. First-run scores vary widely by model; Consistency is usually the lowest dimension. Budget time for scoring: a first run typically returns eight to twelve findings.
</details>

**Identify the single lowest-scoring dimension.** That is your improvement target for Part 3.

---

## Part 3: First Iteration Cycle

### Step 3.1: Note the current instruction set state

Before changing anything, find the message containing your instruction set in the chat timeline and keep a copy of it (a scratch file is fine). You will send the whole updated instruction set as a new message each time, so you can always go back to an earlier version by sending it again. Some builds show a checkpoint control when you hover a message; if yours does, that is a shortcut, not a requirement.

---

### Step 3.2: Make one targeted change

Based on your lowest-scoring dimension, make exactly one specific change to the instruction set. Do not change more than one thing.

<details>
<summary>Targeted change examples by dimension</summary>

**Coverage low:** Add a more specific instruction for the issue type being missed.

```
For null safety: check every .get() call without a default value, every function that accepts Optional parameters without explicit None handling on critical pipeline fields, and every changed except clause: narrowing the exception types caught (for example dropping TypeError) is a null-safety regression.
```

**Accuracy low:** Add a constraint against hallucinated findings.

```
Only flag an issue if you can identify the exact file and line number where it occurs. Do not flag general concerns or patterns you cannot locate in the diff.
```

**Clarity low:** Tighten the output format.

```
Each recommendation must be a single actionable sentence starting with a verb. Example: Add an explicit None check on instrument_id at line 47 before passing it to transform_record().
```

**Consistency low:** Add an explicit output template with required field names.

```
For every finding, output exactly these fields in this order: CRITERION · LOCATION (file:line) · SEVERITY (Critical / Warning / Informational) · CONFIDENCE (High / Medium / Low) · RECOMMENDATION (single actionable sentence starting with a verb). Report each distinct issue once. After the findings, end with: overall recommendation APPROVE / REQUEST CHANGES / ESCALATE.
```

Do **not** add "only report the five criteria": the `de-standards.mdc` rules are also in scope, and you will lose findings (a for-append loop, for instance, is a standards finding, not one of the five).
</details>

Send the **whole** updated instruction set as a new message in the same conversation: type `@`, choose **Branch (Diff with Main)**, then paste the full text ending with `Review the changes on this branch using the updated instructions.`

---

### Step 3.3: Re-score

Score all four dimensions again. Record the new total.

| Result | Action |
|---|---|
| Target dimension improved | Keep the change. Record new total score. |
| Target dimension unchanged or worse | Go back to the Step 3.1 version. Try a different approach to the same dimension. |
| Another dimension dropped significantly | Go back and try a narrower change. Adding an output template *and* a scope restriction in one step is the classic way to fix Consistency and lose Coverage. |

---

## Part 4: Second Iteration Cycle and Generalization Test

### Step 4.1: Second iteration

Identify the new lowest-scoring dimension from your Part 3 score. Make one more targeted change using the same approach as Part 3.

If you have already reached 16 out of 20 with no dimension below 3, move directly to Step 4.2. Do not force an additional change.

---

### Step 4.2: Generalization test on PR 002

Switch to the `pr/002` branch:

```powershell
git checkout pr/002
```

**macOS/Linux:**
```bash
git checkout pr/002
```

Send one message: type `@`, choose **Branch (Diff with Main)**, paste your current instruction set, and end with `Review the changes on this branch.`

Score the pr_002 output on all four dimensions. Compare to your pr_001 score. One planted issue in PR 002 needs reasoning across files (an append-mode write with no de-duplication); another is a narrowed `except` clause. Check whether your agent caught both.

> **If pr_002 scores significantly lower than pr_001:** your instruction changes are over-fitted to pr_001's specific issues. Identify which change caused the over-fitting and broaden or remove it.

---

### Step 4.3: Hard PR test on PR 003

Switch to the `pr/003` branch:

```powershell
git checkout pr/003
```

**macOS/Linux:**
```bash
git checkout pr/003
```

Same one-message shape: tag, instruction set, `Review the changes on this branch.`

PR 003 contains a hard-coded credential. Verify:

- [ ] The credential finding is marked ESCALATE
- [ ] It is reported in a separate ESCALATED section, not in the main list
- [ ] The overall recommendation is ESCALATE, not REQUEST CHANGES or APPROVE

> **If the credential finding appears in the main list with a Critical or Warning severity, or the overall recommendation is not ESCALATE:** your escalation path is confidence-based rather than risk-based. The agent is *sure* the key is a bug, so "escalate when confidence is Low" never fires. Add this sentence to your instruction set and re-run:
>
> ```
> Any credential, secret, token, or API key literal in source code is a security finding: mark it ESCALATE regardless of confidence, report it in a separate ESCALATED section before the other findings, and set the overall recommendation to ESCALATE.
> ```
>
> Escalate-when-unsure is not the same as escalate-when-dangerous. Ship the version that has both.

---

## Part 5: .cursor/BUGBOT.md and Agent Review

### Step 5.1: Understand what you are configuring

Two distinct systems are used in this part. Keep them separate:

| System | What it is | What it reads |
|---|---|---|
| **Bugbot** | PR automation on GitHub, configured under Automations in the Agents Window; needs the repo linked in the Cursor dashboard | `.cursor/BUGBOT.md` (whether it also reads rules is unverified) |
| **Agent Review** | Local in-editor review from the Source Control panel, no GitHub connection needed | `.cursor/rules/*.mdc` **and** `.cursor/BUGBOT.md` |
| **Your in-editor agent** | Chat, Plan, Debug | `.cursor/rules/*.mdc` and `.cursor/BUGBOT.md` |

> Agent Review does read your rules files: on the current build its findings cite `de-standards.mdc` by name. `BUGBOT.md` is the rubric that is *shared* with Bugbot in the cloud, so anything you want enforced on GitHub PRs belongs there too. One sentence to remember: same rubric file, two readers, one in your editor, one on GitHub.

---

### Step 5.2: Read .cursor/BUGBOT.md

The file ships with the repository. In the Explorer, open `.cursor/BUGBOT.md`.

> **The path is `.cursor/BUGBOT.md`**, not `BUGBOT.md` at the project root, and not `.cursor/rules/BUGBOT.md`. A file at the wrong path is silently ignored.

Read the Security, Critical, Warning and Informational sections and compare them with your custom agent's five criteria. Note what the file has that your instruction set does not (the exception-narrowing rule, the append-mode rule) and what it lacks.

<details>
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

If you edit the file, commit it on the branch you are on so the review in Step 5.3 sees your version.

---

### Step 5.3: Run Agent Review

Open Cursor Settings (click the gear icon at the top right of the window) and choose **Git & PRs** in the left list. Scroll to the **Agent Review** section. Confirm **Default Approach** is set to **Quick**. Leave **Start Agent Review on Commit** switched off; you will run the review manually.

Switch back to the `pr/001` branch:

```powershell
git checkout pr/001
```

**macOS/Linux:**
```bash
git checkout pr/001
```

Open the **Source Control** tab in the left sidebar (third icon). Find the **Agent Review** section below Changes and click **Find Issues**. It reviews the diff against `main`, so make sure you are on `pr/001`. The button reads "Reviewing" with a progress ring for about a minute.

The findings appear in the same panel, with **Review Again**, **Fix All Issues**, and a per-finding **Fix**. Clicking a finding opens a diff view with an explanation card, **Fix with Agent**, and **Dismiss**. Do not click any Fix; you are comparing, not fixing.

Run **Review Again** once. Agent Review varies run to run as well; note whether the second pass finds more.

---

### Step 5.4: Compare Agent Review to your custom agent

Fill in this comparison table using the Agent Review output and your best custom agent output from Part 4:

| | Your custom agent | Agent Review |
|---|---|---|
| Known pr_001 issues found | /3 (a tuned custom agent typically finds all three) | /3 (Agent Review at Quick depth often finds 0 to 2, plus a real issue nobody planted) |
| False positives | | |
| Most actionable finding | | |
| Time to produce output | | |

**Write one sentence:**

> When would you use Agent Review instead of your custom agent in your daily work, and when would you use the custom agent instead?

<details>
<summary>Typical answer pattern</summary>

Agent Review is one click and requires no setup; use it for a quick sanity check before pushing. Your custom agent produces more structured output with severity ratings, confidence levels, and DE-specific criteria -- use it before raising a PR or during an asynchronous review process where the output needs to be actionable by someone who was not present during the review.

Neither replaces the other. The professional workflow is: Agent Review before pushing, custom agent before raising the PR.
</details>

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

What was your baseline score and your final score after two iteration cycles? What single change made the biggest difference?

---

**Question 2**

In Step 4.2, did your agent score similarly on pr_002 as on pr_001? If the score dropped, what caused the over-fitting?

---

**Question 3**

After Part 5, when would you use your custom agent versus Agent Review for day-to-day code review on your team? Why is "escalate when unsure" not the same as "escalate when dangerous"?

---

**Question 4**

Write one new rule for `.cursor/BUGBOT.md` based on an issue your agent found in pr_003 that your current BUGBOT.md does not cover.
