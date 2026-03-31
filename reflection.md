# Reflection (Component B)

## What surprised you about AI-assisted coding? Was it easier or harder than you expected? What moment made you think "wow" or "wait, that is not right"?

AI-assisted coding felt **faster for scaffolding** than I expected: a whole Streamlit layout, CSV paths, and coordinator dashboard appeared in one pass, which was a “wow” moment for sheer speed. It was **harder than I expected** when the first version looked fine but broke at runtime—small framework rules (Streamlit reruns, widget keys, pandas dtypes) do not go away just because the code “looks” right. The clearest “wait, that is not right” moment was when totals did not update live and the coordinator table crashed on empty cells: the UI was there, but the behavior was wrong until we debugged like normal engineering.

## What did the AI get wrong? Did you encounter errors, unexpected behavior, or code that did not match what you asked for? How did you fix it?

The AI often **matched the spec on paper** but missed Streamlit and pandas details. Examples from this project: putting fields in `st.form` made the **total price stale** until we switched to a flow that reruns when inputs change; **empty coordinator comments** were read as `NaN` and broke the data editor until we normalized columns with `fillna("")` and string types; and once **`st.session_state` was updated after a widget was created**, Streamlit threw an error—fixed by pre-filling through a separate key before the widget runs. In each case the fix was to **read the error, reason about Streamlit’s execution model**, and patch the smallest part of the code rather than blindly accepting the next AI suggestion.

## Could you explain your code? Pick one section of your app — walk a classmate through what it does, line by line, without looking at Cursor’s explanation.

**Section:** `set_conversation_closed` in `app.py` (closes or reopens the order conversation for one purchase request).

```python
def set_conversation_closed(request_id: int, closed: bool) -> None:
    df = load_requests()
    mask = df["id"].astype(int) == int(request_id)
    df.loc[mask, "conversation_closed"] = 1 if closed else 0
    save_requests(df)
```

1. **`def set_conversation_closed(...)`** — Defines a function that takes which request (`request_id`) and whether the thread should be closed (`True`) or reopened (`False`).
2. **`df = load_requests()`** — Loads the current `requests.csv` into a pandas DataFrame so we can change one row.
3. **`mask = ...`** — Builds a True/False column that is `True` only on the row whose `id` matches this request (IDs are compared as integers so `"3"` and `3` behave consistently).
4. **`df.loc[mask, "conversation_closed"] = ...`** — For those matching rows only, sets the `conversation_closed` column to `1` (closed) or `0` (open). The rest of the table is untouched.
5. **`save_requests(df)`** — Writes the updated DataFrame back to disk so the next page load and the coordinator view see the new state.

Together, this is the **single source of truth** for “is this ticket still in the active conversation list or in the archive?”

## What did you learn from the interview? How did talking to Dorothy (Program Coordinator, Student Purchasing) change what you built, compared to what you might have built without that conversation?

From the interview I learned that the real pain is not “a form exists,” but **keeping everything in one place with enough detail**—Dorothy described wanting to track **when and under what condition** things happen, moving off ad hoc Excel and Google Forms, and needing **all information at once** with **less back-and-forth** with students. Without that conversation I might have built a minimal submit-only page. With it, the app emphasizes a **single coordinator dashboard**, **structured fields** (team, CFO, supplier, item, price, link, notes, etc.), **status and comments in one table**, **in-app notifications** when things change, and **per-order messaging** so coordination does not live only in email. The interview turned a generic CRUD idea into something aligned with how purchasing work actually flows.
