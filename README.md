# GreenWatch

**GreenWatch** is an explainable Python/Streamlit prototype that helps schools and community groups perform an early water-quality risk screen using five easy-to-understand measurements: pH, turbidity, nitrate, dissolved oxygen, and temperature.

## EurekaDev submission

- **Track:** Coding Track
- **Category:** Environmental Science (also fits Computer Science + AI)
- **Team:** Add your team name and members before submitting
- **Innovation:** GreenWatch prioritizes transparency. Instead of giving a mysterious black-box prediction, it shows exactly which measurements increased the score and suggests practical next steps.

## Important scope

This is an educational screening prototype, not a certified water-safety test and not a medical or public-health diagnosis. Users should contact qualified authorities and laboratories before making safety decisions.

## Run locally

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually `http://localhost:8501`.

## How the scoring works

The score begins at 0 and adds transparent points for measurements outside simple screening bands:

- pH: up to 25 points
- Turbidity: up to 25 points
- Nitrate: up to 25 points
- Dissolved oxygen: up to 15 points
- Temperature: up to 10 points

Risk bands are **Low** (<25), **Moderate** (25–54), and **High** (55–100). These thresholds are a prototype design choice for demonstrating explainable logic; they are not a substitute for a local regulatory standard.

## Test

```bash
pytest -q
```

## Files

- `app.py` — Streamlit interface
- `model.py` — explainable scoring logic
- `data/sample_measurements.csv` — example observations
- `tests/test_model.py` — automated tests
- `docs/project_description.md` — ready-to-paste Devpost description
- `docs/video_script.md` — script for a video under four minutes
