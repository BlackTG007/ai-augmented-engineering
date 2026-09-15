# Lab 1: Configure Before You Convert
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** GitHub Copilot in VS Code
**Duration:** 75 minutes
**Day:** Day 1, following Module 1

---

## Prerequisites

- [ ] Module 1 lecture completed
- [ ] VS Code 1.13x or later, signed in to GitHub with a Copilot licence (the Copilot icon in the title bar shows no error). Copilot is built into current VS Code; there is nothing to install
- [ ] Git and Python 3.11+ installed (`git --version`, `python3 --version`). The README **Quick Start** (clone, venv, install, tests) is repeated in Task 0 step 1 if you have not done it
- [ ] Git configured with your name and email (`git config --global user.name` returns a value)
- [ ] pytest accessible from the terminal (`pytest --version` returns a version). Every new terminal needs the venv activated first: `source venv/bin/activate` (Windows: `venv\Scripts\activate`). If the prompt does not start with `(venv)`, pytest will not be found.

---

## A note on coverage

This lab has the same Tasks and the same outcomes as the Cursor version. Where Copilot has a direct equivalent of a Cursor feature, the lab uses it; where the shape differs, the step says so.

| Cursor | Copilot in VS Code (this lab) |
|---|---|
| Modes Agent / Plan / Debug / Multitask / Ask (∞ picker) | Modes **Agent / Ask / Plan** (the **Agent ▾** pill at the bottom left of the chat input). No Debug mode; Lab 2 shows the substitute |
| `.cursor/rules/de-standards.mdc` (`alwaysApply: true`) | `.github/copilot-instructions.md` (always on, plain Markdown, no frontmatter) |
| `.cursor/rules/perl-to-python.mdc` (`globs`) | `.github/instructions/perl-conversion.instructions.md` (`applyTo:` frontmatter) |
| `.cursor/skills/<name>/SKILL.md`, run with `/name` | `.github/skills/<name>/SKILL.md`, run by naming it in the prompt ("Use the pipeline-review skill…"); `/skills` lists them |
| `@` attaches files, `@skill` attaches a skill | **+** (Add Context) at the left of the input → **Files & Folders…** |
| Change summary at the bottom of the chat: Undo / Keep / Review | Change summary just above the input: **Keep** / **Undo**, per-file rows; diff inline in the editor |
| "Explored N files" expander | "Completed N steps" expander with **Read** pills |

**How this lab is written:** each Task has numbered steps. A numbered step is something you do. Text between steps explains what you are looking at; the boxes marked "What you should see" tell you what a correct result looks like. The agent's behaviour varies from run to run: it may ask questions before acting, act at once, or describe a change and wait for your go-ahead. If it asks, answer; if it waits, reply `Go ahead`. The steps describe the end state, not every turn of the conversation.

---

## Lab Overview

Your team is about to start converting a production Perl pipeline to Python. Before anyone touches code, this lab establishes the shared configuration that makes every engineer's agent output consistent and standards-compliant.

Every artifact you build here is used directly in Labs 2, 3, and 4. Do not skip tasks or use different file names from the ones specified.

**What you will build:**
- `.github/copilot-instructions.md`  team DE coding standards applied to every Copilot conversation
- `.github/instructions/perl-conversion.instructions.md`  conversion-specific instructions that activate on Perl and Python files
- `.github/skills/pipeline-review/SKILL.md`  an invocable code review checklist

**What you will observe:**
- The measurable difference in agent output before and after instructions are active
- The behavioural difference between running a skill (named in the prompt) and attaching it as context

---

## Task 0: Get the repository and load the starter files

1. If you have not yet done the README **Quick Start**, do it now; if you have (the repository is cloned, `pytest` passed, and `lab-workspace` is open in VS Code), go to step 2. In a terminal outside VS Code:

   ```bash
   git clone https://github.com/roitraining/ai-augmented-engineering.git
   cd ai-augmented-engineering/lab-workspace
   python3 -m venv venv
   source venv/bin/activate      # Windows PowerShell:  venv\Scripts\activate
   pip install -r requirements.txt
   pytest tests/ -q
   ```

   (Windows: `py -m venv venv` if `python3` is not found.) Expect `42 passed`. Then open VS Code and choose **File → Open Folder** → the `lab-workspace` folder inside `ai-augmented-engineering`.

2. Check which folder is open. The Explorer panel on the left should be headed **LAB-WORKSPACE** with `perl`, `src` and `tests` inside it. If it is headed **AI-AUGMENTED-ENGINEERING** instead, choose **File → Open Folder** and select the `lab-workspace` folder inside the repository. The lab instructions and starter archives live beside `lab-workspace`, outside the folder the agent can see; that is deliberate.

3. Answer the Git notification. When `lab-workspace` opens, a message appears at the bottom right: "A git repository was found in the parent folders of the workspace or the open file(s). Would you like to open the repository?" with **Never** / **Always** / **Yes**. Click **Always**. The repository is one level above the folder you opened; this tells VS Code to use it, so the Source Control panel shows your commits and branches in every lab. Git in the terminal works either way.

4. If VS Code asks whether you trust the authors of the folder, click **Yes, I trust the authors**. In Restricted Mode Copilot cannot read instruction files.

5. Turn on **File → Auto Save**. A check mark appears next to it.

6. Open a terminal inside VS Code: menu **Terminal → New Terminal**. It opens in `lab-workspace/`; every command in this lab runs from there.

7. Make sure the prompt starts with `(venv)`. If it does not, run:

   ```bash
   source venv/bin/activate
   ```

   (Windows: `venv\Scripts\activate`.)

8. Load the Lab 1 starter files:

   ```bash
   python lab.py start 1
   ```

   `lab.py start 1` resets the workspace to the starting point of this lab: it removes every file a lab creates and copies in `../lab-starters/lab1.zip`. It refuses to run if git shows uncommitted changes; if it does, commit first (`git add -A && git commit -m "checkpoint"`) and run it again.

9. Confirm the load:

   ```bash
   python lab.py status
   ```

<details open>
<summary>What you should see</summary>

```
Workspace: .../ai-augmented-engineering/lab-workspace
  lab1       14/14 files identical, 0 extra lab file(s) present  <- matches
  lab2       ...
  lab3       ...
  lab4       ...
  solution   ...
git: uncommitted changes present
```

Only the **lab1** line matters: `14/14 files identical` and `<- matches`. The other lines describe the other labs' starting points and will show missing or extra files; that is expected. `git: uncommitted changes present` is also normal: loading the starter changed files in your working tree, and you have not committed yet.
</details>

10. Verify the Copilot configuration folder:

    ```bash
    ls -R .github/
    ```

<details open>
<summary>What you should see</summary>

```
.github/:
agents    copilot-instructions.md    instructions

.github/agents:
(empty)

.github/instructions:
perl-conversion.instructions.md
```

No `skills/` folder yet; you create the skill in Task 4. (Windows: `Get-ChildItem -Recurse .github`.)
</details>

11. In the Explorer panel on the left, open `.github/copilot-instructions.md`. It must contain only a heading and one comment line. If it already contains six standards, the loader did not run; repeat step 8.

12. Create a branch for this lab's work, so `main` stays exactly what you cloned (later labs compare against it):

    ```bash
    git checkout -b lab1
    ```

13. Commit the starting state:

    ```bash
    git add -A
    git commit -m "Lab 1 start state"
    ```

    The loader removed files that the repository's history still contains (the finished versions of what you build in this lab). Committing makes those removals part of your history, so the agent sees a clean tree instead of "deleted files" it might helpfully restore. `python lab.py status` no longer reports uncommitted changes after this.

---

## Task 1: Mode familiarization

### Task 1.1: Open the mode picker

1. Open the chat panel: menu **View → Chat**, or click the Copilot icon in the title bar at the top of the window and choose **Open Chat**.

2. Look at the bottom row of the chat input. From left to right: **+** (Add Context), the mode pill (**Agent ▾**), the model pill (**Auto ▾**), and a settings icon. A second row shows the run target (**Local ▾**) and the permissions pill (**Default permissions** or **Autopilot (Preview)**).

3. Click the mode pill. The dropdown lists three modes and a **Configure Custom Agent…** entry.

<details open>
<summary>What you should see</summary>

| Mode | What it does |
|---|---|
| **Agent** | Default mode. Plans, edits files, runs terminal commands (asking first), iterates autonomously. |
| **Ask** | Read-only. Answers questions without making any changes to files. |
| **Plan** | Researches the codebase, asks clarifying questions, produces a plan; you then choose **Start Implementation**. |

There is no Debug mode; Lab 2 uses Agent mode with an evidence-first prompt instead.

Two things to know about the **+** at the top of the panel (New Chat): a new chat keeps the mode the previous one was in (unlike Cursor, which always resets to Agent), and the empty new-chat view lists your recent sessions as links. If a step says Ask mode, check the pill after clicking **+**.
</details>

4. Close the dropdown without changing anything. The current mode should be **Agent**.

5. Click the model pill (**Auto ▾**) and read the list, then close it without changing anything. Auto may route different conversations to different models; leave it for this lab.

6. Click the permissions pill. Leave it on **Default permissions**: the agent asks before running each terminal command, with an **Allow ▾** / **Skip** card. **Allow all** and **Autopilot** remove that question; not for today.

---

### Task 1.2: Run the same prompt in Ask mode, then Agent mode

You will send one prompt twice: once in Ask mode, once in Agent mode, each in its own chat, and compare what each mode does with it.

1. Click **+** (New Chat) at the top of the panel, then set the mode pill to **Ask**.

2. Type the following prompt exactly and press Enter:

   ```
   Look at src/ingest.py in this project.
   I need it to meet professional Python standards.
   ```

3. Read the full response. Ask mode is read-only: it can only propose, and no files have changed.

   Above the answer there is a collapsed line such as **Completed 2 steps** with **Read ingest.py** pills. Click it. It lists what the agent read before answering; that list is how you check what an answer was based on.

4. **Before you continue, note:**

   > What did Ask mode propose? Which functions did it single out?

5. Click **+** (New Chat) and set the mode pill to **Agent**.

6. Send the identical prompt from step 2 and press Enter.

7. Watch what happens. Agent mode will most likely begin making changes to the file. If a card asks to run a command (pytest, say), click **Allow**. Wait for it to finish.

8. Look at the change summary **just above the chat input**: a line such as "1 file changed +12 −4" with **Keep** and **Undo** buttons. Click the line to expand the per-file rows.

9. Open `src/ingest.py` in the editor. The change is shown inline (removed lines in red, added in green) with Keep / Undo on each hunk and a "1 of N" navigator at the bottom right. Read it, but do not accept anything.

10. Click **Undo** in the change summary. The file returns to what it was. You are not ready to accept agent changes yet.

<details open>
<summary>What you should see</summary>

The change is already on disk before you click anything (run `git status --short` while the change is pending and `src/ingest.py` shows as modified). Copilot writes the agent's edits immediately; **Keep** means "stop tracking this as pending" and **Undo** is what reverses it.

**Ask mode** should have returned a proposal: what it would change in `src/ingest.py` and why (typically null handling on critical fields, error handling, and logging gaps), without touching any file.

**Agent mode** should have started editing `src/ingest.py` straight away, applying changes based on its judgment of what "professional Python standards" means. The instruction is the same; the mode decides whether it acts.

If Agent mode also only described changes without editing, check the wording: a prompt phrased as a question invites advice even in Agent mode. Tell it what you need and it acts. If it asked "Reuse the existing function?" or similar, that is Copilot's questions dialog; answer it.
</details>

11. **Before you continue, note:**

    > What did Agent mode do differently from Ask mode? Did files change? What did the agent attempt?

---

## Task 2: Build the DE standards instructions file

### Task 2.0: Capture the "before"

Before you write any instructions, record what the agent produces without them. You compare against this in Task 2.3.

1. Click **+** (New Chat). Confirm the mode pill says **Agent**.

2. Send:

   ```
   Write a Python function that reads a list of log file paths
   and counts how many times each IP address appears across all files.
   ```

3. Read the output. Leave this chat open.

4. If the agent created a file, click **Undo** in the change summary; the code in the chat is all you need.

---

### Task 2.1: Understand the file you are about to complete

The instructions file at `.github/copilot-instructions.md` was copied in by the loader in Task 0. It exists but is empty except for a heading and a comment.

1. In the Explorer panel, open `.github/copilot-instructions.md`.

<details open>
<summary>What you should see</summary>

```markdown
# DE Team Coding Standards

<!-- Add your six DE coding standards below this line -->
```

`.github/copilot-instructions.md` is Copilot's always-on instruction file. Its contents are included in every chat in this workspace, automatically, for anyone who opens the folder. No frontmatter, no activation setting: the file applies because it exists at this path. It is the twin of a Cursor rule with `alwaysApply: true`.

Path-scoped instructions (the twin of Cursor's `globs`) are separate files in `.github/instructions/`, covered in Task 3. Unlike Cursor there is exactly one always-on file.
</details>

---

### Task 2.2: Add the six DE coding standards

The six team standards are listed below as one block. Read them once as a set before adding them.

1. Copy the whole block below and paste it into `copilot-instructions.md` on the line just below the comment `<!-- Add your six DE coding standards below this line -->`:

   ```
   All Python function arguments must have type hints.
   All return types must be declared. Use the typing module for complex types.

   Every pipeline function must log on entry and exit using the project logger.
   Format: logger.info(f'Starting {function_name} with {len(records)} records')

   Use pathlib.Path for all file operations.
   Never use os.path or raw string paths passed directly to open().

   Handle None explicitly on all critical fields.
   Never use bare .get() without a default value on any pipeline field.

   Use collections.Counter for all counting and frequency analysis.
   Never use manual dictionary increment patterns.

   When converting Perl to Python, do not produce a line-by-line translation.
   Produce idiomatic Python: list comprehensions, Counter, pathlib, type hints, re module.
   ```

2. Confirm the file is saved (no dot on the tab; Auto Save is on).

---

### Task 2.3: Verify the instructions change agent output

1. Click **+** (New Chat), Agent mode. Copilot reads instruction files at the start of a chat, so the new file only counts from here.

2. Send the same prompt as Task 2.0:

   ```
   Write a Python function that reads a list of log file paths
   and counts how many times each IP address appears across all files.
   ```

3. Read the output. Check it against the standards:

   - [ ] Type hints on all function arguments and the return type
   - [ ] `pathlib.Path` for file handling
   - [ ] `collections.Counter` for counting
   - [ ] `logger.info` calls on entry and exit

4. Ask where the standards came from. Send:

   ```
   Which instruction files applied to that answer?
   ```

<details open>
<summary>What you should see</summary>

The agent names `copilot-instructions.md`, attached automatically as custom instructions. That is the proof that the file is in every chat without being mentioned in the prompt.

Compared with Task 2.0, the code now has the four items on the checklist. The log line usually follows the exact format from the file, even when the function counts files rather than records.
</details>

5. If the agent created a file, click **Undo**.

6. **Before you continue, note:**

   > What specific differences do you observe compared with the Task 2.0 output? Name at least two concrete differences.

<details>
<summary>If the instructions are not applying</summary>

1. Confirm the file is saved and at `.github/copilot-instructions.md` inside `lab-workspace/`. A file at the repository root above `lab-workspace/` is not read.
2. Start a completely new chat (**+**). Instruction files are read at chat start, not mid-conversation.
3. Check the status bar at the bottom left for a Restricted Mode shield. If present, click it and choose **Trust Workspace**.
</details>

---

## Task 3: Read and extend the Perl conversion instructions file

### Task 3.1: Open and read the file

The starter files include a pre-built `perl-conversion.instructions.md` in `.github/instructions/`.

1. In the Explorer panel, open `.github/instructions/perl-conversion.instructions.md`.

2. Read the frontmatter first. The `applyTo:` field means this file activates when Copilot is working with `.pl` or `.py` files, but not for every conversation. That is different from `copilot-instructions.md`, which always applies. It is the twin of Cursor's `globs` field.

3. Read each instruction in the file body.

<details>
<summary>What the file contains</summary>

```
---
applyTo: "**/*.pl,**/*.py"
---

# Perl to Python Conversion Standards

Translate Perl regex using Python's re module.
Convert /.../g patterns to re.finditer() or re.findall().
Pre-compile patterns that are used inside loops: pattern = re.compile(r'...')

Do not translate Perl sigils literally.
Use collections.Counter for counting patterns.
Use dict for hash mappings.
Use set for membership tests.

Use pathlib.Path for all file operations.
No os.path. No raw string paths passed to open().

All function arguments must have type hints.
All return types must be declared.

Replace LWP::UserAgent with the requests library.
Replace JSON::from_json / to_json with the json standard library module.
Replace Time::HiRes with time.time() or time.perf_counter().
Replace Data::Dumper with pprint.

Do not call exit() inside library code or module functions.
Raise exceptions instead. Use custom exception classes where appropriate.

When you see a Perl construct, ask what it is trying to accomplish.
Then write the Python that accomplishes the same thing idiomatically.
Do not produce a line-by-line translation.
```

`applyTo:` is the only required metadata. The value is a glob pattern; several patterns are comma-separated.
</details>

4. **Before you continue, note:**

   > Which instruction in the file covers something you were not expecting? Or: what instruction do you think is missing?

---

### Task 3.2: Add one instruction based on your team's conventions

1. Below the last existing instruction in `perl-conversion.instructions.md`, add one new instruction that covers a Python pattern your team uses that is not already in the file.

<details>
<summary>Examples of instructions you might add</summary>

These are examples only. Write an instruction that reflects your team's actual conventions.

```
Use structlog for all logging. Never use the standard library logging module directly.
```

```
All pipeline functions that process records must include a try/except block
that catches Exception, logs the error with logger.exception(), and re-raises.
```

```
Database connection strings must be read from environment variables using os.environ.get().
Never hardcode connection strings in pipeline code.
```
</details>

2. Confirm the file is saved.

3. Click **+** (New Chat), Agent mode.

4. Attach the Perl file: click **+** (Add Context) at the left of the input, choose **Files & Folders…**, type `ingest.pl` and pick `perl/ingest.pl`. It appears as a chip above the input.

5. Type and send:

   ```
   Review this Perl file and tell me what the key differences will be in the Python equivalent.
   ```

   Notice that the prompt does not mention the instructions file. It does not need to: `perl-conversion.instructions.md` applies to any conversation working with a `.pl` file.

6. Read the response. Then expand the **Completed N steps** line above it: the **Read** pills include `perl-conversion.instructions.md` and `copilot-instructions.md` alongside `ingest.pl`. That is the instructions doing their work without being named in the prompt. If the pills do not show them, send `Which instruction files applied to that answer?`

<details open>
<summary>What you should see</summary>

An answer organised by the differences the instructions ask for, not a line-by-line translation. Look for: `csv` and `pathlib.Path` instead of hand-split lines and string paths; `collections.Counter` for the exchange counts; an explicit sort key for tied counts; explicit `None` handling instead of Perl's `//` and `||`; a list comprehension for the skip loop; exceptions and the project logger instead of `die` and `warn`; and your new instruction from step 1, alongside the existing ones. A closing line such as "those are the conversion-standard differences, not a line-by-line rewrite" is the last instruction in the file speaking.
</details>

<details>
<summary>If your instruction does not appear in the response</summary>

1. Confirm the file is saved.
2. Confirm the frontmatter `applyTo:` field includes `**/*.pl`.
3. Confirm you attached `perl/ingest.pl` as a chip; path-scoped instructions need a matching file in the conversation.
4. Attach the instructions file explicitly: **+** (Add Context) → **Files & Folders…** → `perl-conversion.instructions.md`, and send the prompt again.
</details>

---

## Task 4: Build the pipeline-review skill

### Task 4.1: Create the skill with /create-skill

1. Click **+** (New Chat), Agent mode.

2. Type `/` and choose **create-skill** ("Create a reusable skill (SKILL.md) that packages a workflow") from the list. It becomes a highlighted tag. A pasted `/create-skill` is just text and does nothing; type the slash.

3. After the tag, paste the following and press Enter:

   ```
   Create a new project skill named pipeline-review in .github/skills/.
   It reviews Python pipeline code against DE team standards.
   Check for: schema drift handling, null safety on critical fields, idempotency,
   logging completeness, and type hint coverage.
   Flag each issue as Critical, Warning, or Informational.
   Produce a structured review summary grouped by severity.
   ```

   If the agent says it is "recovering" or "rebuilding" an earlier skill, it found one in the repository's history. Let it finish; Task 4.2 checks the file it produced, and if the five criteria are there the result is the same.

4. Expand the **Completed N steps** line as it works. It reads the instruction files and the pipeline source so that the skill's checks fit this repository; that is what makes a *project* skill different from a generic checklist.

5. If it asks questions (where to store the skill, what to name it), answer them: the location is the project, `.github/skills/`, so that every team member has the skill after cloning. Often there are no questions at all and the skill is created straight away.

6. When it finishes, the change summary above the input lists `.github/skills/pipeline-review/SKILL.md`. Click **Keep**.

---

### Task 4.2: Inspect and verify the skill file

1. In the Explorer panel, open `.github/skills/pipeline-review/SKILL.md`.

2. Confirm the file has YAML frontmatter with at least a `name` field and a `description` field.

3. Read the skill body. Confirm it covers all five review criteria:

   - [ ] Schema drift handling
   - [ ] Null safety on critical fields
   - [ ] Idempotency
   - [ ] Logging completeness
   - [ ] Type hint coverage

4. If any criterion is missing, add it as a numbered item in the skill body. Confirm the file is saved.

5. Type `/skills` in the chat input and press Enter. A quick pick opens listing the skills Copilot knows about; **pipeline-review** appears with the scope **Workspace**. Press Escape to close it.

<details>
<summary>Complete SKILL.md reference</summary>

Your skill file should look similar to this. The exact wording may differ, but all five criteria must be present:

```markdown
---
name: pipeline-review
description: Reviews Python pipeline code against DE team standards. Flags schema drift handling, null safety, idempotency, logging completeness, and type hint coverage.
---

Review the provided Python pipeline code against the following criteria.
For each finding, state the criterion violated, the file and line number,
and a specific recommendation.

Group findings by severity:

## Critical
Issues that will cause data loss, silent failures, or incorrect pipeline output.
- Missing schema validation on incoming data
- None values not handled on record_id, instrument_id, exchange_code, price, volume, or figi fields
- Pipeline steps that are not idempotent

## Warning
Issues that reduce reliability or violate team standards.
- Functions missing type hints on arguments or return values
- Missing logger.info calls on function entry or exit
- File operations not using pathlib.Path

## Informational
Style issues and improvement opportunities.
- for-append loops that could be list comprehensions
- dict counting patterns that should use collections.Counter
```
</details>

---

### Task 4.3: Run the skill by naming it

In Cursor a skill runs when you type `/pipeline-review`. Copilot has no slash per skill: the agent decides to use a skill when the task calls for it, and the reliable way to make that happen is to name the skill in the prompt.

1. Click **+** (New Chat), Agent mode.

2. Send:

   ```
   Use the pipeline-review skill to review src/ingest.py.
   ```

3. Expand the **Completed N steps** line. One of the pills reads **Read skill pipeline-review**: the agent loaded your SKILL.md and followed it.

4. Read the structured output. It should be grouped by severity: Critical, Warning, Informational, with a file and line for each finding and a closing verdict. Notice that a rubric-driven review finds concrete issues in the same file that an open-ended question in Task 1.2 may have called "already in good shape".

<details open>
<summary>What you should see</summary>

A review in the skill's format, not a prose opinion. If you get prose with no severity sections, the skill did not run; check that the file is at `.github/skills/pipeline-review/SKILL.md` and that the prompt names it exactly.

This is the difference from Cursor worth remembering: Copilot skills are picked up on the agent's judgment. Left to itself, asked "review this against our standards", it may write a prose review from the instruction files instead. Name the skill when you want the procedure.
</details>

---

### Task 4.4: Attach the skill as context and compare

1. Click **+** (New Chat), Agent mode.

2. Click **+** (Add Context) → **Files & Folders…**, type `SKILL` and pick `.github/skills/pipeline-review/SKILL.md`. It appears as a chip: the file is attached as reference, not run.

3. Type this message and press Enter:

   ```
   Rewrite resolve_figis in src/ingest.py so that it would pass
   the attached pipeline-review criteria with no Critical findings.
   Show me the diff before applying it.
   ```

4. Read the diff it shows. The prompt asked to see the diff first, so the agent usually describes the change and waits. Do not tell it to apply. If it applied the change anyway, click **Undo** in the change summary; Task 5 is where you make changes on purpose.

5. **Before you continue, note:**

   > What is the specific behavioural difference between naming the skill (Task 4.3) and attaching its file (this Task)? Describe what each one did differently in your own words.

<details open>
<summary>The expected difference</summary>

**Naming the skill** runs the skill's procedure and produces its report. You are handing control to the skill.

**Attaching the file** hands the agent the criteria as reference and lets you ask for something the skill was never written to do; here, to write code that satisfies the rubric. You are keeping control and using the skill as an input.

Name the skill to get the report. Attach it when the rubric is an input to a different task. The Cursor twins are `/pipeline-review` and `@pipeline-review`.
</details>

---

## Task 5: Apply the integrating workflow

### Task 5.1: Explore first in Ask mode

1. Click **+** (New Chat) and set the mode pill to **Ask**.

2. Send the following prompt and press Enter:

   ```
   Look at src/ingest.py. Identify the single function that most needs improvement
   against our team standards. Name the function, describe what is wrong with it,
   and tell me exactly what you would change.
   ```

3. Read the full response. Expand the **Completed N steps** line: the agent read the instruction files, and often the skill, before choosing a function, so "our team standards" in the prompt meant something concrete.

4. **Before switching to Agent mode, be able to say in one sentence what the function does and why the suggested change makes it better.**

   > This is the explore-before-changing gate. If you cannot say it, you are not ready to change it.

   If you cannot, stay in Ask mode and send: `In one sentence: what does that function do, and why does your change make it better?` Then decide whether you agree with the sentence. Asking is allowed; changing code you cannot explain is not.

<details>
<summary>Why this gate matters</summary>

The explore-before-changing discipline is the professional habit this course builds on. The agent is faster at execution than any human. The human advantage is judgment about what to execute.

If you cannot describe in one sentence what the function does and why the change is an improvement, you do not yet understand what you are about to change. Stay in Ask mode and ask more questions before proceeding.
</details>

---

### Task 5.2: Switch to Agent mode and execute

1. Stay in the same chat. Set the mode pill to **Agent**. The agent keeps everything it just told you, so you do not need to name the function again.

2. Send:

   ```
   Apply the improvements you described to that function in src/ingest.py,
   following the standards in our .github instruction files.
   ```

3. Watch the agent work. It may ask to run `pytest`; click **Allow**. If its terminal reports `command not found: pytest`, reply `Run it as ./venv/bin/python -m pytest` (Windows: `venv\Scripts\python -m pytest`).

4. When the agent finishes, open `src/ingest.py` and read the inline diff hunk by hunk before accepting.

<details open>
<summary>What to look for in the diff</summary>

Every change in the diff should be explained by one line in `copilot-instructions.md` or `perl-conversion.instructions.md`: type hints on arguments and the return type; `pathlib.Path` instead of `os.path` or string paths; `logger.info` at entry and exit; explicit `None` checks on critical fields; exceptions logged and re-raised rather than swallowed.

An instruction with nothing to fix in this function produces no change. If the agent chose `resolve_figis`, there is no counting in it, so no `collections.Counter` appears; that is correct, not a miss.

If the diff shows changes that no instruction explains, read each one and ask the agent to explain before accepting.
</details>

5. Click **Keep** in the change summary only after reviewing every changed line.

6. In the same chat, send:

   ```
   Use the pipeline-review skill to review the function you just changed in src/ingest.py
   and report the remaining issues.
   ```

7. **Before you continue, note:**

   > What specific changes did the agent make? Which of the six standards are visible in the diff? What did the pipeline-review skill report as remaining issues?

---

### Task 5.3: Capture learning as an instruction

This Task closes the loop the lab has been building: the skill *reports* problems, the instructions *prevent* them. A finding the instructions do not yet cover becomes an instruction, so every future chat gets it for free.

1. Look at the pipeline-review report from Task 5.2 step 6. For each Critical or Warning finding, check whether one of the six standards in `copilot-instructions.md` already covers it.

2. If a finding is not covered (a swallowed exception or a missing schema check, say), open `.github/copilot-instructions.md` and add one line at the end that would have prevented it. Write it as a direct instruction to the agent, in the same voice as the six standards.

3. Confirm the file is saved.

<details open>
<summary>What you should see</summary>

One new line at the end of `copilot-instructions.md`, or none. If every finding was already covered, your instructions file is well calibrated for this function; note that in the debrief, it is a valid and good outcome. The next chat you open in this project reads the new instruction automatically, which is the difference between fixing a function and fixing a team.
</details>

---

## Lab Debrief

Write answers to these prompts before the room debrief begins. You will share one answer with the group.

---

**Question 1**

In Task 1.2 you ran the same prompt in Ask mode and Agent mode. What was the most significant behavioural difference you observed? Why does that difference matter for the Perl conversion work in Lab 2?

---

**Question 2**

In Tasks 2.0 and 2.3 you ran the same prompt without and with `copilot-instructions.md`. What specific code construct changed? Name the before and after explicitly.

---

**Question 3**

In Tasks 4.3 and 4.4 you ran the skill by naming it and used it as attached context. In your own words, when would you use each approach in your daily work? What does Copilot leave to the agent's judgment that Cursor's `/` makes explicit?

---

**Question 4**

In Task 3.2 you added an instruction to `perl-conversion.instructions.md`. What instruction did you add? Why does your team need it and why was it not already in the file?
