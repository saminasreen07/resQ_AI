"""
ResQAI TN — Authority Dashboard v4
All old features (Live Map, Social Radar, Risk Forecast, Shelters, Resources) +
new features (AI Assignment, Teams, Analytics) in premium UI
"""
import streamlit as st
import random
from datetime import datetime
from supabase_client import get_client
from priority_ai import get_priority_color, calculate_priority
from ai_assignment import assign_team
from social_media_ai import generate_simulated_tweets, get_critical_social_alerts, detect_trending_districts
from predictor import predict_district_risks, get_statewide_risk_summary, DISTRICT_RISK_PROFILES

STATUS_ORDER = ["REPORTED","ACKNOWLEDGED","TEAM_ASSIGNED","EN_ROUTE","ON_SITE","RESOLVED"]
STATUS_COLORS = {"REPORTED":"#64748b","ACKNOWLEDGED":"#3b82f6","TEAM_ASSIGNED":"#8b5cf6","EN_ROUTE":"#f59e0b","ON_SITE":"#ef4444","RESOLVED":"#10b981"}
DISASTER_ICONS = {"Flood":"🌊","Cyclone":"🌀","Fire":"🔥","Landslide":"⛰️","Earthquake":"🫨","Tsunami":"🌊"}
DISTRICT_COORDS = {
    "Chennai":(13.0827,80.2707),"Coimbatore":(11.0168,76.9558),"Madurai":(9.9252,78.1198),
    "Tiruchirappalli":(10.7905,78.7047),"Salem":(11.6643,78.1460),"Tirunelveli":(8.7139,77.7567),
    "Vellore":(12.9165,79.1325),"Erode":(11.3410,77.7172),"Thanjavur":(10.7870,79.1378),
    "Cuddalore":(11.7447,79.7680),"Kancheepuram":(12.8185,79.6947),"Nagapattinam":(10.7672,79.8449),
    "Nilgiris":(11.4064,76.6932),"Dindigul":(10.3624,77.9695),"Tiruppur":(11.1085,77.3411),
    "Kanyakumari":(8.0883,77.5385),"Thoothukudi":(8.7642,78.1348),"Ramanathapuram":(9.3639,78.8395),
    "Nagapattinam":(10.7672,79.8449),"Villupuram":(11.9395,79.4913),"Tiruvallur":(13.1437,79.9085),
}

SHELTER_CAMPS = [
    {"name":"Chennai GH Relief Camp","district":"Chennai","lat":13.0695,"lon":80.2799,"capacity":500,"occupied":210,"contact":"044-25300001","type":"Government Hospital"},
    {"name":"Adyar Cyclone Shelter","district":"Chennai","lat":13.0012,"lon":80.2565,"capacity":300,"occupied":300,"contact":"044-24413000","type":"Cyclone Shelter"},
    {"name":"Kilpauk Medical Camp","district":"Chennai","lat":13.0862,"lon":80.2347,"capacity":400,"occupied":120,"contact":"044-26421009","type":"Medical Camp"},
    {"name":"Cuddalore Govt School Camp","district":"Cuddalore","lat":11.7500,"lon":79.7600,"capacity":300,"occupied":180,"contact":"9445000005","type":"School"},
    {"name":"Nagapattinam Cyclone Shelter","district":"Nagapattinam","lat":10.7700,"lon":79.8500,"capacity":600,"occupied":250,"contact":"9445001001","type":"Cyclone Shelter"},
    {"name":"Thanjavur Relief Camp","district":"Thanjavur","lat":10.7870,"lon":79.1378,"capacity":400,"occupied":390,"contact":"9445001002","type":"Government Camp"},
    {"name":"Madurai GH Camp","district":"Madurai","lat":9.9252,"lon":78.1198,"capacity":350,"occupied":100,"contact":"0452-2534001","type":"Government Hospital"},
    {"name":"Coimbatore Relief Centre","district":"Coimbatore","lat":11.0168,"lon":76.9558,"capacity":450,"occupied":200,"contact":"0422-2300001","type":"Relief Centre"},
    {"name":"Vellore CMC Camp","district":"Vellore","lat":12.9165,"lon":79.1325,"capacity":250,"occupied":80,"contact":"0416-2281000","type":"Medical Camp"},
    {"name":"Tirunelveli School Shelter","district":"Tirunelveli","lat":8.7139,"lon":77.7567,"capacity":200,"occupied":150,"contact":"9445002001","type":"School"},
]

RESOURCE_DATA = [
    {"type":"Rescue Boat","unit":"Flood Response Boat 1","district":"Chennai","status":"Available","contact":"044-25001001"},
    {"type":"Rescue Boat","unit":"Coastal Boat Unit 2","district":"Nagapattinam","status":"Available","contact":"9445003001"},
    {"type":"Ambulance","unit":"108 Emergency Unit 1","district":"Chennai","status":"Available","contact":"108"},
    {"type":"Ambulance","unit":"Mobile Medical Unit","district":"Madurai","status":"Deployed","contact":"0452-2500001"},
    {"type":"Fire Engine","unit":"Fire Brigade Unit 1","district":"Chennai","status":"Available","contact":"101"},
    {"type":"Fire Engine","unit":"Industrial Fire Unit","district":"Coimbatore","status":"Available","contact":"0422-2302101"},
    {"type":"NDRF Team","unit":"NDRF Battalion 4","district":"Chennai","status":"Available","contact":"044-24301234"},
    {"type":"NDRF Team","unit":"NDRF Quick Response","district":"Tiruchirappalli","status":"Standby","contact":"0431-2500100"},
    {"type":"Helicopter","unit":"TN Police Chopper 1","district":"Chennai","status":"Available","contact":"044-28447101"},
    {"type":"JCB/Machinery","unit":"PWD Heavy Equipment","district":"Nilgiris","status":"Available","contact":"0423-2444001"},
    {"type":"Dewatering Pump","unit":"Pump Unit Chennai 1","district":"Chennai","status":"Available","contact":"044-25001002"},
    {"type":"Dewatering Pump","unit":"Flood Control Pump 2","district":"Cuddalore","status":"Available","contact":"9445004001"},
]

def _css():
    st.markdown("""<style>
.auth-wrap{max-width:1200px;margin:0 auto;padding:0 4px 40px}
.auth-hero{background:linear-gradient(135deg,#0a1928,#0b2b3b);border:1px solid rgba(0,188,212,.2);border-radius:22px;padding:32px 36px;margin-bottom:24px;position:relative;overflow:hidden;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px}
.auth-hero::before{content:'';position:absolute;top:-60px;right:-60px;width:280px;height:280px;background:radial-gradient(circle,rgba(0,188,212,.08),transparent 65%);border-radius:50%;pointer-events:none}
.auth-hero-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:2rem;font-weight:700;background:linear-gradient(135deg,#e0f2fe,#bae6fd);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.auth-hero-sub{font-size:.78rem;color:#5f9ea0;letter-spacing:2px;text-transform:uppercase;margin-top:4px}
.live-indicator{display:flex;align-items:center;gap:8px;background:rgba(0,188,212,.1);border:1px solid rgba(0,188,212,.25);border-radius:20px;padding:8px 16px}
.live-dot{width:8px;height:8px;background:#4dd0e1;border-radius:50%;animation:blink 1.2s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
.live-txt{font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:.8rem;color:#4dd0e1;letter-spacing:1.5px}
.mc{background:rgba(15,35,50,0.6);border:1px solid rgba(0,188,212,.15);border-radius:16px;padding:20px 22px;height:100%;position:relative;overflow:hidden}
.mc::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:3px 3px 0 0}
.mc-red::before{background:linear-gradient(90deg,#ef4444,#dc2626)}
.mc-orange::before{background:linear-gradient(90deg,#f97316,#ea580c)}
.mc-yellow::before{background:linear-gradient(90deg,#eab308,#ca8a04)}
.mc-green::before{background:linear-gradient(90deg,#22c55e,#16a34a)}
.mc-blue::before{background:linear-gradient(90deg,#00bcd4,#0097a7)}
.mc-purple::before{background:linear-gradient(90deg,#8b5cf6,#7c3aed)}
.mc-val{font-family:'Plus Jakarta Sans',sans-serif;font-size:2.1rem;font-weight:700;margin-bottom:4px}
.mc-red .mc-val{color:#ef4444}.mc-orange .mc-val{color:#f97316}.mc-yellow .mc-val{color:#eab308}
.mc-green .mc-val{color:#22c55e}.mc-blue .mc-val{color:#4dd0e1}.mc-purple .mc-val{color:#8b5cf6}
.mc-lbl{font-family:'Plus Jakarta Sans',sans-serif;font-size:.68rem;color:#5f9ea0;text-transform:uppercase;letter-spacing:1.5px}
.sec-hdr{font-family:'Plus Jakarta Sans',sans-serif;font-size:1rem;font-weight:700;color:#4dd0e1;text-transform:uppercase;letter-spacing:2px;margin:20px 0 14px;padding-bottom:8px;border-bottom:1px solid rgba(0,188,212,.15);display:flex;align-items:center;gap:8px}
.rpt-card{background:rgba(15,35,50,0.6);border:1px solid rgba(0,188,212,.15);border-radius:14px;padding:16px 18px;margin-bottom:10px;transition:all .2s}
.rpt-card:hover{border-color:rgba(0,188,212,.4);background:rgba(15,35,50,0.8)}
.rpt-card.sel{border-color:#4dd0e1;background:rgba(0,188,212,.1)}
.s-badge{display:inline-block;padding:3px 12px;border-radius:10px;font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:.7rem;letter-spacing:.5px}
.team-card{background:rgba(15,35,50,0.6);border:1px solid rgba(0,188,212,.15);border-radius:12px;padding:16px 18px;margin-bottom:10px}
.team-card.gold{border-color:#4dd0e1;background:rgba(0,188,212,.1)}
.team-card.silver{border-color:rgba(0,188,212,.25)}
.tweet-card{background:rgba(15,35,50,0.6);border:1px solid rgba(0,188,212,.15);border-radius:12px;padding:14px 16px;margin-bottom:10px}
.tweet-card.crit{border-color:#ef4444}
.tweet-card.high{border-color:#f97316}
.risk-bar-bg{background:#1e293b;border-radius:6px;height:8px;margin-top:6px;overflow:hidden}
.risk-bar-fill{height:8px;border-radius:6px;transition:width .5s}
.shelter-card{background:rgba(15,35,50,0.6);border:1px solid rgba(0,188,212,.15);border-radius:12px;padding:14px 16px;margin-bottom:10px}
.res-card{background:rgba(15,35,50,0.6);border:1px solid rgba(0,188,212,.15);border-radius:12px;padding:14px 16px;margin-bottom:10px}
.map-placeholder{background:rgba(15,35,50,0.4);border:1px solid rgba(0,188,212,.15);border-radius:16px;padding:24px;margin:12px 0}
.activity-feed{background:rgba(15,35,50,0.4);border:1px solid rgba(0,188,212,.15);border-radius:14px;padding:16px;max-height:420px;overflow-y:auto}
.af-item{padding:10px 0;border-bottom:1px solid rgba(0,188,212,.1);display:flex;gap:12px;align-items:flex-start}
.af-item:last-child{border-bottom:none}
.af-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-top:4px}
.login-wrap{max-width:420px;margin:80px auto;background:rgba(15,35,50,0.8);border:1px solid rgba(0,188,212,.25);border-radius:22px;padding:40px 36px;text-align:center}
.stButton>button{background:linear-gradient(135deg,#00acc1,#0097a7)!important;color:white!important;border:none!important;border-radius:12px!important;font-family:'Plus Jakarta Sans',sans-serif!important;font-weight:700!important;letter-spacing:1px!important;padding:11px 24px!important;width:100%!important;transition:all .2s!important}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 6px 22px rgba(0,188,212,.35)!important}
</style>""", unsafe_allow_html=True)

def show_authority_dashboard():
    _css()
    if not st.session_state.get("authority_logged_in"): _login(); return
    st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)

    # Hero header
    now_str = datetime.now().strftime("%d %b %Y · %H:%M IST")
    month = datetime.now().month
    season = "NE Monsoon Season Active" if month in [10,11,12] else ("SW Monsoon Season" if month in [6,7,8,9] else "Pre-Monsoon Watch")
    st.markdown(f"""<div class="auth-hero">
      <div>
        <div class="auth-hero-title">⚡ RESQAI COMMAND CENTER</div>
        <div class="auth-hero-sub">Tamil Nadu State Disaster Management Authority · Authority Access · Classified</div>
      </div>
      <div style="text-align:right">
        <div class="live-indicator"><div class="live-dot"></div><span class="live-txt">LIVE MONITORING</span></div>
        <div style="font-size:.74rem;color:#475569;margin-top:8px;">{now_str}</div>
        <div style="font-size:.72rem;color:#334155;">{season}</div>
      </div></div>""", unsafe_allow_html=True)

    try:
        client = get_client()
        reports = client.table("reports").select("*").order("created_at",desc=True).execute().data or []
        teams = client.table("teams").select("*").execute().data or []
    except Exception as e:
        st.error(f"❌ Database error: {e}")
        st.info("Check your `.streamlit/secrets.toml` — make sure Supabase URL and key are correct.")
        return

    # Metrics
    total=len(reports); crit=sum(1 for r in reports if r.get("priority")=="CRITICAL")
    high=sum(1 for r in reports if r.get("priority")=="HIGH"); med=sum(1 for r in reports if r.get("priority")=="MEDIUM")
    low=sum(1 for r in reports if r.get("priority")=="LOW"); resolved=sum(1 for r in reports if r.get("status")=="RESOLVED")
    active=total-resolved; people=sum(r.get("people",0) for r in reports)
    medical=sum(1 for r in reports if r.get("medical")=="Yes"); t_avail=sum(1 for t in teams if t.get("is_available"))
    top_district = max(set(r.get("district","") for r in reports), key=lambda d: sum(1 for r in reports if r.get("district")==d)) if reports else "—"
    st.markdown('<div class="sec-hdr">📊 COMMAND CENTER METRICS</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    for col,cls,val,lbl in [(c1,"mc-blue",total,"TOTAL REPORTS"),(c2,"mc-red",crit,"CRITICAL"),(c3,"mc-orange",high,"HIGH"),(c4,"mc-green",t_avail,"RESOURCES"),(c5,"mc-yellow",top_district,"MOST INCIDENTS")]:
        with col: st.markdown(f'<div class="mc {cls}"><div class="mc-val">{val}</div><div class="mc-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    for col,cls,val,lbl in [(c1,"mc-yellow",med,"MEDIUM"),(c2,"mc-green",low,"LOW"),(c3,"mc-red",medical,"MEDICAL CASES"),(c4,"mc-blue",f"{people:,}","PEOPLE AFFECTED"),(c5,"mc-purple",active,"ACTIVE REPORTS")]:
        with col: st.markdown(f'<div class="mc {cls}"><div class="mc-val">{val}</div><div class="mc-lbl">{"● " if lbl in ["CRITICAL","MEDIUM","LOW"] else ""}{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
        "🗺️ Live Map","📋 Reports & AI","🚁 Resources","📡 Social Radar","🔮 Risk Forecast","🏕️ Shelters","👥 Teams"
    ])

    with tab1: _tab_map(reports)
    with tab2: _tab_reports(reports, teams, client)
    with tab3: _tab_resources()
    with tab4: _tab_social()
    with tab5: _tab_risk()
    with tab6: _tab_shelters()
    with tab7: _tab_teams(teams, reports, client)
    st.markdown('</div>', unsafe_allow_html=True)

def _login():
    st.markdown("""<div class="login-wrap">
      <div style="font-size:2.5rem;margin-bottom:12px;">🛡️</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:1.6rem;font-weight:700;color:#f1f5f9;margin-bottom:4px;">Authority Login</div>
      <div style="font-size:.78rem;color:#475569;margin-bottom:28px;">SDMA Tamil Nadu · Secure Command Access</div>
    </div>""", unsafe_allow_html=True)
    col = st.columns([1,2,1])[1]
    with col:
        pwd = st.text_input("Password", type="password", key="auth_pwd", placeholder="Enter authority password")
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        if st.button("🔐 Login to Command Centre", use_container_width=True):
            correct = st.secrets.get("authority_password","SDMA@TN2024")
            if pwd == correct:
                st.session_state["authority_logged_in"] = True; st.rerun()
            else: st.error("❌ Incorrect password")

def _tab_map(reports):
    st.markdown('<div class="sec-hdr">🗺️ Tamil Nadu Live Disaster Map</div>', unsafe_allow_html=True)
    try:
        import folium
        from folium.plugins import MarkerCluster
        from streamlit_folium import st_folium
        m = folium.Map(location=[10.8505,78.6677], zoom_start=7, tiles="CartoDB dark_matter")
        cluster = MarkerCluster(name="Clustered").add_to(m)
        p_colors = {"CRITICAL":"#FF2D2D","HIGH":"#FF6B00","MEDIUM":"#FFD700","LOW":"#00C851"}
        folium_colors = {"CRITICAL":"red","HIGH":"orange","MEDIUM":"beige","LOW":"green","default":"blue"}
        for r in reports:
            lat=r.get("lat"); lon=r.get("lon")
            if not lat or not lon: continue
            pc=p_colors.get(r.get("priority","LOW"),"#64748b")
            fc=folium_colors.get(r.get("priority","LOW"),"blue")
            popup_html=f"""<div style='font-family:Arial;font-size:12px;min-width:200px;'>
              <b style='color:{pc};'>{r.get('priority','')} — {r.get('disaster','')}</b><br>
              📍 {r.get('district','')} · {r.get('location','')}<br>
              👥 {r.get('people',0)} people · 📞 {r.get('phone','')}<br>
              🎫 {r.get('id','')} · {r.get('status','')}<br>
              <em style='color:#666;'>{str(r.get('created_at',''))[:16]}</em></div>"""
            if r.get("priority") in ["CRITICAL","HIGH"]:
                folium.CircleMarker([lat,lon],radius=20,color=pc,fill=False,weight=2,opacity=0.6).add_to(m)
                folium.Marker([lat,lon],popup=folium.Popup(popup_html,max_width=260),
                    icon=folium.Icon(color=fc,icon="exclamation-sign",prefix="glyphicon")).add_to(m)
            else:
                folium.Marker([lat,lon],popup=folium.Popup(popup_html,max_width=260),
                    icon=folium.Icon(color=fc,icon="warning-sign",prefix="glyphicon")).add_to(cluster)
        folium.LayerControl().add_to(m)
        col1,col2 = st.columns([3,1])
        with col1: st_folium(m, use_container_width=True, height=500)
        with col2:
            st.markdown('<div class="sec-hdr" style="font-size:.75rem;">⚡ LIVE ACTIVITY FEED</div>', unsafe_allow_html=True)
            st.markdown('<div class="activity-feed">', unsafe_allow_html=True)
            for r in reports[:15]:
                pc={"CRITICAL":"#ef4444","HIGH":"#f97316","MEDIUM":"#eab308","LOW":"#22c55e"}.get(r.get("priority","LOW"),"#64748b")
                st.markdown(f"""<div class="af-item">
                  <div class="af-dot" style="background:{pc};"></div>
                  <div>
                    <div style="font-size:.82rem;font-weight:600;color:#e2e8f0;">{DISASTER_ICONS.get(r.get('disaster',''),'⚠️')} {r.get('disaster','')} — {r.get('district','')}</div>
                    <div style="font-size:.72rem;color:#475569;">{str(r.get('created_at',''))[:16]}</div>
                    <div style="font-size:.72rem;color:#64748b;">👥 {r.get('people',0)} · {r.get('priority','')}</div>
                  </div></div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    except ImportError:
        st.warning("📦 Install `folium` and `streamlit-folium` for the live map: `pip install folium streamlit-folium`")
        _fallback_map(reports)

def _fallback_map(reports):
    st.markdown('<div class="map-placeholder">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:Rajdhani,sans-serif;font-weight:700;color:#3b82f6;margin-bottom:12px;">📍 Report Locations (Text View — install folium for interactive map)</div>', unsafe_allow_html=True)
    for r in reports[:10]:
        pc=get_priority_color(r.get("priority","LOW"))
        st.markdown(f'<div style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,.04);font-size:.82rem;"><span style="color:{pc};font-weight:700;">{r.get("priority","")}</span> · {r.get("disaster","")} — {r.get("district","")} · {r.get("location","")} · 👥 {r.get("people",0)}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def _tab_reports(reports, teams, client):
    st.markdown('<div class="sec-hdr">📋 All Reports · AI Assignment</div>', unsafe_allow_html=True)
    fc1,fc2,fc3,fc4 = st.columns(4)
    with fc1: fp=st.selectbox("Priority",["All","CRITICAL","HIGH","MEDIUM","LOW"],key="af_p")
    with fc2: fs=st.selectbox("Status",["All"]+STATUS_ORDER,key="af_s")
    with fc3: fd=st.selectbox("Disaster",["All","Flood","Cyclone","Fire","Landslide","Earthquake","Tsunami"],key="af_d")
    with fc4: fdistrict=st.selectbox("District",["All"]+sorted(set(r.get("district","") for r in reports)),key="af_dist")
    filtered=[r for r in reports if (fp=="All" or r.get("priority")==fp) and (fs=="All" or r.get("status")==fs) and (fd=="All" or r.get("disaster")==fd) and (fdistrict=="All" or r.get("district")==fdistrict)]
    st.markdown(f'<div style="font-size:.78rem;color:#475569;margin-bottom:14px;">Showing {len(filtered)} of {len(reports)} reports</div>', unsafe_allow_html=True)

    col_reports, col_panel = st.columns([3,2])
    with col_reports:
        for r in filtered:
            pc=get_priority_color(r.get("priority","LOW")); sc=STATUS_COLORS.get(r.get("status","REPORTED"),"#64748b")
            sel=(st.session_state.get("sel_report")==r["id"])
            cls="sel" if sel else ""
            st.markdown(f"""<div class="rpt-card {cls}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px;">
                <div>
                  <span style="font-family:'Rajdhani',sans-serif;font-size:.92rem;font-weight:700;color:#e2e8f0;">{r.get('id','')}</span>
                  <span style="font-size:.76rem;color:#475569;margin-left:8px;">{r.get('name','')} · {r.get('phone','')}</span>
                </div>
                <span class="s-badge" style="background:{pc}20;color:{pc};border:1px solid {pc}44;">{r.get('priority','')}</span>
              </div>
              <div style="font-size:.82rem;color:#94a3b8;margin:8px 0 6px;">
                {DISASTER_ICONS.get(r.get('disaster',''),'⚠️')} {r.get('disaster','')} &nbsp;·&nbsp; 📍 {r.get('district','')} — {r.get('location','')} &nbsp;·&nbsp; 👥 {r.get('people',0)}
              </div>
              <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
                <span class="s-badge" style="background:{sc}20;color:{sc};border:1px solid {sc}44;">{r.get('status','').replace('_',' ')}</span>
                <span style="font-size:.7rem;color:#334155;">{str(r.get('created_at',''))[:16]}</span>
              </div></div>""", unsafe_allow_html=True)
            bc1,bc2 = st.columns(2)
            with bc1:
                if st.button("🤖 AI Assign",key=f"ai_{r['id']}"):
                    st.session_state["sel_report"]=r["id"]; st.session_state.pop("ai_sug",None); st.rerun()
            with bc2:
                if st.button("📋 Details",key=f"det_{r['id']}"):
                    st.session_state["sel_report"]=r["id"]; st.rerun()

    with col_panel:
        sel_id=st.session_state.get("sel_report")
        if sel_id:
            sel=next((r for r in reports if r["id"]==sel_id),None)
            if sel:
                pc=get_priority_color(sel.get("priority","LOW"))
                st.markdown(f"""<div style="background:#0d1117;border:1px solid {pc}33;border-radius:16px;padding:18px 20px;margin-bottom:14px;">
                  <div style="font-family:'Rajdhani',sans-serif;font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:8px;">🎫 {sel.get('id')}</div>
                  <div style="font-size:.82rem;color:#94a3b8;line-height:1.7;">{sel.get('description','No description')}</div>
                  <div style="font-size:.76rem;color:#64748b;margin-top:8px;">Needs: {sel.get('specific_needs','—')}</div>
                </div>""", unsafe_allow_html=True)

                # AI Assignment
                st.markdown('<div class="sec-hdr" style="font-size:.78rem;">🤖 AI TEAM ASSIGNMENT</div>', unsafe_allow_html=True)
                if st.button("🤖 Run AI Engine",key="run_ai_btn"):
                    sug=assign_team(sel,teams); st.session_state["ai_sug"]=sug; st.session_state["ai_for"]=sel_id
                sug=st.session_state.get("ai_sug",[])
                if sug and st.session_state.get("ai_for")==sel_id:
                    for i,s in enumerate(sug):
                        t=s["team"]; medal=["🥇","🥈","🥉"][i]; gcls="gold" if i==0 else ("silver" if i==1 else "")
                        ac="#10b981" if t.get("is_available") else "#ef4444"
                        at="Free" if t.get("is_available") else "Busy"
                        st.markdown(f"""<div class="team-card {gcls}">
                          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
                            <span style="font-family:'Rajdhani',sans-serif;font-size:.9rem;font-weight:700;color:#e2e8f0;">{medal} {t.get('name','')}</span>
                            <span style="font-size:.72rem;color:{ac};font-weight:700;">● {at}</span>
                          </div>
                          <div style="font-size:.76rem;color:#64748b;margin-top:5px;">🏷️ {t.get('type','')} · 📍 {t.get('district','')} · 📏 {s['distance_km']} km</div>
                          <div style="font-size:.73rem;color:#475569;margin-top:3px;">{s['reason']}</div>
                        </div>""", unsafe_allow_html=True)
                        if t.get("is_available"):
                            if st.button(f"✅ Assign {t.get('name','')[:20]}",key=f"asgn_{t['id']}_{sel_id}"):
                                try:
                                    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    client.table("reports").update({"status":"TEAM_ASSIGNED","assigned_team_id":t["id"],"status_updated_at":now}).eq("id",sel_id).execute()
                                    client.table("teams").update({"is_available":False,"current_assignment":sel_id}).eq("id",t["id"]).execute()
                                    client.table("status_history").insert({"report_id":sel_id,"status":"TEAM_ASSIGNED","updated_by":"authority","timestamp":now,"note":f"Assigned to {t['name']}"}).execute()
                                    st.success(f"✅ {t['name']} assigned!"); st.session_state.pop("ai_sug",None); st.rerun()
                                except Exception as e: st.error(f"Error: {e}")
                elif not teams:
                    st.warning("No teams in database. Run `supabase_setup.sql` first.")

                # Quick status update
                st.markdown('<div class="sec-hdr" style="font-size:.78rem;margin-top:16px;">📡 STATUS UPDATE</div>', unsafe_allow_html=True)
                cur_s=sel.get("status","REPORTED"); ci=STATUS_ORDER.index(cur_s) if cur_s in STATUS_ORDER else 0
                if ci < len(STATUS_ORDER)-1:
                    nxt=STATUS_ORDER[ci+1]
                    note=st.text_input("Note (optional)",key="upd_note",placeholder="Add context...")
                    if st.button(f"→ Mark {nxt.replace('_',' ')}",key="upd_btn"):
                        try:
                            now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            client.table("reports").update({"status":nxt,"status_updated_at":now}).eq("id",sel_id).execute()
                            client.table("status_history").insert({"report_id":sel_id,"status":nxt,"updated_by":"authority","timestamp":now,"note":note or ""}).execute()
                            st.success(f"Status → {nxt}"); st.rerun()
                        except Exception as e: st.error(f"Error: {e}")
                else: st.success("✅ Report is RESOLVED")
        else:
            st.markdown('<div style="background:#0d1117;border:1px dashed rgba(255,255,255,.08);border-radius:14px;padding:32px;text-align:center;color:#334155;font-size:.84rem;">← Select a report to view details and run AI assignment</div>', unsafe_allow_html=True)

def _tab_resources():
    st.markdown('<div class="sec-hdr">🚁 Rescue Resources Registry</div>', unsafe_allow_html=True)
    by_type={}
    for r in RESOURCE_DATA:
        t=r["type"]; by_type.setdefault(t,[]).append(r)
    c1,c2,c3,c4 = st.columns(4)
    total=len(RESOURCE_DATA); avail=sum(1 for r in RESOURCE_DATA if r["status"]=="Available")
    deployed=sum(1 for r in RESOURCE_DATA if r["status"]=="Deployed"); types=len(by_type)
    for col,cls,val,lbl in [(c1,"mc-blue",total,"TOTAL RESOURCES"),(c2,"mc-green",avail,"AVAILABLE"),(c3,"mc-orange",deployed,"DEPLOYED"),(c4,"mc-purple",types,"RESOURCE TYPES")]:
        with col: st.markdown(f'<div class="mc {cls}"><div class="mc-val">{val}</div><div class="mc-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    f_type=st.selectbox("Filter by Type",["All"]+sorted(by_type.keys()),key="res_type")
    filtered=[r for r in RESOURCE_DATA if f_type=="All" or r["type"]==f_type]
    for r in filtered:
        sc={"Available":"#10b981","Deployed":"#f59e0b","Standby":"#3b82f6"}.get(r["status"],"#64748b")
        st.markdown(f"""<div class="res-card">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <div>
              <span style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#e2e8f0;font-size:.9rem;">{r['unit']}</span>
              <span style="font-size:.75rem;color:#64748b;margin-left:10px;">🏷️ {r['type']}</span>
            </div>
            <span class="s-badge" style="background:{sc}20;color:{sc};border:1px solid {sc}44;">{r['status']}</span>
          </div>
          <div style="font-size:.78rem;color:#64748b;margin-top:6px;">📍 {r['district']} &nbsp;·&nbsp; 📞 {r['contact']}</div>
        </div>""", unsafe_allow_html=True)

def _tab_social():
    st.markdown('<div class="sec-hdr">📡 Social Radar — AI-Powered Signal Detection</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.82rem;color:#475569;margin-bottom:14px;">Simulated real-time monitoring of social media for disaster signals across Tamil Nadu districts.</div>', unsafe_allow_html=True)
    tweets=generate_simulated_tweets(16); critical_alerts=get_critical_social_alerts(tweets); trending=detect_trending_districts(tweets)
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown(f'<div class="mc mc-red"><div class="mc-val">{len(critical_alerts)}</div><div class="mc-lbl">Critical/High Alerts</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="mc mc-orange"><div class="mc-val">{len(tweets)}</div><div class="mc-lbl">Signals Detected</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="mc mc-blue"><div class="mc-val">{trending[0][0] if trending else "—"}</div><div class="mc-lbl">Trending District</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    col1,col2=st.columns([3,1])
    with col1:
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:.78rem;color:#94a3b8;letter-spacing:1.5px;margin-bottom:10px;">INCOMING SIGNALS</div>', unsafe_allow_html=True)
        sev_colors={"CRITICAL":"#ef4444","HIGH":"#f97316","MEDIUM":"#eab308"}
        for t in tweets:
            sc=sev_colors.get(t["severity"],"#64748b"); cls="crit" if t["severity"]=="CRITICAL" else ("high" if t["severity"]=="HIGH" else "")
            st.markdown(f"""<div class="tweet-card {cls}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px;margin-bottom:6px;">
                <span style="font-size:.82rem;color:#64748b;">{t['user']}</span>
                <span class="s-badge" style="background:{sc}20;color:{sc};border:1px solid {sc}44;">{t['severity']}</span>
              </div>
              <div style="font-size:.84rem;color:#cbd5e1;line-height:1.5;margin-bottom:6px;">{t['text']}</div>
              <div style="font-size:.73rem;color:#475569;display:flex;gap:16px;flex-wrap:wrap;">
                <span>📍 {t['district']}</span><span>⚠️ {t['type']}</span>
                <span>❤️ {t['likes']}</span><span>🔁 {t['retweets']}</span><span>🕐 {t['minutes_ago']}m ago</span>
              </div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:.75rem;color:#94a3b8;letter-spacing:1.5px;margin-bottom:10px;">TRENDING DISTRICTS</div>', unsafe_allow_html=True)
        for d,cnt in trending:
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.04);font-size:.82rem;"><span style="color:#94a3b8;">{d}</span><span style="color:#e8341c;font-weight:700;">{cnt}</span></div>', unsafe_allow_html=True)

def _tab_risk():
    st.markdown('<div class="sec-hdr">🔮 Predictive Risk Forecast</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.82rem;color:#475569;margin-bottom:14px;">AI risk analysis based on historical patterns, weather simulation, and seasonal data for Tamil Nadu districts.</div>', unsafe_allow_html=True)
    statewide=get_statewide_risk_summary()
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:.78rem;color:#94a3b8;letter-spacing:1.5px;margin-bottom:10px;">TOP AT-RISK DISTRICTS</div>', unsafe_allow_html=True)
        al_colors={"CRITICAL":"#ef4444","HIGH":"#f97316","MEDIUM":"#eab308","LOW":"#22c55e"}
        for d in statewide:
            ac=al_colors.get(d["alert_level"],"#64748b")
            st.markdown(f"""<div style="background:#0d1117;border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:14px 16px;margin-bottom:8px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#e2e8f0;">{d['district']}</span>
                <span class="s-badge" style="background:{ac}20;color:{ac};border:1px solid {ac}44;">{d['alert_level']}</span>
              </div>
              <div style="font-size:.76rem;color:#64748b;">Primary risk: {d['primary_risk'].upper()} · Score: {d['max_risk_score']}</div>
              <div class="risk-bar-bg"><div class="risk-bar-fill" style="width:{d['max_risk_score']}%;background:{ac};"></div></div>
            </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:.78rem;color:#94a3b8;letter-spacing:1.5px;margin-bottom:10px;">DISTRICT DEEP ANALYSIS</div>', unsafe_allow_html=True)
        sel_d=st.selectbox("Select District",sorted(DISTRICT_RISK_PROFILES.keys()),key="risk_district")
        if sel_d:
            analysis=predict_district_risks(sel_d); w=analysis["weather"]
            st.markdown(f"""<div style="background:#0d1117;border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:16px;margin-bottom:12px;">
              <div style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#94a3b8;font-size:.75rem;letter-spacing:1.5px;margin-bottom:10px;">CURRENT WEATHER SIM</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:.8rem;color:#94a3b8;">
                <div>🌧️ Rainfall: <strong style="color:#e2e8f0;">{w['rainfall_mm']}mm</strong></div>
                <div>🌡️ Temp: <strong style="color:#e2e8f0;">{w['temperature_c']}°C</strong></div>
                <div>💨 Wind: <strong style="color:#e2e8f0;">{w['wind_kmh']} km/h</strong></div>
                <div>💧 Humidity: <strong style="color:#e2e8f0;">{w['humidity_pct']}%</strong></div>
              </div></div>""", unsafe_allow_html=True)
            rc={"flood":"#3b82f6","cyclone":"#8b5cf6","fire":"#ef4444","landslide":"#92400e","earthquake":"#f59e0b","drought":"#84cc16"}
            for risk_type,rdata in analysis["risks"].items():
                c=rc.get(risk_type,"#64748b")
                st.markdown(f"""<div style="margin-bottom:8px;">
                  <div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:4px;">
                    <span style="color:#94a3b8;text-transform:capitalize;">{risk_type}</span>
                    <span style="color:{c};font-weight:700;">{rdata['level']} ({rdata['score']}%)</span>
                  </div>
                  <div class="risk-bar-bg"><div class="risk-bar-fill" style="width:{rdata['score']}%;background:{c};"></div></div>
                </div>""", unsafe_allow_html=True)

def _tab_shelters():
    st.markdown('<div class="sec-hdr">🏕️ Relief Shelter Status</div>', unsafe_allow_html=True)
    total_cap=sum(s["capacity"] for s in SHELTER_CAMPS); total_occ=sum(s["occupied"] for s in SHELTER_CAMPS)
    total_avail=total_cap-total_occ; full_count=sum(1 for s in SHELTER_CAMPS if s["occupied"]>=s["capacity"])
    c1,c2,c3,c4=st.columns(4)
    for col,cls,val,lbl in [(c1,"mc-blue",len(SHELTER_CAMPS),"TOTAL CAMPS"),(c2,"mc-green",f"{total_avail:,}","SPACES AVAILABLE"),(c3,"mc-yellow",f"{int(total_occ/max(total_cap,1)*100)}%","OCCUPANCY"),(c4,"mc-red",full_count,"CAMPS FULL")]:
        with col: st.markdown(f'<div class="mc {cls}"><div class="mc-val">{val}</div><div class="mc-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    f_dist=st.selectbox("Filter by District",["All"]+sorted(set(s["district"] for s in SHELTER_CAMPS)),key="sh_dist")
    filtered=[s for s in SHELTER_CAMPS if f_dist=="All" or s["district"]==f_dist]
    filtered.sort(key=lambda x: x["occupied"]/max(x["capacity"],1), reverse=True)
    for s in filtered:
        avail=s["capacity"]-s["occupied"]; occ_p=int(s["occupied"]/max(s["capacity"],1)*100)
        is_full=avail<=0; c="#ef4444" if is_full else ("#f59e0b" if avail<50 else "#10b981")
        chip="FULL" if is_full else f"{avail} available"
        st.markdown(f"""<div class="shelter-card" style="border-color:{c}22;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px;">
            <span style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#e2e8f0;">{s['name']}</span>
            <span class="s-badge" style="background:{c}20;color:{c};border:1px solid {c}44;">{chip.upper()}</span>
          </div>
          <div style="font-size:.78rem;color:#64748b;margin-bottom:8px;">📍 {s['district']} · 🏷️ {s['type']} · 📞 {s['contact']}</div>
          <div style="background:#1e293b;border-radius:6px;height:6px;overflow:hidden;">
            <div style="width:{occ_p}%;background:{c};height:6px;border-radius:6px;"></div>
          </div>
          <div style="font-size:.73rem;color:#475569;margin-top:4px;">{s['occupied']}/{s['capacity']} occupied · {occ_p}%</div>
        </div>""", unsafe_allow_html=True)

def _tab_teams(teams, reports, client):
    st.markdown('<div class="sec-hdr">👥 Rescue Teams Registry</div>', unsafe_allow_html=True)
    if not teams:
        st.warning("No teams in database. Run `supabase_setup.sql` to insert sample teams.")
        return
    avail_c=sum(1 for t in teams if t.get("is_available")); busy_c=len(teams)-avail_c
    c1,c2,c3=st.columns(3)
    with c1: st.markdown(f'<div class="mc mc-green"><div class="mc-val">{avail_c}</div><div class="mc-lbl">Available</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="mc mc-red"><div class="mc-val">{busy_c}</div><div class="mc-lbl">On Mission</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="mc mc-blue"><div class="mc-val">{len(teams)}</div><div class="mc-lbl">Total Teams</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    for t in teams:
        ac="#10b981" if t.get("is_available") else "#ef4444"; at="AVAILABLE" if t.get("is_available") else "ON MISSION"
        asgn=t.get("current_assignment") or "—"
        st.markdown(f"""<div class="team-card">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <div>
              <span style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#e2e8f0;">{t.get('name','')}</span>
              <span style="font-size:.73rem;color:#475569;margin-left:8px;">{t.get('id','')}</span>
            </div>
            <span style="font-size:.75rem;font-weight:700;color:{ac};">● {at}</span>
          </div>
          <div style="font-size:.78rem;color:#64748b;margin-top:6px;">🏷️ {t.get('type','')} · 📍 {t.get('district','')} · 📋 Assignment: {asgn}</div>
        </div>""", unsafe_allow_html=True)
