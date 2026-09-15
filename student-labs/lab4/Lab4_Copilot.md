# Lab 4: Pipeline Monitoring and CI/CD Gate Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** GitHub Copilot in VS Code
**Duration:** 75 minutes
**Day:** Day 2, following Modules 5 and 6

---

## Prerequisites

- [ ] Modules 5 and 6 lectures completed
- [ ] Lab 3 completed, or not; Task 0 loads the Lab 4 starting point either way
- [ ] The repository's `lab-workspace` folder open in VS Code with Copilot signed in, and the venv active in the terminal
- [ ] pytest accessible from the terminal
- [ ] Optional, for Task 6.2 only: a fork of the repo under your own GitHub account with the Copilot coding agent enabled

---

## Lab Overview

Your pipeline runs overnight. Your on-call engineer arrives each morning to a directory of Airflow failure logs with no clear starting point. Build an observability agent that generates a prioritized incident briefing, investigate the top failure evidence-first, implement a CI/CD gate agent with deterministic PASS/FAIL/ESCALATE output, add schema drift detection, and keep an audit log that records every agent decision.

**Copilot notes for this lab:** everything runs in Agent mode (the **Agent ▾** pill at the bottom left of the chat input). Copilot has no Debug mode; Task 2 uses the evidence-first prompt from Lab 2. Terminal commands the agent wants to run appear as an **Allow ▾** / **Skip** card; the gate agent appends to the audit file that way, so expect several cards in Task 3. Cursor's Agents Window and `/in-cloud` become the chat panel's full-screen **Sessions** view and the **Local ▾** run-target pill in Task 6.

This is the capstone lab. It applies content from Chapters 3 through 6 in one integrated build.

**What you will produce:**
- A morning incident briefing agent with severity-sorted output
- An evidence-first investigation of the top failure with a two-sentence root cause summary
- A CI/CD gate agent with deterministic PASS/FAIL/ESCALATE decisions
- Schema drift detection integrated into the gate decision
- `audit/agent_decisions.jsonl` with a record for every agent decision in this lab

**How this lab is written:** each Task has numbered steps. A numbered step is something you do. Text between steps explains what you are looking at; the boxes marked "What you should see" tell you what a correct result looks like. The agent's behaviour varies from run to run: it may ask questions before acting, act at once, or describe a change and wait for your go-ahead. If it asks, answer; if it waits, reply `Go ahead`. The steps describe the end state, not every turn of the conversation.

---

## Task 0: Load the starter files

Do this whether or not you completed Lab 3. It resets the workspace to the Lab 4 starting point, including the `audit/` folder this lab writes to.

1. Open a terminal inside VS Code: menu **Terminal → New Terminal**. It opens in `lab-workspace/`; every command in this lab runs from there.

2. Make sure the prompt starts with `(venv)`. If it does not, run `source venv/bin/activate` (Windows: `venv\Scripts\activate`).

3. Put away anything unfinished. Run `git status --short`; if it prints anything, commit on the branch you are on:

   ```bash
   git add -A
   git commit -m "Lab 3 checkpoint"
   ```

4. Go back to `main` (Lab 3 left you on a `pr/` branch):

   ```bash
   git checkout main
   ```

5. Load the Lab 4 starter files:

   ```bash
   python lab.py start 4
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
  lab3       ...
  lab4       23/23 files identical, 0 extra lab file(s) present  <- matches
  solution   ...
git: uncommitted changes present
```

Only the **lab4** line matters: `23/23 files identical` and `<- matches`. `git: uncommitted changes present` is normal here; step 7 clears it.
</details>

7. Create the branch this lab works on, then commit the starting state on it:

   ```bash
   git checkout -b lab4
   git add -A
   git commit -m "Lab 4 start state"
   ```

8. Confirm the tests pass and the working files are there:

   ```bash
   pytest tests/ -q
   ls src/ audit/
   ```

<details open>
<summary>What you should see</summary>

`42 passed`. `src/` contains `__init__.py`, `figi_client.py`, `ingest.py`, `transform.py`, `validate.py`. `audit/` contains `agent_decisions.jsonl`.
</details>

9. In the Explorer, open `audit/agent_decisions.jsonl` and leave the tab open. It holds one sample record showing the format; you add records to it by hand in Tasks 1 and 2. (An open file rides along as context in Copilot chats; that is fine here.)

10. Confirm **File → Auto Save** has a check mark next to it.

---

## Task 1: Morning incident briefing agent

### Task 1.1: Examine the log files

1. List and preview the overnight failure logs:

   ```bash
   ls logs/
   head -20 logs/failure_001.log
   ```

   (Windows: `Get-Content logs\failure_001.log -Head 20`.)

2. Open each of the four log files in the editor and skim them. Four failure types are represented: `schema_drift`, `null_rate_spike`, `timeout`, `dependency_failure`.

---

### Task 1.2: Build the briefing agent

1. Open the chat panel (**View → Chat**), click **+** (New Chat) at the top of it, and set the mode pill to **Agent**.

2. Send this prompt:

   ```
   You are a pipeline observability agent.
   The log files are in the logs/ directory. Read each file directly.

   For each failure determine:
   failure_type (schema_drift / null_rate_spike / timeout / dependency_failure / unknown);
   severity (Critical / Warning / Informational);
   affected_stage (which pipeline stage failed);
   recommended_action (one specific actionable next step);
   confidence (High / Medium / Low).

   Sort all failures by severity (Critical first), not by log timestamp.

   Output format:
   ## Morning Incident Briefing -- [date]

   ### CRITICAL
   [failure_type] | [affected_stage] | Confidence: [level]
   Recommended action: [specific action]

   ### WARNING
   [same format]

   ### INFORMATIONAL
   [same format]

   ### Investigation entry point
   [one paragraph bug description for the highest-severity failure,
   ready to paste into a debugging prompt]
   ```

3. Note the time you pressed Enter. The agent reads the four files itself.

4. Read the full briefing. Expand the **Completed N steps** line above it and check the **Read** pills for all four logs; if it read only some, send `Read all four files in logs/ and redo the briefing.` (If it asked to run `cat` or `ls` instead, click **Allow**.)

<details open>
<summary>What you should see</summary>

A briefing with the four failures sorted into severity sections and a final "Investigation entry point" paragraph. The severity split is the model's judgment; a typical result is one Critical, two Warning, one Informational, with the schema drift on top.

No change summary: the briefing agent writes nothing.

From pressing Enter to knowing what to fix first should be under five minutes. If it took longer because the recommended actions were long or vague, send this and read the re-run:

```
Each recommended action must be a single sentence starting with a verb. Maximum 20 words.
If you cannot describe the action in 20 words, the action is not specific enough.
```
</details>

---

### Task 1.3: Add the briefing decision to the audit log

1. In the `audit/agent_decisions.jsonl` tab, add this record on a new line at the end of the file, filling in the bracketed values from your session:

   ```json
   {"agent": "morning_briefing", "timestamp": "[ISO 8601]", "inputs_reviewed": ["logs/failure_001.log", "logs/failure_002.log", "logs/failure_003.log", "logs/failure_004.log"], "decision": "Briefing generated: [X] Critical, [Y] Warning, [Z] Informational", "confidence": "High", "human_review_triggered": false, "model_used": "[model name from the model picker, e.g. Cursor Grok 4.6 High Fast]"}
   ```

   The whole record is one line.

2. Press **Enter** after it so the file ends with a newline. The gate agent in Task 3 appends to the end of the file; without that newline its first record is glued onto yours. Auto Save saves the file.

---

## Task 2: Evidence-first investigation

### Task 2.1: Send the entry point with a reproduce-first instruction

1. Stay in the briefing chat, Agent mode.

2. Send the **Investigation entry point** paragraph from the end of your briefing, followed by these lines with the placeholders filled in from the briefing:

   ```
   [paste the investigation entry point paragraph here]

   To reproduce: run the failed pipeline stage against data/sample_input.csv
   Expected: [what a successful run produces]
   Actual: [what the failure log shows]

   Reproduce it first. Then tell me the root cause. Do not change any file yet.
   ```

3. Click **Allow** on the command cards as it runs the stage.

---

### Task 2.2: Decide what to do with the result

This failure came from an overnight Airflow run, and the log names things that may not exist in this repository. The agent will try to run the stage; what it reports next is the point of the Task.

1. Read everything it says before you type anything.

2. Identify which of three outcomes you got, and act on it:

   - It reproduces the failure and names the line that raises it. Send `Apply the smallest fix for that root cause.`, read the inline diff, then **Keep**.
   - It says the failure cannot be reproduced here and asks what to do. Send: `The DAG is not in this repo. Using the log as evidence, name the function in src/ that would raise this error and propose the smallest fix. Do not apply it.` Then read the proposal and decide as in the next line.
   - It reports that the failure cannot be reproduced and **changes the code anyway**. Do not Keep a change to code that is not failing. Click **Undo** in the change summary.

<details open>
<summary>What you should see</summary>

The third outcome is common on every agent: it runs `validate.py`, reports that the failure does not reproduce, and still writes a null-handling change (often with tests) into `src/`. The change summary lists two or three files. The "do not change any file yet" line in the prompt reduces this; it does not eliminate it.

If you cannot explain why a proposed fix works, or the agent cannot show you the line that raises the error, do not accept it. A fix for a failure it could not reproduce is a guess. Sending `Explain the root cause and the fix in plain language` first is always allowed.
</details>

---

### Task 2.3: Write the root cause summary

1. **Before you continue, note** a two-sentence summary; it goes into the audit log in the next step:

   > Root cause: [what went wrong and why, or "not reproducible in this repo" and what the log shows]
   > Fix applied: [what was changed and how it prevents recurrence, or "none" and why you rejected the proposal]

---

### Task 2.4: Add the investigation to the audit log

1. Add this record on a new line at the end of `audit/agent_decisions.jsonl`, then press **Enter** so the file ends with a newline:

   ```json
   {"agent": "debug_investigation", "timestamp": "[ISO 8601]", "inputs_reviewed": ["logs/[top failure log]", "src/[affected file]"], "decision": "[your two-sentence root cause summary]", "confidence": "High", "human_review_triggered": [true if you rejected the fix, otherwise false], "model_used": "[model name]"}
   ```

---

## Task 3: CI/CD gate agent

### Task 3.1: Read the metrics file

1. Open `metrics/quality_metrics.json` in the Explorer. Note the three named run objects, `clean_run`, `soft_breach` and `critical_failure`, and for each metric its value, threshold, and whether it is marked `critical_on_breach` or `warn_on_breach`.

---

### Task 3.2: Build the gate agent

1. Click **+** (New Chat), Agent mode.

2. Send this prompt:

   ```
   You are a CI/CD quality gate agent.

   Read metrics/quality_metrics.json. Evaluate each metric against its defined threshold.
   A metric breaches its threshold when it is above a maximum or below a minimum.

   Decision rules (apply in this exact order):
   - If any metric marked critical_on_breach breaches its threshold: decision = FAIL
   - If any metric marked warn_on_breach breaches its threshold: decision = ESCALATE
   - If all metrics are within threshold: decision = PASS

   Output exactly this structure:
   {
     "decision": "PASS" | "FAIL" | "ESCALATE",
     "metrics_evaluated": [list of metric names checked],
     "violations": [{metric, value, threshold, severity}],
     "rationale": "one sentence plain-language explanation",
     "timestamp": "ISO 8601 timestamp"
   }

   After the JSON, output a plain-language two-sentence version for the on-call engineer.

   After producing each decision, append one record to audit/agent_decisions.jsonl with these fields:
   agent, timestamp, inputs_reviewed, decision, confidence, human_review_triggered (true if ESCALATE), model_used.
   Append only. Do not rewrite or reformat the existing file.
   If the file does not end with a newline, add one before appending.
   ```

3. Read the response.

<details open>
<summary>What you should see</summary>

The agent may evaluate all three runs straight away, wait for you to name one, or ask whether it should write to the audit file. Either is fine; answer `Yes, append` if it asks. It usually appends the audit records with a short terminal command rather than the file editor, so you may not see a change summary; the `audit/agent_decisions.jsonl` tab updates instead. Each command comes as an **Allow ▾** / **Skip** card; click **Allow** (the ▾ can allow the same command for the rest of the session).
</details>

---

### Task 3.3: Test all three scenarios

1. If the agent has not already evaluated all three runs, send each of these in turn, in the same conversation, and check the decision after each:

   ```
   Evaluate the clean_run metrics.
   ```

   Decision **PASS**.

   ```
   Evaluate the soft_breach metrics.
   ```

   Decision **ESCALATE**.

   ```
   Evaluate the critical_failure metrics.
   ```

   Decision **FAIL**.

2. **Before you continue, note:**

   > Did all three decisions match? If one did not, which rule did the agent apply differently from the way you read it?

---

### Task 3.4: Test decision consistency

1. Run the `critical_failure` evaluation a second time without changing anything:

   ```
   Evaluate the critical_failure metrics.
   ```

2. Compare the two `critical_failure` outputs. The decision and the violations list must be identical (timestamps will differ).

<details open>
<summary>If the decision differs between runs</summary>

The gate agent is exercising judgment rather than applying deterministic rules. Send this, then run the `critical_failure` evaluation twice more; both must produce FAIL with identical violations:

```
The decision logic is deterministic. Apply the rules in the exact order listed above.
Do not exercise judgment about whether to upgrade or downgrade a decision based on any additional context.
```
</details>

3. Check the audit file:

   ```bash
   wc -l audit/agent_decisions.jsonl
   python -c "import json; [json.loads(l) for l in open('audit/agent_decisions.jsonl') if l.strip()]; print('valid JSONL')"
   ```

<details open>
<summary>What you should see</summary>

A line count of at least 7: the sample record, your two hand-written records, and one gate record per evaluation (three scenarios plus the re-run), plus any extra re-runs. Then `valid JSONL`.

If the second command fails with a JSON error, two records share a line: a hand-written record was missing its trailing newline. Put the line break in by hand in the editor and run the check again. Your hand-written records must be untouched otherwise.
</details>

---

## Task 4: Schema drift detection

### Task 4.1: Read the registered schema

1. Open `schemas/expected_schema.json` in the Explorer. Note the field names, data types, and which fields are required.

2. Open `data/sample_input.csv` and compare its header row with the schema. Three schema fields are not in the input: `figi`, `lookup_count`, `exchange_rank`. They are optional output fields.

---

### Task 4.2: Extend the gate agent

1. In the gate agent conversation, send:

   ```
   Also check for schema drift.
   Compare the incoming data schema (read from the first row of data/sample_input.csv)
   against the registered schema in schemas/expected_schema.json.

   Classify each difference:
   - Breaking (required column removed, type incompatibly changed, required field made nullable):
     add schema_drift_breaking to violations, severity=Critical.
     If any breaking drift: decision = FAIL regardless of other metrics.
   - Non-breaking (new column, widened type, optional field added or absent from the input):
     add schema_drift_non_breaking to violations, severity=Warning.
   - Informational (metadata only): note in rationale only.

   Run the full gate check including schema drift against the critical_failure metrics.
   ```

2. Read the output.

<details open>
<summary>What you should see</summary>

Both kinds of finding in one result: the `critical_failure` metric violations and the schema drift findings. The three absent optional columns are reported as non-breaking, and the decision stays FAIL on the metrics. One more gate record lands in the audit file.
</details>

---

## Task 5: Audit log completion

### Task 5.1: Confirm the audit log is complete

1. Open `audit/agent_decisions.jsonl` and confirm it contains records for:

   - [ ] The morning briefing agent (added by hand in Task 1)
   - [ ] The investigation (added by hand in Task 2)
   - [ ] Each CI/CD gate evaluation (appended by the gate agent in Tasks 3 and 4)

<details open>
<summary>What you should see</summary>

Each line is a complete JSON object, like this:

```jsonl
{"agent": "morning_briefing", "timestamp": "2026-08-28T07:00:00Z", "inputs_reviewed": ["logs/failure_001.log", "logs/failure_002.log", "logs/failure_003.log", "logs/failure_004.log"], "decision": "Briefing generated: 1 Critical, 2 Warning, 1 Informational", "confidence": "High", "human_review_triggered": false, "model_used": "Cursor Grok 4.6 High Fast"}
{"agent": "debug_investigation", "timestamp": "2026-08-28T07:15:00Z", "inputs_reviewed": ["logs/failure_001.log", "src/validate.py"], "decision": "Root cause: null rate on exchange_code exceeded threshold due to upstream schema change at 02:14 UTC. Fix applied: none; the failure does not reproduce in this repo and the proposed change was rejected.", "confidence": "High", "human_review_triggered": true, "model_used": "Cursor Grok 4.6 High Fast"}
{"agent": "cicd_gate", "timestamp": "2026-08-28T07:30:00Z", "inputs_reviewed": ["metrics/quality_metrics.json"], "decision": "FAIL", "confidence": "High", "human_review_triggered": false, "model_used": "Cursor Grok 4.6 High Fast"}
```
</details>

---

### Task 5.2: Commit the audit log

1. Commit:

   ```bash
   git add audit/agent_decisions.jsonl
   git commit -m "Add agent audit log for Lab 4 session"
   ```

   This commit is the final mandatory step. Do not skip it under time pressure: an agent system without a committed audit trail is not production-ready.

---

## Task 6: Sessions view and the cloud agent (optional)

Do this Task only if Tasks 1 through 5 are finished. Task 6.1 works on any clone. Task 6.2 stops at a dialog on the shared course repository, and reading that dialog is the lesson; only run it through on a fork you own.

Do not hand off work to a cloud agent when the code's tests need on-premises services (an Oracle database, say). The cloud agent cannot reach them. The Lab 4 starter files run without external connectivity.

### Task 6.1: See the day's agents in one place

1. Click the **maximize** icon in the chat panel header (next to the ✕). The chat fills the window and a **Sessions** column appears on the right: every chat from this lab, auto-titled, with the lines it changed ("+6 −5") and when it ran. This is the twin of Cursor's Agents Window.

2. Click the briefing session, then the gate-agent session. Each opens with its full transcript, including the **Completed N steps** traces and the command cards you allowed.

3. Click **New Session** and send, in Agent mode:

   ```
   Run the CI/CD gate check from metrics/quality_metrics.json for the soft_breach run only.
   Report the decision and violations. Do not write to any file.
   ```

4. Click the maximize icon again to return to the panel.

<details open>
<summary>What you should see</summary>

The new session runs independently of the others and reports ESCALATE with two warnings. Nothing is written: `git status --short` shows no new change. The Sessions list is also your audit trail for the day: which chat touched which files, in order.
</details>

---

### Task 6.2: Hand off the briefing agent to the cloud

1. Click **+** (New Session or New Chat), Agent mode, and paste the morning briefing prompt from Task 1.2 into the input without sending it.

2. Click the run-target pill (**Local ▾**) at the bottom of the input and read the menu: **Continue In: Local · Cloud · Copilot · Claude**. Hover **Cloud**: "Delegate tasks to the GitHub Copilot coding agent … works asynchronously in the cloud to implement changes and pull requests."

3. Choose **Cloud**. Read the dialog that appears.

<details open>
<summary>What you should see</summary>

A **Delegate to cloud agent** dialog: "Cloud agent works asynchronously to create a pull request with your requested changes. This chat's history will be summarized and appended to the pull request as context." It may add that the workspace has uncommitted changes and ask whether to push them, with **Commit Changes and Delegate** · **Delegate** · **Cancel**.

Click **Cancel**. On the shared course repository you cannot push a branch, so the handoff would fail, and even where it succeeds, every delegation opens a pull request on GitHub; that is the design (Cursor's `/in-cloud` runs on a VM and reports back to the editor instead). If you forked the repository to your own account and the Copilot coding agent is enabled there, you may **Delegate** and watch the PR appear on GitHub.
</details>

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

In Task 2, did the agent reproduce the failure? If not, what did it do instead, and would you have kept its change? What does that tell you about accepting a fix for a failure the agent could not run?

---

**Question 2**

In Task 3, did the gate agent produce the same decision on consecutive runs for `critical_failure`? If not, what instruction change made it deterministic?

---

**Question 3**

The audit log was the last mandatory step. In a real deployment, when should the audit log be designed, before or after the agent is built? Why?

---

**Question 4**

Write one instruction you will add to your team's `.github/copilot-instructions.md` this week based on something this lab revealed that your current instructions do not cover.

---

**Question 5**

Write one agent use case from your real DE work that you will scope and build in the next 30 days. Write the Layer 3 test answer: why can you not write a deterministic script for this?
