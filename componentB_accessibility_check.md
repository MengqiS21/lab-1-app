# Purchase Request Manager — prompt / implementation log

This file records notable implementation notes and baseline checks for the project.

---

## Accessibility baseline results

### Color contrast check

**Result: Pass** (after one fix to the theme).

- **Body text on page background:** Theme colors `#2D3B36` on `#F6F9F7` (and similar on secondary background `#EEF4F1`) yield contrast ratios around **11:1** and **10.5:1**, above the WCAG **4.5:1** target for normal text.
- **Primary button (white label on primary color):** The first custom primary green (`#5C8F7B`) with white text was about **3.7:1**, which **failed** the 4.5:1 guideline for typical button labels.
- **Fix:** In `.streamlit/config.toml`, **`primaryColor`** was changed to **`#4A7B66`**, giving white-on-primary contrast of roughly **4.9:1**, which **passes**.

Caption and hint text should still be spot-checked in the browser (Streamlit may tint helper text) if strict compliance is required.

### Semantic headings check

**Result: Pass** (after structural fixes).

- **Requirement:** A single **`st.title()`** for the main app title; major sections use **`st.header()`**; subsections use **`st.subheader()`**; avoid using `st.markdown("## …")` as the only way to mark section titles (so screen readers get a proper outline).
- **Fixes applied:** Ensured one page title; added **`st.header()`** for each main tab section (e.g. Submit Request, Coordinator View); nested content uses **`st.subheader()`**; replaced markdown heading hashes used as titles with Streamlit heading APIs where appropriate.

Later UI refactors may add more widgets; re-check heading order if large sections move.
