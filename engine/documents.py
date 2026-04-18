from __future__ import annotations

import json
import re
from pathlib import Path
from collections import defaultdict

SCHEMES_PATH = Path(__file__).parent.parent / "data" / "schemes.json"

# ---------------------------------------------------------------------------
# Priority table — lower number = higher priority in the checklist.
# Aadhaar and bank passbook appear in nearly every scheme; list them first.
# ---------------------------------------------------------------------------
_PRIORITY: dict[str, int] = {
    "Aadhaar Card":                              1,
    "Bank Passbook":                             2,
    "Income Certificate":                        3,
    "Family Income Certificate":                 3,
    "Caste/Category Certificate":                4,
    "Land Records":                              5,
    "Address Proof":                             6,
    "Passport-size Photographs":                 7,
    "Date of Birth Proof":                       8,
    "Domicile Certificate":                      9,
    "Crop Declaration Form":                    10,
    "Family Status Proof (Joint/Nuclear)":      11,
    "Ration Card":                              12,
    "EWS Certificate":                          13,
    "Disability Certificate":                   14,
    "Academic Certificates / Mark Sheets":      15,
    "PVTG/Tribal Status Certificate":           16,
    "Household Verification Report":            17,
    "Ayushman Bharat Card":                     18,
    "Forest Rights Act (FRA) Patta":            19,
    "Location Tagging Data":                    20,
    "Completion Certificates":                  21,
    "Photographs of Constructed Pucca Houses":  22,
    "Passport":                                 23,
    "English Language Proficiency Certificate": 24,
    "Offer Letter (Study in India Portal)":     25,
    "Visa":                                     26,
    "Work Portfolio / Artistic Credentials":    27,
    "Bank Authorization Letter":                28,
    "Recommendation Letter (State Culture Dept.)": 29,
    "Service Proof (EPF Passbook)":             30,
    "Death Certificate (for Family Pension)":   31,
    "Relationship Proof":                       32,
    "Detailed Project Report":                  33,
    "Patent/Copyright Documents":               34,
    "Sanction Letter":                          35,
    "Incubation Centre Certificate":            36,
}

_DEFAULT_PRIORITY = 50  # anything not explicitly listed

# ---------------------------------------------------------------------------
# Direct mapping for clean structured keys (no spaces, underscore-style).
# ---------------------------------------------------------------------------
_CLEAN_KEY_MAP: dict[str, str] = {
    "aadhaar":                                      "Aadhaar Card",
    "Aadhar Card":                                  "Aadhaar Card",
    "land_records":                                 "Land Records",
    "bank_passbook":                                "Bank Passbook",
    "Category_certificate":                         "Caste/Category Certificate",
    "photographs":                                  "Passport-size Photographs",
    "Address_proof":                                "Address Proof",
    "crop_declaration":                             "Crop Declaration Form",
    "Domicile_certifiate":                          "Domicile Certificate",   # typo in source
    "Income_certificate":                           "Income Certificate",
    "Proof_of_the_Current_Status_of_the_Family(Joint_or_Nuclear)": "Family Status Proof (Joint/Nuclear)",
    "PVTG/Tribal Status Certificate":               "PVTG/Tribal Status Certificate",
    "Household Verification Report/Survey Data":    "Household Verification Report",
    "Location Tagging Data":                        "Location Tagging Data",
    "Completion Certificates":                      "Completion Certificates",
    "Photographs Of Constructed Pucca Houses":      "Photographs of Constructed Pucca Houses",
    "Ayushman Bharat Card":                         "Ayushman Bharat Card",
    "Forest Right Act (FRA) Pattas.":               "Forest Rights Act (FRA) Patta",
}

# ---------------------------------------------------------------------------
# Keyword rules for messy concatenated strings.
# Each entry: (list of substrings to search for, canonical document name).
# Rules are applied in ORDER — more specific phrases must come before
# shorter/generic ones that could match the same text.
# Matching uses case-insensitive substring search on the segment label
# (text before the first ":" when a colon is present, else full segment).
# ---------------------------------------------------------------------------
_KEYWORD_RULES: list[tuple[list[str], str]] = [
    (["ayushman bharat card"],                  "Ayushman Bharat Card"),
    (["forest right act", "fra patta"],         "Forest Rights Act (FRA) Patta"),
    (["pvtg", "tribal status certificate"],     "PVTG/Tribal Status Certificate"),
    (["household verification"],                "Household Verification Report"),
    (["location tagging"],                      "Location Tagging Data"),
    (["photographs of constructed", "pucca house photograph"],
                                                "Photographs of Constructed Pucca Houses"),
    (["completion certificate"],                "Completion Certificates"),
    (["ews certificate"],                       "EWS Certificate"),
    (["crop declaration"],                      "Crop Declaration Form"),
    (["family status", "joint or nuclear"],     "Family Status Proof (Joint/Nuclear)"),
    (["family income certificate"],             "Family Income Certificate"),
    (["income certificate", "income_certificate"],
                                                "Income Certificate"),
    (["domicile certif", "domicile_certif"],    "Domicile Certificate"),
    # Address proof — must come before aadhaar to avoid
    # matching "Aadhaar Card, Voter ID, Passport …" descriptions
    (["address proof", "address_proof"],        "Address Proof"),
    (["caste certificate", "category certificate",
      "category_certificate", "category/ caste",
      "caste certif"],                          "Caste/Category Certificate"),
    (["land record", "land_record"],            "Land Records"),
    (["aadhaar", "aadhar"],                     "Aadhaar Card"),
    (["jan dhan", "bank passbook", "bank_passbook",
      "bank account", "passbook",
      "cheque leave", "bank statement"],        "Bank Passbook"),
    (["ration card"],                           "Ration Card"),
    (["english language proficiency"],          "English Language Proficiency Certificate"),
    (["offer letter", "study in india portal"], "Offer Letter (Study in India Portal)"),
    # "passport" — must appear as a standalone doc, not inside
    # "passport size photograph"; the label-extraction step handles this
    # because "Recent Photograph" labels don't contain "passport" before ":"
    (["passport"],                              "Passport"),
    (["visa"],                                  "Visa"),
    (["academic qualification", "academic transcript",
      "mark sheet", "marksheet"],              "Academic Certificates / Mark Sheets"),
    (["disability certificate"],               "Disability Certificate"),
    (["date of birth proof", "proof of date of birth",
      "birth certificate", "date of birth"],   "Date of Birth Proof"),
    # Generic photograph — kept after address proof and passport rules
    (["photograph", "passport size photograph"],
                                               "Passport-size Photographs"),
    (["detailed project report"],              "Detailed Project Report"),
    (["patent", "copyright"],                  "Patent/Copyright Documents"),
    (["sanction letter"],                      "Sanction Letter"),
    (["incubation center", "incubator"],       "Incubation Centre Certificate"),
    (["work portfolio", "artistic contribution"],
                                               "Work Portfolio / Artistic Credentials"),
    (["bank authorization", "bank authorisation"],
                                               "Bank Authorization Letter"),
    (["recommendation letter", "official recommendation",
      "state or ut culture"],                  "Recommendation Letter (State Culture Dept.)"),
    (["service proof", "epf passbook",
      "employment record"],                    "Service Proof (EPF Passbook)"),
    (["death certificate"],                    "Death Certificate (for Family Pension)"),
    (["relationship proof"],                   "Relationship Proof"),
]


def _label_of(segment: str) -> str:
    """
    For labelled segments like "Address Proof: Submit a copy of …" return only
    the label "Address Proof" so keywords in the explanatory clause are ignored
    (e.g. "Passport" in "Aadhaar Card, Voter ID, Passport, or utility bill").

    Exception: if the label before ":" is a metadata marker (single letter,
    short uppercase word like "FRESH" / "RENEWAL") the full segment text is
    returned instead so document keywords in the body are still found.
    """
    _METADATA = {"a", "b", "c", "i", "ii", "iii", "fresh", "renewal", "note"}
    if ":" in segment:
        label = segment.split(":")[0].strip()
        if label.lower() in _METADATA or len(label) <= 2:
            return segment
        return label
    return segment


def _matches_keyword(kw: str, text: str) -> bool:
    """
    Check whether `kw` appears in `text` (case-insensitive).
    Special case for "passport": require it to NOT be sandwiched between
    "/" or "," so that "Aadhaar/Passport/Voter ID" (an alternatives list)
    does not produce a false "Passport required" result.
    """
    if kw == "passport":
        return bool(re.search(r'(?<![/,(])\bpassport\b(?![/,)])', text, re.IGNORECASE))
    return kw in text


def _normalize(raw: str) -> list[str]:
    """Return a deduplicated list of canonical document names from one raw string."""
    key = raw.strip().rstrip(".")
    if key in _CLEAN_KEY_MAP:
        return [_CLEAN_KEY_MAP[key]]

    segments = [p.strip() for p in raw.replace("\n", ".").split(".") if p.strip()]

    seen: set[str] = set()
    results: list[str] = []

    for seg in segments:
        label = _label_of(seg).lower()
        for keywords, canonical in _KEYWORD_RULES:
            if canonical in seen:
                continue
            if any(_matches_keyword(kw, label) for kw in keywords):
                seen.add(canonical)
                results.append(canonical)

    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_document_checklist(
    matched_schemes: list[str | dict],
    schemes_path: Path = SCHEMES_PATH,
) -> list[dict]:
    """
    Build a deduplicated, priority-sorted document checklist for a set of schemes.

    Parameters
    ----------
    matched_schemes
        Either a list of scheme name strings, or a list of match_result dicts
        (as returned by matcher.match_all / confidence.enrich_all) — in the
        latter case the "scheme" key is used.

    Returns
    -------
    list of dicts, each:
        {
            "document":   str,          # canonical document name
            "needed_for": list[str],    # scheme names that require it
            "priority":   int,          # lower = more important
        }
    sorted by priority ascending, then alphabetically within the same priority.
    """
    # Normalise input to a list of scheme name strings
    scheme_names: list[str] = []
    for item in matched_schemes:
        if isinstance(item, dict):
            scheme_names.append(item["scheme"].strip())
        else:
            scheme_names.append(str(item).strip())

    if not scheme_names:
        return []

    # Load schemes data
    with open(schemes_path, encoding="utf-8") as f:
        all_schemes = json.load(f)

    scheme_lookup: dict[str, dict] = {
        s["scheme"].strip(): s for s in all_schemes
    }

    # Collect canonical docs → set of schemes that require them
    doc_to_schemes: dict[str, set[str]] = defaultdict(set)

    for name in scheme_names:
        scheme = scheme_lookup.get(name)
        if scheme is None:
            continue
        for raw_doc in scheme.get("documents_required", []):
            for canonical in _normalize(raw_doc):
                doc_to_schemes[canonical].add(name)

    if not doc_to_schemes:
        return []

    checklist = [
        {
            "document": doc,
            "needed_for": sorted(schemes),
            "priority": _PRIORITY.get(doc, _DEFAULT_PRIORITY),
        }
        for doc, schemes in doc_to_schemes.items()
    ]

    checklist.sort(key=lambda x: (x["priority"], x["document"]))
    return checklist
