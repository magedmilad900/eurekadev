import streamlit as st
from model import assess_water_quality, risk_color

st.set_page_config(page_title="GreenWatch", page_icon="💧", layout="centered")

st.title("💧 GreenWatch")
st.subheader("A transparent water-quality risk screener for communities")
st.write(
    "GreenWatch turns a few low-cost water measurements into an understandable "
    "risk screen and practical next steps. It is an educational prototype, not a "
    "replacement for certified laboratory testing."
)

with st.sidebar:
    st.header("About this prototype")
    st.info(
        "Designed for schools and community groups that need an early warning "
        "tool before deciding whether to request professional testing."
    )
    st.caption("No personal data is collected. All calculations run locally.")

st.markdown("### Enter measurements")
col1, col2 = st.columns(2)
with col1:
    ph = st.number_input("pH", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
    turbidity = st.number_input("Turbidity (NTU)", min_value=0.0, max_value=500.0, value=2.0, step=0.5)
    nitrate = st.number_input("Nitrate (mg/L)", min_value=0.0, max_value=200.0, value=5.0, step=0.5)
with col2:
    dissolved_oxygen = st.number_input("Dissolved oxygen (mg/L)", min_value=0.0, max_value=20.0, value=7.0, step=0.1)
    temperature = st.number_input("Temperature (°C)", min_value=-10.0, max_value=60.0, value=20.0, step=0.5)
    source = st.selectbox("Water source", ["River/stream", "Lake/pond", "Well", "Unknown"])

if st.button("Assess risk", type="primary", use_container_width=True):
    result = assess_water_quality(ph, turbidity, nitrate, dissolved_oxygen, temperature)
    color = risk_color(result["risk"])
    st.markdown(f"## Risk level: <span style='color:{color}'>{result['risk']}</span>", unsafe_allow_html=True)
    st.metric("Risk score", f"{result['score']}/100")
    st.progress(result["score"] / 100)

    st.markdown("### Why did GreenWatch reach this result?")
    for reason in result["reasons"]:
        st.write(f"- {reason}")

    st.markdown("### Recommended next steps")
    for step in result["recommendations"]:
        st.write(f"- {step}")

    st.warning(
        f"Source recorded for this screening: {source}. If the water is used for drinking, "
        "seek certified laboratory testing before making safety decisions."
    )
else:
    st.info("Enter measurements and click **Assess risk** to see an explainable result.")

st.divider()
st.caption("GreenWatch • EurekaDev prototype • Built with Python and Streamlit")
