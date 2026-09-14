# ai-augmented-engineering

Sample pipeline repository for the **AI-Augmented Engineering for Data Engineers** course.

> This repository is for course delivery only. Do not use in production.

---

## What This Is

A three-stage market data pipeline in Perl (legacy) and Python (conversion target),
used across four hands-on labs to practise AI-augmented engineering with Cursor and GitHub Copilot Enterprise.

## Quick Start

Do this once, before Lab 1. Everything here is what the labs assume is already in place.

```bash
git clone https://github.com/roitraining/ai-augmented-engineering.git
cd ai-augmented-engineering
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows PowerShell
pip install -r requirements.txt
pytest tests/ -q
```

Expect every test to pass. Then open the folder in Cursor (**File → Open Folder**), and if Cursor opens into the Agents Window (a chat screen with no editor), click **IDE ↗** at the top right to get the editor the labs use. Turn on **File → Auto Save**.

Every new terminal starts without the virtual environment: run `source venv/bin/activate` (Windows: `venv\Scripts\activate`) first. If the prompt does not begin with `(venv)`, `pytest` will not be found.

All tests use mock fixtures. The pipeline answers FIGI lookups from `data/figi_fixture.json` when no API key is set, so nothing here needs a network connection.

## Loading a Lab

Each lab's Step 0 starts from a known state. Run the loader from the repository root (the labs tell you which number):

```bash
python lab.py start 2       # reset the workspace to the start of Lab 2
python lab.py solution 2    # load the finished state of Lab 2
python lab.py status        # which lab state the workspace matches
python lab.py list          # what each lab state contains
```

`start N` removes every file a lab produces and extracts `lab-starters/labN.zip` into the workspace (add `--copilot` for `copilot-starters/`). It refuses to run while `git status` shows uncommitted changes, so commit or stash first, or pass `--force`. The finished state of Lab 4 is `lab-starters/solution.zip`. The starters are zipped so the editor's agent cannot read or search finished files ahead of time; instructors use `python lab.py unpack N` / `pack N` to edit them.

## Repository Structure

```
perl/           Perl source -- three-stage market data pipeline
src/            Python source -- idiomatic conversions of each Perl module
tests/          pytest test suites for all Python modules
data/           Sample market data CSV + pre-computed Perl reference output
docs/           Pipeline map and conversion plan (generated during labs)
logs/           Sample Airflow failure logs (Lab 4)
metrics/        Pipeline quality metrics JSON (Lab 4)
schemas/        Expected schema definition (Lab 4)
audit/          Agent decision audit log (Lab 4)
.cursor/        Cursor rules, skills, and Bugbot configuration
lab-starters/   Starter archives for each lab, one zip per lab state (Cursor path)
copilot-starters/ Starter archives for each lab (Copilot path)
instructor-notes/ PR branch specification and instructor reference
AGENTS.md       Cloud Agent onboarding guide
```

## Perl Prerequisites

```bash
# Debian/Ubuntu
sudo apt-get install perl libwww-perl libjson-perl

# macOS
brew install perl
cpan LWP::UserAgent JSON
```

## The Engineered Regression

All five exchange codes (US, GB, DE, FR, JP) each appear in exactly 4 of the 20 sample records.
With all counts tied, Perl's `reverse sort` and Python's `sorted(..., reverse=True)` produce different orderings.
All 20 output records differ in the `exchange_rank` column.
Tests pass. The parity check catches it.
