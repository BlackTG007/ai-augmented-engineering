# Lab 2: Perl to Python Pipeline Conversion
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro or Teams plan)
**Duration:** 90 minutes
**Day:** Day 1, following Module 2

---

## Prerequisites

- [ ] Module 2 lecture completed
- [ ] Lab 1 completed, or Lab 2 starter files loaded (see Step 0)
- [ ] The repository's `lab-workspace` folder open in the Cursor IDE (README Quick Start completed: venv, install, tests pass)
- [ ] pytest accessible from the terminal (`pytest --version` returns a version). Every new terminal needs `source venv/bin/activate` (Windows: `venv\Scripts\activate`) first
- [ ] Git working in the repository (`git status` returns output without an error)

---

## Lab Overview

Your team is converting three Perl pipeline modules to Python. Using the four-step conversion framework from Module 2, you will analyze the pipeline in Ask mode, generate a Plan mode conversion brief, convert the highest-priority module to idiomatic Python, validate with TDD, use Debug mode to locate and fix a known parity difference, and prepare the branch for peer review.

**What you will produce:**
- `docs/pipeline-map.md`: a plain-language architectural map of the Perl pipeline
- `docs/conversion-plan.md`: a Plan mode conversion brief
- `tests/test_ingest.py`: a committed TDD test suite
- `src/ingest.py`: an idiomatic Python conversion with all tests passing
- A parity-confirmed diff against the Perl reference output
- A self-reviewed branch with clean commit history

---

## Step 0: Load Starter Files

Run this before anything else, whether or not you completed Lab 1. It resets the workspace to the starting point of this lab and removes the finished `src/ingest.py` so the TDD sequence in Part 3 can happen.

Open a terminal inside Cursor (menu **Terminal → New Terminal**; make sure the prompt starts with `(venv)`) and run from `lab-workspace/` (the folder open in the editor; a new terminal starts there):

```bash
python lab.py start 2
python lab.py status
git checkout -b convert-ingest
git branch --show-current
```

The status line for `lab2` should end with `<- matches`. If the loader refuses because of uncommitted changes, commit them first (`git add -A && git commit -m "checkpoint"`).

The branch matters: every commit you make in this lab goes on `convert-ingest`, and Part 6 compares it with `main`.

Verify:

```bash
ls .cursor/rules/
ls .cursor/skills/
ls src/
```

<details>
<summary>Expected output</summary>

```
.cursor/rules/
  de-standards.mdc
  perl-to-python.mdc

.cursor/skills/
  pipeline-review/
    SKILL.md
  rework-commits/
    SKILL.md

src/
  __init__.py  figi_client.py  transform.py  validate.py
```

`src/` must **not** contain `ingest.py`; you write that in this lab. `figi_client.py` is provided and is the client your conversion will reuse. If `ingest.py` is there, re-run `python lab.py start 2`.
</details>

---

## Part 1: Codebase Analysis with Ask Mode

### Step 1.1: Switch to Ask mode

Click the **∞** icon at the bottom left of the chat input and select **Ask** (or type `/ask`). The picker shows an icon only; hover it to confirm the mode is Ask before sending any message.

Ask mode is read-only. Nothing you do in this part modifies any file. If you notice files changing, you are in Agent mode; switch back before continuing.

---

### Step 1.2: Map the pipeline

Send the following prompt:

```
Read the three Perl scripts in perl/. For each script tell me: what it does in plain English, what its inputs and outputs are, what external libraries or system calls it makes, and which other scripts depend on it.
```

Read the full response before continuing.

<details>
<summary>What to expect from Ask mode</summary>

Ask mode will search the codebase and return a description of each script without modifying anything. You should see a description of three modules:

- `ingest.pl`: reads raw input records, handles rate limiting, maps identifiers via the OpenFIGI API
- `transform.pl`: applies data transformations to the ingested records
- `validate.pl`: checks output data against the registered schema

`ingest.pl` is your conversion target for this lab. It is the most self-contained module with the clearest input/output signature and the richest set of Perl idioms to convert.
</details>

---

### Step 1.3: Generate the pipeline map

In the same Ask mode conversation, send:

```
Generate a plain-language Markdown document describing the data flow through all three Perl modules from raw input to final output. Include the data transformations at each stage.
```

Read it. Then switch the same conversation to **Agent** (the ∞ dropdown, `Shift+Tab`, or `/agent`) and send:

```
Save that document to docs/pipeline-map.md
```

Click **Keep** in the change summary at the bottom of the chat. Confirm `docs/pipeline-map.md` appears in the Explorer. This document is the specification for Parts 2 and 3.

---

## Part 2: Plan Mode Conversion Brief

### Step 2.1: Switch to Plan mode

Click the mode selector and choose **Plan**.

<details>
<summary>What Plan mode does before writing any code</summary>

When you send a task to Plan mode, the agent:
1. Researches the codebase and the attached files
2. Asks you clarifying questions about requirements it cannot determine from the code
3. Produces a structured, editable implementation plan
4. Waits for you to approve the plan before writing any code

The plan is a reviewable document. Plan mode ends with two buttons, **View Plan** and **Build**; View Plan opens the plan in the editor, Build hands it to the agent as instructions. No code is written until you click Build. Plan mode will write documents when asked (you use that in Step 2.3); it does not write code.
</details>

---

### Step 2.2: Generate the conversion plan

Attach `perl/ingest.pl`: type `@` in the chat input, choose **Files & Folders**, and pick `perl/ingest.pl` so it becomes a tag.

Send the following prompt:

```
Convert ingest.pl to idiomatic Python. It must be testable with pytest and write to src/ingest.py. Ask me any clarifying questions before producing the plan.
```

Notice what you did **not** have to type: pathlib, Counter, type hints, no line-by-line translation. Those are rules now (`de-standards.mdc` always applies; `perl-to-python.mdc` applies because a `.pl` file is attached). Check the plan for them.

Plan mode opens a **Questions** dialog (one question at a time, lettered options, Skip / Continue). The questions vary from run to run, but they cluster on the real ambiguities in `ingest.pl`: how to order exchanges with tied counts, and what to do with rows that have no `instrument_id`. Answer in the spirit of "match the Perl's behaviour, in idiomatic Python": keep rows with a missing `instrument_id` in the output with `figi=UNKNOWN`, as the Perl does; for tied counts, choose idiomatic Python for now, even though it will differ from the Perl reference, because that difference is Part 5. If it asks about tests you have not written yet, say you will write them first and the implementation should match them.

When Plan mode produces the plan, click **View Plan** and **read every step before doing anything else**.

<details>
<summary>What a good conversion plan looks like</summary>

A well-structured plan should include steps covering:

1. Analyzing the Perl module's data flow and dependencies
2. Defining the Python function signatures with type hints
3. Replacing each Perl-specific pattern with its idiomatic Python equivalent
4. Adding logging on entry and exit for each function
5. Writing the module to `src/ingest.py`
6. Verifying the output compiles and passes a basic import test

If any step says "translate X directly" or "port X as-is", edit that step to describe the idiomatic Python equivalent instead. A plan that contains the word "translate" in a conversion step is a plan that will produce Perl expressed in Python syntax.

A good plan also names the rules it is following (type hints, `pathlib.Path`, `Counter`, the exact entry/exit log format), reuses `src/figi_client.py`, and says the tests will mock the FIGI client.
</details>

Edit any step you disagree with.

> ## **STOP. Do NOT click Build.**
> Part 3 writes and commits the tests first. Part 4 returns to this conversation to build. Clicking Build now writes the implementation before the tests exist and breaks the TDD sequence. Leave this conversation open.

---

### Step 2.3: Save the plan to workspace

Stay in the Plan conversation and send:

```
Save this plan to docs/conversion-plan.md
```

Plan mode writes the file itself. Confirm `docs/conversion-plan.md` appears in the Explorer. This becomes team documentation: the next engineer converting a similar Perl module has a starting point.

> **If Agent mode starts writing code immediately without producing a plan:** you are in Agent mode, not Plan mode. Check the mode indicator and switch to Plan mode before retrying.

---

## Part 3: Write TDD Tests Before Converting

> Your Plan conversation is still open with its Build button. Leave it alone until Part 4.

### Step 3.1: Write tests based on the pipeline map

Open a **new** conversation (**+**). It starts in Agent mode.

Send the following prompt:

```
Write pytest tests for the Python equivalent of perl/ingest.pl. Base the tests on the pipeline map in docs/pipeline-map.md. Use the sample input files in data/ as test fixtures. Cover the happy path with valid input, at least one edge case, and the null/empty input case. Do NOT write the implementation. Write only tests. All tests must fail when run against an empty implementation.
```

The agent will probably run pytest itself and fix its own test bugs. That is fine. Check the change summary at the bottom of the chat: the only file listed must be `tests/test_ingest.py`. If `src/ingest.py` appears, click the ✕ next to it (or **Undo**) and tell the agent "tests only".

Read the generated tests carefully. Verify they test the correct inputs and outputs from the pipeline map. Edit any test that does not match the expected behavior documented in `pipeline-map.md`.

> **Do not write any Python implementation code in this step.** Tests only. If you find yourself writing `src/ingest.py`, stop and return to the test file.

---

### Step 3.2: Confirm the tests fail

Run from the terminal:

```powershell
pytest tests\test_ingest.py -v
```

**macOS/Linux:**
```bash
pytest tests/test_ingest.py -v
```

<details>
<summary>Expected output</summary>

Every test should fail with an `ImportError` or `ModuleNotFoundError`, because `src/ingest.py` does not exist yet. The test names are whatever the agent chose; the failure is what matters:

```
FAILED tests/test_ingest.py::test_load_records_happy_path - ModuleNotFoundError: No module named 'src.ingest'
FAILED tests/test_ingest.py::test_empty_input_returns_no_rows - ModuleNotFoundError: ...
FAILED tests/test_ingest.py::test_missing_instrument_id_gets_unknown_figi - ModuleNotFoundError: ...
```

If any test **passes** on an empty implementation, that test is not testing the right behavior. Ask the agent to fix it so it fails correctly before committing.
</details>

---

### Step 3.3: Commit the tests

```powershell
git add tests\test_ingest.py
git commit -m "Add TDD tests for ingest module conversion"
```

**macOS/Linux:**
```bash
git add tests/test_ingest.py
git commit -m "Add TDD tests for ingest module conversion"
```

Or, in the **Source Control** tab (third icon in the left bar): click **+** next to `tests/test_ingest.py`, type the message, click **Commit**.

This commit locks the contract. From this point forward, every agent instruction includes: **do not modify the test file**.

> **The commit is not optional.** Without it, the agent can take the easy path of modifying the tests to make them pass rather than writing correct implementation code. The commit timestamp is your proof that the tests existed before the implementation.

---

## Part 4: Apply the Four-Step Conversion Framework

### Step 4.1: Step 1—Document (already done)

Your `docs/pipeline-map.md` from Part 1 is the Step 1 output. Move directly to Step 2.

---

### Step 4.2: Step 2: Build from the plan

Return to your Plan conversation (Agents sidebar, the conversation titled with your plan) and click **Build**. The plan becomes the agent's instructions. Before it starts, add one line to the message box if it offers one, or send it as the first follow-up:

```
Do not modify tests/test_ingest.py.
```

<details>
<summary>If the Plan conversation is gone</summary>

Open a new Agent mode conversation. Type `@` and attach `perl/ingest.pl` and `docs/conversion-plan.md` (Files & Folders). Send:

```
Refactor ingest.pl into idiomatic Python following conversion-plan.md. Write the output to src/ingest.py. Do not modify tests/test_ingest.py.
```

The rules files supply everything else.
</details>

When the agent completes, open `src/ingest.py`. It should read like Python, not Perl expressed in Python syntax.

<details>
<summary>Signs your conversion is idiomatic vs literal</summary>

**Idiomatic Python (good):**
```python
from collections import Counter
from pathlib import Path
import re

PATTERN = re.compile(r'\b\d{1,3}(?:\.\d{1,3}){3}\b')

def count_ip_addresses(log_files: list[Path]) -> Counter:
    logger.info(f'Starting count_ip_addresses with {len(log_files)} files')
    counts: Counter = Counter()
    for path in log_files:
        counts.update(PATTERN.findall(path.read_text()))
    logger.info(f'Completed count_ip_addresses: {len(counts)} unique IPs')
    return counts
```

**Literal Perl translation (bad):**
```python
def count_ip_addresses(log_files):
    ip_count = {}
    for f in log_files:
        fh = open(f, 'r')
        for line in fh:
            match = re.search(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', line)
            if match:
                ip = match.group(0)
                if ip not in ip_count:
                    ip_count[ip] = 0
                ip_count[ip] += 1
        fh.close()
    return ip_count
```

If your output looks like the second example, stop and ask the agent to refactor for idiomatic Python before continuing.
</details>

---

### Step 4.3: Step 3—Refactor idioms

In the same Agent mode conversation, send:

```
Review the Python you just wrote in src/ingest.py. For each of the following, confirm it is correct or fix it: 1. Any for loop that could be a list comprehension. 2. Any dict counting pattern that should be collections.Counter. 3. Any string path that should be pathlib.Path. 4. Any missing or incomplete type hint. 5. Any function without entry and exit logging.
```

Click **Review** in the change summary and read the diff before accepting. Every change should correspond to one of the five criteria above. If the agent made additional changes, ask it to explain each one before accepting.

---

### Step 4.4: Run the tests and achieve parity

```powershell
pytest tests\test_ingest.py -v
```

**macOS/Linux:**
```bash
pytest tests/test_ingest.py -v
```

For each failing test, read the error message before asking the agent to fix anything. Send the test output to the agent and ask it to fix only the failing tests. Re-run after each fix.

When all tests pass, run the parity check:

```powershell
python -m src.ingest data\sample_input.csv > data\python_output.csv
diff data\python_output.csv data\perl_output_reference.csv
```

> **Windows note:** PowerShell's `>` operator writes UTF-16 by default, which breaks the diff comparison. If the diff produces no output or a binary comparison error, use this instead:
> ```powershell
> python -m src.ingest data\sample_input.csv | Out-File -FilePath data\python_output.csv -Encoding utf8
> ```

**macOS/Linux:**
```bash
python -m src.ingest data/sample_input.csv > data/python_output.csv
diff data/python_output.csv data/perl_output_reference.csv
```

<details>
<summary>What the parity check tells you</summary>

`data/perl_output_reference.csv` is a pre-computed file generated by running the original Perl script against `sample_input.csv`. You do not need Perl installed; the reference output ships with the repository. The pipeline answers FIGI lookups from `data/figi_fixture.json` when no API key is set, so the parity check works offline.

**Empty diff:** parity confirmed. The Python output matches the Perl reference exactly.

**Non-empty diff:** there is at least one difference. If it is only the `exchange_rank` column on rows with equal counts, that is the known parity difference Part 5 works on. Note what it is and move on. Do not fix it here. Any other difference (a `figi` column full of `UNKNOWN`, a missing row) is a real bug in the conversion: fix it now.
</details>

> **If the diff shows a difference in `exchange_rank` on exchanges with equal counts:** that is the difference Part 5 is about. Document it and proceed. Do not fix it now.

---

## Part 5: Debug Mode on the Parity Difference

You know from Part 4 that `exchange_rank` differs from the Perl reference on exchanges with equal counts. This part is not a discovery; it is the workflow. You write a failing test that states the behaviour you want, then let Debug mode find and fix the cause.

### Step 5.0: Write the failing test first

In your Build conversation (Agent mode), send:

```
Write one failing test in tests/test_ingest.py that asserts exchange ranks break ties by exchange_code alphabetically after sorting by count descending. Do not change src/ingest.py.
```

Run it and confirm it is red:

```bash
pytest tests/test_ingest.py -v
```

One new test fails; the rest still pass. Commit it:

```bash
git add tests/test_ingest.py
git commit -m "Add failing test for deterministic exchange rank tie-break"
```

---

### Step 5.1: Switch the same conversation to Debug mode

Stay in the same conversation. Open the mode picker (the ∞ dropdown, `Shift+Tab`, or `/debug`) and choose **Debug**.

<details>
<summary>What Debug mode does differently from Agent mode</summary>

Debug mode works from evidence rather than from reading the code. On the current build the flow is:

1. It reads your description and asks you how to reproduce the problem (or proposes the commands itself)
2. You click **Proceed** and it runs the reproduction
3. It proposes a fix and applies it on disk
4. It asks you to re-run the tests
5. You click **Mark as Fixed** when they pass
6. The change summary appears with **Review** / **Keep**

Do not accept a fix until you can explain why it addresses the root cause. If Debug mode added temporary logging, confirm it is gone before you Keep.
</details>

---

### Step 5.2: Describe the bug to Debug mode

Send:

```
The parity diff shows exchange_rank differs from the Perl reference on tied counts, and the new tie-break test fails. Investigate and fix.
```

Follow Debug mode's reproduction request and click **Proceed**.

<details>
<summary>If you started Debug mode in a fresh conversation</summary>

Give it the full context instead:

```
Bug: the Python output of src/ingest.py differs from the Perl reference output in data/perl_output_reference.csv in the exchange_rank column on exchanges with equal counts. Expected: ties break by exchange_code alphabetically after count descending, as tests/test_ingest.py asserts. To reproduce: pytest tests/test_ingest.py -v, then python -m src.ingest data/sample_input.csv > data/python_output.csv and diff data/python_output.csv data/perl_output_reference.csv.
```
</details>

---

### Step 5.3: Read the fix before you keep it

When Debug mode proposes a fix, read the analysis in full.

**Before accepting the fix, write down:**

> In one sentence, what is the root cause? Why did the Python and Perl outputs disagree on tied records?

<details>
<summary>The root cause explained</summary>

The Perl ranks exchanges with `reverse sort { $exchange_counts{$a} <=> $exchange_counts{$b} } keys %exchange_counts`. The sort input is the keys of a Perl hash, and Perl randomises hash key order per process, so with five exchanges tied at the same count the Perl rank column was **different on every run**. The legacy code never defined a tie order; the reference file captured one accidental ordering.

Python's `sorted(..., reverse=True)` is stable: ties keep first-seen order. So the two outputs disagree, and no secondary key can "match Perl", because Perl had no rule.

The correct fix is to **define** the tie-break: sort by count descending, then `exchange_code` ascending, `sorted(counts, key=lambda e: (-counts[e], e))`. `data/perl_output_reference.csv` was normalised to that same rule, so once the fix is in, the diff is empty. This is the lesson: a conversion is the moment to make undefined behaviour deterministic, not to reproduce an accident.
</details>

> The correct fix is a **one-line** change to the `sorted` call (a tie-break key) plus a docstring update. If the agent rewrites the function, adds special-case logic, or reorders results to reproduce the reference file, click **Undo** and re-prompt: that is fitting the test, not fixing the bug.

Accept the fix only after you can explain it. Verify:

```powershell
pytest tests\test_ingest.py -v
python -m src.ingest data\sample_input.csv > data\python_output.csv
diff data\python_output.csv data\perl_output_reference.csv
```

> **Windows note:** PowerShell's `>` operator writes UTF-16 by default, which breaks the diff comparison. If the diff produces no output or a binary comparison error, use this instead:
> ```powershell
> python -m src.ingest data\sample_input.csv | Out-File -FilePath data\python_output.csv -Encoding utf8
> ```

**macOS/Linux:**
```bash
pytest tests/test_ingest.py -v
python -m src.ingest data/sample_input.csv > data/python_output.csv
diff data/python_output.csv data/perl_output_reference.csv
```

All tests must pass and the diff must be empty before moving to Part 6. Click **Mark as Fixed**, **Keep** the change, and commit:

```bash
git add -A
git commit -m "Break equal-count exchange ranks by exchange_code"
```

---

## Part 6: Self-Review and Branch Cleanup

### Step 6.1: @Branch self-review

Open a new Agent mode conversation.

Type `@` in the chat input and select **Branch (Diff with Main)** from the menu. It becomes a tag at the top of your message and attaches the full diff of your `convert-ingest` branch against `main`. If the diff is empty, confirm you are on `convert-ingest` (`git branch --show-current`) and have committed.

After the tag, type and send:

```
Review all changes on this branch. Look for: 1. Bugs or logic errors that were not in the original Perl. 2. Anything that does not match our .cursor/rules/de-standards.mdc standards. 3. Missing error handling. 4. Functions without complete type hints. 5. Any logging that is missing on entry or exit. Report findings grouped by severity: Critical, Warning, Informational.
```

Expect ten to twenty findings. Fix the Critical and Warning items that are about code you wrote in this lab; note the rest for the PR description.

Then send a follow-up:

```
What questions will reviewers have about these changes? What context should I include in the PR description?
```

Use the response to draft your PR description, and use its "known follow-ups" as your backlog for Lab 3.

---

### Step 6.2: Run /rework-commits

First, make a safety copy of your branch:

```bash
git branch backup-before-rework
```

Open a new Agent mode conversation. Type `/`, choose **rework-commits** from the list so it becomes a tag, and press Enter.

<details>
<summary>What /rework-commits does</summary>

`/rework-commits` is a skill that ships with the sample repository at `.cursor/skills/rework-commits/SKILL.md`. It is not a built-in Cursor command.

When invoked, the skill instructs the agent to:
1. Reset to main (soft reset, changes preserved)
2. Read all changes across modified files
3. Plan a logical sequence of small, semantic commits
4. Create each commit with a descriptive message explaining the why
5. Verify the final diff matches your original branch exactly—no changes lost

The skill only restructures commits. It does not modify code. It runs `git reset` and `git commit` without asking; that is why the backup branch exists.
</details>

Review the proposed commit sequence before the agent creates them. Confirm the sequence covers at minimum:

- [ ] The test file commit (earliest—predates the implementation)
- [ ] The initial Python conversion
- [ ] The idiom refactoring
- [ ] The Debug mode fix

Run final verification:

```powershell
git log --oneline
git diff backup-before-rework --stat
pytest tests\test_ingest.py -v
python -m src.ingest data\sample_input.csv > data\python_output.csv
diff data\python_output.csv data\perl_output_reference.csv
```

> **Windows note:** PowerShell's `>` operator writes UTF-16 by default, which breaks the diff comparison. If the diff produces no output or a binary comparison error, use this instead:
> ```powershell
> python -m src.ingest data\sample_input.csv | Out-File -FilePath data\python_output.csv -Encoding utf8
> ```

**macOS/Linux:**
```bash
git log --oneline
git diff backup-before-rework --stat
pytest tests/test_ingest.py -v
python -m src.ingest data/sample_input.csv > data/python_output.csv
diff data/python_output.csv data/perl_output_reference.csv
```

`git diff backup-before-rework --stat` must print nothing (the code is unchanged, only the commits are different). If it prints anything, `git reset --hard backup-before-rework` and run the skill again. All tests must pass and the parity diff must be empty on the final commit. Your branch is ready for peer review.

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

In Part 2, Plan mode asked clarifying questions before producing the plan. What did those questions reveal about the conversion that you had not anticipated?

---

**Question 2**

Which of the six standards from Lab 1 appeared in the plan and the conversion without being asked for in the prompt? Which, if any, did not?

---

**Question 3**

In Part 5, what did the failing test and Debug mode show you about the legacy tie order that reading the Perl did not? Describe it in one sentence without using the phrase "the fix was."

---

**Question 4**

After `/rework-commits`, how many commits does your branch have? What does the earliest commit message say and why does that order matter?
