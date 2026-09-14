# Lab 1: Configure Before You Convert
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro or Teams plan)
**Duration:** 60 minutes
**Day:** Day 1, following Module 1

---

## Prerequisites

- [ ] Module 1 lecture completed
- [ ] Cursor installed and signed in (Pro or Teams plan)
- [ ] Course repository cloned and the README **Quick Start** completed: virtual environment created, `pip install -r requirements.txt` done, `pytest tests/ -q` passes
- [ ] The repository folder open in the Cursor **IDE** (File → Open Folder), not the Agents Window
- [ ] Git configured with your name and email (`git config --global user.name` returns a value)
- [ ] pytest accessible from the terminal (`pytest --version` returns a version). Every new terminal needs the venv activated first: `source venv/bin/activate` (Windows: `venv\Scripts\activate`). If the prompt does not start with `(venv)`, pytest will not be found.

---

## Lab Overview

Your team is about to start converting a production Perl pipeline to Python. Before anyone touches code, this lab establishes the shared configuration that makes every engineer's agent output consistent and standards-compliant.

Every artifact you build here is used directly in Labs 2, 3, and 4. Do not skip tasks or use different file names from the ones specified.

**What you will build:**
- `.cursor/rules/de-standards.mdc`  team DE coding standards enforced on every agent conversation
- `.cursor/rules/perl-to-python.mdc`  conversion-specific rules that activate on Perl and Python files
- `.cursor/skills/pipeline-review/SKILL.md`  an invocable code review checklist

**What you will observe:**
- The measurable difference in agent output before and after rules are active
- The behavioral difference between `/skill-name` (run as workflow) and `@skill-name` (attach as context)

---

## Step 0: Load Starter Files

**Check which window you are in.** Cursor 3 can open into the **Agents Window**: a chat-style screen with New Chat, Automations and Repositories down the left and no code editor. Everything in this lab happens in the **IDE** (the editor with a chat panel). If you see the Agents Window, click **IDE ↗** at the top right to open the editor.

**Turn on File → Auto Save** (a check mark appears next to it). Every step below that says "save the file" then happens automatically, and an unsaved rules file, the most invisible reason a rule "doesn't work", cannot happen.

Open a terminal inside Cursor (menu **Terminal → New Terminal**). Make sure the prompt starts with `(venv)`; if not, run `source venv/bin/activate` (Windows: `venv\Scripts\activate`). Then run, from the repository root:

```bash
python lab.py start 1
python lab.py status
```

`lab.py start 1` resets the workspace to the starting point of this lab: it removes every file a lab creates and copies in `lab-starters/lab1/`. The status line for `lab1` should end with `<- matches`. It refuses to run if git shows uncommitted changes; commit or stash first (`git add -A && git commit -m "checkpoint"`).

Verify the starter is in place:

```bash
ls .cursor/rules/
```

<details>
<summary>Expected output</summary>

You should see two files listed:

```
de-standards.mdc
perl-to-python.mdc
```

Open `.cursor/rules/de-standards.mdc` from the Explorer panel on the left. It must contain only the frontmatter and one comment line. If it already contains six standards, the loader did not run; repeat `python lab.py start 1`.
</details>

---

## Part 1: Mode Familiarization

### Step 1.1: Open the mode dropdown

Make sure the Cursor chat panel is open. If it is not visible, click the chat-panel toggle at the top right of the window (the speech-bubble icon next to the terminal icon and the gear), or press `Ctrl+I` (Windows) or `Cmd+I` (Mac).

Click the **∞** icon at the bottom left of the chat input (∞ is the Agent icon; the picker shows an icon, not a name). The dropdown lists five modes.

<details>
<summary>What you should see in the dropdown</summary>

The five modes listed are:

| Mode | What it does |
|---|---|
| **Agent** | Default mode. Plans, edits files, runs terminal commands, iterates autonomously. |
| **Plan** | Researches the codebase, asks clarifying questions, produces a plan before writing code. |
| **Debug** | Reproduces the failure, proposes a fix, re-runs, and offers Mark as Fixed. |
| **Multitask** | Splits a request into parallel sub-tasks run by separate agents (Module 5). Leave it alone for now. |
| **Ask** | Read-only. Answers questions without making any changes to files. |

Switch between modes using the dropdown, press `Shift+Tab` to cycle through them, or type the mode as a slash command (`/ask`, `/plan`, `/debug`). After cycling, the picker shows an icon only; hover it or open the dropdown to read the mode name.

Every **new** conversation starts in Agent mode, whatever mode the previous one was in. If a step says Ask mode, switch after clicking **+**.
</details>

Note the current mode. It is most likely **Agent**. Do not change it yet. The picker to its right ("High Fast") is effort and speed, not a model; click it and read the **Model** row if you want to know which model is answering. Leave the default for this lab.

---

### Step 1.2: Run the same prompt in Ask mode, then Agent mode

Switch to **Ask mode** by clicking it in the dropdown.

Type the following prompt exactly and press Enter:

```
Look at src/ingest.py in this project. I need it to meet professional Python standards.
```

Read the full response. Ask mode is read-only: it can only propose, and no files have changed.

**Write down your answer before continuing:**

> What did Ask mode propose? Which functions did it single out?

---

Now switch to **Agent mode** using the dropdown.

Send the identical prompt. Press Enter.

Watch what happens. Agent mode will likely begin making changes to the file.

When the agent finishes, look at the **change summary at the bottom of the chat panel**: it lists `ingest.py` with the number of lines added and removed, and three buttons, **Undo**, **Keep**, and **Review**. Click **Review** to see the diff, then click **Undo**. You are not ready to accept agent changes just yet.

> The change is already on disk. Cursor writes the agent's edits immediately; **Keep** means "stop tracking this as pending" and **Undo** is what reverses it. Nothing is highlighted in the editor until the changed file is open.

**Write down your answer before continuing:**

> What did Agent mode do differently from Ask mode? Did files change? What did the agent attempt?

<details>
<summary>What to expect from each mode</summary>

**Ask mode** should have returned a proposal: what it would change in `src/ingest.py` and why (typically null handling on critical fields, error handling, and logging gaps), without touching any file.

**Agent mode** should have started editing `src/ingest.py` straight away, applying changes based on its judgment of what "professional Python standards" means. The instruction is the same; the mode decides whether it acts.

The key observation: Ask mode is structurally read-only. Agent mode acts. The mode discipline this course teaches: explore with Ask, then switch to Agent when you are ready, exists because of this difference.

If Agent mode also only described changes without editing, check the wording: a prompt phrased as a question ("What would you change?") invites advice even in Agent mode. Tell it what you need and it acts.
</details>

---

## Part 2: Build the DE Standards Rules File

### Step 2.0: Capture the "before"

Before you write any rules, open a new Agent mode conversation (**+**) and send:

```
Write a Python function that reads a list of log file paths and counts how many times each IP address appears across all files.
```

Read the output and leave that conversation open. You will compare against it in Step 2.3. If the agent offers to create a file, click **Undo** in the change summary; the code in the chat is all you need.

---

### Step 2.1: Understand the file you are about to create

The rules file at `.cursor/rules/de-standards.mdc` was copied from the starter files in Step 0. It currently exists but is empty except for the frontmatter header.

Open it now: double-click `.cursor/rules/de-standards.mdc` in the Explorer panel on the left.

<details>
<summary>What the starter file contains</summary>

The starter file has this frontmatter already in place:

```yaml
---
description: DE team coding standards for Python pipeline development
alwaysApply: true
---
```

The `alwaysApply: true` setting means every agent conversation in this project will include these rules automatically. You do not need to reference the file in each prompt.

Above the text, Cursor shows a dropdown (Always Apply / Apply Intelligently / Apply to Specific Files / Apply Manually) and a description box. Those are the same `alwaysApply` and `description` values shown as a form; change either one and the other follows.

**Important:** The file must have the `.mdc` extension. A file named `de-standards.md` in the same directory is silently ignored by Cursor. The extension is not optional.
</details>

---

### Step 2.2: Add the six DE coding standards

The six team standards are listed below. Read them once as a set before typing any of them.

Add the following six rules below the frontmatter in `de-standards.mdc`. Write each as a direct instruction to the agent, not a policy description.

**Rule 1: Type hints**
```
All Python function arguments must have type hints.
All return types must be declared. Use the typing module for complex types.
```

**Rule 2: Logging**
```
Every pipeline function must log on entry and exit using the project logger.
Format: logger.info(f'Starting {function_name} with {len(records)} records')
```

**Rule 3: File handling**
```
Use pathlib.Path for all file operations.
Never use os.path or raw string paths passed directly to open().
```

**Rule 4: Null safety**
```
Handle None explicitly on all critical fields.
Never use bare .get() without a default value on any pipeline field.
```

**Rule 5: Counting patterns**
```
Use collections.Counter for all counting and frequency analysis.
Never use manual dictionary increment patterns.
```

**Rule 6: Perl conversion**
```
When converting Perl to Python, do not produce a line-by-line translation.
Produce idiomatic Python: list comprehensions, Counter, pathlib, type hints, re module.
```

With Auto Save on, the file is already saved (no dot on the tab). If you skipped Auto Save, press `Ctrl+S` (Windows) or `Cmd+S` (Mac).

<details>
<summary>Complete `de-standards.mdc` reference</summary>

Your completed file should look exactly like this:

```
---
description: DE team coding standards for Python pipeline development
alwaysApply: true
---

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
</details>

---

### Step 2.3: Verify the rules change agent output

Open a new Agent mode conversation (**+**).

Send the same prompt as Step 2.0:

```
Write a Python function that reads a list of log file paths and counts how many times each IP address appears across all files.
```

Read the output carefully and compare it with the Step 2.0 conversation. With `de-standards.mdc` active and `alwaysApply: true` set, the output should include all of the following:

- [ ] Type hints on all function arguments and the return type
- [ ] `pathlib.Path` for file handling
- [ ] `collections.Counter` for counting
- [ ] `logger.info` calls on entry and exit, in the rule's exact format (look for `Starting count_ip_addresses with {len(...)} records`; the word "records" for a list of paths is the rule's format string applied verbatim, which is the proof the rule was read)

<details>
<summary>What to do if the rules are not applying</summary>

Check three things in order:

1. **File extension:** The file must be `.mdc`, not `.md`. Check the filename in the file explorer.
2. **Frontmatter syntax:** Open the file and confirm the dashes and field names match exactly. Smart quotes or extra spaces before the dashes will break the parser.
3. **File saved:** Check the tab has no unsaved dot (File → Auto Save should be on), then try the verification prompt again in a fresh conversation.

If none of these fix it, close and reopen Cursor entirely, then try again.
</details>

**Write down your answer before continuing:**

> What specific differences do you observe compared to the Step 2.0 output, produced without the rules file? Name at least two concrete differences in the code.

---

## Part 3: Read and Extend the Perl-to-Python Rules File

### Step 3.1: Open and read the file

The starter files include a pre-built `perl-to-python.mdc` in `.cursor/rules/`. Open it now: double-click it in the Explorer panel.

Read the frontmatter first. Note the `globs` field: this file activates automatically for `*.pl` and `*.py` files, but not for every conversation. This is different from `de-standards.mdc`, which uses `alwaysApply: true`. The dropdown above the text reads **Apply to Specific Files** and shows the two patterns.

Read each rule in the file body.

<details>
<summary>What the perl-to-python.mdc file contains</summary>

```
---
description: Perl to Python conversion standards for the DE pipeline modernisation project
globs: ["**/*.pl", "**/*.py"]
---

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

When you see a Perl construct, ask what it is trying to accomplish.
Then write the Python that accomplishes the same thing idiomatically.
Do not produce a line-by-line translation.
```
</details>

**Write down your answer before continuing:**

> Which rule in `perl-to-python.mdc` covers something you were not expecting? Or: what rule do you think is missing?

---

### Step 3.2: Add one rule based on your team's conventions

Below the last existing rule in `perl-to-python.mdc`, add one new rule that covers a Python pattern your team uses that is not already in the file.

<details>
<summary>Examples of rules you might add</summary>

These are examples only. Write a rule that reflects your team's actual conventions.

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

Save the file.

Verify the rule is being read: open a new Agent mode conversation, type `@`, choose `perl/ingest.pl` from Files & Folders so it becomes a tag, then send:

```
Review this Perl file against the conversion rules in .cursor/rules/perl-to-python.mdc. What would the key differences be in the Python equivalent?
```

The response should mention your new rule alongside the existing ones.

<details>
<summary>What to do if your rule does not appear in the response</summary>

1. Confirm the file is saved.
2. Confirm the frontmatter `globs` field includes `"**/*.pl"`.
3. Confirm you attached `@perl/ingest.pl` in the prompt -- the globs activation requires the agent to be working with a matching file.
4. Try attaching the rule file explicitly: type `@`, choose `.cursor/rules/perl-to-python.mdc`.
</details>

---

## Part 4: Build the Pipeline-Review Skill

### Step 4.1: Create the skill using /create-skill

Open a new Agent mode conversation.

Type `/` and choose **create-skill** from the list. It turns into a highlighted tag; a pasted `/create-skill` is just text and does nothing. After the tag, paste the following and press Enter:

```
Review Python pipeline code against DE team standards. Check for: schema drift handling, null safety on critical fields, idempotency, logging completeness, and type hint coverage. Flag each issue as Critical, Warning, or Informational. Produce a structured review summary grouped by severity.
```

Cursor opens a **Questions** dialog. Answer each question and click **Continue**. The questions, their order, and the option letters vary from run to run; read the options rather than the letters.

<details>
<summary>What questions to expect and how to answer them</summary>

The questions are dynamic -- a specific description produces fewer questions. You will always see at least the storage location question:

**Where should this skill be stored?**
- Project (`.cursor/skills/`), this repo only, shared with anyone who clones it (usually marked Recommended)
- Personal (your user Agent Store), available in every project, on every machine you sign in on
- Other

**Choose the option that says Project (`.cursor/skills/`).** This stores the skill in the repository so every team member has access to it after cloning.

If Cursor asks additional questions about the skill name or description, answer them specifically. The more detail you provide, the better the generated skill body will be.
</details>

---

### Step 4.2: Inspect and verify the skill file

Open `.cursor/skills/pipeline-review/SKILL.md` in the editor.

Confirm the file has YAML frontmatter with at least a `name` field and a `description` field.

Read the skill body. Confirm it covers all five review criteria:

- [ ] Schema drift handling
- [ ] Null safety on critical fields
- [ ] Idempotency
- [ ] Logging completeness
- [ ] Type hint coverage

If any criterion is missing, add it as a numbered item in the skill body. Save the file.

<details>
<summary>Complete SKILL.md reference</summary>

Your skill file should look similar to this. The exact wording may differ based on how /create-skill generated it, but all five criteria must be present:

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

### Step 4.3: Invoke with / and observe the output

Open a new Agent mode conversation.

Type `/`, choose **pipeline-review** from the list, and press Enter. If it asks what to review, type the line below; otherwise it reviews `src/` on its own:

```
Review src/ingest.py
```

Read the structured output. It should be grouped by severity: Critical, Warning, Informational, with a file and line for each finding and a closing verdict. Notice that a rubric-driven review finds concrete issues in the same file that an open-ended question in Step 1.2 may have called "already in good shape".

---

### Step 4.4: Invoke with @ and compare

Open another new Agent mode conversation.

Type `@.cursor/skills/pipeline` in the chat input and choose the entry whose path starts with `.cursor/skills/` (hover the tag to see the full path). This attaches the skill's `SKILL.md` as a file; Cursor has no separate skills category in the `@` menu.

Add this message and press Enter:

```
Rewrite resolve_figis in src/ingest.py so that it would pass the attached pipeline-review criteria with no Critical findings. Show me the diff before applying it.
```

**Write down your answer before continuing:**

> What is the specific behavioral difference between `/pipeline-review` and `@pipeline-review`? Describe what each one did differently in your own words.

<details>
<summary>The expected difference</summary>

**`/pipeline-review`** runs the skill's procedure and produces its report. You are handing control to the skill.

**`@pipeline-review`** hands the agent the criteria as reference and lets you ask for something the skill was never written to do; here, to write code that satisfies the rubric. You are keeping control and using the skill as an input.

Use `/` to get the report. Use `@` when the rubric is an input to a different task.
</details>

---

## Part 5: Apply The Integrating Workflow

### Step 5.1: Explore first in Ask mode

Switch to **Ask mode** using the mode dropdown.

Send the following prompt and press Enter:

```
Look at src/ingest.py. Identify the single function that most needs improvement against our team standards. Name the function, describe what is wrong with it, and tell me exactly what you would change.
```

Read the full response.

**Before switching to Agent mode, write a one-sentence description of what the function does and why the suggested change makes it better.**

> Write your sentence here before continuing. This is the explore-before-changing gate.

<details>
<summary>Why this gate matters</summary>

The explore-before-changing discipline is the professional habit this course builds on. The agent is faster at execution than any human. The human advantage is judgment about what to execute.

If you cannot describe in one sentence what the function does and why the change is an improvement, you do not yet understand what you are about to change. Switch back to Ask mode and ask more questions before proceeding.
</details>

---

### Step 5.2: Switch to Agent mode and execute

Stay in the same conversation. Switch the mode picker to **Agent** (the ∞ dropdown, `Shift+Tab`, or `/agent`). The agent keeps everything it just told you, so you do not need to name the function again. Send:

```
Apply the improvements you described to that function in src/ingest.py, following the standards in our .cursor/rules/ files.
```

Press Enter and watch the agent work. It may run `pytest` on its own and report the result; that is expected.

When the agent finishes, click **Review** in the change summary at the bottom of the chat to examine the diff before accepting.

Then, in the same conversation, type `/`, choose **pipeline-review**, and after the tag type:

```
Review the function you just changed in src/ingest.py and report the remaining issues.
```

<details>
<summary>What to look for in the diff</summary>

The diff should show changes corresponding to the rules in `de-standards.mdc`:

- Type hints added to all function arguments and the return type
- `pathlib.Path` replacing any `os.path` or raw string paths
- `collections.Counter` replacing any manual dict counting
- `logger.info` calls added at function entry and exit
- `None` checks added on critical fields

If the diff shows changes that are not explained by your rules files, read each one and ask the agent to explain before accepting.

Accept using **Keep** only after reviewing every changed line.
</details>

**Write down your answer before continuing:**

> What specific changes did the agent make? Which of the de-standards.mdc rules are visible in the diff? What did /pipeline-review report as remaining issues?

---

### Step 5.3: Capture learning as a rule

If the `/pipeline-review` skill flagged anything as Critical or Warning that your `de-standards.mdc` file does not already cover, open `de-standards.mdc` now.

Add one new rule addressing the gap. Write it as a direct instruction to the agent.

Save the file.

> If the pipeline-review found nothing that de-standards.mdc did not already cover, your rules file is well-calibrated for this function. Note that in the debrief it is a valid and good outcome.

---

## Lab Debrief

Write answers to these prompts before the room debrief begins. You will share one answer with the group.

---

**Question 1**

In Step 1.2 you ran the same prompt in Ask mode and Agent mode. What was the most significant behavioral difference you observed? Why does that difference matter for the Perl conversion work in Lab 2?

---

**Question 2**

In Steps 2.0 and 2.3 you ran the same prompt without and with `de-standards.mdc`. What specific code construct changed? Name the before and after explicitly.

---

**Question 3**

In Step 4.4 you invoked `/pipeline-review` and also used `@pipeline-review`. In your own words, when would you use each invocation method in your daily work?

---

**Question 4**

In Step 3.2 you added a rule to `perl-to-python.mdc`. What rule did you add? Why does your team need it and why was it not already in the file?
