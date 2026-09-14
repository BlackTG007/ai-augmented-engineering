# Lab 1: Configure Before You Convert
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro or Teams plan)
**Duration:** 75 minutes
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

**How this lab is written:** each Task has numbered steps. A numbered step is something you do. Text between steps explains what you are looking at; the boxes marked "What you should see" tell you what a correct result looks like.

---

## Task 0: Load the starter files

1. Check which window you are in. Cursor 3 can open into the **Agents Window**: a chat-style screen with New Chat, Automations and Repositories down the left and no code editor. Everything in this lab happens in the **IDE** (the editor with a chat panel). If you see the Agents Window, click **IDE ↗** at the top right to open the editor.

2. Turn on **File → Auto Save**. A check mark appears next to it. Every step below that says "save the file" then happens automatically.

3. Open a terminal inside Cursor: menu **Terminal → New Terminal**.

4. Make sure the prompt starts with `(venv)`. If it does not, run:

   ```bash
   source venv/bin/activate
   ```

   (Windows: `venv\Scripts\activate`.)

5. Load the Lab 1 starter files. Run from the repository root:

   ```bash
   python lab.py start 1
   ```

   `lab.py start 1` resets the workspace to the starting point of this lab: it removes every file a lab creates and copies in `lab-starters/lab1/`. It refuses to run if git shows uncommitted changes; if it does, commit first (`git add -A && git commit -m "checkpoint"`) and run it again.

6. Confirm the load:

   ```bash
   python lab.py status
   ```

<details open>
<summary>What you should see</summary>

```
Workspace: .../ai-augmented-engineering
  lab1       11/11 files identical, 0 extra lab file(s) present  <- matches
  lab2       ...
  lab3       ...
  lab4       ...
  solution   ...
git: uncommitted changes present
```

Only the **lab1** line matters: `11/11 files identical` and `<- matches`. The other lines describe the other labs' starting points and will show missing or extra files; that is expected. The last line, `git: uncommitted changes present`, is also normal: loading the starter changed files in your working tree, and you have not committed yet.
</details>

7. Verify the rules folder:

   ```bash
   ls .cursor/rules/
   ```

<details open>
<summary>What you should see</summary>

```
de-standards.mdc
perl-to-python.mdc
```
</details>

8. In the Explorer panel on the left, open `.cursor/rules/de-standards.mdc`. It must contain only the frontmatter (the lines between the `---` markers) and one comment line. If it already contains six standards, the loader did not run; repeat step 5.

9. Commit the starting state:

   ```bash
   git add -A
   git commit -m "Lab 1 start state"
   ```

   The loader removed files that the repository's history still contains (the finished versions of what you build in this lab). Committing makes those removals part of your history, so the agent sees a clean tree instead of "deleted files" it might helpfully restore. `python lab.py status` no longer reports uncommitted changes after this.

---

## Task 1: Mode familiarization

### Task 1.1: Open the mode dropdown

1. Make sure the Cursor chat panel is open. If it is not visible, click the chat-panel toggle at the top right of the window (the speech-bubble icon next to the terminal icon and the gear), or press `Ctrl+I` (Windows) or `Cmd+I` (Mac).

2. Click the **∞** icon at the bottom left of the chat input. ∞ is the Agent icon; on a narrow window the picker shows only the icon, on a wide window it shows the icon and the mode name. The dropdown lists five modes.

<details open>
<summary>What you should see</summary>

| Mode | What it does |
|---|---|
| **Agent** | Default mode. Plans, edits files, runs terminal commands, iterates autonomously. |
| **Plan** | Researches the codebase, asks clarifying questions, produces a plan before writing code. |
| **Debug** | Reproduces the failure, proposes a fix, re-runs, and offers Mark as Fixed. |
| **Multitask** | Splits a request into parallel sub-tasks run by separate agents (Module 5). Leave it alone for now. |
| **Ask** | Read-only. Answers questions without making any changes to files. |

You can switch modes three ways: pick one from this dropdown, press `Shift+Tab` to cycle through them, or type the mode as a slash command (`/ask`, `/plan`, `/debug`). After cycling, hover the icon or open the dropdown to read the mode name.

Every **new** conversation starts in Agent mode, whatever mode the previous one was in. If a step says Ask mode, switch after clicking **+**.
</details>

3. Close the dropdown without changing anything. The current mode is most likely **Agent**.

4. Look at the picker to the right of ∞. It reads something like "High Fast". That is effort and speed, not a model; click it and read the **Model** row if you want to know which model is answering. Leave the default for this lab.

---

### Task 1.2: Run the same prompt in Ask mode, then Agent mode

You will send one prompt twice: once in Ask mode, once in Agent mode, each in its own conversation, and compare what each mode does with it.

1. Click **+** to start a new conversation, then switch it to **Ask** mode (∞ dropdown, or type `/ask`).

2. Type the following prompt exactly and press Enter:

   ```
   Look at src/ingest.py in this project.
   I need it to meet professional Python standards.
   ```

3. Read the full response. Ask mode is read-only: it can only propose, and no files have changed.

   Above the answer there is a collapsed line such as **Explored 3 files**. Click it. It lists what the agent read before answering; that list is how you check what an answer was based on.

4. **Before you continue, note:**

   > What did Ask mode propose? Which functions did it single out?

5. Click **+** to start another new conversation. It opens in **Agent** mode; confirm the picker says Agent.

6. Send the identical prompt from step 2 and press Enter.

7. Watch what happens. Agent mode will most likely begin making changes to the file. Wait for it to finish.

8. Look at the **change summary at the bottom of the chat panel**. It lists `ingest.py` with the number of lines added and removed, and three buttons: **Undo**, **Keep**, and **Review**.

9. Click **Review** to see the diff. Read it, but do not accept anything.

10. Click **Undo**. The button changes to **Confirm**; click it. You are not ready to accept agent changes yet.

<details open>
<summary>What you should see</summary>

The change is already on disk before you click anything. Cursor writes the agent's edits immediately; **Keep** means "stop tracking this as pending" and **Undo** is what reverses it. Nothing is highlighted in the editor until the changed file is open.

**Ask mode** should have returned a proposal: what it would change in `src/ingest.py` and why (typically null handling on critical fields, error handling, and logging gaps), without touching any file.

**Agent mode** should have started editing `src/ingest.py` straight away, applying changes based on its judgment of what "professional Python standards" means. The instruction is the same; the mode decides whether it acts.

The key observation: Ask mode is structurally read-only. Agent mode acts. The mode discipline this course teaches, explore with Ask, then switch to Agent when you are ready, exists because of this difference.

If Agent mode also only described changes without editing, check the wording: a prompt phrased as a question ("What would you change?") invites advice even in Agent mode. Tell it what you need and it acts.
</details>

11. **Before you continue, note:**

    > What did Agent mode do differently from Ask mode? Did files change? What did the agent attempt?

---

## Task 2: Build the DE standards rules file

### Task 2.0: Capture the "before"

Before you write any rules, record what the agent produces without them. You compare against this in Task 2.3.

1. Click **+** for a new conversation. It is in Agent mode.

2. Send:

   ```
   Write a Python function that reads a list of log file paths
   and counts how many times each IP address appears across all files.
   ```

3. Read the output. Leave this conversation open.

4. If the agent offered to create a file, click **Undo** in the change summary and then **Confirm**; the code in the chat is all you need.

---

### Task 2.1: Understand the file you are about to complete

The rules file at `.cursor/rules/de-standards.mdc` was copied in by the loader in Task 0. It exists but is empty except for the frontmatter header.

1. In the Explorer panel, double-click `.cursor/rules/de-standards.mdc` to open it.

2. Read the frontmatter at the top of the file:

   ```yaml
   ---
   description: DE team coding standards for Python pipeline development
   alwaysApply: true
   ---
   ```

<details open>
<summary>What you should see</summary>

The `alwaysApply: true` setting means every agent conversation in this project will include these rules automatically. You do not need to reference the file in each prompt.

Above the text, Cursor shows a dropdown (Always Apply / Apply Intelligently / Apply to Specific Files / Apply Manually) and a description box. Those are the same `alwaysApply` and `description` values shown as a form; change either one and the other follows.

**Important:** The file must have the `.mdc` extension. A file named `de-standards.md` in the same directory is silently ignored by Cursor. The extension is not optional. A file with the right extension shows the dropdown; a `.md` file does not.
</details>

---

### Task 2.2: Add the six DE coding standards

The six team standards are listed below as one block. Read them once as a set before adding them.

1. Copy the whole block below and paste it into `de-standards.mdc` on the line after the closing `---` of the frontmatter:

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

   The six paragraphs are, in order: type hints, logging, file handling, null safety, counting patterns, Perl conversion. Each is written as a direct instruction to the agent, not a policy description; that is the form rules should take.

2. Confirm the file is saved: with Auto Save on, the tab shows no dot. If you skipped Auto Save, press `Ctrl+S` (Windows) or `Cmd+S` (Mac).

<details open>
<summary>What you should see</summary>

The file now has the four frontmatter lines, a blank line, and the six paragraphs. The dropdown above the text still reads **Always Apply**. Nothing else changes; rules take effect in the next new conversation.
</details>

---

### Task 2.3: Verify the rules change agent output

1. Click **+** for a new conversation (Agent mode).

2. Send the same prompt as Task 2.0:

   ```
   Write a Python function that reads a list of log file paths
   and counts how many times each IP address appears across all files.
   ```

3. Click the **Explored N files** line above the answer. `de-standards.mdc` should be the first thing the agent read, before any code. That is the rule loading.

4. Read the output and compare it with the Task 2.0 conversation. With `de-standards.mdc` active and `alwaysApply: true` set, the output should include all of the following:

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

5. If the agent created any files, click **Undo** in the change summary and then **Confirm**. Nothing from Task 2 is kept.

6. **Before you continue, note:**

   > What specific differences do you observe compared to the Task 2.0 output, produced without the rules file? Name at least two concrete differences in the code.

---

## Task 3: Read and extend the Perl-to-Python rules file

### Task 3.1: Open and read the file

The starter files include a pre-built `perl-to-python.mdc` in `.cursor/rules/`.

1. In the Explorer panel, double-click `.cursor/rules/perl-to-python.mdc` to open it.

2. Read the frontmatter first. Note the `globs` field: this file activates automatically for `*.pl` and `*.py` files, but not for every conversation. This is different from `de-standards.mdc`, which uses `alwaysApply: true`. The dropdown above the text reads **Apply to Specific Files** and shows the two patterns.

3. Read each rule in the file body.

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

4. **Before you continue, note:**

   > Which rule in `perl-to-python.mdc` covers something you were not expecting? Or: what rule do you think is missing?

---

### Task 3.2: Add one rule based on your team's conventions

1. Below the last existing rule in `perl-to-python.mdc`, add one new rule that covers a Python pattern your team uses that is not already in the file.

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

2. Confirm the file is saved (no dot on the tab).

3. Click **+** for a new conversation (Agent mode).

4. Type `@`, choose **Files & Folders**, and pick `perl/ingest.pl` so it becomes a tag in the message.

5. After the tag, type and send:

   ```
   Review this Perl file and tell me what the key differences will be in the Python equivalent.
   ```

   Notice that the prompt does not mention the rules file. It does not need to: `perl-to-python.mdc` applies to any conversation that has a `.pl` file attached.

6. Read the response. It should mention your new rule alongside the existing ones.

<details>
<summary>What to do if your rule does not appear in the response</summary>

1. Confirm the file is saved.
2. Confirm the frontmatter `globs` field includes `"**/*.pl"`.
3. Confirm you attached `perl/ingest.pl` as a tag; the globs activation requires the agent to be working with a matching file.
4. Try attaching the rule file explicitly: type `@`, choose `.cursor/rules/perl-to-python.mdc`.
</details>

---

## Task 4: Build the pipeline-review skill

### Task 4.1: Create the skill using /create-skill

1. Click **+** for a new conversation (Agent mode).

2. Type `/` and choose **create-skill** from the list. It turns into a highlighted tag. A pasted `/create-skill` is just text and does nothing; type the slash.

3. After the tag, paste the following and press Enter:

   ```
   Create a new project skill named pipeline-review.
   It reviews Python pipeline code against DE team standards.
   Check for: schema drift handling, null safety on critical fields, idempotency,
   logging completeness, and type hint coverage.
   Flag each issue as Critical, Warning, or Informational.
   Produce a structured review summary grouped by severity.
   ```

   If the agent says it is "recovering" or "rebuilding" an earlier skill, it found one in the repository's history. Let it finish; Task 4.2 checks the file it produced, and if the five criteria are there the result is the same.

4. Cursor opens a **Questions** dialog. Answer each question and click **Continue**. The questions, their order, and the option letters vary from run to run; read the options rather than the letters.

<details open>
<summary>What questions to expect and how to answer them</summary>

The questions are dynamic; a specific description produces fewer questions. You will always see at least the storage location question:

**Where should this skill be stored?**
- Project (`.cursor/skills/`), this repo only, shared with anyone who clones it (usually marked Recommended)
- Personal (your user Agent Store), available in every project, on every machine you sign in on
- Other

**Choose the option that says Project (`.cursor/skills/`).** This stores the skill in the repository so every team member has access to it after cloning.

If Cursor asks additional questions about the skill name or description, answer them specifically. The more detail you provide, the better the generated skill body will be.
</details>

---

### Task 4.2: Inspect and verify the skill file

1. In the Explorer panel, open `.cursor/skills/pipeline-review/SKILL.md`.

2. Confirm the file has YAML frontmatter with at least a `name` field and a `description` field.

3. Read the skill body. Confirm it covers all five review criteria:

   - [ ] Schema drift handling
   - [ ] Null safety on critical fields
   - [ ] Idempotency
   - [ ] Logging completeness
   - [ ] Type hint coverage

4. If any criterion is missing, add it as a numbered item in the skill body. Confirm the file is saved.

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

### Task 4.3: Invoke with / and observe the output

1. Click **+** for a new conversation (Agent mode).

2. Type `/`, choose **pipeline-review** from the list, and press Enter.

3. If it asks what to review, type the line below and press Enter; otherwise it reviews `src/` on its own:

   ```
   Review src/ingest.py
   ```

4. Read the structured output. It should be grouped by severity: Critical, Warning, Informational, with a file and line for each finding and a closing verdict. Notice that a rubric-driven review finds concrete issues in the same file that an open-ended question in Task 1.2 may have called "already in good shape".

---

### Task 4.4: Invoke with @ and compare

1. Click **+** for another new conversation (Agent mode).

2. Type `@.cursor/skills/pipeline` in the chat input and choose the entry whose path starts with `.cursor/skills/` (hover the tag to see the full path). This attaches the skill's `SKILL.md` as a file; Cursor has no separate skills category in the `@` menu.

3. After the tag, type this message and press Enter:

   ```
   Rewrite resolve_figis in src/ingest.py so that it would pass
   the attached pipeline-review criteria with no Critical findings.
   Show me the diff before applying it.
   ```

4. Read the response. If the agent applied a change, click **Review** in the change summary to see it, then **Undo** and **Confirm**; Task 5 is where you make changes on purpose.

5. **Before you continue, note:**

   > What is the specific behavioral difference between `/pipeline-review` and `@pipeline-review`? Describe what each one did differently in your own words.

<details open>
<summary>The expected difference</summary>

**`/pipeline-review`** runs the skill's procedure and produces its report. You are handing control to the skill.

**`@pipeline-review`** hands the agent the criteria as reference and lets you ask for something the skill was never written to do; here, to write code that satisfies the rubric. You are keeping control and using the skill as an input.

Use `/` to get the report. Use `@` when the rubric is an input to a different task.
</details>

---

## Task 5: Apply the integrating workflow

### Task 5.1: Explore first in Ask mode

1. Click **+** for a new conversation and switch it to **Ask** mode.

2. Send the following prompt and press Enter:

   ```
   Look at src/ingest.py. Identify the single function that most needs improvement
   against our team standards. Name the function, describe what is wrong with it,
   and tell me exactly what you would change.
   ```

3. Read the full response.

4. **Before switching to Agent mode, be able to say in one sentence what the function does and why the suggested change makes it better.**

   > This is the explore-before-changing gate. If you cannot say it, you are not ready to change it.

<details>
<summary>Why this gate matters</summary>

The explore-before-changing discipline is the professional habit this course builds on. The agent is faster at execution than any human. The human advantage is judgment about what to execute.

If you cannot describe in one sentence what the function does and why the change is an improvement, you do not yet understand what you are about to change. Stay in Ask mode and ask more questions before proceeding.
</details>

---

### Task 5.2: Switch to Agent mode and execute

1. Stay in the same conversation. Switch the mode picker to **Agent** (the ∞ dropdown, `Shift+Tab`, or `/agent`). The agent keeps everything it just told you, so you do not need to name the function again.

2. Send:

   ```
   Apply the improvements you described to that function in src/ingest.py,
   following the standards in our .cursor/rules/ files.
   ```

3. Watch the agent work. It may run `pytest` on its own and report the result; that is expected.

4. When the agent finishes, click **Review** in the change summary at the bottom of the chat and examine the diff before accepting.

<details open>
<summary>What to look for in the diff</summary>

The diff should show changes corresponding to the rules in `de-standards.mdc`:

- Type hints added to all function arguments and the return type
- `pathlib.Path` replacing any `os.path` or raw string paths
- `collections.Counter` replacing any manual dict counting
- `logger.info` calls added at function entry and exit
- `None` checks added on critical fields

If the diff shows changes that are not explained by your rules files, read each one and ask the agent to explain before accepting.
</details>

5. Accept using **Keep** only after reviewing every changed line.

6. In the same conversation, type `/`, choose **pipeline-review**, and after the tag type and send:

   ```
   Review the function you just changed in src/ingest.py and report the remaining issues.
   ```

7. **Before you continue, note:**

   > What specific changes did the agent make? Which of the de-standards.mdc rules are visible in the diff? What did /pipeline-review report as remaining issues?

---

### Task 5.3: Capture learning as a rule

1. If the `/pipeline-review` skill flagged anything as Critical or Warning that your `de-standards.mdc` file does not already cover, open `de-standards.mdc` now.

2. Add one new rule addressing the gap. Write it as a direct instruction to the agent.

3. Confirm the file is saved.

> If the pipeline-review found nothing that de-standards.mdc did not already cover, your rules file is well-calibrated for this function. Note that in the debrief; it is a valid and good outcome.

---

## Lab Debrief

Write answers to these prompts before the room debrief begins. You will share one answer with the group.

---

**Question 1**

In Task 1.2 you ran the same prompt in Ask mode and Agent mode. What was the most significant behavioral difference you observed? Why does that difference matter for the Perl conversion work in Lab 2?

---

**Question 2**

In Tasks 2.0 and 2.3 you ran the same prompt without and with `de-standards.mdc`. What specific code construct changed? Name the before and after explicitly.

---

**Question 3**

In Task 4.4 you invoked `/pipeline-review` and also used `@pipeline-review`. In your own words, when would you use each invocation method in your daily work?

---

**Question 4**

In Task 3.2 you added a rule to `perl-to-python.mdc`. What rule did you add? Why does your team need it and why was it not already in the file?
