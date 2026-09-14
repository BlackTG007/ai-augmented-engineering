# Lab 2: Perl to Python Pipeline Conversion
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro or Teams plan)
**Duration:** 90 minutes
**Day:** Day 1, following Module 2

---

## Prerequisites

- [ ] Module 2 lecture completed
- [ ] Lab 1 completed, or the Lab 2 starter files loaded (Task 0 does this either way)
- [ ] The repository's `lab-workspace` folder open in the Cursor IDE (README Quick Start completed: venv, install, tests pass)
- [ ] pytest accessible from the terminal (`pytest --version` returns a version). Every new terminal needs `source venv/bin/activate` (Windows: `venv\Scripts\activate`) first
- [ ] Git working in the repository (`git status` returns output without an error)

---

## Lab Overview

Your team is converting three Perl pipeline modules to Python. Using the four-step conversion framework from Module 2, you will analyze the pipeline in Ask mode, generate a Plan mode conversion brief, write the tests first, convert the highest-priority module to idiomatic Python, use Debug mode to locate and fix a known parity difference, and prepare the branch for peer review.

**What you will produce:**
- `docs/pipeline-map.md`: a plain-language architectural map of the Perl pipeline
- `docs/conversion-plan.md`: a Plan mode conversion brief
- `tests/test_ingest.py`: a committed TDD test suite
- `src/ingest.py`: an idiomatic Python conversion with all tests passing
- A parity-confirmed diff against the Perl reference output
- A self-reviewed branch with a clean commit history

**How this lab is written:** each Task has numbered steps. A numbered step is something you do. Text between steps explains what you are looking at; the boxes marked "What you should see" tell you what a correct result looks like.

---

## Task 0: Load the starter files

Do this whether or not you completed Lab 1. It resets the workspace to the starting point of this lab and removes the finished `src/ingest.py`, so that the tests-first sequence in Task 3 can happen.

1. Open a terminal inside Cursor: menu **Terminal → New Terminal**. It opens in `lab-workspace/`, the folder open in the editor; every command in this lab runs from there.

2. Make sure the prompt starts with `(venv)`. If it does not, run `source venv/bin/activate` (Windows: `venv\Scripts\activate`).

3. Put away any unfinished Lab 1 work. Run `git status --short`; if it prints anything, commit on the branch you are on:

   ```bash
   git add -A
   git commit -m "Lab 1 checkpoint"
   ```

4. Go back to `main`, which is still exactly what you cloned:

   ```bash
   git checkout main
   ```

5. Load the Lab 2 starter files:

   ```bash
   python lab.py start 2
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
  lab2       12/12 files identical, 0 extra lab file(s) present  <- matches
  lab3       ...
  lab4       ...
  solution   ...
git: uncommitted changes present
```

Only the **lab2** line matters: `12/12 files identical` and `<- matches`. The other lines describe other labs' starting points and will show missing or extra files. `git: uncommitted changes present` is normal at this point; step 10 clears it.
</details>

7. Check what is in the workspace:

   ```bash
   ls .cursor/rules/ .cursor/skills/ src/
   ```

<details open>
<summary>What you should see</summary>

```
.cursor/rules/:
de-standards.mdc    perl-to-python.mdc

.cursor/skills/:
pipeline-review     rework-commits

src/:
__init__.py    figi_client.py    transform.py    validate.py
```

`src/` must **not** contain `ingest.py`; you write that in this lab. `figi_client.py` is provided and is the client your conversion will reuse. If `ingest.py` is there, repeat step 5.
</details>

8. Open `.cursor/rules/de-standards.mdc` in the Explorer. It contains the six standards from Lab 1 (the loader supplies a finished copy, so this lab does not depend on how Lab 1 went).

9. Create the branch this lab works on:

   ```bash
   git checkout -b convert-ingest
   git branch --show-current
   ```

   The second command prints `convert-ingest`. Every commit you make from here goes on this branch, and `main` stays untouched; Task 6 compares the two.

10. Commit the starting state:

    ```bash
    git add -A
    git commit -m "Lab 2 start state"
    ```

    The loader deleted files that the repository's history still contains (the finished `src/ingest.py` among them). Committing makes those removals part of your branch, so the agent sees a clean tree rather than "deleted files" it might helpfully restore.

---

## Task 1: Codebase analysis in Ask mode

### Task 1.1: Start a read-only conversation

1. Click **+** in the chat panel for a new conversation. It starts in Agent mode.

2. Switch it to **Ask**: click the **∞** icon at the bottom left of the chat input and choose **Ask**, or type `/ask`. Confirm the picker shows Ask before sending anything.

   Ask mode is read-only. Nothing you do in this Task modifies a file. If you see files changing, you are in Agent mode; switch back before continuing.

---

### Task 1.2: Map the pipeline

1. Send this prompt:

   ```
   Read the three Perl scripts in perl/.
   For each script tell me: what it does in plain English, what its inputs and outputs are,
   what external libraries or system calls it makes, and which other scripts depend on it.
   ```

2. Read the full response before continuing. Click the **Explored N files** line above the answer to confirm it read all three `.pl` files.

<details open>
<summary>What you should see</summary>

A description of three modules, and no change summary (nothing was written):

- `ingest.pl`: reads raw input records, handles rate limiting, maps identifiers via the OpenFIGI API
- `transform.pl`: applies data transformations to the ingested records
- `validate.pl`: checks output data against the registered schema

`ingest.pl` is your conversion target for this lab. It is the most self-contained module, with the clearest input/output signature and the richest set of Perl idioms to convert.
</details>

---

### Task 1.3: Generate and save the pipeline map

1. In the same conversation, still in Ask mode, send:

   ```
   Generate a plain-language Markdown document describing the data flow
   through all three Perl modules from raw input to final output.
   Include the data transformations at each stage.
   ```

2. Read the document.

3. Switch the same conversation to **Agent** (∞ dropdown, or type `/agent`) and send:

   ```
   Save that document to docs/pipeline-map.md
   ```

4. Look at the change summary at the bottom of the chat. It lists one file, `docs/pipeline-map.md`. Click **Keep**.

5. Confirm `docs/pipeline-map.md` appears in the Explorer. This document is the specification for Tasks 2 and 3.

---

## Task 2: Plan mode conversion brief

### Task 2.1: Switch to Plan mode

1. In the same conversation, open the mode picker (∞) and choose **Plan**, or type `/plan`.

<details open>
<summary>What Plan mode does before writing any code</summary>

When you send a task to Plan mode, the agent researches the codebase and the attached files, asks you clarifying questions about requirements it cannot determine from the code, produces a structured, editable implementation plan, and waits for you to approve it.

Plan mode ends with two buttons, **View Plan** and **Build**. View Plan opens the plan in the editor; Build hands it to the agent as instructions. No code is written until you click Build. Plan mode will write documents when asked (you use that in Task 2.3); it does not write code.
</details>

---

### Task 2.2: Generate the conversion plan

1. Attach the Perl file: type `@` in the chat input, choose **Files & Folders**, and pick `perl/ingest.pl` so it becomes a tag in the message.

2. After the tag, type this prompt and send it:

   ```
   Convert ingest.pl to idiomatic Python.
   It must be testable with pytest and write to src/ingest.py.
   Ask me any clarifying questions before producing the plan.
   ```

   Notice what you did **not** have to type: pathlib, Counter, type hints, no line-by-line translation. Those are rules now (`de-standards.mdc` always applies; `perl-to-python.mdc` applies because a `.pl` file is attached). You check the plan for them in step 4.

3. Answer the **Questions** dialog. Plan mode asks one question at a time, with lettered options and Skip / Continue. The questions vary from run to run, but they cluster on the real ambiguities in `ingest.pl`:

   - Rows with no `instrument_id`: keep them in the output with `figi=UNKNOWN`, as the Perl does.
   - Exchanges with tied counts: choose idiomatic Python for now, even though it will differ from the Perl reference. That difference is Task 5.
   - Tests you have not written yet: say you will write them first and the implementation must match them.

   Answer in the spirit of "match the Perl's behaviour, in idiomatic Python".

4. When the plan appears, click **View Plan** and read every step before doing anything else.

<details open>
<summary>What you should see</summary>

A plan whose steps cover: analysing the Perl module's data flow and dependencies; defining the Python function signatures with type hints; replacing each Perl-specific pattern with its idiomatic Python equivalent; adding entry and exit logging to each function; writing the module to `src/ingest.py`; verifying it imports and runs.

A good plan names the rules it is following (type hints, `pathlib.Path`, `Counter`, the exact entry/exit log format), reuses `src/figi_client.py`, and says the tests will mock the FIGI client.

If any step says "translate X directly" or "port X as-is", that step will produce Perl expressed in Python syntax. Step 5 fixes it.
</details>

5. Edit any step you disagree with, directly in the plan document. Change "translate" steps to describe the idiomatic Python equivalent.

6. **Before you continue, note:**

   > Which of the six standards from Lab 1 appear in the plan without being in your prompt?

> ## STOP. Do not click Build.
> Task 3 writes and commits the tests first. Task 4 returns to this conversation to build. Clicking Build now writes the implementation before the tests exist and breaks the tests-first sequence. Leave this conversation open.

---

### Task 2.3: Save the plan to the workspace

1. Still in the Plan conversation, send:

   ```
   Save this plan to docs/conversion-plan.md
   ```

2. Confirm `docs/conversion-plan.md` appears in the Explorer. Plan mode writes the file itself. This becomes team documentation: the next engineer converting a similar Perl module has a starting point.

   If the agent started writing code instead of a document, you are in Agent mode, not Plan mode. Click **Undo** then **Confirm** in the change summary, check the mode picker, and repeat from Task 2.1.

---

## Task 3: Write the tests before converting

Your Plan conversation is still open with its Build button. Leave it alone until Task 4.

### Task 3.1: Write tests from the pipeline map

1. Click **+** for a new conversation. It starts in Agent mode; leave it there.

2. Send this prompt:

   ```
   Write pytest tests for the Python equivalent of perl/ingest.pl.
   Base the tests on the pipeline map in docs/pipeline-map.md.
   Use the sample input files in data/ as test fixtures.
   Cover the happy path with valid input, at least one edge case, and the null/empty input case.
   Do NOT write the implementation. Write only tests.
   All tests must fail when run against an empty implementation.
   ```

3. Wait for it to finish. The agent will probably run pytest itself and fix its own test bugs; that is fine.

4. Check the change summary at the bottom of the chat. The only file listed must be `tests/test_ingest.py`. If `src/ingest.py` is also listed, click **Undo** next to that file and send `Tests only. Do not create src/ingest.py.`

5. Open `tests/test_ingest.py` and read the tests. Each one should test an input and output described in `docs/pipeline-map.md`. Edit any test that does not match the documented behaviour.

   Do not write any implementation code in this Task. If you find yourself in `src/ingest.py`, stop and return to the test file.

---

### Task 3.2: Confirm the tests fail

1. Run the tests:

   ```bash
   pytest tests/test_ingest.py -v
   ```

<details open>
<summary>What you should see</summary>

Every test fails with `ModuleNotFoundError` or `ImportError`, because `src/ingest.py` does not exist yet. The test names are whatever the agent chose; the failure is what matters:

```
FAILED tests/test_ingest.py::test_load_records_happy_path - ModuleNotFoundError: No module named 'src.ingest'
FAILED tests/test_ingest.py::test_empty_input_returns_no_rows - ModuleNotFoundError: ...
FAILED tests/test_ingest.py::test_missing_instrument_id_gets_unknown_figi - ModuleNotFoundError: ...
```

If any test **passes** against a missing implementation, it is not testing the right behaviour. Ask the agent to fix that test so it fails, then run again.
</details>

---

### Task 3.3: Commit the tests

1. Commit the test file:

   ```bash
   git add tests/test_ingest.py
   git commit -m "Add TDD tests for ingest module conversion"
   ```

   (Or in the **Source Control** panel, third icon in the left bar: **+** next to `tests/test_ingest.py`, type the message, click **Commit**.)

   This commit locks the contract. From here on, every instruction to the agent includes **do not modify the test file**. Without the commit, the agent can take the easy path of changing the tests to make them pass. The commit timestamp is your proof that the tests existed before the implementation.

---

## Task 4: Apply the four-step conversion framework

Step 1 of the framework, Document, is done: `docs/pipeline-map.md` from Task 1 is its output. This Task covers steps 2 and 3, Build and Refactor; Task 5 covers step 4, Validate.

### Task 4.1: Build from the plan

1. Return to your Plan conversation: open the Agents sidebar (the list icon at the top of the chat panel) and click the conversation that produced the plan.

2. Click **Build**. The plan becomes the agent's instructions.

3. As soon as the agent is running, send this as a follow-up message:

   ```
   Do not modify tests/test_ingest.py.
   ```

<details open>
<summary>If the Plan conversation is gone</summary>

Click **+** for a new conversation (Agent mode). Type `@` and attach `perl/ingest.pl` and `docs/conversion-plan.md` (Files & Folders), then send:

```
Refactor ingest.pl into idiomatic Python following conversion-plan.md.
Write the output to src/ingest.py.
Do not modify tests/test_ingest.py.
```

The rules files supply everything else.
</details>

4. When the agent finishes, open `src/ingest.py` from the Explorer and read it. It should read like Python, not Perl expressed in Python syntax.

<details open>
<summary>What you should see</summary>

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

If your `src/ingest.py` looks like the second example, send `Refactor this for idiomatic Python; follow the project rules.` before continuing.
</details>

---

### Task 4.2: Refactor idioms

1. In the same conversation, send:

   ```
   Review the Python you just wrote in src/ingest.py.
   For each of the following, confirm it is correct or fix it:
   1. Any for loop that could be a list comprehension.
   2. Any dict counting pattern that should be collections.Counter.
   3. Any string path that should be pathlib.Path.
   4. Any missing or incomplete type hint.
   5. Any function without entry and exit logging.
   ```

2. Click **Review** in the change summary and read the diff. Every change should correspond to one of the five criteria. If the agent made other changes, ask it to explain each one before you go on.

3. Click **Keep**.

---

### Task 4.3: Run the tests and check parity

1. Run the tests:

   ```bash
   pytest tests/test_ingest.py -v
   ```

2. For each failing test, read the error message before asking the agent for anything. Then paste the test output into the conversation and send it with `Fix only the failing tests. Do not modify tests/test_ingest.py.` Run the tests again after each fix, until all pass.

3. Run the parity check:

   ```bash
   python -m src.ingest data/sample_input.csv > data/python_output.csv
   diff data/python_output.csv data/perl_output_reference.csv
   ```

<details open>
<summary>What you should see</summary>

`data/perl_output_reference.csv` was generated by running the original Perl script against `sample_input.csv`; you do not need Perl installed. The pipeline answers FIGI lookups from `data/figi_fixture.json` when no API key is set, so the check works offline.

**Empty diff:** parity confirmed. The Python output matches the Perl reference exactly. (Possible, but unlikely at this point.)

**Differences only in the `exchange_rank` column, on rows with equal counts:** the known parity difference. That is what Task 5 is about. Note it and move on; do not fix it here.

**Any other difference** (a `figi` column full of `UNKNOWN`, a missing row): a real bug in the conversion. Paste the diff into the conversation and have the agent fix it now, then repeat steps 1–3.

**Windows:** PowerShell's `>` writes UTF-16, and `diff` is not the same command. Use these two lines instead:

```powershell
python -m src.ingest data\sample_input.csv | Out-File -FilePath data\python_output.csv -Encoding utf8
fc.exe data\python_output.csv data\perl_output_reference.csv
```

`FC: no differences encountered` is the empty diff.
</details>

4. **Before you continue, note:**

   > Which rows differ, and in which column?

---

## Task 5: Debug mode on the parity difference

You know from Task 4 that `exchange_rank` differs from the Perl reference on exchanges with equal counts. This Task is not a discovery; it is the workflow. You write a failing test that states the behaviour you want, then let Debug mode find and fix the cause.

### Task 5.1: Write the failing test first

1. In your Build conversation (Agent mode), send:

   ```
   Write one failing test in tests/test_ingest.py that asserts exchange ranks
   break ties by exchange_code alphabetically after sorting by count descending.
   Do not change src/ingest.py.
   ```

2. Run the tests and confirm the new one is red:

   ```bash
   pytest tests/test_ingest.py -v
   ```

   One new test fails; the rest still pass.

3. Commit it:

   ```bash
   git add tests/test_ingest.py
   git commit -m "Add failing test for deterministic exchange rank tie-break"
   ```

---

### Task 5.2: Switch the same conversation to Debug mode

1. Stay in the same conversation. Open the mode picker (∞) and choose **Debug**, or type `/debug`.

<details open>
<summary>What Debug mode does differently from Agent mode</summary>

Debug mode works from evidence rather than from reading the code. On the current build the flow is: it reads your description and asks how to reproduce the problem (or proposes the commands itself); you click **Proceed** and it runs the reproduction; it proposes a fix and applies it on disk; it asks you to re-run the tests; you click **Mark as Fixed** when they pass; the change summary appears with **Review** / **Keep**.

Do not accept a fix until you can explain why it addresses the root cause. If Debug mode added temporary logging, confirm it is gone before you Keep.
</details>

---

### Task 5.3: Describe the bug

1. Send:

   ```
   The parity diff shows exchange_rank differs from the Perl reference on tied counts,
   and the new tie-break test fails. Investigate and fix.
   ```

2. When Debug mode proposes how to reproduce the problem, click **Proceed**.

<details open>
<summary>If you started Debug mode in a fresh conversation</summary>

Give it the full context instead:

```
Bug: the Python output of src/ingest.py differs from the Perl reference output
in data/perl_output_reference.csv in the exchange_rank column on exchanges with equal counts.
Expected: ties break by exchange_code alphabetically after count descending,
as tests/test_ingest.py asserts.
To reproduce: pytest tests/test_ingest.py -v,
then python -m src.ingest data/sample_input.csv > data/python_output.csv
and diff data/python_output.csv data/perl_output_reference.csv.
```
</details>

---

### Task 5.4: Read the fix before you keep it

1. When Debug mode proposes a fix, read its analysis in full.

2. **Before you continue, note:**

   > In one sentence, what is the root cause? Why did the Python and Perl outputs disagree on tied records?

<details open>
<summary>The root cause</summary>

The Perl ranks exchanges with `reverse sort { $exchange_counts{$a} <=> $exchange_counts{$b} } keys %exchange_counts`. The sort input is the keys of a Perl hash, and Perl randomises hash key order per process, so with five exchanges tied at the same count the Perl rank column was **different on every run**. The legacy code never defined a tie order; the reference file captured one accidental ordering.

Python's `sorted(..., reverse=True)` is stable: ties keep first-seen order. So the two outputs disagree, and no secondary key can "match Perl", because Perl had no rule.

The correct fix **defines** the tie-break: sort by count descending, then `exchange_code` ascending, `sorted(counts, key=lambda e: (-counts[e], e))`. `data/perl_output_reference.csv` was normalised to that same rule, so once the fix is in, the diff is empty. This is the lesson: a conversion is the moment to make undefined behaviour deterministic, not to reproduce an accident.
</details>

3. Check the size of the fix. The correct fix is a **one-line** change to the `sorted` call (a tie-break key) plus a docstring update. If the agent rewrote the function, added special-case logic, or reordered results to reproduce the reference file, click **Undo** then **Confirm** and send `The fix is a tie-break key on the sort. Nothing else.` That is fitting the test, not fixing the bug.

4. Verify:

   ```bash
   pytest tests/test_ingest.py -v
   python -m src.ingest data/sample_input.csv > data/python_output.csv
   diff data/python_output.csv data/perl_output_reference.csv
   ```

   (Windows: the two lines from Task 4.3.) All tests pass and the diff is empty. Do not go on to Task 6 until both are true.

5. Click **Mark as Fixed**, then **Keep** in the change summary.

6. Commit:

   ```bash
   git add -A
   git commit -m "Break equal-count exchange ranks by exchange_code"
   ```

---

## Task 6: Self-review and branch cleanup

### Task 6.1: Review the branch with @Branch

1. Click **+** for a new conversation (Agent mode).

2. Type `@` in the chat input and choose **Branch (Diff with Main)**. It becomes a tag at the top of your message and attaches the full diff of `convert-ingest` against `main`.

   If the diff is empty, confirm you are on `convert-ingest` (`git branch --show-current`) and that you committed in Task 5.4.

3. After the tag, type this prompt and send it:

   ```
   Review all changes on this branch. Look for:
   1. Bugs or logic errors that were not in the original Perl.
   2. Anything that does not match our .cursor/rules/de-standards.mdc standards.
   3. Missing error handling.
   4. Functions without complete type hints.
   5. Any logging that is missing on entry or exit.
   Report findings grouped by severity: Critical, Warning, Informational.
   ```

4. Read the findings. Expect ten to twenty. Fix the Critical and Warning items that are about code you wrote in this lab (send them back to the agent one at a time, with `Do not modify tests/test_ingest.py`), and note the rest for the PR description. Commit any fixes:

   ```bash
   git add -A
   git commit -m "Address self-review findings"
   ```

5. Send a follow-up:

   ```
   What questions will reviewers have about these changes?
   What context should I include in the PR description?
   ```

6. **Before you continue, note:**

   > Two things from that answer that belong in your PR description, and one "known follow-up" for Lab 3.

---

### Task 6.2: Run /rework-commits

1. Make a safety copy of your branch:

   ```bash
   git branch backup-before-rework
   ```

2. Click **+** for a new conversation (Agent mode). Type `/`, choose **rework-commits** from the list so it becomes a tag, and press Enter.

<details open>
<summary>What /rework-commits does</summary>

`/rework-commits` is a skill that ships with the sample repository at `.cursor/skills/rework-commits/SKILL.md`. It is not a built-in Cursor command.

The skill instructs the agent to soft-reset to `main` (changes preserved), read all changes across the modified files, plan a logical sequence of small, semantic commits, create each commit with a message explaining the why, and verify the final diff matches your original branch exactly.

The skill only restructures commits. It does not modify code. It runs `git reset` and `git commit` without asking; that is why the backup branch exists.
</details>

3. Read the proposed commit sequence before the agent creates the commits (if it asks). Confirm the sequence covers, at minimum: the test-file commit (earliest, before the implementation), the initial Python conversion, the idiom refactoring, and the Debug mode fix.

4. Run the final verification:

   ```bash
   git log --oneline
   git diff backup-before-rework --stat
   pytest tests/test_ingest.py -v
   python -m src.ingest data/sample_input.csv > data/python_output.csv
   diff data/python_output.csv data/perl_output_reference.csv
   ```

   (Windows: the two lines from Task 4.3 for the last two commands.)

<details open>
<summary>What you should see</summary>

`git log --oneline` shows the reworked commits, tests first. `git diff backup-before-rework --stat` prints **nothing**: the code is unchanged, only the commits are different. All tests pass and the parity diff is empty.

If `git diff backup-before-rework --stat` prints anything, restore and try again:

```bash
git reset --hard backup-before-rework
```

then repeat from step 2.
</details>

Your branch is ready for peer review. Stay on `convert-ingest`; Lab 3's Task 0 moves you where it needs you.

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

In Task 2, Plan mode asked clarifying questions before producing the plan. What did those questions reveal about the conversion that you had not anticipated?

---

**Question 2**

Which of the six standards from Lab 1 appeared in the plan and the conversion without being asked for in the prompt? Which, if any, did not?

---

**Question 3**

In Task 5, what did the failing test and Debug mode show you about the legacy tie order that reading the Perl did not? Describe it in one sentence without using the phrase "the fix was."

---

**Question 4**

After `/rework-commits`, how many commits does your branch have? What does the earliest commit message say, and why does that order matter?
