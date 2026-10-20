import csv
import io
from datetime import datetime

import streamlit as st

from model import assess_water_quality, risk_color

st.set_page_config(
    page_title="GreenWatch",
    page_icon="GW",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Visual system ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Shadows+Into+Light+Two&display=swap');

    :root {
        --ink: #18253f;
        --muted: #65718a;
        --bg: #fbf8ff;
        --sky: #ccefff;
        --mint: #d7f6e7;
        --yellow: #fff0bf;
        --pink: #ffd7cf;
        --coral: #ff9f91;
        --blue: #55c7dc;
        --green: #5ac58b;
        --purple: #a995ff;
        --lilac: #eee9ff;
        --navy: #344b86;
    }

    /* One font system everywhere: page, sidebar, widgets, tables and controls. */
    html, body, *, [class*="css"], [data-testid], [data-baseweb],
    button, input, textarea, select, option, label, p, span, div,
    h1, h2, h3, h4, h5, h6, small, li, td, th {
        font-family: 'Shadows Into Light Two', cursive !important;
    }
    /* Keep Streamlit's own interface icons on their icon font. Without this,
       the global cartoon font can expose names such as keyboard_double_arrow_left. */
    [data-testid="stIconMaterial"], .material-symbols-rounded,
    .material-symbols-outlined, .material-icons, .material-icons-outlined,
    [class*="material-symbols"], [class*="material-icons"] {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        font-weight: normal !important;
        letter-spacing: normal !important;
    }
    html { font-size: 18px; }
    body, h1, h2, h3, h4, h5, h6, p, label { color: var(--ink); }
    .stApp { background: radial-gradient(circle at 6% 8%, #ffe1d9 0, transparent 25%), radial-gradient(circle at 96% 12%, #d7f3ff 0, transparent 28%), radial-gradient(circle at 80% 92%, #e9ddff 0, transparent 28%), var(--bg); }
    .block-container { max-width: 1160px; padding-top: 2.4rem; padding-bottom: 4.5rem; }
    [data-testid="stVerticalBlock"] { gap: 1rem; }
    [data-testid="column"] { padding: .25rem .45rem; }
    h1, h2, h3 { color: var(--ink); letter-spacing: .3px; font-weight: 800 !important; }
    h1 { font-size: clamp(3.2rem, 7vw, 5.7rem) !important; line-height: .98; letter-spacing: -1.5px; margin: .35rem 0 1.15rem !important; }
    h2 { font-size: 2.55rem !important; margin: .25rem 0 1rem !important; }
    h3 { font-size: 1.65rem !important; margin: .1rem 0 .7rem !important; }
    p, label, .stMarkdown, .stButton button, .stSelectbox, .stNumberInput,
    [data-testid="stCaptionContainer"], [data-testid="stWidgetLabel"] { font-size: 1.12rem; }

    [data-testid="stSidebar"] { background: linear-gradient(180deg, #eef9ff 0%, #f0ebff 55%, #fff3dd 100%); border-right: 1px solid rgba(52,75,134,.14); min-width: 330px; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: var(--ink) !important; }
    [data-testid="stSidebar"] .stRadio label { font-size: 1.15rem; font-weight: 800; }
    [data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"] { gap: 14px; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        position: relative; display: flex; align-items: center; min-height: 76px;
        padding: 15px 16px !important; margin: 0 !important; border: 3px solid var(--ink);
        border-radius: 24px; background: #ffffff; box-shadow: 5px 5px 0 rgba(24,37,63,.9);
        transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
        overflow: visible;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label::after {
        content: ''; position: absolute; inset: 5px; border: 2px dashed rgba(24,37,63,.35);
        border-radius: 17px; pointer-events: none;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { transform: translate(-3px,-3px) rotate(-1deg); box-shadow: 8px 8px 0 rgba(24,37,63,.9); }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) { background: var(--yellow); transform: translate(-2px,-2px) rotate(1deg); box-shadow: 7px 7px 0 rgba(24,37,63,.9); }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:nth-child(1) { background: #d7f6e7; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:nth-child(2) { background: #ccefff; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:nth-child(3) { background: #eee9ff; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:nth-child(4) { background: #ffd7cf; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked)::before { content: '●'; position: absolute; right: 14px; top: 8px; font-size: 1.1rem; z-index: 2; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label p { font-size: 1.35rem !important; font-weight: 800; z-index: 1; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label input { accent-color: var(--ink); transform: scale(1.35); margin-right: 10px; }

    .hero { min-height: 390px; border: 1px solid rgba(52,75,134,.12); border-radius: 42px; padding: 4.4rem 4.5rem; margin-bottom: 2.2rem; background: linear-gradient(125deg, #d6f5ff 0%, #eee7ff 54%, #ffe1d6 100%); box-shadow: 0 25px 60px rgba(67, 66, 120, .16); position: relative; overflow: hidden; display: flex; align-items: center; }
    .hero:before { content: ''; position: absolute; width: 300px; height: 300px; right: -70px; bottom: -110px; border-radius: 50%; background: rgba(255,255,255,.48); }
    .hero:after { content: '◦  •  ◦'; position: absolute; right: 34px; top: 24px; color: rgba(255,255,255,.9); font-size: 3rem; letter-spacing: 12px; }
    .hero h1 { margin: 0; }
    .hero p { max-width: 780px; color: #42577b; font-size: 1.5rem; margin: 1.1rem 0 0; line-height: 1.35; }
    .eyebrow { text-transform: uppercase; font-size: 1rem; letter-spacing: 2px; color: #5268a0; font-weight: 700; margin-bottom: .45rem; }

    .card { position: relative; background: rgba(255,255,255,.8); border: 1px solid rgba(52,75,134,.14); border-radius: 32px; padding: 2.2rem 2.35rem; min-height: 190px; box-shadow: 0 18px 42px rgba(67, 66, 120, .1); margin-bottom: 1.6rem; backdrop-filter: blur(10px); }
    .card h3 { margin: 0 0 .25rem; }
    .card p { color: var(--muted); margin: 0; }
    .card.card-peach { background: #ffe0d8; border: 3px solid #d96f65; box-shadow: inset 0 0 0 3px rgba(255,255,255,.42), 7px 7px 0 #d96f65; }
    .card.card-aqua { background: #d5f4fb; border: 3px solid #4a9eb4; box-shadow: inset 0 0 0 3px rgba(255,255,255,.48), 7px 7px 0 #4a9eb4; }
    .card.card-lavender { background: #ebe5ff; border: 3px solid #7966c2; box-shadow: inset 0 0 0 3px rgba(255,255,255,.48), 7px 7px 0 #7966c2; }
    .card.card-mint { background: #d9f5e5; border: 3px solid #4b9d72; box-shadow: inset 0 0 0 3px rgba(255,255,255,.48), 7px 7px 0 #4b9d72; }
    .card.card-sun { background: #fff0bd; border: 3px solid #c89c43; box-shadow: inset 0 0 0 3px rgba(255,255,255,.48), 7px 7px 0 #c89c43; }
    .card.card-rose { background: #ffd9e5; border: 3px solid #bd6586; box-shadow: inset 0 0 0 3px rgba(255,255,255,.48), 7px 7px 0 #bd6586; }
    .card.card-peach::after, .card.card-aqua::after, .card.card-lavender::after, .card.card-mint::after, .card.card-sun::after, .card.card-rose::after { content: '•  ·  •'; position: absolute; right: 18px; top: 8px; color: rgba(24,37,63,.35); font-size: 1.4rem; letter-spacing: 5px; }
    .metric-card { text-align: center; background: linear-gradient(145deg,#f7f5ff,#e4f8ff); }
    .metric-number { font-size: 3.8rem; color: var(--navy); line-height: 1; font-weight: bold; }
    .metric-label { color: var(--muted); font-size: 1.1rem; }
    .tip { background: linear-gradient(135deg,#fff4ca,#ffe3df); border: 1px solid rgba(52,75,134,.14); border-radius: 22px; padding: 1.4rem 1.6rem; box-shadow: 0 10px 26px rgba(67, 66, 120, .08); }
    .success-box { background: linear-gradient(135deg,#ddf9e9,#d8f1ff); border: 1px solid rgba(52,75,134,.14); border-radius: 22px; padding: 1.4rem 1.6rem; box-shadow: 0 10px 26px rgba(67, 66, 120, .08); }
    .footer { text-align: center; color: var(--muted); padding: 3rem 0 1rem; font-size: 1rem; }
    .brand { display: inline-block; background: linear-gradient(135deg,#ffffff,#e8e1ff); border: 1px solid rgba(52,75,134,.12); border-radius: 18px; padding: .35rem 1rem; box-shadow: 0 8px 20px rgba(67,66,120,.12); font-size: 1.8rem; font-weight: 800; }
    .mono-icon { display: inline-grid; place-items: center; width: 1.35em; height: 1.35em; border: 2px solid var(--ink); border-radius: 50%; font-size: .8em; line-height: 1; }
    div.stButton > button, div.stDownloadButton > button { border: 0; border-radius: 18px; background: linear-gradient(135deg,var(--navy),var(--purple)); color: white !important; font-weight: 800; padding: .95rem 1.5rem; box-shadow: 0 10px 20px rgba(52,75,134,.22); transition: transform .2s, box-shadow .2s; }
    div.stButton > button *, div.stDownloadButton > button * { color: white !important; }
    div.stButton > button:hover, div.stDownloadButton > button:hover { background: linear-gradient(135deg,#263b73,#8064dc); color: white !important; transform: translateY(-3px); box-shadow: 0 15px 24px rgba(52,75,134,.28); }
    [data-testid="stMetric"] { background: rgba(255,255,255,.8); border: 1px solid rgba(52,75,134,.14); border-radius: 24px; padding: 1.4rem; box-shadow: 0 12px 28px rgba(67, 66, 120, .1); }
    input, textarea, select, [data-baseweb="select"] > div, [data-baseweb="input"] > div { border: 1px solid rgba(52,75,134,.22) !important; border-radius: 16px !important; background: rgba(255,255,255,.9) !important; min-height: 48px; font-family: 'Shadows Into Light Two', cursive !important; font-size: 1.12rem !important; }
    input::placeholder, textarea::placeholder { font-family: 'Shadows Into Light Two', cursive !important; color: #8a91a4 !important; }
    [data-baseweb="select"] *, [data-baseweb="popover"] *, [role="listbox"] * { font-family: 'Shadows Into Light Two', cursive !important; }
    [data-testid="stExpander"] { border: 1px solid rgba(52,75,134,.14); border-radius: 24px; background: rgba(255,255,255,.72); box-shadow: 0 12px 28px rgba(67, 66, 120, .08); padding: .3rem; }
    [data-testid="stDataFrame"], [data-testid="stTable"] { border: 1px solid rgba(52,75,134,.14); border-radius: 22px; overflow: hidden; margin: .8rem 0 1rem; }
    [data-testid="stProgressBar"] { padding: .25rem 0 .8rem; }
    [data-testid="stProgressBar"] > div > div { background: linear-gradient(90deg, #5ac58b, #a995ff, #ff9f91); border-radius: 999px; }
    [data-testid="stAlert"] { border-radius: 20px; margin: 1rem 0; }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] { font-family: 'Shadows Into Light Two', cursive !important; }
    [data-testid="stRadio"] label, [data-testid="stCheckbox"] label, [data-testid="stSelectbox"] label { font-family: 'Shadows Into Light Two', cursive !important; }
    .hero-art { position: absolute; right: 7%; bottom: 7%; font-size: 8rem; filter: drop-shadow(0 18px 10px rgba(61,77,130,.16)); animation: floaty 4s ease-in-out infinite; }
    @keyframes floaty { 50% { transform: translateY(-12px) rotate(4deg); } }
    .slide-card { min-height: 320px; padding: 3rem; border-radius: 36px; }
    @media (max-width: 700px) {
        .block-container { padding-top: 1rem; }
        .hero { min-height: 430px; padding: 2.2rem 1.5rem; align-items: flex-start; }
        .hero-art { right: 50%; transform: translateX(50%); bottom: 5%; font-size: 7rem; }
        .hero p { font-size: 1.25rem; }
        h1 { font-size: 3.3rem !important; }
        h2 { font-size: 2rem !important; }
        .card { padding: 1.35rem; border-radius: 26px; }
        .slide-card { min-height: 390px; padding: 2rem 1.2rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- State ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ---------- Sidebar navigation ----------
with st.sidebar:
    st.markdown("<div class='brand'><span class='mono-icon'>◉</span> GreenWatch</div>", unsafe_allow_html=True)
    st.caption("Little measurements. Better decisions.")
    st.divider()
    page = st.radio(
        "Explore",
        ["⌂ Home", "◌ Water Check", "▦ My Dashboard", "✿ Learn & Act"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("### Why GreenWatch?")
    st.info("A friendly, explainable first screen for schools and communities. It runs locally and stores no personal data.")
    st.caption("GreenWatch")


def metric_card(number, label, color="#2389c9", tone="card-aqua"):
    return f"<div class='card metric-card {tone}'><div class='metric-number' style='color:{color}'>{number}</div><div class='metric-label'>{label}</div></div>"


def show_result(result, source):
    color = risk_color(result["risk"])
    st.markdown(
        f"<div class='card card-lavender' style='border-top:8px solid {color};'><h2>Screening result: <span style='color:{color}'>{result['risk']}</span></h2><p>Water source: {source} · Score: {result['score']}/100</p></div>",
        unsafe_allow_html=True,
    )
    st.progress(result["score"] / 100)
    left, right = st.columns(2)
    with left:
        st.markdown("### ◌ What influenced the score?")
        for reason in result["reasons"]:
            st.markdown(f"- {reason}")
    with right:
        st.markdown("### → Suggested next steps")
        for step in result["recommendations"]:
            st.markdown(f"- {step}")
    st.markdown(
        "<div class='tip'><b>Friendly reminder:</b> GreenWatch is an educational screening tool, not a certified laboratory test. Do not use it alone to decide whether water is safe to drink.</div>",
        unsafe_allow_html=True,
    )


# ---------- Pages ----------
if page == "⌂ Home":
    st.markdown(
        "<div class='hero'><div><div class='eyebrow'>Community water intelligence</div><h1>Make every drop count.</h1><p>GreenWatch turns simple water measurements into a colorful, understandable first step for environmental action.</p></div><div class='hero-art'>◉</div></div>",
        unsafe_allow_html=True,
    )
    a, b, c = st.columns(3)
    with a:
        st.markdown("<div class='card card-mint'><h3>◌ Simple</h3><p>Five easy measurements, one friendly result.</p></div>", unsafe_allow_html=True)
    with b:
        st.markdown("<div class='card card-aqua'><h3>◎ Explainable</h3><p>See exactly what made the score change.</p></div>", unsafe_allow_html=True)
    with c:
        st.markdown("<div class='card card-peach'><h3>⌁ Community-first</h3><p>Built for classrooms, clubs, and local groups.</p></div>", unsafe_allow_html=True)

    st.markdown("## Ready for a quick check?")
    st.markdown("Use the menu on the left to start a water check, explore your dashboard, or learn how to take action.")
    x, y = st.columns([1, 1])
    with x:
        st.markdown("<div class='success-box'><b>Our design promise</b><br>Clear guidance without pretending that a prototype can replace experts.</div>", unsafe_allow_html=True)
    with y:
        st.markdown("<div class='tip'><b>Best for a demo</b><br>Try a normal sample first, then enter concerning values to see the explanation change.</div>", unsafe_allow_html=True)

elif page == "◌ Water Check":
    st.markdown("<div class='eyebrow'>Step 1 of 1</div><h1>◌ Check your water</h1>", unsafe_allow_html=True)
    st.write("Enter readings from a test kit or classroom experiment. All fields stay on this page.")
    with st.container():
        st.markdown("<div class='card card-aqua'><h3>⌖ Sample details</h3><p>Give your observation a little context.</p></div>", unsafe_allow_html=True)
        source = st.selectbox("Water source", ["River / stream", "Lake / pond", "Well", "School fountain", "Unknown"])
        location = st.text_input("Location nickname (optional)", placeholder="e.g. North creek")
    st.markdown("### ∙ Measurements")
    col1, col2, col3 = st.columns(3)
    with col1:
        ph = st.number_input("pH", 0.0, 14.0, 7.0, 0.1, help="Acidity or alkalinity")
        turbidity = st.number_input("Turbidity (NTU)", 0.0, 500.0, 2.0, 0.5)
    with col2:
        nitrate = st.number_input("Nitrate (mg/L)", 0.0, 200.0, 5.0, 0.5)
        dissolved_oxygen = st.number_input("Dissolved oxygen (mg/L)", 0.0, 20.0, 7.0, 0.1)
    with col3:
        temperature = st.number_input("Temperature (°C)", -10.0, 60.0, 20.0, 0.5)
        st.markdown("<div class='tip'>i Tip: record readings at the same time and place when comparing samples.</div>", unsafe_allow_html=True)

    if st.button("Assess my sample  →", use_container_width=True):
        result = assess_water_quality(ph, turbidity, nitrate, dissolved_oxygen, temperature)
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "location": location.strip() or "Unnamed sample",
            "source": source,
            "risk": result["risk"],
            "score": result["score"],
            "pH": ph,
            "turbidity": turbidity,
            "nitrate": nitrate,
            "oxygen": dissolved_oxygen,
            "temperature": temperature,
        }
        st.session_state.last_result = (result, source)
        st.session_state.history.append(entry)
        st.success("Your sample was added to My Dashboard.")

    if st.session_state.last_result:
        show_result(*st.session_state.last_result)

elif page == "▦ My Dashboard":
    st.markdown("<div class='eyebrow'>Your session summary</div><h1>▦ My dashboard</h1>", unsafe_allow_html=True)
    history = st.session_state.history
    if not history:
        st.markdown("<div class='card card-lavender'><h3>No samples yet ·</h3><p>Run your first Water Check and your personal session dashboard will appear here.</p></div>", unsafe_allow_html=True)
    else:
        high = sum(1 for item in history if item["risk"] == "High")
        moderate = sum(1 for item in history if item["risk"] == "Moderate")
        average = round(sum(item["score"] for item in history) / len(history))
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(metric_card(len(history), "Samples checked", tone="card-mint"), unsafe_allow_html=True)
        with m2:
            st.markdown(metric_card(average, "Average risk score", "#8067d9", "card-lavender"), unsafe_allow_html=True)
        with m3:
            st.markdown(metric_card(f"{high + moderate}", "Samples needing attention", "#e87952", "card-peach"), unsafe_allow_html=True)

        st.markdown("### ≡ Recent samples")
        st.dataframe(history[::-1], use_container_width=True, hide_index=True)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=history[0].keys())
        writer.writeheader()
        writer.writerows(history)
        st.download_button("↓ Download session CSV", output.getvalue(), "greenwatch_samples.csv", "text/csv", use_container_width=True)
        if st.button("× Clear session history"):
            st.session_state.history = []
            st.session_state.last_result = None
            st.rerun()

elif page == "✿ Learn & Act":
    st.markdown("<div class='eyebrow'>Small actions, real impact</div><h1>✿ Learn & act</h1>", unsafe_allow_html=True)
    st.write("Use these mini-guides to turn a measurement into a thoughtful environmental conversation.")
    topics = {
        "◌ Understand the readings": [
            "pH describes how acidic or alkaline water is.",
            "Turbidity describes how cloudy water is because of suspended particles.",
            "Nitrate can rise because of fertilizer, wastewater, or runoff.",
            "Dissolved oxygen helps describe conditions for aquatic life.",
        ],
        "□ Make observations useful": [
            "Write down the date, time, weather, and exact location.",
            "Take a photo of unusual color, foam, algae, or nearby runoff.",
            "Repeat surprising readings before drawing conclusions.",
            "Never taste unknown water or handle it without appropriate care.",
        ],
        "⌁ Turn data into action": [
            "Share repeated concerns with a teacher, local environmental group, or authority.",
            "Compare multiple locations instead of blaming a single source immediately.",
            "Ask for certified laboratory testing when drinking water may be affected.",
            "Use the data to start a student project about prevention and conservation.",
        ],
    }
    for title, bullets in topics.items():
        with st.expander(title, expanded=True):
            for bullet in bullets:
                st.markdown(f"- {bullet}")
    st.markdown("<div class='success-box'><b>GreenWatch principle:</b> good environmental technology should make people more curious, more informed, and more connected to qualified experts.</div>", unsafe_allow_html=True)

st.markdown("<div class='footer'>GreenWatch</div>", unsafe_allow_html=True)
