from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

RuleVerdict = Literal["matched", "failed", "uncertain"]

SCHEMES_PATH = Path(__file__).parent.parent / "data" / "schemes.json"

# 18 states with notified PVTG populations under PM JANMAN
_PVTG_STATES = {
    "andhra pradesh", "chhattisgarh", "gujarat", "jharkhand", "kerala",
    "madhya pradesh", "maharashtra", "manipur", "odisha", "rajasthan",
    "tamil nadu", "telangana", "tripura", "uttarakhand", "west bengal",
    "andaman and nicobar islands", "dadra and nagar haveli", "jammu and kashmir",
}

_FARMER_OCCUPATIONS = {"farmer", "agriculturist", "cultivator", "agricultural_worker", "agricultural_labourer"}
_ARTISAN_OCCUPATIONS = {
    "artisan", "craftsperson", "blacksmith", "carpenter", "goldsmith",
    "potter", "weaver", "tailor", "cobbler", "sculptor", "locksmith",
    "boat_maker", "armorer", "hammer_and_tool_kit_maker", "fishing_net_maker",
    "barber", "washerman", "dhobi", "garland_maker", "toy_maker", "basket_maker",
}
_TRADER_OCCUPATIONS = {"trader", "shopkeeper", "retailer", "vyapari", "self_employed_retail"}
_MANUAL_LABOR_OCCUPATIONS = {
    "daily_wage_worker", "laborer", "manual_worker", "construction_worker",
    "domestic_worker", "ragpicker", "daily_wage_labourer",
}
_GOVT_OCCUPATIONS = {
    "government_employee", "central_government_employee",
    "state_government_employee", "psu_employee",
}
_URBAN_OCCUPATIONS = {
    "ragpicker", "beggar", "domestic_worker", "street_vendor", "cobbler",
    "hawker", "vendor", "construction_worker", "plumber", "mason", "painter",
    "welder", "security_guard", "sweeper", "sanitation_worker",
    "home_based_worker", "artisan", "handicrafts", "tailor", "driver",
    "conductor", "rickshaw_puller", "transport_worker", "shop_worker",
    "helper", "delivery", "waiter", "electrician", "mechanic", "assembler",
    "repair_worker", "washer_man", "dhobi", "chowkidar", "watchman",
    # compound real-world occupation strings
    "auto_rickshaw_driver", "e_rickshaw_driver", "taxi_driver", "cab_driver",
    "delivery_worker", "gig_worker", "platform_worker",
}

# PM Vishwakarma: 18 notified traditional trades (official list)
_PM_VISHWAKARMA_TRADES = {
    "carpenter", "boat_maker", "armorer", "blacksmith", "hammer_and_tool_kit_maker",
    "locksmith", "goldsmith", "potter", "sculptor", "stone_carver", "cobbler",
    "shoemaker", "mason", "basket_maker", "mat_maker", "broom_maker", "coir_weaver",
    "toy_maker", "doll_maker", "barber", "garland_maker", "washerman", "tailor",
    "fishing_net_maker",
}

# Notified minority communities under National Commission for Minorities Act 1992
_MINORITY_RELIGIONS = {"muslim", "christian", "sikh", "buddhist", "jain", "parsi"}


def _eval(value, condition) -> RuleVerdict:
    """Return uncertain if value is None, else matched/failed based on condition."""
    if value is None:
        return "uncertain"
    return "matched" if condition(value) else "failed"


def _occ(user: dict, values: set) -> RuleVerdict:
    occ = user.get("occupation")
    # Treat "none"/"n/a"/"" strings the same as None (BUG-010 fix)
    if occ is None or str(occ).strip().lower() in ("none", "n/a", ""):
        return "uncertain"
    return "matched" if occ.lower() in values else "failed"


# ---------------------------------------------------------------------------
# Rule evaluators
# Each takes a user dict and returns RuleVerdict.
# Inclusion evaluators: matched = user satisfies criterion.
# Exclusion evaluators: matched = exclusion DOES apply (bad for user).
# ---------------------------------------------------------------------------
_EVALUATORS: dict[str, callable] = {
    # --- Age ---
    "Is_adult":                                     lambda u: _eval(u.get("age"), lambda v: v >= 18),
    "age_18_or_above":                              lambda u: _eval(u.get("age"), lambda v: v >= 18),
    "age_18_to_70":                                 lambda u: _eval(u.get("age"), lambda v: 18 <= v <= 70),
    "age_14_to_45_for_skilling_and_education":      lambda u: _eval(u.get("age"), lambda v: 14 <= v <= 45),
    "age_18_to_45_for_women_leadership_and_entrepreneurship": lambda u: (
        "uncertain" if u.get("age") is None or u.get("gender") is None
        else ("matched" if 18 <= u["age"] <= 45 and u["gender"].lower() in ("female", "woman", "f") else "failed")
    ),
    "age_60_or_above":                              lambda u: _eval(u.get("age"), lambda v: v >= 60),
    "age_18_to_40":                                 lambda u: _eval(u.get("age"), lambda v: 18 <= v <= 40),
    "age_58_or_above_for_superannuation_pension":   lambda u: _eval(u.get("age"), lambda v: v >= 58),
    "age_50_to_58_for_early_pension":               lambda u: _eval(u.get("age"), lambda v: 50 <= v < 58),
    "spouse_or_child_of_deceased_EPF_member_for_family_pension": lambda u: "uncertain",
    # exclusions
    "below_60_years_of_age":                        lambda u: _eval(u.get("age"), lambda v: v < 60),
    "above_45_years_of_age":                        lambda u: _eval(u.get("age"), lambda v: v > 45),
    "joined_at_age_58_or_above":                    lambda u: "uncertain",

    # --- Residence ---
    "Residence_is_rural":                           lambda u: _eval(u.get("area"), lambda v: v.lower() == "rural"),

    # --- Land ---
    "land_ownership":                               lambda u: _eval(u.get("land_ownership"), lambda v: v is True),
    "landless_manual_casual_labour_household":      lambda u: (
        "uncertain" if u.get("land_ownership") is None
        else (
            "matched" if u["land_ownership"] is False and (u.get("occupation") or "").lower() in _MANUAL_LABOR_OCCUPATIONS
            else "failed" if u["land_ownership"] is True
            else "uncertain"
        )
    ),
    "already_covered_5_hectares_of_land":           lambda u: _eval(u.get("land_size_hectares"), lambda v: v >= 5),
    "owns_5_acres_or_more_irrigated_land_two_crop_seasons": lambda u: _eval(u.get("land_size_hectares"), lambda v: v >= 2.02),
    "owns_2_5_acres_irrigated_land_with_irrigation_equipment": lambda u: _eval(u.get("land_size_hectares"), lambda v: v >= 1.01),
    "owns_7_5_or_more_acres_land_with_irrigation_equipment":   lambda u: _eval(u.get("land_size_hectares"), lambda v: v >= 3.04),

    # --- Bank / Aadhaar ---
    "bank_account_holder_in_participating_bank":    lambda u: _eval(u.get("bank_account"), lambda v: v is True),
    "aadhaar_seeded_bank_account": lambda u: (
        "uncertain" if u.get("aadhaar") is None or u.get("bank_account") is None
        else ("matched" if u["aadhaar"] and u["bank_account"] else "failed")
    ),

    # --- Occupation: farmer ---
    "Is_farmer":                                    lambda u: _occ(u, _FARMER_OCCUPATIONS),

    # --- Occupation: artisan / PM Vishwakarma ---
    # trade_type (new field) takes precedence when provided; fallback to occupation
    "artisan_or_craftsperson_working_with_hands_and_tools": lambda u: (
        _eval(u.get("trade_type"), lambda v: v.lower() in _PM_VISHWAKARMA_TRADES)
        if u.get("trade_type") is not None
        else _occ(u, _ARTISAN_OCCUPATIONS)
    ),
    "self_employed_in_unorganized_sector":          lambda u: _occ(u, _ARTISAN_OCCUPATIONS | _TRADER_OCCUPATIONS | _MANUAL_LABOR_OCCUPATIONS),
    "engaged_in_one_of_18_traditional_trades":      lambda u: (
        _eval(u.get("trade_type"), lambda v: v.lower() in _PM_VISHWAKARMA_TRADES)
        if u.get("trade_type") is not None
        else _occ(u, _ARTISAN_OCCUPATIONS)
    ),

    # --- Occupation: trader / NPS ---
    "self_employed_shop_or_retail_owner_or_vyapari": lambda u: _occ(u, _TRADER_OCCUPATIONS),

    # --- Occupation: government employee (used as exclusion) ---
    "government_employee":                          lambda u: _occ(u, _GOVT_OCCUPATIONS),
    "government_employee_or_family_member_of_government_employee": lambda u: _occ(u, _GOVT_OCCUPATIONS),
    "non_agricultural_government_enterprise_employee": lambda u: _occ(u, _GOVT_OCCUPATIONS),
    "retired_central_or_state_government_employee": lambda u: _eval(
        u.get("occupation"), lambda v: "retired" in v.lower()
    ),
    "apprentice":                                   lambda u: _eval(u.get("occupation"), lambda v: v.lower() == "apprentice"),

    # --- Occupation: Ayushman Bharat urban categories ---
    "ragpicker":                                    lambda u: _eval(u.get("occupation"), lambda v: v.lower() == "ragpicker"),
    "beggar":                                       lambda u: _eval(u.get("occupation"), lambda v: v.lower() == "beggar"),
    "domestic_worker":                              lambda u: _eval(u.get("occupation"), lambda v: "domestic" in v.lower()),
    "street_vendor_or_cobbler_or_hawker":           lambda u: _occ(u, {"street_vendor", "cobbler", "hawker", "vendor"}),
    "construction_worker_or_plumber_or_mason_or_painter_or_welder_or_security_guard": lambda u: _occ(
        u, {"construction_worker", "plumber", "mason", "painter", "welder", "security_guard"}
    ),
    "sweeper_or_sanitation_worker":                 lambda u: _occ(u, {"sweeper", "sanitation_worker"}),
    "home_based_worker_or_artisan_or_handicrafts_or_tailor": lambda u: _occ(
        u, {"home_based_worker", "artisan", "handicrafts", "tailor"}
    ),
    "transport_worker_or_driver_or_conductor_or_rickshaw_puller": lambda u: _occ(
        u, {"driver", "conductor", "rickshaw_puller", "transport_worker",
            "auto_rickshaw_driver", "e_rickshaw_driver", "taxi_driver", "cab_driver"}
    ),
    "shop_worker_or_helper_or_delivery_or_waiter":  lambda u: _occ(u, {"shop_worker", "helper", "delivery", "waiter"}),
    "electrician_or_mechanic_or_assembler_or_repair_worker": lambda u: _occ(
        u, {"electrician", "mechanic", "assembler", "repair_worker"}
    ),
    "washer_man_or_chowkidar":                      lambda u: _occ(u, {"washer_man", "dhobi", "chowkidar", "watchman"}),

    # --- Income ---
    "income_tax_payer":                             lambda u: _eval(u.get("annual_income"), lambda v: v > 500000),
    "professional_tax_payer":                       lambda u: "uncertain",
    "personal_income_not_exceeding_4000_per_month": lambda u: _eval(u.get("annual_income"), lambda v: v <= 48000),
    "household_monthly_income_above_6000":          lambda u: _eval(u.get("annual_income"), lambda v: v > 72000),
    "gross_family_income_below_4.5_lakh_per_annum": lambda u: _eval(u.get("annual_income"), lambda v: v < 450000),
    "gross_family_income_above_4_5_lakh_per_annum": lambda u: _eval(u.get("annual_income"), lambda v: v >= 450000),
    "annual_turnover_below_1.5_crore":              lambda u: _eval(u.get("annual_income"), lambda v: v < 15_000_000),
    "annual_turnover_above_1_5_crore":              lambda u: _eval(u.get("annual_income"), lambda v: v >= 15_000_000),
    "monthly_income_above_10k":                     lambda u: _eval(u.get("annual_income"), lambda v: v > 120_000),
    "pay_not_exceeding_15000_per_month":            lambda u: _eval(u.get("annual_income"), lambda v: v <= 180_000),
    "new_entrant_with_wages_above_15000_from_sept_2014": lambda u: _eval(u.get("annual_income"), lambda v: v > 180_000),

    # --- Caste ---
    "SC_or_ST_household":                           lambda u: _eval(u.get("caste_category"), lambda v: v.upper() in ("SC", "ST")),
    "belongs_to_PVTG":                              lambda u: _eval(u.get("caste_category"), lambda v: v.upper() == "PVTG"),
    "SC_entrepreneur_holds_51_percent_ownership_and_management_control": lambda u: _eval(
        u.get("caste_category"), lambda v: v.upper() == "SC"
    ),
    "non_SC_entrepreneur_ST_or_OBC_or_general":     lambda u: _eval(
        u.get("caste_category"), lambda v: v.upper() in ("ST", "OBC", "GENERAL")
    ),

    # --- State ---
    "resides_in_18_states_with_notified_PVTG_population": lambda u: _eval(
        u.get("state"), lambda v: v.lower() in _PVTG_STATES
    ),

    # --- Disability ---
    "disabled_member_and_no_able_bodied_adult":     lambda u: _eval(u.get("disability"), lambda v: v is True),

    # --- Everything that cannot be determined from the standard profile ---
    # Loan / prior-benefit history
    "not_availed_PMEGP_or_PM_SVANidhi_or_Mudra_in_last_5_years": lambda u: "uncertain",
    "received_PMEGP_loan_in_last_5_years":          lambda u: "uncertain",
    "has_outstanding_Mudra_or_PM_SVANidhi_loan":    lambda u: "uncertain",
    "another_family_member_already_registered":     lambda u: "uncertain",
    "one_member_per_family":                        lambda u: "uncertain",
    "benefit_already_availed_within_7_years_for_same_land": lambda u: "uncertain",
    "enrolled_under_PM_Shram_Yogi_Maandhan_or_PM_Kisan_Maandhan": lambda u: "uncertain",
    "covered_under_government_contributed_NPS_or_EPFO_or_ESIC": lambda u: (
        _eval(u.get("epf_member"), lambda v: v is True)
        if u.get("epf_member") is not None else "uncertain"
    ),
    # Employment / pension history — resolved by new epf_member / years_of_service fields
    "EPF_member_under_1952_scheme_or_exempted_establishment": lambda u: _eval(u.get("epf_member"), lambda v: v is True),
    "minimum_10_years_eligible_service":            lambda u: _eval(u.get("years_of_service"), lambda v: v >= 10),
    "contributed_to_Employees_Pension_Fund":        lambda u: _eval(u.get("epf_member"), lambda v: v is True),
    "employee_of_establishment_with_approved_exemption_from_EPS": lambda u: "uncertain",
    "pension_above_10k":                            lambda u: "uncertain",
    # Document / process checks — evaluated scheme-aware in match_scheme(); kept
    # here only as an "uncertain" fallback if called outside that context.
    "Mandatory_info_required_complete":             lambda u: "uncertain",
    "documents_required_complete":                  lambda u: "uncertain",
    "consents_to_auto_debit":                       lambda u: "uncertain",
    # Housing / assets
    "single_room_kaccha_house":                     lambda u: "uncertain",
    "no_adult_member_aged_16_to_59":                lambda u: "uncertain",
    "no_adult_male_member_aged_16_to_59":           lambda u: "uncertain",
    "owns_two_three_or_four_wheeler_or_motorized_fishing_boat": lambda u: _eval(u.get("owns_vehicle"), lambda v: v is True),
    "owns_mechanized_farming_equipment":            lambda u: "uncertain",
    "kisan_card_credit_limit_above_50k":            lambda u: "uncertain",
    "owns_refrigerator_or_landline":                lambda u: "uncertain",
    "three_or_more_rooms_with_pucca_walls_and_roof": lambda u: "uncertain",
    "institutional_land_ownership":                 lambda u: "uncertain",
    "constitutional_posts":                         lambda u: "uncertain",
    "professional":                                 lambda u: "uncertain",
    "NRI_household":                                lambda u: "uncertain",
    # Survey / portal identifiers
    "identified_PM_JANMAN_beneficiary_for_on_grid_connection": lambda u: "uncertain",
    "unelectrified_household_not_covered_under_RDSS_for_solar_power": lambda u: "uncertain",
    "resides_in_kaccha_house_for_pucca_house_benefit": lambda u: "uncertain",
    "identified_through_state_physical_survey_on_PM_Gati_Shakti_portal": lambda u: "uncertain",
    # Study in India
    "foreign_national":                             lambda u: "uncertain",
    "Indian_national":                              lambda u: "uncertain",
    "completed_qualifying_education_as_per_course_norms": lambda u: "uncertain",
    "applied_through_Study_in_India_portal":        lambda u: "uncertain",
    "valid_passport":                               lambda u: "uncertain",
    "meets_academic_and_language_requirements_of_chosen_institution": lambda u: "uncertain",
    "admission_outside_Study_in_India_portal":      lambda u: "uncertain",
    "NRI_not_eligible_for_SII_scholarship":         lambda u: "uncertain",
    "applying_for_medical_or_dental_degree_programme": lambda u: "uncertain",
    # Veteran artists
    "significant_contribution_to_art_letters_or_traditional_scholarship": lambda u: "uncertain",
    "state_pension_of_at_least_500_per_month_or_recommended_by_Zonal_Cultural_Centre": lambda u: "uncertain",
    "receiving_financial_assistance_under_other_ministry_of_culture_schemes": lambda u: "uncertain",
    "no_state_artist_pension_or_verified_artistic_credentials": lambda u: "uncertain",
    # PM-USP / scholarship
    "above_80th_percentile_in_class_12_board_exam": lambda u: "uncertain",
    "pursuing_regular_degree_course":               lambda u: "uncertain",
    "institution_recognized_by_AICTE_or_relevant_regulatory_body": lambda u: "uncertain",
    "50_percent_marks_and_75_percent_attendance_for_renewal": lambda u: "uncertain",
    "correspondence_or_distance_or_diploma_student": lambda u: "uncertain",
    "already_availing_another_scholarship_or_fee_waiver_scheme": lambda u: "uncertain",
    "took_gap_year_after_class_12":                 lambda u: "uncertain",
    "below_80th_percentile_in_class_12_board":      lambda u: "uncertain",
    "studying_in_non_AISHE_coded_institution":      lambda u: "uncertain",
    # VCF-SC
    "project_in_manufacturing_or_services_or_allied_sector_including_startups": lambda u: "uncertain",
    "6_months_SC_ownership_for_assistance_up_to_50L": lambda u: "uncertain",
    "12_months_SC_ownership_for_assistance_above_50L": lambda u: "uncertain",
    "incubated_tech_startup_by_IIT_or_NIT_or_DST_recognized_incubator": lambda u: "uncertain",
    "SC_entrepreneur_with_patent_or_copyright_and_commercial_potential": lambda u: "uncertain",
    "government_sanctioned_or_appraised_project":   lambda u: "uncertain",
    "SC_shareholding_below_51_percent":             lambda u: "uncertain",
    "company_not_under_manufacturing_services_or_allied_sector": lambda u: "uncertain",
    # PMFBY / PMSBY — coverage exclusions, not eligibility gates
    "damage_from_war_or_nuke":                      lambda u: "uncertain",
    "damage_malicious":                             lambda u: "uncertain",
    "damage_from_preventable_risk":                 lambda u: "uncertain",
    "damage_from_theft_or_grazing":                 lambda u: "uncertain",
    "damage_from_post_harvest_losses_beyond_cutoff_period": lambda u: "uncertain",
    "non_notified_crop_or_area":                    lambda u: "uncertain",
    "uses_non_registered_components":               lambda u: "uncertain",
    "death_or_disability_due_to_self_inflicted_injury_or_suicide": lambda u: "uncertain",
    "death_or_disability_due_to_intoxication_or_substance_abuse": lambda u: "uncertain",
    "death_or_disability_due_to_criminal_act_or_terrorism": lambda u: "uncertain",
    "death_or_disability_due_to_war_nuclear_or_riot": lambda u: "uncertain",
    "partial_disability_without_qualifying_limb_or_sight_loss": lambda u: "uncertain",
    # PM VIKAS
    "education_qualification_as_per_NSQF_norms_for_skilling_or_NIOS_norms_for_education": lambda u: "uncertain",
    # If minority_religion is known and is a notified minority → exclusion doesn't fire
    # If not a minority → uncertain (quota depends on seat availability, not deterministic)
    "non_minority_community_member_exceeding_25_percent_seat_quota": lambda u: (
        "failed" if str(u.get("minority_religion") or "").lower() in _MINORITY_RELIGIONS
        else "uncertain"
    ),
}


def _evaluate_rule(rule_id: str, user: dict) -> RuleVerdict:
    evaluator = _EVALUATORS.get(rule_id)
    if evaluator is None:
        return "uncertain"
    return evaluator(user)


# ---------------------------------------------------------------------------
# Document and mandatory-info completeness — scheme-aware checks.
# These replace the generic "uncertain" lambdas when called from match_scheme.
# ---------------------------------------------------------------------------

# Each entry: raw document key as it appears in documents_required →
# a function (user) → RuleVerdict
_DOC_CHECKS: dict[str, callable] = {
    # Identity
    "aadhaar":                          lambda u: _eval(u.get("aadhaar"), lambda v: v is True),
    "Aadhar Card":                      lambda u: _eval(u.get("aadhaar"), lambda v: v is True),
    # Land
    "land_records":                     lambda u: _eval(u.get("land_ownership"), lambda v: v is True),
    # Bank
    "bank_passbook":                    lambda u: _eval(u.get("bank_account"), lambda v: v is True),
    # Caste — General category doesn't need a certificate; SC/ST/OBC/PVTG can
    # provide one. Only unknown caste is uncertain.
    "Category_certificate":             lambda u: "uncertain" if u.get("caste_category") is None else "matched",
    # Crop — only a farmer can produce a crop declaration
    "crop_declaration":                 lambda u: _eval(
        u.get("occupation"),
        lambda v: v.lower() in _FARMER_OCCUPATIONS
    ),
    # PVTG/tribal status
    "PVTG/Tribal Status Certificate":   lambda u: _eval(
        u.get("caste_category"), lambda v: v.upper() == "PVTG"
    ),
}

# Each entry: field name from Mandatory_info_required →
# a function (user) → RuleVerdict
_INFO_CHECKS: dict[str, callable] = {
    "Bank_Account_Details":     lambda u: _eval(u.get("bank_account"), lambda v: v is True),
    "ID_proof":                 lambda u: _eval(u.get("aadhaar"), lambda v: v is True),
    "Age":                      lambda u: "matched" if u.get("age") is not None else "uncertain",
    "Gender":                   lambda u: "matched" if u.get("gender") is not None else "uncertain",
    "Category":                 lambda u: "matched" if u.get("caste_category") is not None else "uncertain",
    "Income_details":           lambda u: "matched" if u.get("annual_income") is not None else "uncertain",
    "Land_details":             lambda u: _eval(u.get("land_ownership"), lambda v: v is True),
    "Household_details":        lambda u: "matched" if u.get("family_size") is not None else "uncertain",
    "Tribal_group_status":      lambda u: _eval(
        u.get("caste_category"), lambda v: v.upper() == "PVTG"
    ),
    "Annual_turnover":          lambda u: "matched" if u.get("annual_income") is not None else "uncertain",
    "Caste":                    lambda u: "matched" if u.get("caste_category") is not None else "uncertain",
}


def _eval_docs_complete(scheme: dict, user: dict) -> RuleVerdict:
    """
    Check whether the user can produce every document required by this scheme.

    - "failed"    — at least one required document is provably absent
                    (e.g. land_records required but land_ownership=False)
    - "matched"   — every checkable document passes and none are uncertain
    - "uncertain" — all known checks pass but some documents cannot be
                    verified from the profile alone
    """
    has_uncertain = False
    for doc in scheme.get("documents_required", []):
        check = _DOC_CHECKS.get(doc)
        if check is None:
            has_uncertain = True
            continue
        result = check(user)
        if result == "failed":
            return "failed"
        if result == "uncertain":
            has_uncertain = True
    return "uncertain" if has_uncertain else "matched"


def _eval_info_complete(scheme: dict, user: dict) -> RuleVerdict:
    """
    Check whether the user has supplied all mandatory information fields.

    Same logic as _eval_docs_complete but operates on Mandatory_info_required.
    """
    has_uncertain = False
    for field in scheme.get("Mandatory_info_required", []):
        check = _INFO_CHECKS.get(field)
        if check is None:
            has_uncertain = True
            continue
        result = check(user)
        if result == "failed":
            return "failed"
        if result == "uncertain":
            has_uncertain = True
    return "uncertain" if has_uncertain else "matched"


_AB_SCHEME_NAME = "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana"
_COMPLETENESS_RULES = frozenset({"documents_required_complete", "Mandatory_info_required_complete"})


def _get_inclusion_rules(scheme: dict, user: dict) -> list[str]:
    """Return the applicable inclusion rule list for this scheme and user."""
    rules = scheme.get("rules", {})
    if "inclusion" in rules:
        return rules["inclusion"]
    # Ayushman Bharat dual-list routing
    area = (user.get("area") or "").lower()
    if area == "urban" and "inclusion_if_Urban" in rules:
        return rules["inclusion_if_Urban"]
    if area == "rural" and "inclusion_if_rural" in rules:
        return rules["inclusion_if_rural"]
    # area unknown — merge both lists so nothing is silently dropped
    combined = rules.get("inclusion_if_rural", []) + rules.get("inclusion_if_Urban", [])
    return combined


def _gap_analysis(failed: list[str], uncertain: list[str]) -> list[dict]:
    """Describe what the user needs to satisfy to improve eligibility."""
    gaps = []
    for rule in failed:
        gaps.append({"rule": rule, "status": "failed", "action": f"Does not satisfy: {rule.replace('_', ' ')}"})
    for rule in uncertain:
        gaps.append({"rule": rule, "status": "uncertain", "action": f"Missing info for: {rule.replace('_', ' ')}"})
    return gaps


def match_scheme(scheme: dict, user: dict) -> dict:
    """Evaluate a single scheme against a user profile."""
    scheme_name = scheme["scheme"].strip()
    rules = scheme.get("rules", {})
    inclusion_rules = _get_inclusion_rules(scheme, user)
    exclusion_rules = rules.get("exclusions", [])

    matched: list[str] = []
    failed: list[str] = []
    uncertain_inclusion: list[str] = []
    uncertain_exclusion: list[str] = []

    if scheme_name == _AB_SCHEME_NAME:
        # AB inclusion criteria are OR-logic (any one household/occupation type
        # qualifies), except completeness rules which remain AND.
        or_criteria = [r for r in inclusion_rules if r not in _COMPLETENESS_RULES]
        completeness = [r for r in inclusion_rules if r in _COMPLETENESS_RULES]

        # secc_listed=True is a direct SECC-survey confirmation — short-circuits the OR loop
        any_matched = user.get("secc_listed") is True
        any_uncertain = False
        if not any_matched:
            for rule in or_criteria:
                v = _evaluate_rule(rule, user)
                if v == "matched":
                    any_matched = True
                    break
                elif v == "uncertain":
                    any_uncertain = True

        if any_matched:
            matched.append("AB_eligibility_criterion")
        elif any_uncertain:
            uncertain_inclusion.append("AB_eligibility_criterion")
        else:
            failed.append("AB_eligibility_criterion")

        for rule in completeness:
            if rule == "documents_required_complete":
                v = _eval_docs_complete(scheme, user)
            elif rule == "Mandatory_info_required_complete":
                v = _eval_info_complete(scheme, user)
            else:
                v = _evaluate_rule(rule, user)
            if v == "matched":
                matched.append(rule)
            elif v == "failed":
                failed.append(rule)
            else:
                uncertain_inclusion.append(rule)
    else:
        for rule in inclusion_rules:
            if rule == "documents_required_complete":
                verdict = _eval_docs_complete(scheme, user)
            elif rule == "Mandatory_info_required_complete":
                verdict = _eval_info_complete(scheme, user)
            else:
                verdict = _evaluate_rule(rule, user)
            if verdict == "matched":
                matched.append(rule)
            elif verdict == "failed":
                failed.append(rule)
            else:
                uncertain_inclusion.append(rule)

    for rule in exclusion_rules:
        verdict = _evaluate_rule(rule, user)
        if verdict == "matched":
            # Exclusion applies — bad for user
            failed.append(rule)
        elif verdict == "failed":
            # Exclusion does not apply — good for user
            matched.append(rule)
        else:
            uncertain_exclusion.append(rule)

    uncertain = uncertain_inclusion + uncertain_exclusion
    total = len(matched) + len(failed) + len(uncertain)
    confidence = round(len(matched) / total, 4) if total > 0 else 0.0

    return {
        "scheme": scheme_name,
        "ministry": scheme.get("ministry", "").strip(),
        "confidence": confidence,
        "matched_rules": matched,
        "failed_rules": failed,
        "uncertain_rules": uncertain,
        "uncertain_inclusion_rules": uncertain_inclusion,
        "uncertain_exclusion_rules": uncertain_exclusion,
        "gap_analysis": _gap_analysis(failed, uncertain),
    }


def match_all(user: dict, schemes_path: Path = SCHEMES_PATH) -> list[dict]:
    """Match user against all schemes, sorted by confidence descending."""
    with open(schemes_path, encoding="utf-8") as f:
        schemes = json.load(f)
    results = [match_scheme(s, user) for s in schemes]
    results.sort(key=lambda r: r["confidence"], reverse=True)
    return results


def top_matches(user: dict, n: int = 5, min_confidence: float = 0.0) -> list[dict]:
    """Return top-n scheme matches above a confidence threshold."""
    return [r for r in match_all(user) if r["confidence"] >= min_confidence][:n]
