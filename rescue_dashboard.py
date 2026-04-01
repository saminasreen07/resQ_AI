"""
ResQAI TN — Rescue Team Dashboard
Teams log in, see their assignment, update status in real time
"""
import streamlit as st
from datetime import datetime
from supabase_client import get_client
from priority_ai import get_priority_color

STATUS_FLOW = ["TEAM_ASSIGNED", "EN_ROUTE", "ON_SITE", "RESOLVED"]
STATUS_LABELS = {
    "TEAM_ASSIGNED": "Assignment received — prepare to deploy",
    "EN_ROUTE":      "Travelling to incident location",
    "ON_SITE":       "At the location, actively working",
    "RESOLVED":      "Situation handled, mission complete",
}
STATUS_ICONS = {
    "TEAM_ASSIGNED": "📋",
    "EN_ROUTE":      "🚗",
    "ON_SITE":       "📍",
    "RESOLVED":      "✅",
}

def _inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=DM+Sans:wght@300;400;500&display=swap');
.rescue-page { max-width:700px; margin:0 auto; }
.task-card { background:#0d1117; border:2px solid rgba(232,52,28,0.3); border-radius:18px; padding:24px; margin-bottom:20px; }
.task-title { font-family:'Rajdhani',sans-serif; font-size:1.4rem; font-weight:700; color:#f1f5f9; margin-bottom:4px; }
.info-row { display:flex; gap:20px; flex-wrap:wrap; font-size:0.82rem; color:#64748b; margin:8px 0; }
.status-pill { display:inline-block; padding:5px 16px; border-radius:20px; font-family:'Rajdhani',sans-serif; font-weight:700; font-size:0.85rem; letter-spacing:0.5px; }
.upd-btn { background:linear-gradient(135deg,#1e3a1e,#166534) !important; border-color:rgba(34,197,94,0.3) !important; color:#4ade80 !important; }
.stButton > button { background:linear-gradient(135deg,#c0251a,#e8341c) !important; color:white !important; border:none !important; border-radius:10px !important; font-family:'Rajdhani',sans-serif !important; font-weight:700 !important; letter-spacing:1px !important; width:100% !important; }
label { color:#94a3b8 !important; font-size:0.85rem !important; }
.stTextArea > div > textarea { background:#111 !important; color:#e2e8f0 !important; border:1px solid rgba(255,255,255,0.1) !important; border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)


def show_rescue_dashboard():
    _inject_css()
    st.markdown('<div class="rescue-page">', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:2rem;">🚒</div>
        <div style="font-family:'Rajdhani',sans-serif;font-size:1.5rem;font-weight:700;color:#f1f5f9;">Rescue Team Portal</div>
        <div style="font-size:0.78rem;color:#475569;">Select your team to view assigned task</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        client = get_client()
        teams_res = client.table("teams").select("*").execute()
        teams = teams_res.data or []
    except Exception as e:
        st.error(f"Database error: {e}")
        return

    if not teams:
        st.warning("No teams registered. Add teams to the `teams` table in Supabase.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    team_names = [t["name"] for t in teams]
    selected_team_name = st.selectbox("Select Your Team", ["— Choose Team —"] + team_names, key="rescue_team_sel")

    if selected_team_name == "— Choose Team —":
        st.markdown('</div>', unsafe_allow_html=True)
        return

    team = next((t for t in teams if t["name"] == selected_team_name), None)
    if not team:
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── Team info ──────────────────────────────────────────────────────────
    avail_color = "#10b981" if team.get("is_available") else "#ef4444"
    avail_text  = "Available" if team.get("is_available") else "On Mission"
    st.markdown(f"""
    <div style="background:#0d1117;border:1px solid rgba(255,255,255,0.06);border-radius:14px;padding:16px;margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:700;color:#e2e8f0;">{team['name']}</div>
                <div style="font-size:0.78rem;color:#64748b;">{team.get('type','')} Team · {team.get('district','')}</div>
            </div>
            <span style="font-size:0.78rem;font-weight:700;color:{avail_color};">● {avail_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    assignment_id = team.get("current_assignment")

    if not assignment_id:
        st.info("✅ No active assignment. Standing by.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── Fetch assigned report ──────────────────────────────────────────────
    try:
        res = client.table("reports").select("*").eq("id", assignment_id).execute()
        if not res.data:
            st.warning("Assignment record not found in database.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        report = res.data[0]

        hist_res = client.table("status_history").select("*").eq("report_id", assignment_id).order("timestamp").execute()
        history = hist_res.data or []
        history_map = {h["status"]: h["timestamp"] for h in history}
    except Exception as e:
        st.error(f"Error fetching assignment: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── Task card ──────────────────────────────────────────────────────────
    p_color = get_priority_color(report.get("priority","LOW"))
    current_status = report.get("status", "TEAM_ASSIGNED")

    st.markdown(f"""
    <div class="task-card">
        <div class="task-title">🆘 Active Mission: {report.get('disaster','')} Response</div>
        <div class="info-row">
            <span>🎫 {report.get('id','')}</span>
            <span>📍 {report.get('district','')} · {report.get('location','')}</span>
            <span>👥 {report.get('people',0)} people affected</span>
        </div>
        <div class="info-row">
            <span>📞 Caller: {report.get('name','')} · {report.get('phone','')}</span>
        </div>
        <div style="margin:12px 0;">
            <span class="status-pill" style="background:{p_color}22;color:{p_color};border:1px solid {p_color}44;">
                {report.get('priority','')} PRIORITY
            </span>
            &nbsp;
            <span class="status-pill" style="background:#1e293b;color:#94a3b8;border:1px solid rgba(255,255,255,0.1);">
                {current_status.replace('_',' ')}
            </span>
        </div>
        <div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:12px;font-size:0.82rem;color:#94a3b8;">
            <strong style="color:#e2e8f0;">Situation:</strong> {report.get('description','')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Needs ──────────────────────────────────────────────────────────────
    needs_str = report.get("specific_needs","")
    if needs_str:
        st.markdown(f"""
        <div style="background:#0d1117;border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:14px;margin-bottom:16px;">
            <div style="font-family:'Rajdhani',sans-serif;font-size:0.75rem;color:#475569;letter-spacing:1px;margin-bottom:8px;">REQUIRED RESOURCES</div>
            <div style="font-size:0.82rem;color:#94a3b8;">{needs_str.replace(',',' · ')}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Status Timeline ─────────────────────────────────────────────────────
    st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:0.75rem;color:#475569;letter-spacing:1px;margin-bottom:10px;">MISSION TIMELINE</div>', unsafe_allow_html=True)
    status_order_all = ["REPORTED","ACKNOWLEDGED","TEAM_ASSIGNED","EN_ROUTE","ON_SITE","RESOLVED"]
    current_idx = status_order_all.index(current_status) if current_status in status_order_all else 0
    for i, s in enumerate(STATUS_FLOW):
        global_idx = status_order_all.index(s)
        if global_idx < current_idx:    cls = "done"
        elif global_idx == current_idx: cls = "active"
        else:                            cls = "pending"
        icon = STATUS_ICONS.get(s,"•")
        ts = history_map.get(s,"")
        color_map = {"done":"#10b981","active":"#e8341c","pending":"#334155"}
        c = color_map[cls]
        st.markdown(f"""
        <div style="display:flex;gap:12px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
            <div style="font-size:1.1rem;width:24px;text-align:center;">{icon}</div>
            <div>
                <div style="font-family:'Rajdhani',sans-serif;font-weight:600;font-size:0.88rem;color:{c};">{s.replace('_',' ')}</div>
                <div style="font-size:0.72rem;color:#334155;">{STATUS_LABELS.get(s,'')}{' · ' + ts if ts else ''}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Update Status Button ────────────────────────────────────────────────
    flow_idx = STATUS_FLOW.index(current_status) if current_status in STATUS_FLOW else -1
    if 0 <= flow_idx < len(STATUS_FLOW) - 1:
        next_status = STATUS_FLOW[flow_idx + 1]
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        note = st.text_area("Add a note (optional)", key="rescue_note", height=70, placeholder="e.g. Roads blocked, requesting JCB support...")
        if st.button(f"📡 Update Status: {next_status.replace('_',' ')}", key="rescue_upd"):
            _rescue_update(client, report["id"], team["id"], next_status, note)
            st.success(f"✅ Status updated to {next_status}")
            st.rerun()
    elif current_status == "RESOLVED":
        st.success("🎉 Mission complete! This assignment has been resolved.")

    st.markdown('</div>', unsafe_allow_html=True)


def _rescue_update(client, report_id, team_id, new_status, note=""):
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        client.table("reports").update({
            "status": new_status,
            "status_updated_at": now,
        }).eq("id", report_id).execute()

        client.table("status_history").insert({
            "report_id": report_id,
            "status": new_status,
            "updated_by": "rescue_team",
            "timestamp": now,
            "note": note or "",
        }).execute()

        if new_status == "RESOLVED":
            client.table("teams").update({
                "is_available": True,
                "current_assignment": None,
            }).eq("id", team_id).execute()
    except Exception as e:
        st.error(f"❌ Failed to update status: {e}")
