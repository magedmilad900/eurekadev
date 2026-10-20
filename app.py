import csv
import io
from datetime import datetime

import streamlit as st

from model import assess_water_quality, risk_color

st.set_page_config(
    page_title="GreenWatch | Water Intelligence",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Visual system ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Shadows+Into+Light+Two&display=swap');

    :root {
        --ink: #17324d;
        --muted: #668096;
        --cream: #fffaf0;
        --sky: #dff5ff;
        --mint: #dff8e8;
        --yellow: #fff1a8;
        --coral: #ffb4a2;
        --blue: #2389c9;
        --green: #22a06b;
        --purple: #8067d9;
    }

    html, body, [class*="css"] {
        font-family: 'Shadows Into Light Two', cursive;
        color: var(--ink);
    }
    .stApp {
        background: radial-gradient(circle at 8% 5%, #fff3ad 0, transparent 22%),
                    radial-gradient(circle at 95% 18%, #c9f2ff 0, transparent 28%),
                    linear-gradient(135deg, #fffdf7 0%, #f1fbff 100%);
    }
    .block-container { max-width: 1180px; padding-top: 1.2rem; }
    h1, h2, h3 { color: var(--ink); letter-spacing: .3px; }
    h1 { font-size: 3.2rem !important; line-height: 1.05; }
    h2 { font-size: 2rem !important; }
    h3 { font-size: 1.4rem !important; }
    p, label, .stMarkdown, .stButton button, .stSelectbox, .stNumberInput { font-size: 1.08rem; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e9f9ff 0%, #f7edff 55%, #fff8d9 100%);
        border-right: 2px solid rgba(35,137,201,.12);
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: var(--ink); }
    [data-testid="stSidebar"] .stRadio label { font-size: 1.15rem; }

    .hero {
        border-radius: 30px; padding: 2.4rem 2.7rem; margin-bottom: 1.5rem;
        background: linear-gradient(120deg, #b9efff 0%, #e2f9d7 48%, #fff0a9 100%);
        box-shadow: 0 14px 40px rgba(49, 117, 146, .15);
        position: relative; overflow: hidden;
    }
    .hero:after { content: '✦  ✧  ✦'; position: absolute; right: 28px; top: 18px; color: #fff; font-size: 2rem; }
    .hero h1 { margin: 0; }
    .hero p { max-width: 760px; color: #315a6c; font-size: 1.35rem; margin: .7rem 0 0; }
    .eyebrow { text-transform: uppercase; font-size: .95rem; letter-spacing: 2px; color: #357895; font-weight: 700; }

    .card {
        background: rgba(255,255,255,.88); border: 1px solid rgba(35,137,201,.14);
        border-radius: 22px; padding: 1.25rem 1.35rem; min-height: 125px;
        box-shadow: 0 8px 25px rgba(58, 104, 128, .08); margin-bottom: 1rem;
    }
    .card h3 { margin: 0 0 .25rem; }
    .card p { color: var(--muted); margin: 0; }
    .metric-card { text-align: center; background: linear-gradient(145deg,#fff,#edfaff); }
    .metric-number { font-size: 2.7rem; color: var(--blue); line-height: 1; font-weight: bold; }
    .metric-label { color: var(--muted); font-size: 1rem; }
    .tip { background: #fff6c7; border-left: 7px solid #f4c542; border-radius: 14px; padding: 1rem 1.2rem; }
    .success-box { background: #e5faed; border-left: 7px solid var(--green); border-radius: 14px; padding: 1rem 1.2rem; }
    .footer { text-align: center; color: var(--muted); padding: 2rem 0 1rem; font-size: 1rem; }
    div.stButton > button { border-radius: 16px; border: 0; background: linear-gradient(90deg,#2389c9,#8067d9); color: white; font-weight: bold; padding: .7rem 1.2rem; }
    div.stButton > button:hover { background: linear-gradient(90deg,#176caa,#624abf); color: white; transform: translateY(-1px); }
    [data-testid="stMetric"] { background: white; border-radius: 16px; padding: 1rem; border: 1px solid #dceef5; }
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
    st.markdown("# 💧 GreenWatch")
    st.caption("Little measurements. Better decisions.")
    st.divider()
    page = st.radio(
        "Explore",
        ["🏡 Home", "🔬 Water Check", "📊 My Dashboard", "🌱 Learn & Act"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("### Why GreenWatch?")
    st.info("A friendly, explainable first screen for schools and communities. It runs locally and stores no personal data.")
    st.caption("EurekaDev • Coding Track")


def metric_card(number, label, color="#2389c9"):
    return f"<div class='card metric-card'><div class='metric-number' style='color:{color}'>{number}</div><div class='metric-label'>{label}</div></div>"


def show_result(result, source):
    color = risk_color(result["risk"])
    st.markdown(
        f"<div class='card' style='border-top:8px solid {color};'><h2>Screening result: <span style='color:{color}'>{result['risk']}</span></h2><p>Water source: {source} · Score: {result['score']}/100</p></div>",
        unsafe_allow_html=True,
    )
    st.progress(result["score"] / 100)
    left, right = st.columns(2)
    with left:
        st.markdown("### 🔎 What influenced the score?")
        for reason in result["reasons"]:
            st.markdown(f"- {reason}")
    with right:
        st.markdown("### 🧭 Suggested next steps")
        for step in result["recommendations"]:
            st.markdown(f"- {step}")
    st.markdown(
        "<div class='tip'><b>Friendly reminder:</b> GreenWatch is an educational screening tool, not a certified laboratory test. Do not use it alone to decide whether water is safe to drink.</div>",
        unsafe_allow_html=True,
    )


# ---------- Pages ----------
if page == "🏡 Home":
    st.markdown(
        "<div class='hero'><div class='eyebrow'>Community water intelligence</div><h1>Make every drop count. 💧</h1><p>GreenWatch turns simple water measurements into a colorful, understandable first step for environmental action.</p></div>",
        unsafe_allow_html=True,
    )
    a, b, c = st.columns(3)
    with a:
        st.markdown("<div class='card'><h3>🌈 Simple</h3><p>Five easy measurements, one friendly result.</p></div>", unsafe_allow_html=True)
    with b:
        st.markdown("<div class='card'><h3>🔍 Explainable</h3><p>See exactly what made the score change.</p></div>", unsafe_allow_html=True)
    with c:
        st.markdown("<div class='card'><h3>🤝 Community-first</h3><p>Built for classrooms, clubs, and local groups.</p></div>", unsafe_allow_html=True)

    st.markdown("## Ready for a quick check?")
    st.markdown("Use the menu on the left to start a water check, explore your dashboard, or learn how to take action.")
    x, y = st.columns([1, 1])
    with x:
        st.markdown("<div class='success-box'><b>Our design promise</b><br>Clear guidance without pretending that a prototype can replace experts.</div>", unsafe_allow_html=True)
    with y:
        st.markdown("<div class='tip'><b>Best for a demo</b><br>Try a normal sample first, then enter concerning values to see the explanation change.</div>", unsafe_allow_html=True)

elif page == "🔬 Water Check":
    st.markdown("<div class='eyebrow'>Step 1 of 1</div><h1>🔬 Check your water</h1>", unsafe_allow_html=True)
    st.write("Enter readings from a test kit or classroom experiment. All fields stay on this page.")
    with st.container():
        st.markdown("<div class='card'><h3>📍 Sample details</h3><p>Give your observation a little context.</p></div>", unsafe_allow_html=True)
        source = st.selectbox("Water source", ["River / stream", "Lake / pond", "Well", "School fountain", "Unknown"])
        location = st.text_input("Location nickname (optional)", placeholder="e.g. North creek")
    st.markdown("### 📏 Measurements")
    col1, col2, col3 = st.columns(3)
    with col1:
        ph = st.number_input("pH", 0.0, 14.0, 7.0, 0.1, help="Acidity or alkalinity")
        turbidity = st.number_input("Turbidity (NTU)", 0.0, 500.0, 2.0, 0.5)
    with col2:
        nitrate = st.number_input("Nitrate (mg/L)", 0.0, 200.0, 5.0, 0.5)
        dissolved_oxygen = st.number_input("Dissolved oxygen (mg/L)", 0.0, 20.0, 7.0, 0.1)
    with col3:
        temperature = st.number_input("Temperature (°C)", -10.0, 60.0, 20.0, 0.5)
        st.markdown("<div class='tip'>💡 Tip: record readings at the same time and place when comparing samples.</div>", unsafe_allow_html=True)

    if st.button("✨ Assess my sample", use_container_width=True):
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

elif page == "📊 My Dashboard":
    st.markdown("<div class='eyebrow'>Your session summary</div><h1>📊 My dashboard</h1>", unsafe_allow_html=True)
    history = st.session_state.history
    if not history:
        st.markdown("<div class='card'><h3>No samples yet 🌱</h3><p>Run your first Water Check and your personal session dashboard will appear here.</p></div>", unsafe_allow_html=True)
    else:
        high = sum(1 for item in history if item["risk"] == "High")
        moderate = sum(1 for item in history if item["risk"] == "Moderate")
        average = round(sum(item["score"] for item in history) / len(history))
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(metric_card(len(history), "Samples checked"), unsafe_allow_html=True)
        with m2:
            st.markdown(metric_card(average, "Average risk score", "#8067d9"), unsafe_allow_html=True)
        with m3:
            st.markdown(metric_card(f"{high + moderate}", "Samples needing attention", "#e87952"), unsafe_allow_html=True)

        st.markdown("### 🧾 Recent samples")
        st.dataframe(history[::-1], use_container_width=True, hide_index=True)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=history[0].keys())
        writer.writeheader()
        writer.writerows(history)
        st.download_button("⬇️ Download session CSV", output.getvalue(), "greenwatch_samples.csv", "text/csv", use_container_width=True)
        if st.button("🧹 Clear session history"):
            st.session_state.history = []
            st.session_state.last_result = None
            st.rerun()

elif page == "🌱 Learn & Act":
    st.markdown("<div class='eyebrow'>Small actions, real impact</div><h1>🌱 Learn & act</h1>", unsafe_allow_html=True)
    st.write("Use these mini-guides to turn a measurement into a thoughtful environmental conversation.")
    topics = {
        "🧪 Understand the readings": [
            "pH describes how acidic or alkaline water is.",
            "Turbidity describes how cloudy water is because of suspended particles.",
            "Nitrate can rise because of fertilizer, wastewater, or runoff.",
            "Dissolved oxygen helps describe conditions for aquatic life.",
        ],
        "📸 Make observations useful": [
            "Write down the date, time, weather, and exact location.",
            "Take a photo of unusual color, foam, algae, or nearby runoff.",
            "Repeat surprising readings before drawing conclusions.",
            "Never taste unknown water or handle it without appropriate care.",
        ],
        "🤝 Turn data into action": [
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

st.markdown("<div class='footer'>GreenWatch · EurekaDev prototype · Built with Python + Streamlit · Made for curious communities</div>", unsafe_allow_html=True)
