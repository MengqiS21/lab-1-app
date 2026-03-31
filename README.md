# Purchase Request Manager

A [Streamlit](https://streamlit.io/) web app for student program teams to submit purchase requests and for coordinators to review them, send updates, and exchange messages per order. All data lives in local CSV files in the project folder (no database).

## What this project does

- **Students** use the **Submit Request** tab to file requests (team, CFO, supplier, item, quantity, unit price with auto total, link or non-Amazon details, notes). Submissions are appended to `requests.csv`.
- **Students** use **Team inbox** after entering their team number: **Order updates** (coordinator pushes, dismiss with **Got it**) and **Order messages** (expand an order to chat; archived closed threads appear under **Archived**).
- **Coordinators** unlock **Coordinator View** with a password, filter requests, edit status and comments in the table, and save. Saving can notify teams and append to message threads.
- **Coordinators** use **Order conversation** at the top of the **Requests table** tab to reply to teams and **Close ticket**; closed threads appear under the **Archive** tab and can be reopened.

Optional UI theme and accessibility settings are in `.streamlit/config.toml`.

## Requirements

- Python 3.10 or newer recommended
- Dependencies: `streamlit`, `pandas` (see `requirements.txt`)

## How to run the app (reproduce the environment)

From the project root (the folder that contains `app.py`):

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies and start the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens in the browser (usually [http://localhost:8501](http://localhost:8501)). Stop the server with `Ctrl+C` in the terminal.

## How to reproduce the main workflows

1. **Submit a request**  
   Open **Submit Request**, fill required fields (provide either a purchase link or non-Amazon product info), click **Submit request**. A new row appears in `requests.csv`.

2. **Coordinator review**  
   Open **Coordinator View**, enter the coordinator password (see below), unlock, use filters if needed, edit **Status** or **Coordinator comment**, click **Save changes**. Notifications and thread entries are written when status or comment changes.

3. **Student inbox**  
   On **Submit Request**, enter the same **Team #** as on the request, then read **Order updates** and open orders under **Order messages**.

4. **Coordinator chat and close**  
   In **Coordinator View**, **Requests table** tab, use **Order conversation** to choose an open request, **Send reply** if needed, then **Close ticket**. Check **Archive** for closed threads.

5. **Clean slate (optional)**  
   To reset all local data, stop the app and delete these files if they exist: `requests.csv`, `notifications.csv`, `thread_messages.csv`. Restart the app; empty files with headers are recreated on first use.

## Coordinator password (local demo)

The default password is set in `app.py` as `COORDINATOR_PASSWORD`. For a fresh checkout, open `app.py` and read that constant (it may differ from older notes). Change it before any real deployment.

## Data files (all under the project folder)

| File | Role |
|------|------|
| `requests.csv` | One row per purchase request, including status, coordinator comment, and `conversation_closed` (0 open, 1 closed). |
| `notifications.csv` | Student-facing **Order updates** alerts (dismiss with **Got it**). |
| `thread_messages.csv` | Per order chat lines (`student` or `coordinator`). |

These files are created automatically when needed. They are plain CSV and can be backed up or inspected in a spreadsheet editor.

## Project layout

| Path | Purpose |
|------|---------|
| `app.py` | Main Streamlit application |
| `requirements.txt` | Python dependencies |
| `.streamlit/config.toml` | Streamlit theme (light, accessible contrast) |
| `mock_requests.csv` | Optional sample data for demos (not loaded by the app unless you import manually) |

## Troubleshooting

- **`streamlit: command not found`**  
  Activate the virtual environment first, or run `python -m streamlit run app.py` using the same interpreter where you ran `pip install`.

- **Deploy to Streamlit Community Cloud**  
  Push the project to GitHub, then connect the repo in the cloud UI. Set secrets there for any password you do not want in code.
