# This app is a Purchase Request Manager built with Streamlit.
# Students submit team purchase requests and store them in a local CSV.
# Coordinators review requests in a table, update status and notes, and chat
# with teams in per order threads. Closed conversations move to an archive.
# I use pandas for CSV read and write and keep notifications and threads in
# separate CSV files so nothing needs a database.

from __future__ import annotations

import hashlib
import html
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------

APP_TITLE = "Purchase Request Manager"
APP_DIR = Path(__file__).resolve().parent
CSV_PATH = APP_DIR / "requests.csv"
NOTIFICATIONS_PATH = APP_DIR / "notifications.csv"
THREAD_PATH = APP_DIR / "thread_messages.csv"
COORDINATOR_PASSWORD = "coord2026"

THREAD_COLUMNS = [
    "id",
    "request_id",
    "team",
    "sender",
    "body",
    "timestamp",
    "read_by_coordinator",
]

NOTIFICATION_COLUMNS = [
    "id",
    "team",
    "request_id",
    "message",
    "created_at",
    "read",
    "kind",
]
# kind: status | comment | status_and_note (for inbox labels)

CSV_COLUMNS = [
    "id",
    "timestamp",
    "team",
    "cfo",
    "supplier",
    "item",
    "quantity",
    "unit_price",
    "total_price",
    "link",
    "non_amazon_info",
    "notes",
    "status",
    "coordinator_comment",
    "conversation_closed",
]

STATUS_OPTIONS = ["Pending", "Approved", "Rejected", "Needs Info"]

TEAM_SUGGESTIONS = [str(i) for i in range(1, 21)]


def ensure_csv_exists() -> None:
    if not CSV_PATH.exists():
        pd.DataFrame(columns=CSV_COLUMNS).to_csv(CSV_PATH, index=False)


def ensure_notifications_csv() -> None:
    if not NOTIFICATIONS_PATH.exists():
        pd.DataFrame(columns=NOTIFICATION_COLUMNS).to_csv(NOTIFICATIONS_PATH, index=False)


def ensure_thread_csv() -> None:
    if not THREAD_PATH.exists():
        pd.DataFrame(columns=THREAD_COLUMNS).to_csv(THREAD_PATH, index=False)


def load_thread_messages() -> pd.DataFrame:
    ensure_thread_csv()
    df = pd.read_csv(THREAD_PATH, dtype={"id": "Int64", "request_id": "Int64"})
    for col in THREAD_COLUMNS:
        if col not in df.columns:
            df[col] = 0 if col in ("read_by_coordinator", "id", "request_id") else ""
    df = df[THREAD_COLUMNS]
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    df["request_id"] = pd.to_numeric(df["request_id"], errors="coerce").astype("Int64")
    for col in ("team", "sender", "body", "timestamp"):
        df[col] = df[col].fillna("").astype(str)
        df.loc[df[col] == "nan", col] = ""
    df["read_by_coordinator"] = (
        pd.to_numeric(df["read_by_coordinator"], errors="coerce").fillna(0).astype(int)
    )
    return df


def save_thread_messages(df: pd.DataFrame) -> None:
    df = df[THREAD_COLUMNS].copy()
    df.to_csv(THREAD_PATH, index=False)


def next_thread_id(df: pd.DataFrame) -> int:
    if df.empty or df["id"].isna().all():
        return 1
    return int(df["id"].max()) + 1


def append_thread_batch(rows: list[dict]) -> None:
    if not rows:
        return
    df = load_thread_messages()
    nid = next_thread_id(df)
    out = []
    for r in rows:
        out.append({**r, "id": nid})
        nid += 1
    df = pd.concat([df, pd.DataFrame(out)], ignore_index=True)
    save_thread_messages(df)


def _build_coordinator_thread_row(
    team: str,
    request_id: int,
    item: str,
    old_status: str,
    new_status: str,
    old_comment: str,
    new_comment: str,
) -> dict | None:
    """Plain-text thread line when coordinator updates a request (same triggers as notifications)."""
    os, ns = old_status.strip(), new_status.strip()
    oc, nc = old_comment.strip(), new_comment.strip()
    status_changed = os != ns
    comment_changed = oc != nc
    if not status_changed and not comment_changed:
        return None

    item_short = (item[:60] + "…") if len(item) > 60 else item
    lines: list[str] = [f"[Coordinator] Request #{request_id} — {item_short}"]
    if status_changed:
        lines.append(f"Status: {os} → {ns}")
    if comment_changed:
        if nc:
            lines.append(f"Note: {nc}")
        else:
            lines.append("Note: (removed)")

    body = "\n".join(lines)
    ts = datetime.now().isoformat(timespec="seconds")
    return {
        "request_id": int(request_id),
        "team": team.strip(),
        "sender": "coordinator",
        "body": body,
        "timestamp": ts,
        "read_by_coordinator": 1,
    }


def append_student_thread_message(team: str, request_id: int, body: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    append_thread_batch(
        [
            {
                "request_id": int(request_id),
                "team": team.strip(),
                "sender": "student",
                "body": body.strip(),
                "timestamp": ts,
                "read_by_coordinator": 0,
            }
        ]
    )


def set_conversation_closed(request_id: int, closed: bool) -> None:
    df = load_requests()
    mask = df["id"].astype(int) == int(request_id)
    df.loc[mask, "conversation_closed"] = 1 if closed else 0
    save_requests(df)


def append_coordinator_reply_message(team: str, request_id: int, body: str) -> None:
    if not str(body).strip():
        return
    append_thread_batch(
        [
            {
                "request_id": int(request_id),
                "team": str(team).strip(),
                "sender": "coordinator",
                "body": str(body).strip(),
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "read_by_coordinator": 1,
            }
        ]
    )


def load_notifications() -> pd.DataFrame:
    ensure_notifications_csv()
    df = pd.read_csv(NOTIFICATIONS_PATH, dtype={"id": "Int64", "request_id": "Int64"})
    for col in NOTIFICATION_COLUMNS:
        if col not in df.columns:
            df[col] = 0 if col == "read" else ""
    df = df[NOTIFICATION_COLUMNS]
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    df["request_id"] = pd.to_numeric(df["request_id"], errors="coerce").astype("Int64")
    df["team"] = df["team"].fillna("").astype(str)
    df["message"] = df["message"].fillna("").astype(str)
    df["created_at"] = df["created_at"].fillna("").astype(str)
    df["read"] = pd.to_numeric(df["read"], errors="coerce").fillna(0).astype(int)
    df["kind"] = df["kind"].fillna("update").astype(str)
    df.loc[df["kind"] == "nan", "kind"] = "update"
    return df


def save_notifications(df: pd.DataFrame) -> None:
    df = df[NOTIFICATION_COLUMNS].copy()
    df.to_csv(NOTIFICATIONS_PATH, index=False)


def next_notification_id(df: pd.DataFrame) -> int:
    if df.empty or df["id"].isna().all():
        return 1
    return int(df["id"].max()) + 1


def _notification_kind_label(kind: str) -> str:
    return {
        "status": "Status update",
        "comment": "Coordinator note",
        "status_and_note": "Status & note",
        "update": "Update",
    }.get(kind, "Update")


def _build_coordinator_notification_row(
    team: str,
    request_id: int,
    item: str,
    old_status: str,
    new_status: str,
    old_comment: str,
    new_comment: str,
) -> dict | None:
    """Build one notification row, or None if nothing changed."""
    os, ns = old_status.strip(), new_status.strip()
    oc, nc = old_comment.strip(), new_comment.strip()
    status_changed = os != ns
    comment_changed = oc != nc
    if not status_changed and not comment_changed:
        return None

    item_short = (item[:70] + "…") if len(item) > 70 else item
    lines: list[str] = [f"**Request #{request_id}** — _{item_short}_"]

    if status_changed:
        lines.append(f"**Status:** {os} → **{ns}**")
    if comment_changed:
        if nc:
            lines.append(f"**Note:** {nc}")
        else:
            lines.append("_The coordinator removed the previous note._")

    if status_changed and comment_changed:
        kind = "status_and_note"
    elif status_changed:
        kind = "status"
    else:
        kind = "comment"

    msg = "\n\n".join(lines)
    ts = datetime.now().isoformat(timespec="seconds")
    return {
        "team": team.strip(),
        "request_id": int(request_id),
        "message": msg,
        "created_at": ts,
        "read": 0,
        "kind": kind,
    }


def append_coordinator_notifications_batch(rows: list[dict]) -> None:
    if not rows:
        return
    df = load_notifications()
    nid = next_notification_id(df)
    out_rows = []
    for r in rows:
        row = {**r, "id": nid}
        nid += 1
        out_rows.append(row)
    df = pd.concat([df, pd.DataFrame(out_rows)], ignore_index=True)
    save_notifications(df)


def mark_notification_read(nid: int) -> None:
    df = load_notifications()
    df.loc[df["id"] == nid, "read"] = 1
    save_notifications(df)


def load_requests() -> pd.DataFrame:
    ensure_csv_exists()
    df = pd.read_csv(CSV_PATH, dtype={"id": "Int64"})
    for col in CSV_COLUMNS:
        if col not in df.columns:
            if col == "conversation_closed":
                df[col] = 0
            else:
                df[col] = ""
    df = df[CSV_COLUMNS]
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    df["conversation_closed"] = (
        pd.to_numeric(df["conversation_closed"], errors="coerce").fillna(0).astype(int).clip(0, 1)
    )
    # Empty CSV cells become NaN/float; st.data_editor text columns need real strings.
    text_cols = [
        "team",
        "cfo",
        "supplier",
        "item",
        "link",
        "non_amazon_info",
        "notes",
        "status",
        "coordinator_comment",
    ]
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str)
        df.loc[df[col] == "nan", col] = ""
    return df


def save_requests(df: pd.DataFrame) -> None:
    df = df[CSV_COLUMNS].copy()
    df.to_csv(CSV_PATH, index=False)


def next_id(df: pd.DataFrame) -> int:
    if df.empty or df["id"].isna().all():
        return 1
    return int(df["id"].max()) + 1


def init_session_state() -> None:
    if "coord_unlocked" not in st.session_state:
        st.session_state.coord_unlocked = False
    if "student_form_nonce" not in st.session_state:
        st.session_state.student_form_nonce = 0
    if "coord_last_save_hint" not in st.session_state:
        st.session_state.coord_last_save_hint = ""


def parse_ts(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def bordered_container():
    """Streamlit ≥1.33 supports border=True on containers."""
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    init_session_state()
    ensure_csv_exists()
    ensure_notifications_csv()
    ensure_thread_csv()

    st.title(APP_TITLE)
    st.caption("Students submit purchase requests; coordinators review and update status.")

    tab_submit, tab_coord = st.tabs(["Submit Request", "Coordinator View"])

    with tab_submit:
        render_student_form()

    with tab_coord:
        render_coordinator_view()


def render_student_alerts_tab(team_key: str) -> None:
    df = load_notifications()
    df = df[df["team"].astype(str).str.strip() == team_key]
    if df.empty:
        st.success("No alerts yet for this team.")
        return

    unread = df[df["read"] == 0].sort_values("created_at", ascending=False)
    read = df[df["read"] == 1].sort_values("created_at", ascending=False)

    if not unread.empty:
        st.success(f"You have **{len(unread)}** new update(s) from the coordinator.")
        for _, row in unread.iterrows():
            rid = int(row["id"])
            kind = str(row.get("kind", "update"))
            label = _notification_kind_label(kind)
            c1, c2 = st.columns([5, 1])
            with c1:
                st.caption(f"{label} · {row['created_at']}")
                st.markdown(row["message"])
            with c2:
                if st.button("Got it", key=f"ndismiss_{rid}", type="secondary"):
                    mark_notification_read(rid)
                    st.rerun()
    else:
        st.info("No unread alerts — you're caught up.")

    if not read.empty:
        with st.expander("Earlier alerts"):
            for _, row in read.iterrows():
                kind = str(row.get("kind", "update"))
                label = _notification_kind_label(kind)
                st.caption(f"{label} · {row['created_at']}")
                st.markdown(row["message"])
                st.markdown("")


def render_student_order_thread(team_key: str, request_id: int, *, read_only: bool = False) -> None:
    """Single order: conversation + optional reply (used inside expanders)."""
    tm = load_thread_messages()
    sid = int(request_id)
    thread = tm[
        (tm["request_id"].astype(int) == sid)
        & (tm["team"].astype(str).str.strip() == team_key)
    ].sort_values("timestamp")

    if thread.empty:
        st.caption(
            "No messages yet. When the coordinator updates status or adds a note, it will show here."
        )
    for _, row in thread.iterrows():
        who = "Coordinator" if row["sender"] == "coordinator" else "Your team"
        st.caption(f"{row['timestamp']} · **{who}**")
        st.markdown(str(row["body"]).replace("\n", "\n\n"))

    if read_only:
        st.caption("_This order conversation was closed by the coordinator (read-only)._")
        return

    reply = st.text_area(
        "Message to coordinator",
        key=f"stu_order_reply_{sid}_{team_key}",
        height=100,
        placeholder="Write a message about this order…",
    )
    if st.button("Send", key=f"stu_order_send_{sid}_{team_key}", type="primary"):
        if not str(reply).strip():
            st.error("Please enter a message.")
        else:
            append_student_thread_message(team_key, sid, str(reply))
            st.success("Sent.")
            st.rerun()


def render_student_order_messages_expanders(team_key: str) -> None:
    """Open + archived order threads (titles provided by parent)."""
    req_df = load_requests()
    req_df = req_df[req_df["team"].astype(str).str.strip() == team_key].copy()
    if req_df.empty:
        st.info("No orders yet. Submit a purchase request below first.")
        return

    req_df = req_df.sort_values("id", ascending=False)
    open_df = req_df[req_df["conversation_closed"].astype(int) == 0]
    closed_df = req_df[req_df["conversation_closed"].astype(int) == 1]

    if open_df.empty and closed_df.empty:
        st.info("No orders yet.")
        return

    if not open_df.empty:
        for _, row in open_df.iterrows():
            rid = int(row["id"])
            item_preview = str(row["item"])[:48] + ("…" if len(str(row["item"])) > 48 else "")
            title = f"Order #{rid} — {item_preview}"
            with st.expander(title, expanded=False):
                render_student_order_thread(team_key, rid, read_only=False)

    if not closed_df.empty:
        st.markdown(
            '<p style="margin:1rem 0 0.35rem 0;font-size:0.95rem;font-weight:600;'
            'color:rgba(45,59,54,0.85);">Archived</p>',
            unsafe_allow_html=True,
        )
        st.caption("Closed by the coordinator — view only.")
        for _, row in closed_df.iterrows():
            rid = int(row["id"])
            item_preview = str(row["item"])[:40] + ("…" if len(str(row["item"])) > 40 else "")
            title = f"[Closed] Order #{rid} — {item_preview}"
            with st.expander(title, expanded=False):
                render_student_order_thread(team_key, rid, read_only=True)


def render_student_notifications() -> None:
    st.subheader("Team inbox")
    st.caption(
        "Enter your **Team #** (same as on your requests). Everything below is grouped under **Order updates**."
    )
    st.text_input(
        "Team # for inbox",
        key="student_notify_team",
        placeholder="e.g. 3 (same as on your purchase requests)",
    )
    team_key = str(st.session_state.get("student_notify_team", "")).strip()
    if not team_key:
        st.info("Type your team number above to load your inbox.")
        st.divider()
        return

    st.subheader("Order updates")
    with bordered_container():
        st.markdown(
            '<p style="margin:0 0 0.15rem 0;font-size:0.95rem;font-weight:600;'
            'color:rgba(45,59,54,0.9);">Coordinator updates</p>',
            unsafe_allow_html=True,
        )
        st.caption("Status changes and notes — dismiss each with **Got it** when you’ve read it.")
        render_student_alerts_tab(team_key)

        st.divider()

        st.markdown(
            '<p style="margin:0 0 0.15rem 0;font-size:0.95rem;font-weight:600;'
            'color:rgba(45,59,54,0.9);">Order messages</p>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Open an order to chat with the coordinator. **Archived** (if any) lists past closed threads."
        )
        render_student_order_messages_expanders(team_key)

    st.divider()


def _coord_format_request_option(rid: int, team: str, item: str) -> str:
    ip = str(item)[:36] + ("…" if len(str(item)) > 36 else "")
    return f"#{int(rid)} · Team {team} · {ip}"


def render_coordinator_open_conversations(df_all: pd.DataFrame) -> None:
    """Active tickets: reply here or close when done."""
    st.subheader("Order conversation")
    st.caption(
        "Teams write from **Submit Request → Team inbox → Order messages**. "
        "Reply below, then **Close ticket** when the conversation is finished (it moves to **Archive**)."
    )
    open_df = df_all[df_all["conversation_closed"].astype(int) == 0].copy()
    if open_df.empty:
        st.info("No open order conversations.")
        return

    open_df = open_df.sort_values("id", ascending=False)
    choices: dict[str, int] = {}
    for _, row in open_df.iterrows():
        rid = int(row["id"])
        lab = _coord_format_request_option(rid, str(row["team"]), str(row["item"]))
        choices[lab] = rid

    label = st.selectbox(
        "Open conversation",
        list(choices.keys()),
        key="coord_open_conv_pick",
    )
    pid = int(choices[label])
    rq = open_df[open_df["id"].astype(int) == pid].iloc[0]
    team_nm = str(rq["team"]).strip()

    tm = load_thread_messages()
    full_thread = tm[tm["request_id"].astype(int) == pid].sort_values("timestamp")

    st.caption(f"Request **#{pid}** · Team **{team_nm}**")
    if full_thread.empty:
        st.caption("No thread messages yet — students can post from their inbox, or add a note in the table below.")
    for _, row in full_thread.iterrows():
        who = "Coordinator" if row["sender"] == "coordinator" else f"Team {row['team']}"
        st.caption(f"{row['timestamp']} · **{who}**")
        st.markdown(str(row["body"]).replace("\n", "\n\n"))
        st.markdown("")

    reply = st.text_area(
        "Reply to team",
        key=f"coord_reply_{pid}",
        height=100,
        placeholder="Type a message to the team…",
    )
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Send reply", key=f"coord_send_reply_{pid}", type="primary"):
            if not str(reply).strip():
                st.error("Enter a message to send.")
            else:
                append_coordinator_reply_message(team_nm, pid, str(reply))
                st.success("Sent.")
                st.rerun()
    with b2:
        if st.button("Close ticket", key=f"coord_close_{pid}", type="secondary"):
            set_conversation_closed(pid, True)
            st.success("Ticket closed — find it under **Archive**.")
            st.rerun()


def render_coordinator_archive(df_all: pd.DataFrame) -> None:
    """Read-only closed threads; optional reopen. One row per ticket — details only when expanded."""
    st.subheader("Archive")
    st.caption("Closed conversations — click a row to expand and read the thread or reopen.")
    closed_df = df_all[df_all["conversation_closed"].astype(int) == 1].copy()
    if closed_df.empty:
        st.info("No archived conversations yet.")
        return

    closed_df = closed_df.sort_values("id", ascending=False)
    tm = load_thread_messages()

    for _, rq in closed_df.iterrows():
        pid = int(rq["id"])
        team_nm = str(rq["team"]).strip()
        title = _coord_format_request_option(pid, team_nm, str(rq["item"]))
        with st.expander(title, expanded=False):
            st.caption(f"Request **#{pid}** · Team **{team_nm}** · _closed_")
            full_thread = tm[tm["request_id"].astype(int) == pid].sort_values("timestamp")
            if full_thread.empty:
                st.caption("_No messages in thread._")
            else:
                for _, row in full_thread.iterrows():
                    who = "Coordinator" if row["sender"] == "coordinator" else f"Team {row['team']}"
                    st.caption(f"{row['timestamp']} · **{who}**")
                    st.markdown(str(row["body"]).replace("\n", "\n\n"))
                    st.markdown("")
            if st.button("Reopen conversation", key=f"coord_reopen_{pid}"):
                set_conversation_closed(pid, False)
                st.success("Reopened — it appears again under **Order conversation**.")
                st.rerun()


def render_student_form() -> None:
    if "submitted_flash" in st.session_state and st.session_state.submitted_flash:
        st.success(st.session_state.submitted_flash)
        st.session_state.submitted_flash = None

    # h2 under page title (h1): major section for this tab — do not skip heading levels.
    st.header("Submit Request")
    render_student_notifications()

    st.subheader("New purchase request")
    st.caption(
        "Fill in all required fields; provide a purchase link **or** non-Amazon product details. "
        "**Total** updates as you change quantity or unit price."
    )

    key_suffix = str(st.session_state.student_form_nonce)

    # Not using st.form: form widgets do not rerun until submit, so the Total would stay $0 while editing.

    c1, c2 = st.columns(2)
    with c1:
        team_mode = st.radio(
            "Team #",
            ["Choose from list", "Type team number"],
            horizontal=True,
            key=f"team_mode_{key_suffix}",
        )
    with c2:
        if team_mode == "Choose from list":
            team = st.selectbox(
                "Team",
                TEAM_SUGGESTIONS,
                label_visibility="collapsed",
                key=f"team_select_{key_suffix}",
            )
        else:
            team = st.text_input(
                "Team #",
                placeholder="e.g. 7",
                label_visibility="collapsed",
                key=f"team_text_{key_suffix}",
            )

    cfo = st.text_input("CFO name *", placeholder="Full name", key=f"cfo_{key_suffix}")
    supplier = st.text_input("Provider / Supplier name *", key=f"sup_{key_suffix}")
    item = st.text_input("Item name *", key=f"item_{key_suffix}")

    q1, q2, q3 = st.columns(3)
    with q1:
        quantity = st.number_input("Quantity *", min_value=1, value=1, step=1, key=f"qty_{key_suffix}")
    with q2:
        unit_price = st.number_input(
            "Unit price (USD) *",
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.2f",
            key=f"unit_{key_suffix}",
        )
    with q3:
        total_price = float(quantity) * float(unit_price)
        st.metric("Total", f"${total_price:,.2f}")

    link = st.text_input(
        "Purchase link (URL)",
        placeholder="https://…",
        key=f"link_{key_suffix}",
    )
    non_amazon = st.text_area(
        "Non-Amazon product info",
        placeholder="Store name, SKU, how to order, estimated price source… (required if no link)",
        height=120,
        key=f"na_{key_suffix}",
    )
    notes = st.text_area("Notes (optional)", height=68, key=f"notes_{key_suffix}")

    submitted = st.button("Submit request", type="primary", use_container_width=True)

    if submitted:
        team_s = str(team).strip()
        cfo_s = cfo.strip()
        supplier_s = supplier.strip()
        item_s = item.strip()
        link_s = link.strip()
        non_amazon_s = non_amazon.strip()

        errors: list[str] = []
        if not team_s:
            errors.append("Team # is required.")
        if not cfo_s:
            errors.append("CFO name is required.")
        if not supplier_s:
            errors.append("Supplier name is required.")
        if not item_s:
            errors.append("Item name is required.")
        if quantity < 1:
            errors.append("Quantity must be at least 1.")
        if unit_price < 0:
            errors.append("Unit price cannot be negative.")
        if not link_s and not non_amazon_s:
            errors.append("Provide a purchase link **or** non-Amazon product info.")

        if errors:
            for e in errors:
                st.error(e)
            return

        df = load_requests()
        new_id = next_id(df)
        ts = datetime.now().isoformat(timespec="seconds")
        row = {
            "id": new_id,
            "timestamp": ts,
            "team": team_s,
            "cfo": cfo_s,
            "supplier": supplier_s,
            "item": item_s,
            "quantity": int(quantity),
            "unit_price": round(float(unit_price), 2),
            "total_price": round(float(quantity) * float(unit_price), 2),
            "link": link_s,
            "non_amazon_info": non_amazon_s,
            "notes": notes.strip(),
            "status": "Pending",
            "coordinator_comment": "",
            "conversation_closed": 0,
        }
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        save_requests(df)
        st.session_state.student_form_nonce += 1
        st.session_state.submitted_flash = f"Request **#{new_id}** submitted successfully."
        st.session_state.student_notify_team = team_s
        st.rerun()


def render_coordinator_view() -> None:
    st.header("Coordinator View")

    if not st.session_state.coord_unlocked:
        st.subheader("Coordinator access")
        pwd = st.text_input("Password", type="password", key="coord_pwd")
        if st.button("Unlock dashboard"):
            if pwd == COORDINATOR_PASSWORD:
                st.session_state.coord_unlocked = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.caption("Use the coordinator password from your program lead (default for local demo: see README).")
        return

    col_lock, _ = st.columns([1, 4])
    with col_lock:
        if st.button("Lock"):
            st.session_state.coord_unlocked = False
            st.rerun()

    df_all = load_requests()
    if df_all.empty:
        st.info("No requests yet.")
        return

    df_all = df_all.copy()
    df_all["_dt"] = parse_ts(df_all["timestamp"])

    # Filters
    st.subheader("Filters")
    fc1, fc2, fc3, fc4 = st.columns(4)
    teams = sorted(df_all["team"].astype(str).unique().tolist())
    with fc1:
        team_filter = st.multiselect("Team #", options=teams, default=[])
    with fc2:
        status_filter = st.multiselect("Status", options=STATUS_OPTIONS, default=[])
    with fc3:
        dmin = df_all["_dt"].min()
        dmax = df_all["_dt"].max()
        if pd.isna(dmin):
            dmin = datetime.now()
        if pd.isna(dmax):
            dmax = datetime.now()
        date_from = st.date_input("From date", value=dmin.date(), key="dfrom")
    with fc4:
        date_to = st.date_input("To date", value=dmax.date(), key="dto")

    mask = pd.Series(True, index=df_all.index)
    if team_filter:
        mask &= df_all["team"].astype(str).isin(team_filter)
    if status_filter:
        mask &= df_all["status"].astype(str).isin(status_filter)
    d_from = pd.Timestamp(date_from)
    d_to = pd.Timestamp(date_to) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    mask &= (df_all["_dt"] >= d_from) & (df_all["_dt"] <= d_to)

    df_view = df_all.loc[mask].copy()

    # Prominent totals (filtered set)
    total_sum = pd.to_numeric(df_view["total_price"], errors="coerce").fillna(0).sum()
    n_req = len(df_view)
    n_open_conv = int((df_all["conversation_closed"].astype(int) == 0).sum())
    n_arch = int((df_all["conversation_closed"].astype(int) == 1).sum())
    st.subheader("Summary")
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Total amount (filtered)", f"${total_sum:,.2f}")
    with m2:
        st.metric("Requests (filtered)", f"{n_req}")
    with m3:
        all_sum = pd.to_numeric(df_all["total_price"], errors="coerce").fillna(0).sum()
        st.metric("All-time total (all requests)", f"${all_sum:,.2f}")
    with m4:
        st.metric("Open conversations", n_open_conv)
    with m5:
        st.metric("Archived conversations", n_arch)

    dash_tab, summary_tab, archive_tab = st.tabs(["Requests table", "Summary by team", "Archive"])

    with dash_tab:
        render_coordinator_open_conversations(df_all)
        st.divider()
        st.subheader("All requests")
        st.caption(
            "Edit **status** and **coordinator comment** inline, then click **Save changes**. "
            "When you save, the **team** for each edited row gets an inbox message if **status** "
            "or **note** changed."
        )

        display_cols = [
            "id",
            "timestamp",
            "team",
            "cfo",
            "supplier",
            "item",
            "quantity",
            "unit_price",
            "total_price",
            "link",
            "non_amazon_info",
            "notes",
            "status",
            "coordinator_comment",
        ]
        editor_df = df_view[display_cols].copy()

        filter_sig = "|".join(
            [
                ",".join(sorted(map(str, team_filter))),
                ",".join(sorted(status_filter)),
                str(date_from),
                str(date_to),
                str(len(editor_df)),
            ]
        )
        editor_key = hashlib.sha256(filter_sig.encode()).hexdigest()[:32]

        edited = st.data_editor(
            editor_df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True, format="%d"),
                "timestamp": st.column_config.TextColumn("Submitted", disabled=True),
                "team": st.column_config.TextColumn("Team #", disabled=True),
                "cfo": st.column_config.TextColumn("CFO", disabled=True),
                "supplier": st.column_config.TextColumn("Supplier", disabled=True),
                "item": st.column_config.TextColumn("Item", disabled=True),
                "quantity": st.column_config.NumberColumn("Qty", disabled=True),
                "unit_price": st.column_config.NumberColumn("Unit $", disabled=True, format="$%.2f"),
                "total_price": st.column_config.NumberColumn("Total $", disabled=True, format="$%.2f"),
                "link": st.column_config.TextColumn("Link", disabled=True, width="small"),
                "non_amazon_info": st.column_config.TextColumn("Non-Amazon info", disabled=True, width="medium"),
                "notes": st.column_config.TextColumn("Notes", disabled=True, width="small"),
                "status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS, required=True),
                "coordinator_comment": st.column_config.TextColumn("Coordinator comment", width="medium"),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            key=f"coord_editor_{editor_key}",
        )

        save_col, hint_col = st.columns([1, 4])
        with save_col:
            save_clicked = st.button("Save changes", type="primary", key="coord_save_changes_btn")
        with hint_col:
            if st.session_state.coord_last_save_hint:
                h = html.escape(st.session_state.coord_last_save_hint)
                st.markdown(
                    f'<div style="display:flex;align-items:center;min-height:2.65rem;">'
                    f'<span style="font-size:0.875rem;color:rgba(45,59,54,0.72);">'
                    f"Last save: {h}</span></div>",
                    unsafe_allow_html=True,
                )

        if save_clicked:
            full_before = load_requests()
            full = load_requests()
            id_to_row = edited.set_index("id")
            pending_notifications: list[dict] = []
            pending_threads: list[dict] = []
            for i in full.index:
                rid = int(full.at[i, "id"])
                if rid not in id_to_row.index:
                    continue
                old_status = str(full_before.at[i, "status"]).strip()
                new_status = str(id_to_row.at[rid, "status"]).strip()
                old_comment = str(full_before.at[i, "coordinator_comment"]).strip()
                raw_new_c = id_to_row.at[rid, "coordinator_comment"]
                if pd.isna(raw_new_c):
                    new_comment = ""
                else:
                    new_comment = str(raw_new_c).strip()
                    if new_comment.lower() == "nan":
                        new_comment = ""

                full.at[i, "status"] = new_status
                full.at[i, "coordinator_comment"] = new_comment

                built = _build_coordinator_notification_row(
                    str(full_before.at[i, "team"]).strip(),
                    rid,
                    str(full_before.at[i, "item"]).strip(),
                    old_status,
                    new_status,
                    old_comment,
                    new_comment,
                )
                if built:
                    pending_notifications.append(built)
                trow = _build_coordinator_thread_row(
                    str(full_before.at[i, "team"]).strip(),
                    rid,
                    str(full_before.at[i, "item"]).strip(),
                    old_status,
                    new_status,
                    old_comment,
                    new_comment,
                )
                if trow:
                    pending_threads.append(trow)
            save_requests(full)
            append_coordinator_notifications_batch(pending_notifications)
            append_thread_batch(pending_threads)
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.coord_last_save_hint = f"{ts} — rows updated; teams notified if status/note changed."
            st.success("Saved.")
            st.rerun()

    with summary_tab:
        st.caption("Rows reflect the same **Team**, **Status**, and **date** filters as the table above.")
        g = df_view.copy()
        if g.empty:
            st.info("No requests match the current filters.")
        else:
            g["total_price"] = pd.to_numeric(g["total_price"], errors="coerce").fillna(0)
            g["status"] = g["status"].astype(str)

            summary = (
                g.groupby("team", dropna=False)
                .agg(
                    requests=("id", "count"),
                    total_requested=("total_price", "sum"),
                    approved=("status", lambda x: (x == "Approved").sum()),
                    pending=("status", lambda x: (x == "Pending").sum()),
                    rejected=("status", lambda x: (x == "Rejected").sum()),
                    needs_info=("status", lambda x: (x == "Needs Info").sum()),
                )
                .reset_index()
            )
            summary = summary.rename(
                columns={
                    "team": "Team #",
                    "requests": "Requests",
                    "total_requested": "Total requested ($)",
                    "approved": "Approved",
                    "pending": "Pending",
                    "rejected": "Rejected",
                    "needs_info": "Needs info",
                }
            )
            st.dataframe(
                summary.sort_values("Team #", key=lambda s: s.astype(str)),
                use_container_width=True,
                hide_index=True,
            )

    with archive_tab:
        render_coordinator_archive(df_all)


if __name__ == "__main__":
    main()
