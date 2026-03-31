# Design Decision Log

Every week, record one design decision using this template. The goal is to practice naming **trade-offs**, which is central to architectural thinking.

---

## The template

| Field | Your entry |
|--------|------------|
| **Decision** | What did you decide? |
| **Alternatives considered** | What else could you have done? |
| **Why you chose this** | What constraint drove it? |
| **Trade-off** | What did you give up? |
| **When would you choose differently?** | Under what conditions? |

---

## Decision prompt (this week)

**Why did you put everything in one file (`app.py`) instead of splitting it into multiple files?**

*If you had split into multiple files, answer the flipped question: why did you choose to split?*

Think about:

- How many lines of code does your app have? At what point does a single file become hard to navigate?
- What would change if you needed to add five more features next week?
- What did the AI tool (Cursor) produce: one file or many? Did you accept that structure, or did you change it?

---

## Example entry (Purchase Request Manager)

| Field | Your entry |
|--------|------------|
| **Decision** | Keep the Streamlit app in a **single module**, `app.py` (on the order of ~1000 lines), with helpers and view functions defined in the same file. Data access uses separate CSV files, but not separate Python modules. |
| **Alternatives considered** | Split by feature: e.g. `notifications.py`, `threads.py`, `student_views.py`, `coordinator_views.py`, `data_io.py`. Or split by layer: `models/`, `ui/`, `services/`. |
| **Why you chose this** | The assignment asked for a small, reproducible lab app; a **one-file** layout matches common Streamlit tutorials, keeps `streamlit run app.py` obvious, and avoids import path issues for beginners. The AI assistant also iterated in one place, which made changes faster to review. |
| **Trade-off** | **Navigation and reuse**: scrolling a long file is harder than jumping between small files. **Testing** is also easier per module when you split. **Merge conflicts** are more likely if two people edit the same file. |
| **When would you choose differently?** | If the file passed **~1500–2000 lines**, or if **more than one developer** worked on the repo regularly, or if we needed **unit tests** on pure logic (CSV rules, notification builders) without running Streamlit. Adding five features next week would push toward at least `data.py` + `ui_student.py` + `ui_coordinator.py` or similar. |

### Short answers to the reflection questions

1. **Line count / single-file navigation**  
   This app is roughly **one thousand lines** in `app.py`. A single file starts to feel heavy when you search for a function by name often, or when unrelated features (student, coordinator, threads) are far apart. There is no fixed number; many teams use **~300–500 lines per file** as a soft rule, but tools and search matter more than the exact count.

2. **Five more features next week**  
   I would likely **extract** at least: CSV load/save and column names, notification builders, and thread append logic into a **`data` or `services` module**, and keep Streamlit only in `ui` files. That keeps new features from growing one long file.

3. **What Cursor / AI produced**  
   The assistant started from a **single `app.py`** and a **`README`**, which matches the assignment’s file structure. I **accepted** that shape for the lab and extended it in place. If the course had required a package layout, I would refactor into modules after the behavior was stable.

---

## Blank entry (copy for next week)

| Field | Your entry |
|--------|------------|
| **Decision** | |
| **Alternatives considered** | |
| **Why you chose this** | |
| **Trade-off** | |
| **When would you choose differently?** | |

**Prompt for next week:** *(instructor or you fill in)*
