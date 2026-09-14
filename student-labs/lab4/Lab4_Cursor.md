# Lab 4: Pipeline Monitoring and CI/CD Gate Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro or Teams plan)
**Duration:** 75 minutes
**Day:** Day 2, following Modules 5 and 6

---

## Prerequisites

- [ ] Modules 5 and 6 lectures completed
- [ ] Lab 3 completed, or Lab 4 starter files loaded (see Step 0)
- [ ] The repository's `lab-workspace` folder open in the Cursor IDE, with the venv active in the terminal
- [ ] pytest accessible from the terminal
- [ ] Optional, for Part 6.2 only: a fork of the repo under your own GitHub account, linked at `cursor.com/dashboard` with the Cursor GitHub app installed

---

## Lab Overview

Your pipeline runs overnight. Your on-call engineer arrives each morning to a directory of Airflow failure logs with no clear starting point. Build an observability agent that generates a prioritized incident briefing, apply Debug mode to the top failure, implement a CI/CD gate agent with deterministic PASS/FAIL/ESCALATE output, add schema drift detection, and implement an audit log that records every agent decision.

This is the capstone lab. It applies content from Chapters 3 through 6 in one integrated build.

**What you will produce:**
- A morning incident briefing agent with severity-sorted output
- A Debug mode investigation of the top failure with a two-sentence root cause summary
- A CI/CD gate agent with deterministic PASS/FAIL/ESCALATE decisions
- Schema drift detection integrated into the gate decision
- `audit/agent_decisions.jsonl` with a record for every agent decision in this lab

---

## Step 0: Load Starter Files

Run this before anything else, whether or not you completed Lab 3. It resets the workspace to the Lab 4 starting point, including the `audit/` folder this lab writes to.

Open a terminal inside Cursor (menu **Terminal → New Terminal**; make sure the prompt starts with `(venv)`). If you are on a `pr/` branch from Lab 3, go back to `main` first. Commit anything outstanding, then run from `lab-workspace/` (the folder open in the editor; a new terminal starts there):

```bash
git checkout main
python lab.py start 4
python lab.py status
git add -A && git commit -m "Lab 4 start state"
pytest tests/ -q
ls src/ audit/
```

<details>
<summary>Expected output</summary>

`lab.py status` shows `lab4 … <- matches`. All tests pass (about 42). `src/` contains `__init__.py`, `figi_client.py`, `ingest.py`, `transform.py`, `validate.py`. `audit/agent_decisions.jsonl` exists and contains one sample record showing the correct format.

Open `audit/agent_decisions.jsonl` in the editor now and leave the tab open; you add records to it by hand in Parts 1 and 2. Confirm **File → Auto Save** is on.
</details>

---

## Part 1: Morning Incident Briefing Agent

### Step 1.1: Examine the log files

Open a terminal. List and preview the overnight failure logs:

```powershell
ls logs\
Get-Content logs\failure_001.log -Head 20
```

**macOS/Linux:**
```bash
ls logs/
head -20 logs/failure_001.log
```

Note the four failure types represented across the log files: `schema_drift`, `null_rate_spike`, `timeout`, `dependency_failure`.

---

### Step 1.2: Build the briefing agent

Open a new Agent mode conversation. Send:

```
You are a pipeline observability agent. The log files are in the logs/ directory. Read each file directly.

For each failure determine: failure_type (schema_drift / null_rate_spike / timeout / dependency_failure / unknown); severity (Critical / Warning / Informational); affected_stage (which pipeline stage failed); recommended_action (one specific actionable next step); confidence (High / Medium / Low).

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

### Debug mode entry point
[one paragraph bug description for the highest-severity failure, ready to paste directly into Debug mode]
```

Press Enter. The agent reads the four files itself. Read the full briefing before continuing. The severity split is the model's judgment; a typical result is one Critical, two Warning, one Informational, with the schema drift on top.

**Time yourself:** from pressing Enter to knowing what to fix first should be under five minutes.

<details>
<summary>What to do if the briefing takes more than five minutes to read</summary>

The recommended action for each finding is too long or too vague. Add this constraint to your instruction set and re-run:

```
Each recommended action must be a single sentence starting with a verb. Maximum 20 words. If you cannot describe the action in 20 words, the action is not specific enough.
```
</details>

---

### Step 1.3: Add the briefing decision to the audit log

Open `audit/agent_decisions.jsonl`. Append a record for the briefing agent. Fill in the values from your actual session:

```json
{"agent": "morning_briefing", "timestamp": "[ISO 8601]", "inputs_reviewed": ["logs/failure_001.log", "logs/failure_002.log", "logs/failure_003.log", "logs/failure_004.log"], "decision": "Briefing generated: [X] Critical, [Y] Warning, [Z] Informational", "confidence": "High", "human_review_triggered": false, "model_used": "[model name from the model picker, e.g. Cursor Grok 4.6 High Fast]"}
```

The whole record is one line. Press **Enter** after it so the file ends with a newline: the gate agent in Part 3 appends to the end of the file, and without that newline its first record is glued onto yours. Auto Save saves the file.

---

## Part 2: Debug Mode Investigation

### Step 2.1: Switch the same conversation to Debug mode

Stay in the briefing conversation. Open the mode picker (the ∞ dropdown, `Shift+Tab`, or `/debug`) and choose **Debug**.

Send the **Debug mode entry point** paragraph from the end of your briefing, followed by these three lines with the placeholders filled in from the briefing:

```
[paste the Debug mode entry point paragraph here]

To reproduce: run the failed pipeline stage against data/sample_input.csv
Expected: [what a successful run produces]
Actual: [what the failure log shows]
```

---

### Step 2.2: Follow the Debug mode workflow

Debug mode reads the report and tries to reproduce the failure (it may ask you how, or run the stage itself), proposes a fix and applies it on disk, re-runs, and offers **Mark as Fixed**.

Read everything it says before you click anything. This failure came from an overnight Airflow run, and the log names things that may not exist in this repository. Watch for one of three outcomes:

- It reproduces the failure and fixes the line that raised it. Read the explanation, then Keep.
- It tells you the failure cannot be reproduced here and asks what to do. Answer: `The DAG is not in this repo. Using the log as evidence, name the function in src/ that would raise this error and propose the smallest fix.`
- It proves the failure cannot be reproduced and **proposes a fix anyway**. Do not Keep a change to code that is not failing. Click **Undo** in the change summary.

> **If you cannot explain why the proposed fix works, or it cannot show you the line that raises the error:** do not accept it. Ask Debug mode to explain the root cause and the fix in plain language first. A fix for a failure it could not reproduce is a guess.

---

### Step 2.3: Write and save the root cause summary

Before moving to Part 3, write a two-sentence summary:

```
Root cause: [what went wrong and why, or "not reproducible in this repo" and what the log shows]
Fix applied: [what was changed and how it prevents recurrence, or "none" and why you rejected the proposal]
```

Save this summary. It goes into the audit log in Part 5.

---

### Step 2.4: Add the Debug investigation to the audit log

Append a record to `audit/agent_decisions.jsonl` (one line, then press Enter so the file ends with a newline):

```json
{"agent": "debug_mode_investigation", "timestamp": "[ISO 8601]", "inputs_reviewed": ["logs/[top failure log]", "src/[affected file]"], "decision": "[your two-sentence root cause summary]", "confidence": "High", "human_review_triggered": [true if you rejected the fix], "model_used": "[model name]"}
```

---

## Part 3: CI/CD Gate Agent

### Step 3.1: Read the metrics file

Open `metrics/quality_metrics.json`. Note the three named run objects: `clean_run`, `soft_breach`, `critical_failure`. Note the metric names, values, and threshold fields across all three runs.

---

### Step 3.2: Build the gate agent

Open a new Agent mode conversation. Send:

```
You are a CI/CD quality gate agent.

Read metrics/quality_metrics.json. Evaluate each metric against its defined threshold. A metric breaches its threshold when it is above a maximum or below a minimum.

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

After producing each decision, append one record to audit/agent_decisions.jsonl with these fields: agent, timestamp, inputs_reviewed, decision, confidence, human_review_triggered (true if ESCALATE), model_used. Append only. Do not rewrite or reformat the existing file. If the file does not end with a newline, add one before appending.
```

The agent may evaluate all three runs straight away, or wait for you to name one. Either is fine. It usually appends the audit records with a short terminal command rather than the file editor, so you may not see a Keep button.

---

### Step 3.3: Test all three scenarios

If the agent has not already evaluated all three runs, send each of these in the same conversation:

```
Evaluate the clean_run metrics.
```

Verify decision is **PASS**.

```
Evaluate the soft_breach metrics.
```

Verify decision is **ESCALATE**.

```
Evaluate the critical_failure metrics.
```

Verify decision is **FAIL**.

---

### Step 3.4: Test decision consistency

Run the `critical_failure` evaluation a second time without changing anything:

```
Evaluate the critical_failure metrics.
```

The decision and violations list must be identical between runs (timestamps will differ).

<details>
<summary>What to do if the decision differs between runs</summary>

The gate agent is exercising model judgment rather than applying deterministic rules. Add this to your instruction set:

```
The decision logic is deterministic. Apply the rules in the exact order listed above. Do not exercise judgment about whether to upgrade or downgrade a decision based on any additional context.
```

Re-run the critical_failure evaluation twice. Both must produce FAIL with identical violations.
</details>

Check that `audit/agent_decisions.jsonl` has a new record for each evaluation run: one per scenario plus the re-run. Confirm the file is still valid JSON Lines and your hand-written records are untouched:

```bash
wc -l audit/agent_decisions.jsonl
python -c "import json; [json.loads(l) for l in open('audit/agent_decisions.jsonl') if l.strip()]; print('valid JSONL')"
```

If two records share a line, a hand-written record was missing its trailing newline. Fix the line break in the editor and re-run the check.

---

## Part 4: Schema Drift Detection

### Step 4.1: Read the registered schema

Open `schemas/expected_schema.json`. Note the field names, data types, and which fields are required.

---

### Step 4.2: Extend the gate agent

In the gate agent conversation, send:

```
Also check for schema drift. Compare the incoming data schema (read from the first row of data/sample_input.csv) against the registered schema in schemas/expected_schema.json.

Classify each difference:
- Breaking (required column removed, type incompatibly changed, required field made nullable): add schema_drift_breaking to violations, severity=Critical. If any breaking drift: decision = FAIL regardless of other metrics.
- Non-breaking (new column, widened type, optional field added or absent from the input): add schema_drift_non_breaking to violations, severity=Warning.
- Informational (metadata only): note in rationale only.

Run the full gate check including schema drift against the critical_failure metrics.
```

Verify the output includes both quality metric violations and schema drift findings. The input file lacks three optional columns (`figi`, `lookup_count`, `exchange_rank`); expect them reported as non-breaking, and the decision to stay FAIL on the metrics.

---

## Part 5: Audit Log Completion

### Step 5.1: Confirm the audit log is complete

Open `audit/agent_decisions.jsonl`. Confirm it contains records for:

- [ ] The morning briefing agent (added manually in Part 1)
- [ ] The Debug mode investigation (added manually in Part 2)
- [ ] Each CI/CD gate evaluation (appended automatically by the gate agent in Part 3)

<details>
<summary>Expected audit log structure</summary>

Each line is a complete JSON object. The file should look like this:

```jsonl
{"agent": "morning_briefing", "timestamp": "2026-08-28T07:00:00Z", "inputs_reviewed": ["logs/failure_001.log", "logs/failure_002.log", "logs/failure_003.log", "logs/failure_004.log"], "decision": "Briefing generated: 1 Critical, 2 Warning, 1 Informational", "confidence": "High", "human_review_triggered": false, "model_used": "Cursor Grok 4.6 High Fast"}
{"agent": "debug_mode_investigation", "timestamp": "2026-08-28T07:15:00Z", "inputs_reviewed": ["logs/failure_001.log", "src/validate.py"], "decision": "Root cause: null rate on exchange_code exceeded threshold due to upstream schema change at 02:14 UTC. Fix applied: added explicit None check before the transform step.", "confidence": "High", "human_review_triggered": false, "model_used": "Cursor Grok 4.6 High Fast"}
{"agent": "cicd_gate", "timestamp": "2026-08-28T07:30:00Z", "inputs_reviewed": ["metrics/quality_metrics.json"], "decision": "FAIL", "confidence": "High", "human_review_triggered": false, "model_used": "Cursor Grok 4.6 High Fast"}
```
</details>

---

### Step 5.2: Commit the audit log

```powershell
git add audit\agent_decisions.jsonl
git commit -m "Add agent audit log for Lab 4 session"
```

**macOS/Linux:**
```bash
git add audit/agent_decisions.jsonl
git commit -m "Add agent audit log for Lab 4 session"
```

> **The audit log commit is the final mandatory step.** Do not skip it under time pressure. An agent system without a committed audit trail is not production-ready.

---

## Part 6: Cloud Agents Window (Optional)

Complete this part only if all of Parts 1 through 5 are finished. Step 6.1 works on any clone. Step 6.2 needs a repository you administer, linked in the Cursor dashboard at `cursor.com/dashboard` with the Cursor GitHub app installed; on the shared course repository, expect it to stop at the message quoted below, which is itself the lesson.

> **Do not attempt Cloud Agent tasks if `src/` requires Oracle database connectivity to run its tests.** Cloud Agent VMs cannot reach on-premises services. The Lab 4 starter files are designed to run without external connectivity.

---

### Step 6.1: Launch a parallel gate check

Open the Agents Window: click **Agents Window ↗** at the top right of the editor. (Multitask also works from the chat panel in the editor; the Agents Window is where you can watch several agents at once.)

Start a new conversation, type `/multitask` (or choose **Multitask** from the mode picker) and send:

```
Run the CI/CD gate check from metrics/quality_metrics.json for the soft_breach run only. Report the decision and violations. Do not write to any file.
```

Watch for **1 subagent running** under the message; click it and the subagent opens as its own tab with its own prompt, model and result. Return to the editor with **IDE ↗**. The task runs independently and should report ESCALATE with two warnings.

---

### Step 6.2: Hand off the briefing agent to /in-cloud

In the Agents Window, start a new conversation.

Type `/`, choose **in-cloud** from the Commands list, then the morning briefing task description. The Cloud Agent clones the repository, runs on its own VM, and reports back.

Monitor progress from the Agents Window.

<details>
<summary>What you will most likely see</summary>

On a repository that is not linked, the cloud task shows **Couldn't start** and the agent reports one of these:

```
The Cursor app needs to be installed on your repository.
To enable them, link this repo in the Cursor dashboard, install the Cursor GitHub app on <repo>, then run /in-cloud again.
```

```
Cloud agents need a linked git remote, and this workspace has none, so I can't start one here.
```

The first appears when the remote exists but is not linked; the second when there is no remote at all. Installing the Cursor GitHub app needs admin rights on the repository. If you cloned the course repository, you do not have them: read the message, note what it asks for, and return to the debrief. If you forked the repository to your own account, link the fork at `cursor.com/dashboard`, install the app, and retry.
</details>

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

In Part 2, did Debug mode reproduce the failure? If not, what did it do instead, and would you have kept its change? What does that tell you about accepting a fix for a failure the agent could not run?

---

**Question 2**

In Part 3, did the gate agent produce the same decision on consecutive runs for `critical_failure`? If not, what instruction change made it deterministic?

---

**Question 3**

The audit log was the last mandatory step. In a real deployment, when should the audit log be designed—before or after the agent is built? Why?

---

**Question 4**

Write one rule you will add to your team's `.cursor/rules/` file this week based on something this lab revealed that your current rules do not cover.

---

**Question 5**

Write one agent use case from your real DE work that you will scope and build in the next 30 days. Write the Layer 3 test answer: why can you not write a deterministic script for this?
