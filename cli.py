"""
KALAM — Hinglish conversational CLI.

Collects user profile through structured questions, then runs the matching engine.
No external API calls — all NLU is pure string matching and if/else logic.
(In production an LLM would replace the parse_* helpers.)
"""
from __future__ import annotations

import re
import sys
import os
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.matcher import match_all
from engine.confidence import enrich_all
from engine.documents import get_document_checklist
from engine.sequence import get_application_order

# ---------------------------------------------------------------------------
# Input normalisation helpers
# ---------------------------------------------------------------------------

_STATE_ALIASES: dict[str, str] = {
    "up": "uttar pradesh", "mp": "madhya pradesh", "hp": "himachal pradesh",
    "uk": "uttarakhand", "ap": "andhra pradesh", "tn": "tamil nadu",
    "wb": "west bengal", "mh": "maharashtra", "ka": "karnataka",
    "kl": "kerala", "rj": "rajasthan", "hr": "haryana", "pb": "punjab",
    "br": "bihar", "jh": "jharkhand", "or": "odisha", "as": "assam",
    "gj": "gujarat", "cg": "chhattisgarh", "ga": "goa", "mn": "manipur",
    "ml": "meghalaya", "mz": "mizoram", "nl": "nagaland", "sk": "sikkim",
    "tr": "tripura", "ar": "arunachal pradesh", "j&k": "jammu and kashmir",
    "jk": "jammu and kashmir", "dl": "delhi", "ch": "chandigarh",
    "ts": "telangana", "tg": "telangana",
}

_OCCUPATION_MAP: list[tuple[list[str], str]] = [
    (["kisan", "kheti", "farming", "farm", "kisaan", "agriculture"], "farmer"),
    (["mazdoor", "majdoor", "labour", "daily wage", "daily_wage", "mgnrega"], "daily_wage_labourer"),
    (["agricultural labour", "khet mazdoor", "khet majdoor"], "agricultural_labourer"),
    (["lohar", "kumhar", "darzi", "sunar", "carpenter", "artisan", "craftsman",
      "lohaar", "tailor", "blacksmith", "goldsmith", "potter", "weaver",
      "sculptor", "cobbler", "mason", "fisherman", "washerman", "barber"], "artisan"),
    (["auto", "rickshaw", "driver", "taxi", "cab"], "auto_rickshaw_driver"),
    (["dukan", "shop", "business", "vyapari", "trader", "retail"], "small_business_owner"),
    (["sarkari", "government", "govt", "sarkaari"], "government_employee"),
    (["naukri", "private job", "company", "office", "corporate", "private sector",
      "private_sector", "salaried"], "private_sector_employee"),
    (["ghar ka kaam", "domestic", "household"], "domestic_worker"),
    (["student", "padhai", "college", "school", "vidyarthi"], "student"),
    (["self employed", "self-employed", "apna kaam", "freelance"], "self_employed"),
    (["berozgaar", "unemployed", "job nahi", "kaam nahi"], "unemployed"),
]

_TRADE_MAP: dict[str, str] = {
    "lohar": "blacksmith", "lohaar": "blacksmith",
    "kumhar": "potter", "kumhaar": "potter",
    "darzi": "tailor",
    "sunar": "goldsmith",
    "carpenter": "carpenter", "badhai": "carpenter",
    "weaver": "weaver", "bunkar": "weaver",
    "cobbler": "cobbler", "mochi": "cobbler",
    "blacksmith": "blacksmith",
    "goldsmith": "goldsmith",
    "potter": "potter",
    "tailor": "tailor",
    "sculptor": "sculptor",
    "mason": "mason", "rajmistri": "mason",
    "fisherman": "fisherman", "machuara": "fisherman",
    "washerman": "washerman", "dhobi": "washerman",
    "barber": "barber", "nai": "barber",
    "mali": "mali",
}

_MINORITY_MAP: dict[str, str] = {
    "muslim": "Muslim", "islam": "Muslim", "musalman": "Muslim",
    "christian": "Christian", "isai": "Christian",
    "sikh": "Sikh", "sardar": "Sikh",
    "buddhist": "Buddhist", "baudh": "Buddhist",
    "jain": "Jain",
    "parsi": "Parsi", "zoroastrian": "Parsi",
}


def _lower(s: str) -> str:
    return s.strip().lower()


def parse_bool(text: str) -> bool | None:
    """Return True/False/None for yes/no/don't-know responses."""
    t = _lower(text)
    if any(w in t for w in ["haan", "haa", " ha ", "^ha$", "yes", "ji", "bilkul", "zaroor", "sahi", "h "]):
        return True
    if re.search(r"\bha\b", t) or t in ("ha", "h"):
        return True
    if any(w in t for w in ["nahi", "nahin", "nah", "no", "na ", "^na$", "nope", "nhi"]):
        return False
    if re.search(r"\bna\b", t) or t in ("na", "n"):
        return False
    if any(w in t for w in ["pata nahi", "nahi pata", "don't know", "dont know",
                              "idea nahi", "nhi pata", "pta nhi", "maloom nahi",
                              "pata nhi", "unknown", "?"]):
        return None
    return None


def parse_int(text: str) -> int | None:
    """Extract first integer from text. 'lagbhag 45 saal' → 45."""
    nums = re.findall(r"\d+", text)
    if nums:
        return int(nums[0])
    return None


def parse_float(text: str) -> float | None:
    """Extract first float from text. '2.5 hectare' → 2.5."""
    m = re.search(r"\d+\.?\d*", text)
    if m:
        return float(m.group())
    return None


def parse_state(text: str) -> str | None:
    t = _lower(text)
    if t in _STATE_ALIASES:
        return _STATE_ALIASES[t]
    for alias, full in _STATE_ALIASES.items():
        if alias in t or full in t:
            return full
    # If it looks like a real state name, return as-is
    if len(t) > 3:
        return t
    return None


def parse_occupation(text: str) -> tuple[str | None, str | None]:
    """Returns (occupation, trade_type). trade_type only set for artisans."""
    t = _lower(text)
    # Check for specific trade first
    for trade_kw, trade_canonical in _TRADE_MAP.items():
        if trade_kw in t:
            return "artisan", trade_canonical
    for keywords, occ in _OCCUPATION_MAP:
        if any(kw in t for kw in keywords):
            return occ, None
    return None, None


def parse_caste(text: str) -> str | None:
    t = _lower(text)
    if any(w in t for w in ["general", "unreserved", "open", "forward"]):
        return "General"
    if any(w in t for w in ["obc", "other backward", "pichda"]):
        return "OBC"
    if "pvtg" in t or "particularly vulnerable" in t:
        return "PVTG"
    if any(w in t for w in [" st ", "^st$", "scheduled tribe", "adivasi", "tribal"]):
        return "ST"
    if any(w in t for w in [" sc ", "^sc$", "scheduled caste", "dalit", "harijan"]):
        return "SC"
    if re.search(r"\bst\b", t):
        return "ST"
    if re.search(r"\bsc\b", t):
        return "SC"
    return None


def parse_gender(text: str) -> str | None:
    t = _lower(text)
    if any(w in t for w in ["female", "mahila", "aurat", "woman", "ladki", "girl"]):
        return "female"
    if any(w in t for w in ["transgender", "kinnar", "hijra", "third gender"]):
        return "transgender"
    if any(w in t for w in ["male", "mard", "aadmi", "man", "ladka", "boy", "purush"]):
        return "male"
    return None


def parse_minority(text: str) -> str | None:
    t = _lower(text)
    if any(w in t for w in ["nahi", "no", "na", "hindu", "nope"]):
        return None  # Not minority
    for kw, canonical in _MINORITY_MAP.items():
        if kw in t:
            return canonical
    # "haan" without specifying which — will ask follow-up
    if any(w in t for w in ["haan", "yes", "ji", "ha"]):
        return "__ask_which__"
    return None


def parse_marital(text: str) -> str | None:
    t = _lower(text)
    if any(w in t for w in ["widowed", "vidhwa", "widow", "vidhur"]):
        return "widowed"
    if any(w in t for w in ["remarried", "doosri shadi", "dusri shadi"]):
        return "remarried"
    if any(w in t for w in ["married", "shaadi", "byah", "vivah", "shadi"]):
        return "married"
    if any(w in t for w in ["divorced", "talaq", "talak"]):
        return "divorced"
    if any(w in t for w in ["single", "akela", "akeli", "unmarried", "nahi hui"]):
        return "single"
    return None


def is_quit(text: str) -> bool:
    t = _lower(text)
    return any(w in t for w in ["quit", "exit", "band karo", "band kare", "chodo", "chhodo", "bye"])


def is_garbage(text: str) -> bool:
    t = text.strip()
    if len(t) < 2:
        return True
    if re.fullmatch(r"[^a-zA-Z0-9\u0900-\u097F]+", t):
        return True
    return False


# ---------------------------------------------------------------------------
# Free-form Hinglish parser — single entry point for app.py / cli.py
# ---------------------------------------------------------------------------

def parse_hinglish(text: str) -> dict:
    """
    Parse a free-form Hinglish sentence and return a partial profile dict.
    Only fields that can be confidently extracted are included.
    Callers should merge the result into an existing profile dict.

    Example:
        "Main 35 saal ka kisan hoon UP se, 2 bigha zameen hai"
        → {'age': 35, 'occupation': 'farmer', 'state': 'uttar pradesh',
           'land_ownership': True, 'land_size_hectares': 0.81}
    """
    t = _lower(text)
    extracted: dict = {}

    # Age — "35 saal", "umar 40", "age 28", bare number near age keywords
    age_m = re.search(
        r"(?:umar|age|saal ka|saal ki|year old|saal)\s*[:\s]*(\d{1,3})"
        r"|(\d{1,3})\s*(?:saal|year|sal)\b",
        t,
    )
    if age_m:
        raw_age = int(age_m.group(1) or age_m.group(2))
        if 5 <= raw_age <= 120:
            extracted["age"] = raw_age

    # Gender
    g = parse_gender(text)
    if g:
        extracted["gender"] = g

    # State — full names first (avoids "ka"→Karnataka firing on "saal ka")
    # Short 2-letter aliases only match when adjacent to location keywords
    _loc_ctx = r"(?:se|mein|ki|ke|state|rehta|rehti|hoon|district)\b"
    state_found = False
    for alias, full in _STATE_ALIASES.items():
        if full in t:
            extracted["state"] = full
            state_found = True
            break
    if not state_found:
        for alias, full in _STATE_ALIASES.items():
            if len(alias) <= 2:
                # require location context nearby for short codes
                if re.search(rf"\b{re.escape(alias)}\b\s*{_loc_ctx}|{_loc_ctx}\s*\b{re.escape(alias)}\b", t):
                    extracted["state"] = full
                    break
            else:
                if re.search(rf"\b{re.escape(alias)}\b", t):
                    extracted["state"] = full
                    break

    # Area
    if any(w in t for w in ["rural", "gaon", "village", "gram", "deh"]):
        extracted["area"] = "rural"
    elif any(w in t for w in ["urban", "city", "shehar", "shahar", "town", "metro", "nagar"]):
        extracted["area"] = "urban"

    # Caste
    c = parse_caste(text)
    if c:
        extracted["caste_category"] = c

    # Marital status
    ms = parse_marital(text)
    if ms:
        extracted["marital_status"] = ms

    # Occupation + trade
    occ, trade = parse_occupation(text)
    if occ:
        extracted["occupation"] = occ
    if trade:
        extracted["trade_type"] = trade

    # Income — "income 50000", "50k", "5 lakh", "salary 15000/month"
    income_m = re.search(
        r"(?:income|salary|kamai|aay|amdani)[^\d]*(\d[\d,]*)"
        r"|(\d[\d,]*)\s*(?:rupee|rs\.?|/-|per month|mahine|₹)",
        t,
    )
    if income_m:
        raw_inc = (income_m.group(1) or income_m.group(2)).replace(",", "")
        inc = int(raw_inc)
        # Detect per-month and annualise
        if "month" in t or "mahine" in t or "per month" in t:
            inc *= 12
        extracted["annual_income"] = inc
    else:
        # "X lakh" pattern
        lakh_m = re.search(r"(\d+(?:\.\d+)?)\s*lakh", t)
        if lakh_m:
            extracted["annual_income"] = int(float(lakh_m.group(1)) * 100000)

    # Land ownership + size
    if any(w in t for w in ["zameen hai", "apni zameen", "land hai", "kheti hai",
                              "khet hai", "owns land", "land ownership"]):
        extracted["land_ownership"] = True
    elif any(w in t for w in ["zameen nahi", "no land", "bina zameen", "land nahi"]):
        extracted["land_ownership"] = False

    # Land size — bigha → hectare (1 bigha ≈ 0.2 ha in most states)
    bigha_m = re.search(r"(\d+(?:\.\d+)?)\s*bigha", t)
    if bigha_m:
        extracted["land_ownership"] = True
        extracted["land_size_hectares"] = round(float(bigha_m.group(1)) * 0.2, 2)
    hectare_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:hectare|ha\b)", t)
    if hectare_m:
        extracted["land_ownership"] = True
        extracted["land_size_hectares"] = float(hectare_m.group(1))
    acre_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:acre|ekad)", t)
    if acre_m:
        extracted["land_ownership"] = True
        extracted["land_size_hectares"] = round(float(acre_m.group(1)) * 0.405, 2)

    # Boolean fields — keyword presence
    _bool_signals: list[tuple[str, list[str], list[str]]] = [
        ("aadhaar",      ["aadhaar hai", "aadhaar card hai", "aadhaar number"],
                         ["aadhaar nahi", "no aadhaar"]),
        ("bank_account", ["bank account hai", "bank mein account", "jan dhan", "account hai"],
                         ["bank account nahi", "no bank", "account nahi"]),
        ("disability",   ["disability hai", "viklang", "divyang", "disabled"],
                         ["disability nahi", "no disability"]),
        ("secc_listed",  ["bpl hai", "bpl list", "secc", "bpl mein", "bpl card"],
                         ["bpl nahi", "secc nahi", "not in bpl"]),
        ("owns_vehicle", ["gaadi hai", "scooter hai", "bike hai", "car hai",
                          "vehicle hai", "motorbike"],
                         ["gaadi nahi", "vehicle nahi", "no vehicle", "gaadi nahi hai"]),
        ("epf_member",   ["epf hai", "pf hai", "epf member", "provident fund"],
                         ["epf nahi", "pf nahi", "no epf"]),
    ]
    for field, pos_kws, neg_kws in _bool_signals:
        if any(kw in t for kw in pos_kws):
            extracted[field] = True
        elif any(kw in t for kw in neg_kws):
            extracted[field] = False

    # Minority religion
    mr = parse_minority(text)
    if mr and mr != "__ask_which__":
        extracted["minority_religion"] = mr

    # Family size — "5 log hain", "paanch sadasya", "family of 4"
    fam_m = re.search(r"(\d+)\s*(?:log|sadasya|member|angg|family member)", t)
    if fam_m:
        extracted["family_size"] = int(fam_m.group(1))

    return extracted


# ---------------------------------------------------------------------------
# Contradiction detection
# ---------------------------------------------------------------------------

_CONTRADICTION_PAIRS: list[tuple[str, str, list[str], list[str]]] = [
    ("occupation", "farmer", ["mazdoor", "labour", "naukri", "driver", "student"],
     "Pehle aapne kisan bataya tha, ab yeh bol rahe hain — kaunsa sahi hai?"),
    ("occupation", "government_employee", ["student", "unemployed", "mazdoor"],
     "Pehle aapne sarkari naukri batayi thi — ab kuch aur bol rahe hain. Kaunsa sahi hai?"),
    ("area", "rural", ["urban", "city", "shehar", "metro"],
     "Pehle aapne rural bataya tha — ab urban lag raha hai. Kaunsa sahi hai?"),
    ("area", "urban", ["rural", "gaon", "village", "gram"],
     "Pehle aapne urban bataya tha — ab rural lag raha hai. Kaunsa sahi hai?"),
]


def check_contradiction(profile: dict, field: str, raw_input: str) -> str | None:
    """Return a contradiction warning string, or None if no contradiction."""
    if field not in profile or profile[field] is None:
        return None
    old = str(profile[field])
    t = _lower(raw_input)
    for cf, old_val, conflict_kws, msg in _CONTRADICTION_PAIRS:
        if cf == field and old == old_val:
            if any(kw in t for kw in conflict_kws):
                return msg
    return None


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _fmt_profile(profile: dict) -> str:
    labels = {
        "age": "Umar", "gender": "Gender", "state": "State", "area": "Area",
        "caste_category": "Caste", "marital_status": "Marital Status",
        "family_size": "Family Size", "minority_religion": "Minority Religion",
        "occupation": "Kaam", "annual_income": "Saal ki Income",
        "land_ownership": "Zameen", "land_size_hectares": "Zameen ka Size",
        "aadhaar": "Aadhaar", "bank_account": "Bank Account",
        "disability": "Disability", "secc_listed": "SECC/BPL List",
        "owns_vehicle": "Vehicle", "epf_member": "EPF Member",
        "years_of_service": "Service Years", "trade_type": "Trade",
    }
    lines = []
    for k, label in labels.items():
        if k in profile and profile[k] is not None:
            v = profile[k]
            if isinstance(v, bool):
                v = "Haan" if v else "Nahi"
            lines.append(f"  {label}: {v}")
    return "\n".join(lines) if lines else "  (kuch nahi mila)"


def _show_results(results: list[dict]) -> None:
    eligible = [r for r in results if r["match_quality"] in ("strong", "partial")]
    near_miss = [r for r in results if r["match_quality"] == "weak" and r.get("confidence", 0) > 0.2]

    if not eligible and not near_miss:
        print("\nAbhi koi scheme match nahi hui. Lekin yeh schemes kareeb hain:")
        for r in results[:5]:
            print(f"  • {r['scheme']} ({r['confidence']:.0%})")
        return

    if eligible:
        print("\n✅ Aap in schemes ke liye ELIGIBLE hain:\n")
        for r in eligible:
            stars = "★★★" if r["match_quality"] == "strong" else "★★☆"
            print(f"  {stars} {r['scheme']}  ({r['confidence']:.0%} confidence)")
            print(f"       {r['explanation']}")
            print()

    if near_miss:
        print("⚠️  In schemes ke KAREEB hain (thoda sa gap hai):\n")
        for r in near_miss[:4]:
            failed = r.get("failed_rules", [])
            gap = ", ".join(failed[:2]) if failed else "thodi si information missing"
            print(f"  • {r['scheme']}  ({r['confidence']:.0%})")
            print(f"    Gap: {gap}")
        print()

    # Document checklist
    top_eligible = eligible[:5]
    if top_eligible:
        docs = get_document_checklist(top_eligible)
        if docs:
            print("📋 Yeh documents taiyaar rakhein:\n")
            for d in docs[:10]:
                schemes_str = " + ".join(d["needed_for"][:2])
                print(f"  • {d['document']}  [{schemes_str}]")
            print()

    # Application sequence
    try:
        seq = get_application_order(results)
        if seq:
            print("📌 Application sequence (pehle yeh, phir yeh):\n")
            for i, step in enumerate(seq[:8], 1):
                label = step.get("scheme", step.get("node", ""))
                desc = step.get("description", "")
                suffix = f" — {desc[:70]}" if desc and i <= 3 else ""
                print(f"  {i}. {label}{suffix}")
            print()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Question flow
# ---------------------------------------------------------------------------

QUESTIONS: list[dict] = [
    # Round 1 — Basic Info
    {"field": "age",            "q": "Aapki umar kitni hai?",                                  "round": 1},
    {"field": "gender",         "q": "Aap male hain, female, ya transgender?",                 "round": 1},
    {"field": "state",          "q": "Aap kis state mein rehte hain?",                         "round": 1},
    {"field": "area",           "q": "Aapka area rural hai ya urban?",                         "round": 1},
    # Round 2 — Identity & Family
    {"field": "caste_category", "q": "Aapki caste category kya hai? (General / OBC / SC / ST)","round": 2},
    {"field": "marital_status", "q": "Aap shaadi-shuda hain?",                                 "round": 2},
    {"field": "family_size",    "q": "Ghar mein kitne log hain?",                               "round": 2},
    {"field": "minority_religion","q": "Kya aap minority community se hain? (Muslim, Christian, Sikh, etc.)", "round": 2},
    # Round 3 — Economic
    {"field": "occupation",     "q": "Aap kya kaam karte hain?",                               "round": 3},
    {"field": "annual_income",  "q": "Saal ki income lagbhag kitni hai? (pata nahi bhi bol sakte hain)", "round": 3},
    {"field": "land_ownership", "q": "Kya aapke paas apni zameen hai?",                        "round": 3},
    # land_size_hectares asked conditionally
    # Round 4 — Documents & Access
    {"field": "aadhaar",        "q": "Kya aapke paas Aadhaar card hai?",                       "round": 4},
    {"field": "bank_account",   "q": "Kya aapka bank account hai?",                            "round": 4},
    {"field": "disability",     "q": "Kya aap kisi disability se affected hain?",              "round": 4},
    # Round 5 — Scheme-specific
    {"field": "secc_listed",    "q": "Kya aapka naam SECC / BPL list mein hai? (pata nahi bhi chalega)", "round": 5},
    {"field": "owns_vehicle",   "q": "Kya aapke paas gaadi ya scooter hai?",                  "round": 5},
    {"field": "epf_member",     "q": "Kya aap EPF / PF member hain?",                          "round": 5},
]

_BOOL_FIELDS = {"land_ownership", "aadhaar", "bank_account", "disability",
                "secc_listed", "owns_vehicle", "epf_member"}
_INT_FIELDS = {"age", "family_size", "annual_income"}
_FLOAT_FIELDS = {"land_size_hectares"}


def _parse_answer(field: str, raw: str) -> tuple[Any, str | None]:
    """
    Parse user answer for a given field.
    Returns (value, error_message). value=None means 'don't know'.
    error_message is set when input is unrecognisable.
    """
    if field in _BOOL_FIELDS:
        v = parse_bool(raw)
        # parse_bool returns None for both "don't know" and "unrecognised"
        # Distinguish: if text has yes/no keywords it would have matched; otherwise ask again
        t = _lower(raw)
        recognised_yn = any(w in t for w in [
            "haan", "haa", "yes", "ji", "bilkul", "nahi", "nahin", "nah", "no", "na",
            "pata nahi", "nahi pata", "don't know", "idea nahi", "nhi pata", "pta nhi",
        ]) or re.search(r"\bha\b|\bna\b", t)
        if v is None and not recognised_yn:
            return None, "Samajh nahi aaya — 'haan', 'nahi', ya 'pata nahi' bolein."
        return v, None

    if field in _INT_FIELDS:
        if any(w in _lower(raw) for w in ["pata nahi", "nahi pata", "don't know", "idea nahi", "nhi pata"]):
            return None, None
        v = parse_int(raw)
        if v is None:
            return None, "Samajh nahi aaya — ek number batayein."
        return v, None

    if field in _FLOAT_FIELDS:
        v = parse_float(raw)
        if v is None:
            return None, "Samajh nahi aaya — number mein batayein (jaise '2' ya '0.5')."
        return v, None

    if field == "gender":
        v = parse_gender(raw)
        if v is None:
            return None, "Samajh nahi aaya — 'male', 'female', ya 'transgender' bolein."
        return v, None

    if field == "state":
        v = parse_state(raw)
        if v is None:
            return None, "State ka naam dobara bolein? (jaise 'Uttar Pradesh', 'Bihar')"
        return v, None

    if field == "area":
        t = _lower(raw)
        if any(w in t for w in ["rural", "gaon", "village", "gram", "deh"]):
            return "rural", None
        if any(w in t for w in ["urban", "city", "shehar", "shahar", "town", "metro", "nagar"]):
            return "urban", None
        return None, "Samajh nahi aaya — 'rural' (gaon) ya 'urban' (shehar) bolein."

    if field == "caste_category":
        v = parse_caste(raw)
        if v is None:
            return None, "Samajh nahi aaya — General, OBC, SC, ya ST mein se bolein."
        return v, None

    if field == "marital_status":
        v = parse_marital(raw)
        if v is None:
            return None, "Samajh nahi aaya — 'shaadi-shuda', 'single', 'widowed', etc. bolein."
        return v, None

    if field == "occupation":
        if any(w in _lower(raw) for w in ["pata nahi", "kuch nahi", "bekar", "none"]):
            return "none", None
        occ, _ = parse_occupation(raw)
        if occ is None:
            # Store raw text so engine can handle it
            return raw.strip()[:40], None
        return occ, None

    if field == "minority_religion":
        v = parse_minority(raw)
        if v == "__ask_which__":
            return None, "Kaunsi community? Muslim, Christian, Sikh, Buddhist, Jain, ya Parsi?"
        return v, None

    return raw.strip() or None, None


# ---------------------------------------------------------------------------
# Main conversation loop
# ---------------------------------------------------------------------------

GREETING = """
╔══════════════════════════════════════════════════════╗
║        KALAM — Welfare Scheme Advisor                ║
║        Aapka swagat hai!                             ║
╚══════════════════════════════════════════════════════╝

Namaste! Main KALAM hoon — aapka welfare scheme advisor.

Main aapko bataunga ki aap kaun si government schemes ke
liye eligible hain — PM Kisan, Ayushman Bharat, MGNREGA,
aur 15+ aur schemes.

Kuch simple sawaal poochunga. Agar kuch pata nahi hai,
sirf 'pata nahi' bol dein — koi baat nahi.

('quit' likhein chodne ke liye)
"""


def _ask(question: str) -> str:
    print(f"\nKALAM: {question}")
    try:
        return input("Aap:   ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\nAlvida! Take care. 🙏")
        sys.exit(0)


def run() -> None:
    print(GREETING)

    profile: dict[str, Any] = {}
    # Track which fields have been explicitly set (including None = "don't know")
    answered: set[str] = set()

    # -----------------------------------------------------------------------
    # Phase 1 — Collect all fields
    # -----------------------------------------------------------------------
    q_index = 0
    questions = list(QUESTIONS)

    while q_index < len(questions):
        qdef = questions[q_index]
        field = qdef["field"]

        # Skip if already answered
        if field in answered:
            q_index += 1
            continue

        raw = _ask(qdef["q"])

        if is_quit(raw):
            print("\nAlvida! Take care.")
            return

        if is_garbage(raw):
            print("KALAM: Samajh nahi aaya, dobara batayein?")
            continue  # re-ask same question

        # Parse the answer
        value, err = _parse_answer(field, raw)

        if err:
            # If error is actually a clarifying question, re-prompt with it
            print(f"KALAM: {err}")
            continue  # re-ask same question

        # Contradiction check
        if field in profile and profile[field] is not None:
            contradiction_msg = check_contradiction(profile, field, raw)
            if contradiction_msg:
                confirm_raw = _ask(contradiction_msg)
                if is_quit(confirm_raw):
                    print("\nAlvida! Take care.")
                    return
                # Re-parse the clarification
                value, err2 = _parse_answer(field, confirm_raw)
                if err2:
                    print(f"KALAM: {err2}")
                    continue

        # Store the value
        profile[field] = value
        answered.add(field)

        # Show confirmation
        if value is None:
            print(f"  [Samajh gaya: {field} — pata nahi]")
        elif isinstance(value, bool):
            print(f"  [Samajh gaya: {field} = {'haan' if value else 'nahi'}]")
        else:
            print(f"  [Samajh gaya: {field} = {value}]")

        # Conditional follow-up: land size
        if field == "land_ownership" and value is True:
            if "land_size_hectares" not in answered:
                questions.insert(q_index + 1, {
                    "field": "land_size_hectares",
                    "q": "Kitni zameen hai hectare mein?",
                    "round": 3,
                })

        # Conditional follow-up: trade type for artisans
        if field == "occupation" and value == "artisan":
            if "trade_type" not in answered:
                questions.insert(q_index + 1, {
                    "field": "trade_type",
                    "q": "Kaunsa kaam karte hain? (lohar, kumhar, darzi, carpenter, etc.)",
                    "round": 5,
                })

        # Conditional follow-up: minority religion — which one
        if field == "minority_religion" and value is None:
            # parse_minority returned None could mean "not minority" OR "don't know"
            pass  # already handled in _parse_answer via __ask_which__

        # Conditional follow-up: trade_type parse (field inserted above)
        if field == "trade_type":
            t = _lower(raw)
            trade = None
            for kw, canonical in _TRADE_MAP.items():
                if kw in t:
                    trade = canonical
                    break
            if trade:
                profile["trade_type"] = trade
                print(f"  [Samajh gaya: trade_type = {trade}]")

        q_index += 1

    # -----------------------------------------------------------------------
    # Phase 2 — Profile summary + confirmation
    # -----------------------------------------------------------------------
    print("\n" + "─" * 54)
    print("KALAM: Yeh raha aapka profile:\n")
    print(_fmt_profile(profile))
    print("─" * 54)

    while True:
        confirm = _ask("Kya yeh sahi hai? (haan / nahi, ya jo field badalni hai woh batayein)")

        if is_quit(confirm):
            print("\nAlvida!")
            return

        if any(w in _lower(confirm) for w in ["haan", "haa", "yes", "ji", "sahi", "bilkul", "theek"]) \
                or re.search(r"\bha\b", _lower(confirm)):
            break

        # User wants to correct something — detect which field
        corrected = False
        for qdef in QUESTIONS:
            field = qdef["field"]
            if field.replace("_", " ") in _lower(confirm) or field in _lower(confirm):
                raw2 = _ask(f"Sahi value batayein ({field}):")
                value2, err2 = _parse_answer(field, raw2)
                if err2:
                    print(f"KALAM: {err2}")
                else:
                    profile[field] = value2
                    print(f"  [Updated: {field} = {value2}]")
                    corrected = True
                break

        if not corrected:
            # Let user type the correction freeform
            print("KALAM: Kaunsa field badalna hai? Seedha batayein (jaise 'age 40' ya 'area urban').")
            raw3 = _ask("")
            # Try to parse "field value" pattern
            parts = raw3.strip().split(None, 1)
            if len(parts) == 2:
                f, v_raw = parts
                f = f.strip().lower()
                for qdef in QUESTIONS:
                    if qdef["field"].lower() == f or qdef["field"].replace("_", " ") == f:
                        value3, err3 = _parse_answer(qdef["field"], v_raw)
                        if not err3:
                            profile[qdef["field"]] = value3
                            print(f"  [Updated: {qdef['field']} = {value3}]")
                        break

        print("\nKALAM: Updated profile:\n")
        print(_fmt_profile(profile))

    # -----------------------------------------------------------------------
    # Phase 3 — Run engine and show results
    # -----------------------------------------------------------------------
    print("\nKALAM: Theek hai! Ab check karta hoon schemes...")

    try:
        raw_results = match_all(profile)
        results = enrich_all(raw_results)
    except Exception as e:
        print(f"\nKALAM: Khed hai, ek technical error aaya: {e}")
        return

    _show_results(results)

    # -----------------------------------------------------------------------
    # Phase 4 — Follow-up Q&A
    # -----------------------------------------------------------------------
    print("─" * 54)
    print("KALAM: Koi aur sawaal? (kisi scheme ke baare mein pooch sakte hain, ya 'quit' karein)")

    while True:
        followup = _ask("")

        if is_quit(followup):
            print("\nAlvida! Good luck with your applications. 🙏")
            return

        t = _lower(followup)

        if "document" in t or "kagaz" in t or "kaagaz" in t:
            eligible = [r for r in results if r["match_quality"] in ("strong", "partial")]
            docs = get_document_checklist(eligible[:5])
            if docs:
                print("\n📋 Document Checklist:\n")
                for d in docs:
                    print(f"  • {d['document']}  [{', '.join(d['needed_for'][:2])}]")
            else:
                print("KALAM: Documents ki list abhi available nahi hai.")

        elif "sequence" in t or "pehle" in t or "order" in t or "apply" in t:
            try:
                seq = get_application_order(results)
                print("\n📌 Application Order:\n")
                for i, step in enumerate(seq[:10], 1):
                    label = step.get("scheme", step.get("node", ""))
                    desc = step.get("description", "")
                    suffix = f"\n     {desc[:100]}" if desc and i <= 3 else ""
                    print(f"  {i}. {label}{suffix}")
            except Exception as e:
                print(f"KALAM: Sequence fetch error: {e}")

        elif any(scheme_kw in t for r in results for scheme_kw in [_lower(r["scheme"])[:10]]):
            # User asked about a specific scheme
            for r in results:
                if _lower(r["scheme"])[:10] in t or any(
                    word in t for word in _lower(r["scheme"]).split()[:2]
                ):
                    print(f"\nKALAM: {r['scheme']}")
                    print(f"  Confidence: {r['confidence']:.0%}  ({r['match_quality']})")
                    print(f"  {r['explanation']}")
                    if r.get("failed_rules"):
                        print(f"  Failed rules: {', '.join(r['failed_rules'][:3])}")
                    break

        else:
            print("KALAM: Is baare mein aur information chahiye to 'documents', 'sequence', ya scheme ka naam poochein.")


if __name__ == "__main__":
    run()
