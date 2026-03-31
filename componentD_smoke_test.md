# Component D — Smoke Test (Validation Exercise)

## What is a smoke test?

A **smoke test** is the simplest form of testing: you turn the thing on and check whether smoke comes out.

In software, a smoke test answers one question:

> **Does the application start and perform its most basic functions without crashing?**

It is **not** thorough. It is **not** detailed. It is the **minimum bar** for “this build is not obviously broken.” Professional teams often run a smoke test after every meaningful code change.

### Why this matters

- Most deployed software is smoke-tested before it reaches end users.
- Smoke tests are **fast** and catch **catastrophic** problems early (crash on startup, blank page, broken main flow).
- Apps built with AI can still **fail** smoke tests: code may look fine but crash due to a missing import, wrong path, or a typo.

---

## Instructions

You will **systematically** verify that the app works and **document** what you tested and what happened. Casual clicking without writing it down does **not** count as a valid submission.

### Step 1: Start your app (if it is not already running)

```bash
streamlit run app.py
```

Confirm:

- The app opens in the browser.
- There are **no error messages** in the terminal that stop the server.
- The page loads without a red Streamlit error block (unless you are testing a failure on purpose).

**Notes:**

- Date / time tested: 2026-03-31 (local time, afternoon run)
- Browser: Chrome (localhost:8501)
- Terminal: server started successfully after activating `.venv`; non-blocking warnings observed (Streamlit `use_container_width` deprecation + pandas FutureWarning). No startup-stopping error remained.

---

### Step 2: Identify 3 features to test

Pick **three distinct features** your users can **see or interact with**. A feature might be:

- A **tab** (e.g. Submit Request vs Coordinator View)
- A **form** or **button** (submit request, save changes, send message)
- A **table** or **data editor**
- A **filter** or **text input** (team number, date range)
- A **metric** or **summary** area
- An **expander** or **inbox** section

**My three features:**

1. Submit Request form (student flow)
2. Coordinator View unlock + editable requests table
3. Coordinator Order conversation (message team + close/archive behavior)

---

### Step 3: Test each feature and record the results

For **each** feature, perform a **specific** action and record **expected** vs **actual** behavior.

---

## Test Recording

| # | Feature tested | Action you took | Expected result | Actual result | Pass / Fail |
|---|----------------|-----------------|-----------------|---------------|-------------|
| 1 | Submit Request form | Filled required fields (Team #, item, qty, price, link/alternate info path) and clicked **Submit request** | Request is accepted, success toast appears, and a new row is appended in `requests.csv` with calculated total | Form submitted without crash; success message displayed; request row appeared in app table and persisted to CSV | Pass |
| 2 | Coordinator View unlock + table edit | Entered coordinator password, opened dashboard, changed one request status/comment, then clicked **Save changes** | Coordinator panel unlocks; edited row saves; confirmation message shown; student update is queued when status/comment changes | Unlock succeeded; edited values persisted after rerun; save confirmation shown; notification/message side effects executed as designed | Pass |
| 3 | Order conversation (non-Approved only) | In Coordinator **Order conversation**, selected a Pending/Needs Info request, sent message, then closed ticket; verified Approved requests do not appear in this panel | Message is posted to thread; close moves ticket to Archive; Approved items are excluded from open conversation list | Message appeared in thread immediately; close moved item under Archive tab; Approved request stayed out of conversation list | Pass |

---

### Step 4: Screenshot

Take **one screenshot** of the running app that shows **at least one** of the features you tested.

**Attach or link the screenshot here:**

- File name or path: test_screeshot.png
- What the screenshot shows (one sentence): coordinator view

---

### Step 5: Fix any failures

If any test **failed**:

1. Copy the **error message** or describe the **unexpected** behavior.
2. Fix in code or ask your AI tool for help.
3. **Re-run** the same smoke steps and **update the table** (add a note like “Re-tested after fix: Pass”).

**Failures and fixes (fill in):**

| Feature # | What failed | Error or behavior | Fix summary | Re-test result |
|-----------|-------------|-------------------|-------------|----------------|
| N/A | No smoke-test failures in this run | N/A | N/A | All 3 features passed |

---

## Quality gate checklist (before submission)

Use this list before you submit Component D:

- [x] Smoke test **table** completed with **3** tested features
- [x] Any **failed** test is **fixed and re-tested**, **or** clearly **documented** with reason
- [x] **Screenshot** of the running app included (shows at least one tested feature)
- [x] **Accessibility baseline** recorded elsewhere (color contrast + semantic headings), e.g. `componentB_accessibility_check.md` or course template

---

## Optional: quick startup check (every time)

After pulling new code or changing dependencies:

```bash
source .venv/bin/activate   # or Windows equivalent
pip install -r requirements.txt
streamlit run app.py
```

If this fails, fix **before** deeper testing.
