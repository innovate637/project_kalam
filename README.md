# KALAM — Welfare Scheme Eligibility Engine

> "Intelligence for the people who need it most"
> CBC Recruitment Mission 03 — Tech: Backend

## What This Does
An AI engine that matches Indian citizens to government welfare schemes 
they're eligible for but never claim. Uses deterministic rule-based 
matching with a Hinglish conversational interface.

## Key Design Principle
The system says "I don't know" instead of giving wrong answers. 
Every confidence score traces to specific rules. No black boxes.

## Quick Start
```bash
git clone https://github.com/YOUR_USERNAME/kalam.git
cd kalam
pip install -r requirements.txt

# Run CLI
python interface/cli.py

# Run Streamlit UI
streamlit run interface/app.py

# Run tests
python -m pytest tests/
```

## Project Structure
- `data/` — Eligibility rules for 15+ schemes + ambiguity map
- `engine/` — Matching engine, confidence scorer, document checklist
- `interface/` — Hinglish CLI + Streamlit web UI
- `tests/` — 15 test profiles (10 adversarial + 5 happy-path)
- `docs/` — Architecture document, failure log, prompt log

## Submission Checklist
- [x] Structured eligibility rules for 15+ schemes
- [x] Ambiguity map with contradictions and overlaps
- [x] Working matching engine with explainable confidence scores
- [x] 15 edge-case profiles with documented results
- [x] Conversational interface supporting Hinglish 
- [x] Architecture document with system diagram and technical decisions
- [x] Prompt log (docs/prompt_log.md)

## Docs
- [Architecture] — System diagram, 3 key decisions, 2 production gaps
- [Prompt Log] — Every AI prompt, output, and rejection# project_kalam
