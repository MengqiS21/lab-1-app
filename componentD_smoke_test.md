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

**Notes (fill in):**

- Date / time tested:
- Browser:
- Terminal: any warnings? (paste or summarize)

---

### Step 2: Identify 3 features to test

Pick **three distinct features** your users can **see or interact with**. A feature might be:

- A **tab** (e.g. Submit Request vs Coordinator View)
- A **form** or **button** (submit request, save changes, send message)
- A **table** or **data editor**
- A **filter** or **text input** (team number, date range)
- A **metric** or **summary** area
- An **expander** or **inbox** section

**My three features (fill in):**

1. Feature 1:
2. Feature 2:
3. Feature 3:

---

### Step 3: Test each feature and record the results

For **each** feature, perform a **specific** action and record **expected** vs **actual** behavior.

---

## Recording template (copy and fill)

| # | Feature tested | Action you took | Expected result | Actual result | Pass / Fail |
|---|----------------|-----------------|-----------------|---------------|-------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

### Example rows (Purchase Request Manager — replace with your real test)

| # | Feature tested | Action you took | Expected result | Actual result | Pass / Fail |
|---|----------------|-----------------|-----------------|---------------|-------------|
| 1 | Submit Request form | Filled required fields and clicked Submit | New row in `requests.csv` and success message | | |
| 2 | Coordinator View | Entered password and unlocked | Dashboard and table visible | | |
| 3 | Team inbox | Entered team # and opened Order messages expander | Thread or empty state loads without error | | |

---

### Step 4: Screenshot

Take **one screenshot** of the running app that shows **at least one** of the features you tested.

**Attach or link the screenshot here:**

- File name or path:
- What the screenshot shows (one sentence):

---

### Step 5: Fix any failures

If any test **failed**:

1. Copy the **error message** or describe the **unexpected** behavior.
2. Fix in code or ask your AI tool for help.
3. **Re-run** the same smoke steps and **update the table** (add a note like “Re-tested after fix: Pass”).

**Failures and fixes (fill in):**

| Feature # | What failed | Error or behavior | Fix summary | Re-test result |
|-----------|-------------|-------------------|-------------|----------------|
| | | | | |

---

## Quality gate checklist (before submission)

Use this list before you submit Component D:

- [ ] Smoke test **table** completed with **3** tested features
- [ ] Any **failed** test is **fixed and re-tested**, **or** clearly **documented** with reason
- [ ] **Screenshot** of the running app included (shows at least one tested feature)
- [ ] **Accessibility baseline** recorded elsewhere (color contrast + semantic headings), e.g. `componentB_accessibility_check.md` or course template

---

## Optional: quick startup check (every time)

After pulling new code or changing dependencies:

```bash
source .venv/bin/activate   # or Windows equivalent
pip install -r requirements.txt
streamlit run app.py
```

If this fails, fix **before** deeper testing.
