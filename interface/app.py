"""
KALAM — Streamlit web UI.
No external API calls. NLU via parse_hinglish() from cli.py (keyword/regex).
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from interface.cli import parse_hinglish
from engine.matcher import match_all
from engine.confidence import enrich_all
from engine.documents import get_document_checklist
from engine.sequence import get_application_order

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="KALAM — Welfare Scheme Advisor",
    page_icon="🌾",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------

if "profile" not in st.session_state:
    st.session_state.profile = {}
if "results" not in st.session_state:
    st.session_state.results = []
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------------------------------------------------
# Field metadata (label, type, options)
# ---------------------------------------------------------------------------

FIELD_META: dict[str, dict] = {
    "age":               {"label": "Umar (saal mein)",     "type": "int"},
    "gender":            {"label": "Gender",                "type": "select",
                          "options": ["", "male", "female", "transgender"]},
    "state":             {"label": "State",                 "type": "text"},
    "area":              {"label": "Area",                  "type": "select",
                          "options": ["", "rural", "urban"]},
    "caste_category":    {"label": "Caste Category",        "type": "select",
                          "options": ["", "General", "OBC", "SC", "ST", "PVTG"]},
    "marital_status":    {"label": "Marital Status",        "type": "select",
                          "options": ["", "single", "married", "widowed", "remarried", "divorced"]},
    "occupation":        {"label": "Kaam / Occupation",     "type": "select",
                          "options": ["", "farmer", "agricultural_labourer", "daily_wage_labourer",
                                      "artisan", "auto_rickshaw_driver", "small_business_owner",
                                      "government_employee", "private_sector_employee",
                                      "domestic_worker", "student", "self_employed", "unemployed", "none"]},
    "annual_income":     {"label": "Saal ki Income (Rs.)",  "type": "int"},
    "land_ownership":    {"label": "Apni zameen hai?",      "type": "bool"},
    "land_size_hectares":{"label": "Zameen (hectares)",     "type": "float"},
    "aadhaar":           {"label": "Aadhaar card hai?",     "type": "bool"},
    "bank_account":      {"label": "Bank account hai?",     "type": "bool"},
    "disability":        {"label": "Disability hai?",       "type": "bool"},
    "secc_listed":       {"label": "BPL/SECC list mein?",  "type": "bool"},
    "owns_vehicle":      {"label": "Gaadi/vehicle hai?",   "type": "bool"},
    "epf_member":        {"label": "EPF/PF member hai?",   "type": "bool"},
    "minority_religion": {"label": "Minority religion",    "type": "select",
                          "options": ["", "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Parsi"]},
    "family_size":       {"label": "Ghar mein kitne log",  "type": "int"},
    "trade_type":        {"label": "Trade (if artisan)",   "type": "select",
                          "options": ["", "carpenter", "tailor", "blacksmith", "goldsmith", "potter",
                                      "sculptor", "cobbler", "mason", "weaver", "fisherman",
                                      "washerman", "barber", "mali", "dhobi", "lohar", "kumhar",
                                      "darzi", "rajmistri"]},
}

PRIMARY_FIELDS   = ["age", "gender", "state", "area", "caste_category",
                    "occupation", "annual_income", "aadhaar", "bank_account"]
SECONDARY_FIELDS = ["marital_status", "land_ownership", "land_size_hectares",
                    "disability", "secc_listed", "owns_vehicle", "epf_member",
                    "minority_religion", "family_size", "trade_type"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _profile_complete_enough() -> bool:
    p = st.session_state.profile
    return sum(1 for f in PRIMARY_FIELDS if f in p and p[f] is not None) >= 4


def _run_engine() -> None:
    profile = {k: v for k, v in st.session_state.profile.items() if v is not None}
    st.session_state.results = enrich_all(match_all(profile))
    st.session_state.show_results = True


def _ambiguity_notes(results: list[dict]) -> list[str]:
    notes = []
    for r in results:
        for rule in r.get("uncertain_rules", []):
            if "secc" in rule.lower() or "bpl" in rule.lower():
                notes.append("BPL/SECC list membership uncertain — confirm for better Ayushman Bharat accuracy.")
                break
        if r.get("blocked_by") == "monthly_income_above_10k":
            notes.append(f"{r['scheme']}: Income threshold block — verify exact monthly figure.")
    return list(dict.fromkeys(notes))


def _render_field_widget(field: str, key_suffix: str = "") -> None:
    """Render an editable widget for a single profile field, updating session state directly."""
    meta = FIELD_META.get(field)
    if not meta:
        return
    current = st.session_state.profile.get(field)
    key = f"widget_{field}{key_suffix}"

    if meta["type"] == "bool":
        options = ["", "Haan", "Nahi"]
        current_str = "Haan" if current is True else ("Nahi" if current is False else "")
        chosen = st.selectbox(meta["label"], options,
                              index=options.index(current_str) if current_str in options else 0,
                              key=key)
        if chosen == "Haan":
            st.session_state.profile[field] = True
        elif chosen == "Nahi":
            st.session_state.profile[field] = False

    elif meta["type"] == "select":
        options = meta["options"]
        current_str = str(current) if current is not None else ""
        idx = options.index(current_str) if current_str in options else 0
        chosen = st.selectbox(meta["label"], options, index=idx, key=key)
        if chosen:
            st.session_state.profile[field] = chosen

    elif meta["type"] == "int":
        default = int(current) if isinstance(current, (int, float)) and current else 0
        val = st.number_input(meta["label"], min_value=0, value=default, step=1, key=key)
        if val > 0:
            st.session_state.profile[field] = int(val)

    elif meta["type"] == "float":
        default = float(current) if isinstance(current, (int, float)) and current else 0.0
        val = st.number_input(meta["label"], min_value=0.0, value=default, step=0.1, key=key)
        if val > 0:
            st.session_state.profile[field] = round(val, 2)

    elif meta["type"] == "text":
        val = st.text_input(meta["label"], value=str(current) if current else "", key=key)
        if val.strip():
            st.session_state.profile[field] = val.strip().lower()


# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------

st.title("KALAM — Aapke liye Sarkari Yojanaein")
st.caption("Apni details batao, hum batayenge kaunsi schemes aapke liye hain")

# ── Sidebar: profile fields ──────────────────────────────────────────────────
with st.sidebar:
    st.header("Aapka Profile")

    profile = st.session_state.profile
    edit_mode = st.toggle("Sab fields edit karo", key="edit_toggle")
    st.divider()

    if edit_mode:
        st.subheader("Basic Info")
        for field in PRIMARY_FIELDS:
            _render_field_widget(field, "_sb")
        st.subheader("Additional Info")
        for field in SECONDARY_FIELDS:
            _render_field_widget(field, "_sb2")
    else:
        for field in PRIMARY_FIELDS + SECONDARY_FIELDS:
            meta = FIELD_META.get(field, {})
            label = meta.get("label", field)
            val = profile.get(field)
            if val is None:
                st.markdown(f"??? **{label}**: _pata nahi_")
            elif isinstance(val, bool):
                st.markdown(f"OK **{label}**: {'Haan' if val else 'Nahi'}")
            elif field == "annual_income" and isinstance(val, (int, float)):
                st.markdown(f"OK **{label}**: Rs. {int(val):,}")
            else:
                st.markdown(f"OK **{label}**: {val}")

    st.divider()
    if st.button("Profile Reset karo", use_container_width=True):
        for key in ["profile", "results", "show_results", "chat_history"]:
            del st.session_state[key]
        st.rerun()

# ── Section 1: Chat input ────────────────────────────────────────────────────
st.subheader("Apni situation batao")

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Hinglish mein likhein",
        placeholder="Apni situation batao... (jaise: Main 35 saal ka kisan hoon UP se, 2 bigha zameen hai)",
        label_visibility="collapsed",
    )
    col_submit, col_example = st.columns([1, 4])
    with col_submit:
        submitted = st.form_submit_button("Bhejo", use_container_width=True)
    with col_example:
        st.caption("Example: 'Main 28 saal ki aurat hoon, SC hoon, rural Bihar se, khet mazdoori karti hoon'")

if submitted:
    if not user_input.strip():
        st.warning("Kuch toh likhein!")
    else:
        extracted = parse_hinglish(user_input.strip())
        if extracted:
            st.session_state.profile.update(extracted)
            st.session_state.chat_history.append(user_input.strip())
            understood_parts = []
            for k, v in extracted.items():
                lbl = FIELD_META.get(k, {}).get("label", k)
                understood_parts.append(f"**{lbl}**: {v}")
            st.success("Samajh gaya: " + " | ".join(understood_parts))
        else:
            st.warning("Kuch samajh nahi aaya. Thoda detail mein batao ya neeche fields fill karo.")

if st.session_state.chat_history:
    with st.expander(f"Pichli {len(st.session_state.chat_history)} baat(ein)"):
        for msg in st.session_state.chat_history:
            st.markdown(f"- {msg}")

# ── Missing primary fields — inline fill ──────────────────────────────────────
missing_primary = [f for f in PRIMARY_FIELDS
                   if f not in st.session_state.profile or st.session_state.profile[f] is None]
if missing_primary:
    st.subheader("Yeh bhi batao (zaroori fields)")
    cols = st.columns(min(len(missing_primary), 3))
    for i, field in enumerate(missing_primary):
        with cols[i % 3]:
            _render_field_widget(field, "_inline")

# ── Check Eligibility button ──────────────────────────────────────────────────
st.divider()
btn_col, hint_col = st.columns([1, 3])
with btn_col:
    check_clicked = st.button(
        "Check Eligibility",
        type="primary",
        use_container_width=True,
        disabled=not _profile_complete_enough(),
    )
with hint_col:
    if not _profile_complete_enough():
        st.caption("Kam se kam 4 primary fields bharo phir check kar sakte hain.")
    else:
        st.caption("Profile ready hai — eligibility check karo!")

if check_clicked:
    with st.spinner("Schemes check ho rahi hain..."):
        _run_engine()

# ── Section 2: Results ────────────────────────────────────────────────────────
if st.session_state.show_results and st.session_state.results:
    results = st.session_state.results
    eligible  = [r for r in results if r["match_quality"] in ("strong", "partial")]
    near_miss = [r for r in results if r["match_quality"] == "weak" and r.get("confidence", 0) > 0.2]
    ineligible = [r for r in results if r["match_quality"] == "ineligible"]

    st.divider()
    st.subheader("Results")

    for note in _ambiguity_notes(results):
        st.warning(f"Note: {note}")

    # Eligible
    if eligible:
        st.markdown("### Aap in schemes ke liye ELIGIBLE hain")
        for r in eligible:
            conf_pct = int(r["confidence"] * 100)
            quality_tag = "Strong match" if r["match_quality"] == "strong" else "Partial match"
            header = f"{r['scheme']} — {conf_pct}% ({quality_tag})"
            with st.expander(header, expanded=(conf_pct >= 60)):
                st.markdown(f"_{r['explanation']}_")
                c1, c2 = st.columns(2)
                with c1:
                    matched = r.get("matched_rules", [])
                    if matched:
                        st.markdown("**Matched:**")
                        for rule in matched[:6]:
                            st.markdown(f"  - {rule.replace('_', ' ')}")
                with c2:
                    uncertain = r.get("uncertain_rules", [])
                    if uncertain:
                        st.markdown("**Uncertain (missing data):**")
                        for rule in uncertain[:4]:
                            st.markdown(f"  - {rule.replace('_', ' ')}")
    else:
        st.info("Koi scheme strong/partial match nahi hui.")

    # Near-miss
    if near_miss:
        st.markdown("### In schemes ke KAREEB hain (gap hai)")
        for r in near_miss:
            conf_pct = int(r["confidence"] * 100)
            failed = r.get("failed_rules", [])
            gap_str = ", ".join(f.replace("_", " ") for f in failed[:3]) if failed else "missing data"
            with st.expander(f"{r['scheme']} — {conf_pct}% | Gap: {gap_str}"):
                st.markdown(f"_{r['explanation']}_")
                if failed:
                    st.markdown("**Failed rules:**")
                    for rule in failed:
                        st.markdown(f"  - {rule.replace('_', ' ')}")

    # Hard blocked
    blocked = [r for r in ineligible if r.get("blocked_by")]
    if blocked:
        with st.expander(f"{len(blocked)} schemes hard-blocked hain"):
            for r in blocked:
                b = r["blocked_by"].replace("_", " ")
                st.markdown(f"- **{r['scheme']}** — _{b}_")

    # ── Section 3: Action Plan ─────────────────────────────────────────────────
    st.divider()
    st.subheader("Action Plan")
    doc_col, seq_col = st.columns(2)

    with doc_col:
        st.markdown("#### Documents Taiyaar Rakhein")
        try:
            top = eligible[:5] if eligible else results[:5]
            docs = get_document_checklist(top)
            if docs:
                for d in docs:
                    schemes_str = " + ".join(d["needed_for"][:2])
                    # use doc name as key, truncated to avoid Streamlit key length issues
                    st.checkbox(d["document"], key=f"doc_{d['document'][:40]}", value=False)
                    st.caption(f"Needed for: {schemes_str}")
            else:
                st.info("Documents list generate nahi ho saki.")
        except Exception as e:
            st.error(f"Document checklist error: {e}")

    with seq_col:
        st.markdown("#### Application Sequence (Pehle yeh karein)")
        try:
            seq = get_application_order(results)
            for i, step in enumerate(seq[:10], 1):
                label = step.get("scheme", step.get("node", ""))
                desc  = step.get("description", "")
                st.markdown(f"**{i}.** {label}")
                if desc and i <= 3:
                    st.caption(f"   {desc[:120]}")
        except Exception as e:
            st.error(f"Sequence error: {e}")
