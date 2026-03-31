# Part 3: Testing & Validation

## Edge cases

### Edge case 1: Resource open across midnight (hours span two calendar days)

**What we tested:** A resource with `hours_open` later than `hours_close` (e.g. `22:00` open, `06:00` close), simulating overnight availability.

**Why it matters:** If “open now” logic only checks `start <= current_time <= end` on the same calendar day, overnight hours are wrong: the space would show as closed when it should be open late at night or early morning. Handling wrap-around avoids false negatives for students relying on “Open right now only.”

**Outcome:** Confirmed the app treats overnight windows correctly (current time after open **or** before close).

---

### Edge case 2: Empty search with all filters at default

**What we tested:** Clear the search box, category = All, floor = Any, “Open right now only” unchecked, then Reset.

**Why it matters:** This is the baseline state. If the UI or filter logic mishandles empty strings (e.g. treating `""` as a substring match everywhere) or Reset does not fully sync `session_state`, users can see zero results or stale filters. Verifying the full list appears and pills show “none” keeps the main browse path trustworthy.

**Outcome:** All resources listed; active filters caption shows no unintended constraints.

---

## Assert statement (data integrity)

The following assert verifies that every resource in the in-memory list has the required keys and that categories and floors match the allowed vocabulary (catching typos or incomplete seed data at import time):

```python
ALLOWED_CATEGORIES = {"Study", "Maker", "Storage", "Print", "Other"}
ALLOWED_FLOORS = {"1F", "2F", "3F"}
REQUIRED_KEYS = {
    "name", "category", "floor", "hours_open", "hours_close",
    "description", "location_tip", "access_notes", "pro_tip", "tags",
}

for r in RESOURCES:
    assert REQUIRED_KEYS.issubset(r.keys()), f"Missing keys in resource: {r.get('name', r)}"
    assert r["category"] in ALLOWED_CATEGORIES, f"Bad category: {r['category']}"
    assert r["floor"] in ALLOWED_FLOORS, f"Bad floor: {r['floor']}"
    assert isinstance(r["tags"], list), f"tags must be a list for {r['name']}"
```

---

## Prompt log

### Initial prompt

> Under the current work directory, create a subfolder `app2` and build a Streamlit app called **GIX Wayfinder** for new GIX students to find campus resources. Store resources as a Python list of dictionaries in the script with keys: name, category, floor, hours, description, location_tip, access_notes, pro_tip. Add search, category dropdown, floor radio, “open now” checkbox, reset, AND filters, expander cards, session state, no CSV—single `app.py`.

### One refinement

> Add a **`tags` field** to each resource and include tags in the text search (name, description, tags). Show **active filter pills** so users can see what is applied.

**What changed:** Search scope expanded beyond name/description; data model gained `tags`; UI gained explicit “active filters” feedback.

**Why:** Students often search by informal words (“bike,” “quiet”) that appear in tags but not in the title. Pills reduce confusion when results look “wrong” because a hidden filter is still on.
