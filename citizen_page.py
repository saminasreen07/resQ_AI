"""
ResQAI TN — Citizen Dashboard  (v4 — session_state bug fixed, premium UI)
BUG FIX: widget keys (w_*) are separated from storage keys (s_*) so
         Streamlit never sees "duplicate widget key" and name/phone/location
         are always saved correctly and shown in the review page.
"""
import streamlit as st, random, math
from datetime import datetime
from supabase_client import get_client
from priority_ai import calculate_priority, get_priority_color, get_priority_response

TN_DISTRICTS = [
    "Ariyalur","Chengalpattu","Chennai","Coimbatore","Cuddalore",
    "Dharmapuri","Dindigul","Erode","Kallakurichi","Kancheepuram",
    "Kanyakumari","Karur","Krishnagiri","Madurai","Mayiladuthurai",
    "Nagapattinam","Namakkal","Nilgiris","Perambalur","Pudukkottai",
    "Ramanathapuram","Ranipet","Salem","Sivaganga","Tenkasi","Thanjavur",
    "Theni","Tiruchirappalli","Tirunelveli","Tirupathur","Tiruppur",
    "Tiruvallur","Tiruvannamalai","Tiruvarur","Thoothukudi","Vellore",
    "Villupuram","Virudhunagar",
]
DISTRICT_COORDS = {
    "Chennai":(13.0827,80.2707),"Coimbatore":(11.0168,76.9558),"Madurai":(9.9252,78.1198),
    "Tiruchirappalli":(10.7905,78.7047),"Salem":(11.6643,78.1460),"Tirunelveli":(8.7139,77.7567),
    "Vellore":(12.9165,79.1325),"Erode":(11.3410,77.7172),"Thanjavur":(10.7870,79.1378),
    "Cuddalore":(11.7447,79.7680),"Kancheepuram":(12.8185,79.6947),"Nagapattinam":(10.7672,79.8449),
    "Nilgiris":(11.4064,76.6932),"Dindigul":(10.3624,77.9695),"Tiruppur":(11.1085,77.3411),
    "Kanyakumari":(8.0883,77.5385),"Thoothukudi":(8.7642,78.1348),"Ramanathapuram":(9.3639,78.8395),
    "Pudukkottai":(10.3797,78.8219),"Sivaganga":(9.8476,78.4800),"Virudhunagar":(9.5851,77.9624),
    "Theni":(10.0104,77.4770),"Namakkal":(11.2195,78.1678),"Karur":(10.9601,78.0766),
    "Dharmapuri":(12.1211,78.1582),"Krishnagiri":(12.5186,78.2137),"Tiruvannamalai":(12.2253,79.0747),
    "Villupuram":(11.9395,79.4913),"Ariyalur":(11.1401,79.0760),"Perambalur":(11.2344,78.8808),
    "Tiruvarur":(10.7677,79.6364),"Mayiladuthurai":(11.1018,79.6516),"Tiruvallur":(13.1437,79.9085),
    "Chengalpattu":(12.6921,79.9729),"Ranipet":(12.9375,79.3327),"Kallakurichi":(11.7384,78.9600),
    "Tenkasi":(8.9594,77.3152),"Tirupathur":(12.4960,78.5680),
}
DISASTER_NEEDS = {
    "Flood":{"icon":"🌊","color":"#3b82f6","desc":"Floodwater rises fast — report exact needs.","needs":[
        {"key":"boat_rescue","label":"🚤 Boat Rescue"},{"key":"pump_dewater","label":"💧 Dewatering Pump"},
        {"key":"medical","label":"🏥 Medical Aid"},{"key":"food_water","label":"🍱 Food & Water"},
        {"key":"shelter","label":"🏕️ Emergency Shelter"},{"key":"evacuation","label":"🚌 Evacuation"},
    ]},
    "Cyclone":{"icon":"🌀","color":"#8b5cf6","desc":"Seek shelter immediately.","needs":[
        {"key":"shelter","label":"🏕️ Emergency Shelter"},{"key":"evacuation","label":"🚌 Evacuation"},
        {"key":"medical","label":"🏥 Medical Aid"},{"key":"food_water","label":"🍱 Food & Water"},
        {"key":"power_restore","label":"⚡ Power Restoration"},{"key":"debris_clear","label":"🚜 Debris Clearing"},
    ]},
    "Fire":{"icon":"🔥","color":"#ef4444","desc":"Move away from fire, report location.","needs":[
        {"key":"firefighting","label":"🚒 Fire Fighting"},{"key":"evacuation","label":"🚌 Evacuation"},
        {"key":"medical","label":"🏥 Medical/Burns"},{"key":"shelter","label":"🏕️ Emergency Shelter"},
        {"key":"food_water","label":"🍱 Food & Water"},{"key":"gas_leak","label":"⚠️ Gas Leak Control"},
    ]},
    "Landslide":{"icon":"⛰️","color":"#92400e","desc":"Stay away from slopes.","needs":[
        {"key":"heavy_machinery","label":"🚜 JCB/Heavy Machinery"},{"key":"medical","label":"🏥 Medical Aid"},
        {"key":"search_rescue","label":"🔦 Search & Rescue"},{"key":"shelter","label":"🏕️ Shelter"},
        {"key":"road_clear","label":"🛣️ Road Clearing"},{"key":"food_water","label":"🍱 Food & Water"},
    ]},
    "Earthquake":{"icon":"🫨","color":"#f59e0b","desc":"Move to open ground immediately.","needs":[
        {"key":"search_rescue","label":"🔦 Search & Rescue"},{"key":"medical","label":"🏥 Medical Aid"},
        {"key":"heavy_machinery","label":"🚜 Heavy Machinery"},{"key":"shelter","label":"🏕️ Emergency Shelter"},
        {"key":"food_water","label":"🍱 Food & Water"},{"key":"structural_check","label":"🏗️ Structural Safety"},
    ]},
    "Tsunami":{"icon":"🌊","color":"#06b6d4","desc":"Move to higher ground immediately.","needs":[
        {"key":"boat_rescue","label":"🚤 Boat Rescue"},{"key":"evacuation","label":"🚌 Evacuation"},
        {"key":"medical","label":"🏥 Medical Aid"},{"key":"food_water","label":"🍱 Food & Water"},
        {"key":"shelter","label":"🏕️ Emergency Shelter"},{"key":"missing_persons","label":"🔍 Missing Persons"},
    ]},
}
STATUS_TIMELINE = [
    ("REPORTED","📥","Report received by system"),
    ("ACKNOWLEDGED","👁️","Authority has reviewed your report"),
    ("TEAM_ASSIGNED","👥","Rescue team has been assigned"),
    ("EN_ROUTE","🚗","Team is travelling to you"),
    ("ON_SITE","📍","Team has arrived at your location"),
    ("RESOLVED","✅","Situation resolved"),
]
ALL_NEED_KEYS = ["boat_rescue","pump_dewater","medical","food_water","shelter","evacuation",
                 "power_restore","debris_clear","firefighting","gas_leak","heavy_machinery",
                 "search_rescue","road_clear","structural_check","missing_persons"]

def _gen_id():
    return f"TN-{''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789',k=8))}"

def _css():
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');
.c-wrap{max-width:860px;margin:0 auto;padding:0 4px 40px}
.c-hero{background:linear-gradient(135deg,#0c0f18,#160810,#0c0f18);border:1px solid rgba(232,52,28,.2);border-radius:24px;padding:48px 40px 36px;margin-bottom:28px;text-align:center;position:relative;overflow:hidden}
.c-hero::before{content:'';position:absolute;top:-80px;right:-80px;width:300px;height:300px;background:radial-gradient(circle,rgba(232,52,28,.1),transparent 65%);border-radius:50%;pointer-events:none}
.c-hero-chip{display:inline-flex;align-items:center;gap:8px;background:rgba(232,52,28,.12);border:1px solid rgba(232,52,28,.35);color:#e8341c;border-radius:30px;padding:6px 18px;font-family:'Rajdhani',sans-serif;font-weight:700;font-size:.78rem;letter-spacing:2px;margin-bottom:16px}
.c-dot{width:7px;height:7px;background:#e8341c;border-radius:50%;animation:blink 1.4s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.c-hero-title{font-family:'Rajdhani',sans-serif;font-size:2.3rem;font-weight:700;color:#f8fafc;line-height:1.1;margin:0 0 10px}
.c-hero-title span{color:#e8341c}
.c-hero-sub{color:#94a3b8;font-size:.88rem;margin:0;line-height:1.7}
.c-hotlines{display:flex;justify-content:center;gap:20px;flex-wrap:wrap;margin-top:18px;padding-top:16px;border-top:1px solid rgba(255,255,255,.06)}
.c-hotline{font-size:.76rem;color:#475569}.c-hotline span{color:#94a3b8;font-weight:600}
.step-bar{display:flex;border-radius:14px;overflow:hidden;margin-bottom:24px;border:1px solid rgba(255,255,255,.07)}
.s-item{flex:1;padding:13px 6px;text-align:center;font-family:'Rajdhani',sans-serif;font-weight:700;font-size:.8rem;letter-spacing:.5px;background:#0d1117;color:#334155;border-right:1px solid rgba(255,255,255,.06);transition:all .3s}
.s-item:last-child{border-right:none}
.s-item.s-active{background:rgba(232,52,28,.12);color:#ff6b55}
.s-item.s-done{background:rgba(16,185,129,.08);color:#10b981}
.sec-lbl{font-family:'Rajdhani',sans-serif;font-weight:700;font-size:.72rem;letter-spacing:2.5px;color:#64748b;text-transform:uppercase;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,.05)}
.form-card{background:#0d1117;border:1px solid rgba(255,255,255,.08);border-radius:18px;padding:26px 28px;margin-bottom:18px}
.hint-text{color:#64748b;font-size:.8rem;margin-bottom:16px;line-height:1.5}
.dis-box{border-radius:14px;padding:14px 18px;margin:12px 0 16px;font-size:.83rem;border:1px solid}
.need-hint{background:rgba(255,255,255,.02);border:1px dashed rgba(255,255,255,.1);border-radius:12px;padding:18px;color:#475569;font-size:.84rem;text-align:center;margin:8px 0}
.review-card{background:#0d1117;border:1px solid rgba(255,255,255,.08);border-radius:18px;overflow:hidden;margin-bottom:18px}
.rv-row{display:grid;grid-template-columns:160px 1fr;border-bottom:1px solid rgba(255,255,255,.05)}
.rv-row:last-child{border-bottom:none}
.rv-key{padding:13px 18px;font-size:.78rem;color:#64748b;background:rgba(255,255,255,.02);font-weight:600;display:flex;align-items:flex-start;gap:6px}
.rv-val{padding:13px 18px;font-size:.86rem;color:#e2e8f0;line-height:1.5}
.success-wrap{background:linear-gradient(135deg,#030f06,#051209);border:2px solid rgba(16,185,129,.3);border-radius:22px;padding:44px 36px;text-align:center}
.ticket-id{font-family:'Rajdhani',sans-serif;font-size:2.4rem;font-weight:700;color:#10b981;letter-spacing:4px;display:block;margin:18px 0 8px}
.p-pill{display:inline-block;padding:5px 18px;border-radius:30px;font-family:'Rajdhani',sans-serif;font-weight:700;font-size:.86rem}
.tl-wrap{background:#0a0e17;border:1px solid rgba(255,255,255,.06);border-radius:16px;padding:18px 22px}
.tl-row{display:flex;gap:14px;padding:11px 0;border-bottom:1px solid rgba(255,255,255,.04)}
.tl-row:last-child{border-bottom:none}
.tl-ico{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.88rem;flex-shrink:0}
.tl-ico.done{background:rgba(16,185,129,.15);border:1px solid rgba(16,185,129,.4)}
.tl-ico.active{background:rgba(232,52,28,.15);border:1px solid rgba(232,52,28,.5)}
.tl-ico.pending{background:#0d1117;border:1px solid rgba(255,255,255,.07)}
.tl-lbl{font-family:'Rajdhani',sans-serif;font-weight:700;font-size:.88rem}
.tl-lbl.done{color:#10b981}.tl-lbl.active{color:#e8341c}.tl-lbl.pending{color:#1e293b}
.tl-desc{font-size:.73rem;color:#334155;margin-top:2px}
.tl-ts{font-size:.72rem;color:#10b981;margin-top:2px}
.stTextInput>div>input,.stTextArea>div>textarea,.stNumberInput>div>input{background:#0d1117!important;border:1px solid rgba(255,255,255,.12)!important;color:#e2e8f0!important;border-radius:12px!important;font-size:.9rem!important}
.stTextInput>div>input:focus,.stTextArea>div>textarea:focus{border-color:rgba(232,52,28,.5)!important;box-shadow:0 0 0 3px rgba(232,52,28,.08)!important}
.stTextInput label,.stTextArea label,.stNumberInput label,.stSelectbox label{color:#94a3b8!important;font-size:.84rem!important;font-weight:500!important}
.stCheckbox span{color:#cbd5e1!important;font-size:.88rem!important}
.stSelectbox>div>div{background:#0d1117!important;border:1px solid rgba(255,255,255,.12)!important;color:#e2e8f0!important;border-radius:12px!important}
.stButton>button{background:linear-gradient(135deg,#b91c1c,#e8341c)!important;color:white!important;border:none!important;border-radius:12px!important;font-family:'Rajdhani',sans-serif!important;font-size:1rem!important;font-weight:700!important;letter-spacing:1px!important;padding:12px 28px!important;width:100%!important;transition:all .2s!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 28px rgba(232,52,28,.38)!important}
.streamlit-expanderHeader{color:#94a3b8!important;font-size:.88rem!important}
</style>""", unsafe_allow_html=True)

def show_citizen_page():
    _css()
    st.markdown('<div class="c-wrap">', unsafe_allow_html=True)
    if st.session_state.get("report_submitted"):
        _show_success(); st.markdown('</div>', unsafe_allow_html=True); return

    with st.expander("🔍 Already reported? Track your ticket here", expanded=False):
        _tracker()

    st.markdown("""<div class="c-hero">
      <div class="c-hero-chip"><div class="c-dot"></div>EMERGENCY REPORTING SYSTEM</div>
      <h1 class="c-hero-title">Report a Disaster,<br><span>Get Help Fast</span></h1>
      <p class="c-hero-sub">AI-powered priority engine · Tamil Nadu SDMA · Available 24/7<br>
      Your report is instantly reviewed and teams dispatched based on AI priority scoring.</p>
      <div class="c-hotlines">
        <div class="c-hotline">🚒 SDMA: <span>1070</span></div>
        <div class="c-hotline">🚑 Ambulance: <span>108</span></div>
        <div class="c-hotline">🔥 Fire: <span>101</span></div>
        <div class="c-hotline">👮 Police: <span>100</span></div>
        <div class="c-hotline">🆘 NDRF: <span>011-24363260</span></div>
      </div></div>""", unsafe_allow_html=True)

    step = st.session_state.get("form_step", 1)
    labels = ["1 · Personal","2 · Location","3 · Disaster","4 · Review & Submit"]
    bar = '<div class="step-bar">'
    for i, lbl in enumerate(labels, 1):
        cls = "s-done" if i < step else ("s-active" if i == step else "")
        pfx = "✓ " if i < step else ""
        bar += f'<div class="s-item {cls}">{pfx}{lbl}</div>'
    bar += '</div>'
    st.markdown(bar, unsafe_allow_html=True)

    if step == 1:   _step1()
    elif step == 2: _step2()
    elif step == 3: _step3()
    elif step == 4: _step4()
    st.markdown('</div>', unsafe_allow_html=True)

def _step1():
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-lbl">👤 Personal Information</div>', unsafe_allow_html=True)
    st.markdown('<div class="hint-text">Your details help rescue teams contact you and confirm your identity. All information is kept confidential.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full Name *", key="w_name",
                             value=st.session_state.get("s_name",""), placeholder="e.g. Ravi Kumar")
    with c2:
        phone = st.text_input("Mobile Number (10 digits) *", key="w_phone",
                              value=st.session_state.get("s_phone",""), placeholder="9876543210", max_chars=10)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Continue to Location →", key="btn_s1"):
        if not name.strip(): st.error("⚠️ Full name is required"); return
        if not phone.strip().isdigit() or len(phone.strip()) != 10: st.error("⚠️ Enter a valid 10-digit mobile number"); return
        st.session_state["s_name"] = name.strip()
        st.session_state["s_phone"] = phone.strip()
        st.session_state["form_step"] = 2; st.rerun()

def _step2():
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-lbl">📍 Location Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="hint-text">The more precise your location, the faster rescue teams can reach you. Include street names and landmarks.</div>', unsafe_allow_html=True)
    prev_d = st.session_state.get("s_district","— Select District —")
    opts = ["— Select District —"] + TN_DISTRICTS
    d_idx = opts.index(prev_d) if prev_d in opts else 0
    c1, c2 = st.columns(2)
    with c1: district = st.selectbox("District *", opts, index=d_idx, key="w_district")
    with c2: people = st.number_input("People Affected *", min_value=1, max_value=100000,
                                       value=int(st.session_state.get("s_people",1)), step=1, key="w_people")
    location = st.text_input("Exact Location / Landmark *", key="w_location",
                              value=st.session_state.get("s_location",""),
                              placeholder="e.g. Near Adyar Bridge, behind GH Hospital, Anna Nagar 3rd Street")
    st.markdown('</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back", key="btn_s2b"): st.session_state["form_step"] = 1; st.rerun()
    with c2:
        if st.button("Continue to Disaster →", key="btn_s2"):
            if district == "— Select District —": st.error("⚠️ Please select your district"); return
            if not location.strip(): st.error("⚠️ Please enter your exact location or landmark"); return
            st.session_state["s_district"] = district
            st.session_state["s_location"] = location.strip()
            st.session_state["s_people"] = int(people)
            st.session_state["form_step"] = 3; st.rerun()

def _step3():
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-lbl">⚠️ Disaster Type & Emergency Needs</div>', unsafe_allow_html=True)
    prev_d = st.session_state.get("s_disaster","— Select Type —")
    opts = ["— Select Type —","Flood","Cyclone","Fire","Landslide","Earthquake","Tsunami"]
    d_idx = opts.index(prev_d) if prev_d in opts else 0
    disaster = st.selectbox("What type of disaster is this? *", opts, index=d_idx, key="w_disaster")
    needs = {}
    if disaster in DISASTER_NEEDS:
        info = DISASTER_NEEDS[disaster]
        c = info["color"]
        st.markdown(f'<div class="dis-box" style="background:{c}0d;border-color:{c}44;"><strong style="color:{c};font-size:.9rem;">{info["icon"]} {disaster} detected</strong><div style="color:#94a3b8;font-size:.78rem;margin-top:4px;">{info["desc"]}</div></div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#94a3b8;font-size:.82rem;margin-bottom:10px;font-weight:500;">✅ Select all emergency needs that apply:</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, nd in enumerate(info["needs"]):
            with cols[i%2]:
                needs[nd["key"]] = st.checkbox(nd["label"], value=st.session_state.get(f"sn_{nd['key']}",False), key=f"wn_{nd['key']}")
    else:
        st.markdown('<div class="need-hint">⬆️ Select a disaster type above to see specific emergency need options</div>', unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1: needs["medical"] = st.checkbox("🏥 Medical Aid", key="wn_medical")
        with c2: needs["food_water"] = st.checkbox("🍱 Food & Water", key="wn_food_water")
        with c3: needs["shelter"] = st.checkbox("🏕️ Shelter", key="wn_shelter")
    st.markdown('<div class="sec-lbl" style="margin-top:20px;">📝 Describe the Situation</div>', unsafe_allow_html=True)
    desc = st.text_area("Describe what is happening *", height=110,
                         value=st.session_state.get("s_desc",""),
                         placeholder="How serious? How many trapped? Street names, landmarks, what help is needed most urgently...",
                         key="w_desc")
    st.markdown('</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back", key="btn_s3b"): st.session_state["form_step"] = 2; st.rerun()
    with c2:
        if st.button("Review & Submit →", key="btn_s3"):
            if disaster == "— Select Type —": st.error("⚠️ Please select the disaster type"); return
            if not desc.strip() or len(desc.strip()) < 10: st.error("⚠️ Please describe the situation (at least 10 characters)"); return
            st.session_state["s_disaster"] = disaster
            st.session_state["s_needs"] = needs
            st.session_state["s_desc"] = desc.strip()
            for k, v in needs.items(): st.session_state[f"sn_{k}"] = v
            st.session_state["form_step"] = 4; st.rerun()

def _step4():
    name=st.session_state.get("s_name",""); phone=st.session_state.get("s_phone","")
    district=st.session_state.get("s_district",""); location=st.session_state.get("s_location","")
    people=int(st.session_state.get("s_people",1)); disaster=st.session_state.get("s_disaster","")
    needs=st.session_state.get("s_needs",{}); desc=st.session_state.get("s_desc","")
    active = [k.replace("_"," ").title() for k,v in needs.items() if v]
    st.markdown('<div class="sec-lbl">📋 Review Your Report Before Submitting</div>', unsafe_allow_html=True)
    if not name or not phone: st.error("⚠️ Name or phone is missing — please go back to Step 1 and fill them in")
    rows = [
        ("👤 Name", name or "⚠️ MISSING"),("📞 Phone", phone or "⚠️ MISSING"),
        ("📍 District", district),("🗺️ Location", location or "⚠️ MISSING"),
        ("⚠️ Disaster", f'<span style="color:#e8341c;font-weight:700;">{disaster}</span>'),
        ("👥 People", f"{people:,} people"),
        ("🆘 Needs", ", ".join(active) if active else "<em style='color:#475569;'>None selected</em>"),
        ("📝 Description", desc),
    ]
    html = '<div class="review-card">'
    for k, v in rows:
        html += f'<div class="rv-row"><div class="rv-key">{k}</div><div class="rv-val">{v}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Edit Report", key="btn_s4b"): st.session_state["form_step"] = 3; st.rerun()
    with c2:
        if st.button("🚨 Submit Emergency Report", key="btn_submit"):
            if not name or not phone or not district or not location or not disaster:
                st.error("⚠️ Required fields are missing. Go back and fill in Name, Phone, Location, and Disaster Type.")
            else: _submit(name,phone,district,location,people,disaster,needs,desc)

def _submit(name,phone,district,location,people,disaster,needs,desc):
    base=DISTRICT_COORDS.get(district,(10.0,78.0))
    lat=round(base[0]+random.uniform(-.12,.12),4); lon=round(base[1]+random.uniform(-.12,.12),4)
    medical="Yes" if needs.get("medical") else "No"
    food="Yes" if needs.get("food_water") else "No"
    shelter="Yes" if needs.get("shelter") else "No"
    needs_str=",".join(k for k,v in needs.items() if v)
    priority,score=calculate_priority({"disaster":disaster,"people":people,"medical":medical,"food":food,"shelter":shelter})
    tid=_gen_id(); now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row={"id":tid,"name":name,"phone":phone,"district":district,"location":location,
         "disaster":disaster,"people":people,"medical":medical,"food":food,"shelter":shelter,
         "specific_needs":needs_str,"description":desc,"priority":priority,"priority_score":score,
         "status":"REPORTED","lat":lat,"lon":lon,"created_at":now,"status_updated_at":now}
    try:
        client=get_client()
        client.table("reports").insert(row).execute()
        client.table("status_history").insert({"report_id":tid,"status":"REPORTED","updated_by":"citizen","timestamp":now,"note":"Submitted via ResQAI TN citizen portal"}).execute()
        st.session_state.update({"report_submitted":True,"sub_ticket":tid,"sub_priority":priority,"sub_score":score,"sub_response":get_priority_response(priority)})
        for k in ["form_step","s_name","s_phone","s_district","s_location","s_people","s_disaster","s_needs","s_desc"]+[f"sn_{k}" for k in ALL_NEED_KEYS]: st.session_state.pop(k,None)
        st.rerun()
    except Exception as e:
        st.error(f"❌ Could not save report. Check your Supabase credentials.\n\n`{e}`")

def _show_success():
    ticket=st.session_state.get("sub_ticket",""); priority=st.session_state.get("sub_priority","")
    score=st.session_state.get("sub_score",0); resp=st.session_state.get("sub_response","")
    pc=get_priority_color(priority)
    st.markdown(f"""<div class="success-wrap">
      <div style="font-size:3rem;margin-bottom:10px;">✅</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:1.8rem;font-weight:700;color:#10b981;margin-bottom:6px;">Report Submitted Successfully!</div>
      <div style="color:#475569;font-size:.88rem;margin-bottom:24px;">Registered with Tamil Nadu SDMA · Rescue teams are being notified</div>
      <span class="ticket-id">{ticket}</span>
      <div style="color:#475569;font-size:.82rem;margin-bottom:22px;">📸 Screenshot this Ticket ID to track your report status</div>
      <div style="margin-bottom:16px;">AI Priority: <span class="p-pill" style="background:{pc}20;color:{pc};border:1px solid {pc}44;">{priority} (Score: {score}/14)</span></div>
      <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:14px 24px;display:inline-block;color:#94a3b8;font-size:.86rem;">
        ⏱ Estimated Response: <strong style="color:#e2e8f0;">{resp}</strong>
      </div></div><div style="height:20px;"></div>""", unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        if st.button("📝 Submit Another Report"):
            st.session_state.pop("report_submitted",None); st.session_state["form_step"]=1; st.rerun()
    with c2:
        if st.button("🏠 Back to Home"):
            st.session_state["page"]="home"; st.session_state.pop("report_submitted",None); st.rerun()

def _tracker():
    st.markdown('<div style="color:#94a3b8;font-size:.84rem;margin-bottom:10px;">Enter the Ticket ID from your submission confirmation to track your report status in real-time.</div>', unsafe_allow_html=True)
    c1,c2=st.columns([3,1])
    with c1: tid=st.text_input("Ticket ID",placeholder="e.g. TN-ABCD1234",key="tracker_input",label_visibility="collapsed")
    with c2: go=st.button("🔍 Track",key="tracker_go",use_container_width=True)
    if not go: return
    if not tid.strip(): st.warning("Please enter a Ticket ID"); return
    try:
        client=get_client()
        res=client.table("reports").select("*").eq("id",tid.strip().upper()).execute()
        if not res.data: st.error("❌ No report found with that Ticket ID. Please check the ID."); return
        r=res.data[0]
        hist=client.table("status_history").select("*").eq("report_id",tid.strip().upper()).order("timestamp").execute()
        hist_map={h["status"]:h["timestamp"] for h in (hist.data or [])}
        pc=get_priority_color(r.get("priority","LOW"))
        s_order=[s[0] for s in STATUS_TIMELINE]; cur=r.get("status","REPORTED")
        ci=s_order.index(cur) if cur in s_order else 0
        st.markdown(f"""<div style="background:#0d1117;border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:16px 20px;margin:10px 0;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px;">
            <span style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:700;color:#f1f5f9;">{r.get('id')}</span>
            <span class="p-pill" style="background:{pc}20;color:{pc};border:1px solid {pc}44;">{r.get('priority','')}</span>
          </div>
          <div style="font-size:.82rem;color:#64748b;">⚠️ {r.get('disaster','')} &nbsp;·&nbsp; 📍 {r.get('district','')} — {r.get('location','')} &nbsp;·&nbsp; 👥 {r.get('people',0)} people</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="tl-wrap">', unsafe_allow_html=True)
        for i,(key,ico,desc) in enumerate(STATUS_TIMELINE):
            cls="done" if i<ci else ("active" if i==ci else "pending")
            ts=hist_map.get(key,""); ts_html=f'<div class="tl-ts">✓ {ts}</div>' if ts else ""
            st.markdown(f'<div class="tl-row"><div class="tl-ico {cls}">{ico}</div><div><div class="tl-lbl {cls}">{key.replace("_"," ")}</div><div class="tl-desc">{desc}</div>{ts_html}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error fetching report: {e}")
