from __future__ import annotations

# Uncertain rules get partial credit — missing data is not the same as failing.
# A scheme with all-uncertain rules scores 0.4, not 0 and not 1.
UNCERTAIN_CREDIT: float = 0.4

# ---------------------------------------------------------------------------
# Critical rules per scheme (stripped names, matching matcher.py output).
# If ANY critical rule appears in failed_rules the confidence collapses to 0.
# ---------------------------------------------------------------------------
CRITICAL_RULES: dict[str, frozenset[str]] = {
    "PM Kisan": frozenset({
        "Is_farmer",
    }),
    "MGNREGA": frozenset({
        "Residence_is_rural",
    }),
    "PM Fasal Bima Yojana (PMFBY)": frozenset({
        "Is_farmer",
        "land_ownership",
    }),
    "PM Krishi Sinchayee Yojana (PMKSY)": frozenset({
        "Is_farmer",
    }),
    "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana": frozenset({
        "income_tax_payer",
        "government_employee",
        "monthly_income_above_10k",
        "AB_eligibility_criterion",
        # Asset exclusions — any one of these is an absolute SECC bar when verifiable
        "owns_two_three_or_four_wheeler_or_motorized_fishing_boat",
        "owns_mechanized_farming_equipment",
        "owns_refrigerator_or_landline",
        "three_or_more_rooms_with_pucca_walls_and_roof",
    }),
    "PM Janjati Adivasi Nyaya Maha Abhiyan (PM JANMAN)": frozenset({
        "belongs_to_PVTG",
        "resides_in_18_states_with_notified_PVTG_population",
    }),
    "Pradhan Mantri Suraksha Bima Yojana": frozenset({
        "age_18_to_70",
        "bank_account_holder_in_participating_bank",
    }),
    "PM Vishwakarma": frozenset({
        "artisan_or_craftsperson_working_with_hands_and_tools",
        "engaged_in_one_of_18_traditional_trades",
    }),
    "Pradhan Mantri Virasat ka Samvardhan": frozenset({
        "age_14_to_45_for_skilling_and_education",
    }),
    "National Pension Scheme For Traders And Self Employed Persons": frozenset({
        "self_employed_shop_or_retail_owner_or_vyapari",
        "age_18_to_40",
    }),
    "Venture Capital Fund for Scheduled Castes": frozenset({
        "SC_entrepreneur_holds_51_percent_ownership_and_management_control",
        "non_SC_entrepreneur_ST_or_OBC_or_general",  # if this triggers, hard blocked
    }),
    "Study in India Programme": frozenset({
        "foreign_national",
        "Indian_national",  # exclusion — if triggered means Indian national = blocked
    }),
    "Scheme For Financial Assistance For Veteran Artists": frozenset({
        "age_60_or_above",
        "significant_contribution_to_art_letters_or_traditional_scholarship",
    }),
    "Pradhan Mantri Uchchatar Shiksha Protsahan (PM-USP)": frozenset({
        "above_80th_percentile_in_class_12_board_exam",
        "gross_family_income_below_4.5_lakh_per_annum",
    }),
    "Employees' Pension Scheme": frozenset({
        "EPF_member_under_1952_scheme_or_exempted_establishment",
    }),
}

# ---------------------------------------------------------------------------
# Human-readable labels for rule IDs used in explanation strings.
# Falls back to replacing underscores if not listed here.
# ---------------------------------------------------------------------------
_RULE_LABELS: dict[str, str] = {
    "Is_farmer": "must be a farmer",
    "Is_adult": "must be an adult (18+)",
    "Residence_is_rural": "must reside in a rural area",
    "land_ownership": "must own land",
    "bank_account_holder_in_participating_bank": "must hold a bank account",
    "aadhaar_seeded_bank_account": "Aadhaar-linked bank account required",
    "age_18_to_70": "age must be 18–70",
    "age_18_or_above": "must be 18 or older",
    "age_18_to_40": "age must be 18–40",
    "age_60_or_above": "must be 60 or older",
    "age_14_to_45_for_skilling_and_education": "age must be 14–45",
    "age_58_or_above_for_superannuation_pension": "must be 58+ for superannuation",
    "age_50_to_58_for_early_pension": "age must be 50–58 for early pension",
    "belongs_to_PVTG": "must belong to a PVTG community",
    "resides_in_18_states_with_notified_PVTG_population": "must reside in one of the 18 PVTG states",
    "SC_or_ST_household": "must be an SC/ST household",
    "SC_entrepreneur_holds_51_percent_ownership_and_management_control": "must be an SC entrepreneur with 51%+ ownership",
    "non_SC_entrepreneur_ST_or_OBC_or_general": "non-SC entrepreneurs are excluded",
    "artisan_or_craftsperson_working_with_hands_and_tools": "must be a hand-tool artisan",
    "engaged_in_one_of_18_traditional_trades": "must work in one of the 18 traditional trades",
    "self_employed_in_unorganized_sector": "must be self-employed in the unorganised sector",
    "self_employed_shop_or_retail_owner_or_vyapari": "must be a self-employed trader/shopkeeper",
    "EPF_member_under_1952_scheme_or_exempted_establishment": "must be an EPF member",
    "above_80th_percentile_in_class_12_board_exam": "must score above 80th percentile in Class 12",
    "gross_family_income_below_4.5_lakh_per_annum": "family income must be below ₹4.5 lakh/year",
    "income_tax_payer": "income-tax payers are excluded",
    "government_employee": "government employees are excluded",
    "foreign_national": "must be a foreign national",
    "Indian_national": "Indian nationals are excluded from this scheme",
    "significant_contribution_to_art_letters_or_traditional_scholarship": "must have significant artistic contributions",
    "Mandatory_info_required_complete": "mandatory info not yet verified",
    "documents_required_complete": "required documents not yet verified",
    "annual_turnover_below_1.5_crore": "annual turnover must be below ₹1.5 crore",
    "age_18_to_45_for_women_leadership_and_entrepreneurship": "women aged 18–45 for leadership component",
    "personal_income_not_exceeding_4000_per_month": "personal income must be ≤ ₹4,000/month",
    "pay_not_exceeding_15000_per_month": "monthly pay must not exceed ₹15,000",
    "landless_manual_casual_labour_household": "must be a landless manual-labour household",
    "already_covered_5_hectares_of_land": "excluded if already covered 5+ hectares",
}


def _label(rule: str) -> str:
    return _RULE_LABELS.get(rule, rule.replace("_", " "))


def _short_list(rules: list[str], limit: int = 3) -> str:
    """Render a rule list as a readable comma-separated string, capped at `limit`."""
    shown = [_label(r) for r in rules[:limit]]
    suffix = f" (+{len(rules) - limit} more)" if len(rules) > limit else ""
    return ", ".join(shown) + suffix


def _match_quality(confidence: float, blocked: bool) -> str:
    if blocked or confidence == 0.0:
        return "ineligible"
    if confidence >= 0.85:
        return "strong"
    if confidence >= 0.55:
        return "partial"
    return "weak"


def _build_explanation(
    scheme: str,
    n_matched: int,
    n_failed: int,
    n_uncertain_incl: int,
    n_uncertain_excl: int,
    confidence: float,
    blocked_by: str | None,
) -> str:
    n_uncertain = n_uncertain_incl + n_uncertain_excl
    n_total = n_matched + n_failed + n_uncertain
    if blocked_by:
        return (
            f"Confidence 0.00: hard blocked — critical rule failed: "
            f"'{_label(blocked_by)}'"
        )
    parts = [f"Confidence {confidence:.2f}: matched {n_matched}/{n_total} rules"]
    if n_failed:
        parts.append(f"{n_failed} failed")
    if n_uncertain_incl:
        parts.append(f"{n_uncertain_incl} uncertain (missing data — partial credit applied)")
    if n_uncertain_excl:
        parts.append(f"{n_uncertain_excl} uncertain exclusions (no credit)")
    if n_failed == 0 and n_uncertain == 0:
        parts.append("all rules satisfied")
    return "; ".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_confidence(
    scheme_name: str,
    matched_rules: list[str],
    failed_rules: list[str],
    uncertain_rules: list[str],
    uncertain_inclusion_rules: list[str] | None = None,
) -> dict:
    """
    Compute a confidence score and explanation from pre-classified rule lists.

    uncertain_inclusion_rules: subset of uncertain_rules that came from inclusion
    checks (these get UNCERTAIN_CREDIT). Uncertain exclusion rules get 0 credit
    — an unverified exclusion cannot inflate eligibility.

    Returns a dict with:
        confidence    — float 0.0–1.0
        explanation   — human-readable string
        blocked_by    — rule id that triggered a hard block, or None
        match_quality — "strong" | "partial" | "weak" | "ineligible"
    """
    n_matched = len(matched_rules)
    n_failed = len(failed_rules)
    n_uncertain = len(uncertain_rules)
    n_uncertain_incl = len(uncertain_inclusion_rules) if uncertain_inclusion_rules is not None else n_uncertain
    n_uncertain_excl = n_uncertain - n_uncertain_incl
    n_total = n_matched + n_failed + n_uncertain

    # Check critical rules first
    critical = CRITICAL_RULES.get(scheme_name.strip(), frozenset())
    blocked_by: str | None = None
    for rule in failed_rules:
        if rule in critical:
            blocked_by = rule
            break

    if blocked_by:
        return {
            "confidence": 0.0,
            "explanation": _build_explanation(
                scheme_name, n_matched, n_failed, n_uncertain_incl, n_uncertain_excl, 0.0, blocked_by
            ),
            "blocked_by": blocked_by,
            "match_quality": "ineligible",
        }

    if n_total == 0:
        return {
            "confidence": 0.0,
            "explanation": "Confidence 0.00: no rules to evaluate",
            "blocked_by": None,
            "match_quality": "ineligible",
        }

    # Only uncertain inclusion rules get partial credit; exclusion uncertainties do not.
    score = (n_matched + n_uncertain_incl * UNCERTAIN_CREDIT) / n_total
    score = round(min(score, 1.0), 4)

    return {
        "confidence": score,
        "explanation": _build_explanation(
            scheme_name, n_matched, n_failed, n_uncertain_incl, n_uncertain_excl, score, None
        ),
        "blocked_by": None,
        "match_quality": _match_quality(score, False),
    }


def enrich(match_result: dict) -> dict:
    """
    Take a match_result from matcher.match_scheme and replace its raw confidence
    with the weighted, critical-rule-aware score plus explanation fields.

    Mutates and returns the same dict.
    """
    result = compute_confidence(
        scheme_name=match_result["scheme"],
        matched_rules=match_result["matched_rules"],
        failed_rules=match_result["failed_rules"],
        uncertain_rules=match_result["uncertain_rules"],
        uncertain_inclusion_rules=match_result.get("uncertain_inclusion_rules"),
    )
    match_result["confidence"] = result["confidence"]
    match_result["explanation"] = result["explanation"]
    match_result["blocked_by"] = result["blocked_by"]
    match_result["match_quality"] = result["match_quality"]
    return match_result


def enrich_all(match_results: list[dict]) -> list[dict]:
    """Enrich every result in a list, then re-sort by confidence descending."""
    enriched = [enrich(r) for r in match_results]
    enriched.sort(key=lambda r: r["confidence"], reverse=True)
    return enriched
