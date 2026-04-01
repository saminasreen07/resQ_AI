"""
ResQAI TN — Main Application
Tamil Nadu AI-Powered Disaster Resource Coordination System
Run: streamlit run app.py
"""
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="ResQAI TN — Disaster Response",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Session state defaults ──────────────────────────────────────────────────
for key, default in [
    ("page", "home"),
    ("report_submitted", False),
    ("authority_logged_in", False),
    ("form_step", 1),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Live report count (from Supabase, graceful fallback) ─────────────────────
def _get_live_count():
    try:
        from supabase_client import get_client
        res = get_client().table("reports").select("id", count="exact").execute()
        return res.count or 0
    except Exception:
        return 0

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stApp"] {
    background: #080b10 !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stApp { background: #080b10 !important; }
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { 
    padding: 2rem 3rem !important; 
    max-width: 1200px !important; 
    margin: auto !important;
}
section[data-testid="stSidebar"] { display: none !important; }

/* Navbar */
.navbar {
    background: rgba(8,11,16,0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(232,52,28,0.15);

    display: flex;
    flex-direction: column;   /* stack logo + buttons */
    align-items: center;
    justify-content: center;

    padding: 14px 20px;
}

.nav-buttons {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;
    width: 100%;
    margin-top: 14px;
}
            
.nav-buttons button {
    min-width: 140px;
    padding: 12px 18px;
    border-radius: 14px;
}
            
.nav-brand {
    display: flex;
    align-items: center;
    gap: 10px;
}
.nav-logo {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #c0251a, #e8341c);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
}
.nav-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: 1px;
}
.nav-sub {
    font-size: 0.65rem;
    color: #475569;
    display: block;
    margin-top: -2px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.live-badge {
    background: rgba(232,52,28,0.12);
    border: 1px solid rgba(232,52,28,0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    color: #e8341c;
    display: flex;
    align-items: center;
    gap: 6px;
}
.live-dot {
    width: 6px; height: 6px;
    background: #e8341c;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(1.3)} }

/* Page content padding */
.page-content {
    padding: 28px 32px;
    max-width: 1200px;
    margin: 0 auto;
}

/* Home page */
.home-hero {
    background: linear-gradient(135deg, #0d0d0d 0%, #1a0808 50%, #0d0d0d 100%);
    border: 1px solid rgba(232,52,28,0.15);
    border-radius: 24px;
    padding: 60px 40px;
    text-align: center;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.home-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(232,52,28,0.08), transparent 70%);
    border-radius: 50%;
}
.home-hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(59,130,246,0.05), transparent 70%);
    border-radius: 50%;
}
.hero-eyebrow {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 3px;
    color: #e8341c;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.hero-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 3rem;
    font-weight: 700;
    color: #f8fafc;
    line-height: 1.1;
    margin-bottom: 16px;
}
.hero-title span { color: #e8341c; }
.hero-sub {
    color: #64748b;
    font-size: 1rem;
    max-width: 500px;
    margin: 0 auto 32px;
}
.card-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.feature-card {
    background: #0d1117;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 24px;
    text-align: left;
    transition: all 0.2s;
}
.feature-card:hover { border-color: rgba(232,52,28,0.3); transform: translateY(-2px); }
.fc-icon { font-size: 1.6rem; margin-bottom: 12px; }
.fc-title { font-family: 'Rajdhani', sans-serif; font-size: 1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 6px; }
.fc-desc { font-size: 0.8rem; color: #475569; line-height: 1.5; }
.stat-strip {
    display: flex;
    gap: 0;
    background: #0d1117;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 24px;
}
.stat-item {
    flex: 1;
    padding: 18px 20px;
    text-align: center;
    border-right: 1px solid rgba(255,255,255,0.06);
}
.stat-item:last-child { border-right: none; }
.stat-val { font-family: 'Rajdhani', sans-serif; font-size: 1.6rem; font-weight: 700; }
.stat-lbl { font-size: 0.7rem; color: #475569; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #c0251a, #e8341c) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    padding: 12px 26px !important;
    width: auto !important;   /* THIS FIXES STRETCHING */
    min-width: 160px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(232,52,28,0.35) !important;
}

/* Input fields */
.stTextInput > div > input,
.stTextArea > div > textarea,
.stSelectbox > div > div {
    background: #0d1117 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}
label { color: #94a3b8 !important; font-size: 0.85rem !important; }
.stTabs [data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    color: #64748b !important;
}
.stTabs [aria-selected="true"] { color: #e8341c !important; }

/* Hide Streamlit branding */
[data-testid="stDecoration"] { display: none !important; }
            
@media (max-width: 768px) {

    .nav-buttons {
        flex-direction: column;
        gap: 12px;
    }

    .nav-buttons button {
        width: 100%;
        max-width: 320px;
    }

}

/* ─── NAV BUTTON CENTER FIX ─── */

div[data-testid="stHorizontalBlock"] {
    justify-content: center !important;
    align-items: center !important;
    gap: 16px !important;
}

div[data-testid="stHorizontalBlock"] > div {
    display: flex !important;
    justify-content: center !important;
}

/* BUTTON STYLE */
.stButton > button {
    background: linear-gradient(135deg, #c0251a, #e8341c) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    padding: 12px 26px !important;
    min-width: 160px !important;
    width: auto !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(232,52,28,0.35) !important;
}

/* ─── MOBILE RESPONSIVE ─── */
@media (max-width: 768px) {

    div[data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        align-items: center !important;
        gap: 12px !important;
    }

    div[data-testid="stHorizontalBlock"] > div {
        width: 100% !important;
        max-width: 320px !important;
    }

    .stButton > button {
        width: 100% !important;
    }
}


</style>
""", unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────────────────────
live_count = _get_live_count()
st.markdown(f"""
<div class="navbar">
    <div class="nav-brand">
        <div class="nav-logo">🚨</div>
        <div>
            <span class="nav-name">ResQAI TN</span>
            <span class="nav-sub">Tamil Nadu Disaster Response</span>
        </div>
    </div>
    <div class="live-badge">
        <div class="live-dot"></div>
        {live_count} LIVE REPORTS
    </div>
</div>
""", unsafe_allow_html=True)

# ── Nav buttons ───────────────────────────────────────────────────────────────
left, c1, c2, c3, c4, right = st.columns([2,1,1,1,1,2])

with c1:
    if st.button("🏠 Home", key="nav_home", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()

with c2:
    if st.button("🚨 Report", key="nav_report", use_container_width=True):
        st.session_state["page"] = "citizen"
        st.session_state["form_step"] = 1
        st.rerun()

with c3:
    if st.button("🛡️ Authority", key="nav_auth", use_container_width=True):
        st.session_state["page"] = "authority"
        st.rerun()

with c4:
    if st.button("🚒 Rescue", key="nav_rescue", use_container_width=True):
        st.session_state["page"] = "rescue"
        st.rerun()

st.markdown('<div class="page-content">', unsafe_allow_html=True)

# ── Page routing ──────────────────────────────────────────────────────────────
page = st.session_state.get("page", "home")

if page == "home":
    # ── Home Page ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="home-hero">
        <div class="hero-eyebrow">🚨 AI-Powered Emergency System</div>
        <div class="hero-title">Tamil Nadu's<br><span>Disaster Response</span><br>Command Centre</div>
        <div class="hero-sub">AI-prioritised rescue coordination, real-time status tracking, and resource allocation for Tamil Nadu's 38 districts.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card-grid">
        <div class="feature-card">
            <div class="fc-icon">🚨</div>
            <div class="fc-title">Citizen Reporting</div>
            <div class="fc-desc">4-step guided form, AI priority scoring, instant ticket ID for tracking your report in real time.</div>
        </div>
        <div class="feature-card">
            <div class="fc-icon">🛡️</div>
            <div class="fc-title">Authority Command</div>
            <div class="fc-desc">Live reports dashboard, AI team assignment engine, status updates, and district analytics.</div>
        </div>
        <div class="feature-card">
            <div class="fc-icon">🚒</div>
            <div class="fc-title">Rescue Teams</div>
            <div class="fc-desc">Field teams view their assignment, update mission status in real time, and free up when resolved.</div>
        </div>
        <div class="feature-card">
            <div class="fc-icon">🤖</div>
            <div class="fc-title">AI Assignment Engine</div>
            <div class="fc-desc">Matches teams to disasters by type compatibility, distance (geopy), and urgency score.</div>
        </div>
        <div class="feature-card">
            <div class="fc-icon">📊</div>
            <div class="fc-title">Live Analytics</div>
            <div class="fc-desc">District-level breakdown, disaster type distribution, priority heatmap — all in real time.</div>
        </div>
        <div class="feature-card">
            <div class="fc-icon">🗄️</div>
            <div class="fc-title">Supabase Backend</div>
            <div class="fc-desc">All data in Supabase — reports, teams, status history. No CSV files. Real-time sync.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stat strip
    st.markdown(f"""
    <div class="stat-strip">
        <div class="stat-item">
            <div class="stat-val" style="color:#e8341c;">{live_count}</div>
            <div class="stat-lbl">Reports Filed</div>
        </div>
        <div class="stat-item">
            <div class="stat-val" style="color:#3b82f6;">38</div>
            <div class="stat-lbl">Districts Covered</div>
        </div>
        <div class="stat-item">
            <div class="stat-val" style="color:#10b981;">6</div>
            <div class="stat-lbl">Disaster Types</div>
        </div>
        <div class="stat-item">
            <div class="stat-val" style="color:#f59e0b;">24/7</div>
            <div class="stat-lbl">System Active</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🚨 Report a Disaster", key="home_report"):
            st.session_state["page"] = "citizen"
            st.session_state["form_step"] = 1
            st.rerun()
    with c2:
        if st.button("🛡️ Authority Login", key="home_auth"):
            st.session_state["page"] = "authority"
            st.rerun()
    with c3:
        if st.button("🚒 Rescue Team Portal", key="home_rescue"):
            st.session_state["page"] = "rescue"
            st.rerun()

elif page == "citizen":
    from citizen_page import show_citizen_page
    show_citizen_page()

elif page == "authority":
    from authority_dashboard import show_authority_dashboard
    show_authority_dashboard()

elif page == "rescue":
    from rescue_dashboard import show_rescue_dashboard
    show_rescue_dashboard()

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center;padding:20px 0 10px;border-top:1px solid rgba(255,255,255,0.04);margin-top:32px;">
    <div style="display:flex;justify-content:center;gap:28px;flex-wrap:wrap;font-size:0.75rem;color:#334155;">
        <span>🚒 SDMA: 1070</span>
        <span>🚑 Ambulance: 108</span>
        <span>🔥 Fire: 101</span>
        <span>👮 Police: 100</span>
        <span>🆘 NDRF: 011-24363260</span>
    </div>
    <div style="font-size:0.65rem;color:#1e293b;margin-top:8px;">ResQAI TN · Built for TNWISE Hackathon 2026</div>
</div>
""", unsafe_allow_html=True)
