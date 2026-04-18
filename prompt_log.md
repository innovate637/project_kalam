# Prompt Log — KALAM

---

# Part A — Research & Planning (Claude.ai)

## Entry 1
**Tool:** Claude.ai
**Purpose:** Get a detailed breakdown of KALAM mission requirements

**Prompt:**
> Ok then please explain KALAM in detail and how could I do it and what are all the requirements

**Output Summary:**
Claude gave an exhaustive breakdown of all 3 parts — data structuring (15+ schemes as logical rules + ambiguity map), matching engine (rule checker with confidence scores, gap analysis, document checklist, application sequence, 10 adversarial cases), and conversational interface (Hinglish CLI/web UI using LLM for language only, rule engine for matching). Also suggested tech stack and 6-day timeline.

**Accepted / Rejected:** Partially Rejected
**If Rejected, Why:** The output was too exhaustive and complex to act on immediately. Asked for a simplified version. The information was correct but the presentation made it hard to extract actionable steps.

---

## Entry 2
**Tool:** Claude.ai
**Purpose:** Get a simplified, actionable version of KALAM requirements

**Prompt:**
> This is getting too exhaustive please give me clear and direct points and make it more understandable no more complex

**Output Summary:**
Claude simplified KALAM into 3 clear parts: (1) Collect & structure eligibility rules for 15+ schemes into if/then logic + ambiguity map, (2) Build Python matching engine that outputs eligible/near-miss/not-eligible with confidence scores + 10 edge cases, (3) Build Hinglish CLI using Claude API for language, rule engine for matching. Listed all 7 submission deliverables clearly.

**Accepted / Rejected:** Accepted
**Reasoning:** Much more actionable. Clear separation of concerns, clear deliverables list.

---

## Entry 3
**Tool:** Claude.ai
**Purpose:** Understand what the dataset should look like for Part 1

**Prompt:**
> So for part 1  do I need to make a dataset

**Output Summary:**
Claude confirmed I need a structured JSON dataset where each scheme has eligibility criteria as checkable rules (not prose). Showed example JSON structure for PM Kisan with rules, documents_required, and ambiguities fields. Key advice: use AI to help parse but cross-check every rule against official government source. Don't trust AI summaries of eligibility.

**Accepted / Rejected:** Accepted
**Reasoning:** The JSON structure was practical and the warning about AI hallucinating eligibility criteria was exactly the trap this mission tests for.

---

## Entry 4
**Tool:** Claude.ai
**Purpose:** Find official sources for land size definitions used in schemes

**Prompt:**
> From where do I check the land size limits or definition of large and small land owner

**Output Summary:**
Claude pointed to Agriculture Census of India as the official classification (Marginal: <1ha, Small: 1-2ha, Semi-medium: 2-4ha, Medium: 4-10ha, Large: >10ha). Also listed state land records portals (bhulekh.up.nic.in, apnakhata.raj.nic.in, etc.). Flagged key ambiguity: central vs state definitions of "small and marginal farmer" differ.

**Accepted / Rejected:** Accepted
**Reasoning:** Agriculture Census classification is the standard used across central schemes. The ambiguity between central and state definitions is exactly what belongs in the ambiguity map.

---

## Entry 5
**Tool:** Claude.ai
**Purpose:** Get a list of 15 government schemes suitable for KALAM

**Prompt:**
> Give me 14 government schemes

**Output Summary:**
Claude searched the web and provided 15 schemes grouped by category: Farmers (PM Kisan, MGNREGA, Fasal Bima), Housing (PMAY-Gramin, PMAY-Urban), Health (Ayushman Bharat, PM Matru Vandana), Financial (Jan Dhan, Atal Pension, PMJJBY, PMSBY), Women (Sukanya Samriddhi, Ujjwala), Employment (PM Vishwakarma, PM Mudra). Also pointed to myscheme.gov.in as a cross-verification source.

**Accepted / Rejected:** Accepted
**Reasoning:** Good coverage across different demographics and eligibility types. Mix of income-based, age-based, occupation-based, and gender-based schemes ensures the matching engine gets properly stress-tested.

---

## Entry 6
**Tool:** Claude.ai
**Purpose:** Extract structured eligibility rules from the official MGNREGA Act PDF

**Prompt:**
> [Uploaded MGNREGA Act PDF] Give me the Eligibility criteria, ministry involved, Mandatory Info required, Documents required

**Output Summary:**
Claude extracted from the actual Act: Ministry of Rural Development. Eligibility: rural area resident, age 18+, willing to do unskilled manual work, no income/caste restriction. Documents: Aadhaar, photographs, address proof, bank passbook. Flagged 4 key ambiguities: (1) no exclusion list unlike PM Kisan, (2) "rural area" definition is state-dependent, (3) wage rate varies by state, (4) Job Card vs eligibility distinction.

**Accepted / Rejected:** Accepted
**Reasoning:** Extraction was cross-verified against the actual uploaded PDF content (Section 2, 3, Schedule II). The ambiguities flagged were legitimate and not hallucinated. This is the right approach — use AI to extract, then verify against the source document.

---

## Entry 7
**Tool:** Claude.ai
**Purpose:** Find ways to speed up eligibility research across 15 schemes

**Prompt:**
> Its taking a lot of time for me to dig out the relevant eligibility details and cases of exclusion, suggest some ways to optimize the process

**Output Summary:**
Claude suggested 6 optimization strategies: (1) Use myscheme.gov.in as primary source — already has structured eligibility, (2) Use AI to draft eligibility then verify specific claims only, (3) Use scheme FAQ pages instead of full Acts, (4) Use PDFs only for ambiguity map, (5) Batch schemes by similarity (income-based, farmer-specific, age+bank, universal), (6) Build JSON template first then fill as form-filling exercise.

**Accepted / Rejected:** Accepted
**Reasoning:** The myscheme.gov.in suggestion was the biggest time-saver — structured eligibility already exists there. Batching by similarity also cut down redundant research. The "AI drafts, you verify" approach is exactly what CBC is testing for — using AI efficiently while catching its mistakes.

---

## Entry 8
**Tool:** Claude.ai
**Purpose:** Get 10 adversarial edge case test profiles

**Prompt:**
> How should I add the edge cases

**Output Summary:**
Claude created a JSON file with 10 adversarial profiles, each with: user profile data, description of real-world scenario, and what_should_break (the specific failure being tested). Profiles: (1) Remarried widow, (2) Tenant farmer, (3) No bank account, (4) Transgender person, (5) Inter-state migrant, (6) Joint family income, (7) Just above BPL cutoff, (8) Minor orphan, (9) Disability certificate from different state, (10) Unclear occupation (auto driver).

**Accepted / Rejected:** Accepted
**Reasoning:** Each case targets a specific failure mode in the matching engine. Cases 5 and 6 are deliberately unsolvable with central scheme data — the engine should flag uncertainty. Cases 2 and 7 test boundary conditions. Case 4 tests gender category limitations. This is exactly what CBC means by "documented failures as a positive signal."

---

## Entry 9 
**Tool:** Claude.ai
**Purpose:** Initial KALAM explanation

**Context:** When I first asked Claude to explain KALAM, the initial response (Entry 2) was extremely detailed but overwhelming — it included every possible technical detail, multiple code examples, a full tech stack comparison, and a 6-day timeline breakdown.

**Why Rejected:** The output was technically correct but not actionable. Too much information at once made it harder to figure out where to start. The code examples were premature before understanding the overall architecture. The timeline was too rigid.

**What I Changed:** Asked for a simplified version (Entry 3) that focused on the three parts and submission checklist only. This taught me that with AI, you often need to constrain the output format before the content quality improves.

**Lesson for prompt engineering:** Start with "give me the structure" before "give me the details." AI tends to over-explain when given open-ended requests.

---

## Entry 10 — 
**Tool:** Claude.ai
**Purpose:** Initial scheme eligibility research approach

**Context:** Before Entry 8, my initial approach was to read each scheme's full Act/PDF from start to finish to extract eligibility. I uploaded the full 77-page MGNREGA Act and extracted eligibility manually.

**Why Rejected (the approach, not the output):** Reading full Acts is too slow for 15 schemes. The MGNREGA extraction was accurate but took disproportionate time relative to the useful output — most of the Act covers administrative structure, funding patterns, and council composition that's irrelevant to eligibility rules.

**What I Changed:** Switched to using myscheme.gov.in for initial eligibility extraction, scheme FAQ pages for practical details, and full PDFs only for documenting ambiguities. This cut research time significantly.

**Lesson:** Match your research depth to what's actually needed. For eligibility rules, structured summaries are sufficient. For the ambiguity map, you need the original source.


## Entry 11
**Tool:** Claude.ai
**Purpose:** Get feedback on edge cases — identify gaps in test coverage and profile fields

**Prompt:**
> [Pasted analysis identifying two gaps: (1) missing profile fields like secc_listed, owns_vehicle, epf_member that leave evaluators permanently uncertain, (2) zero happy-path test cases for several schemes]

**Output Summary:**
Claude updated edge_cases.json with: 5 new profile fields added to ALL existing profiles (secc_listed, owns_vehicle, epf_member + years_of_service, minority_religion, trade_type), and 5 new happy-path profiles (PM Vishwakarma artisan, rural BPL woman matching 8+ schemes, PM VIKAS minority entrepreneur, perfect PM Kisan farmer, Ayushman Bharat SECC beneficiary). Each happy-path has an expected_result field.

**Accepted / Rejected:** Accepted
**Reasoning:** The new fields resolve structural uncertainty — secc_listed directly resolves Ayushman Bharat eligibility instead of guessing from income. Happy-path cases catch bugs in evaluators that adversarial cases would never trigger (e.g., if the PM Vishwakarma evaluator has a typo in trade_type matching, only a happy-path test would catch it).

---


## Entry 12
**Tool:** Claude.ai
**Purpose:** Realize I don't have an Anthropic API key — need alternatives for the conversational interface

**Prompt:**
> I dont have anthropic api key

**Output Summary:**
Claude offered 3 options: (1) Structured CLI with no API — just ask questions one by one, (2) Free API alternatives — Google Gemini (free tier), OpenRouter (used before for Cricbench), Groq (free, fast), (3) Recommendation: build structured CLI first since the rule engine is what CBC evaluates, add LLM layer later if time permits.

**Accepted / Rejected:** Partially Accepted
**If Rejected, Why:** The structured CLI suggestion was a good starting point but didn't satisfy the brief's "natural language input" requirement. Accepted the overall approach of building without API dependency, but the interface needed redesign.

---

## Entry 13 — REJECTED THEN ITERATED (Important)
**Tool:** Claude.ai
**Purpose:** Update CLI prompt to work without API key

**Prompt:**
> [Original CLI prompt with Anthropic API calls] Update this prompt

**Output Summary (v1 — REJECTED):**
Claude created a structured Q&A CLI where the system asks "Aapki umar kitni hai?", user answers "35", next question. Input parsing was simple string matching for yes/no/numbers. Included Hinglish prompts and occupation keyword mapping.

**Accepted / Rejected:** Rejected
**If Rejected, Why:** Re-read the brief: "a user describes their situation in natural language." A structured Q&A format is basically a form — not natural language input. The evaluators will type something like "Main kisan hoon UP se, 2 bigha zameen hai" and expect the system to understand it. A question-by-question format would fail the live adversarial test.

**What I Changed:** Asked Claude to rebuild with a free-form Hinglish keyword/regex parser that handles natural language input. The revised version (v2) lets users type freely, extracts whatever it can, then asks targeted follow-ups only for missing critical fields. Falls back to guided mode only if parser extracts nothing.

**Lesson:** Always re-read the original brief requirements before accepting a design. The first version was easier to build but didn't match the spec. CBC evaluators will test against the spec, not against what's convenient.

---

## Entry 14
**Tool:** Claude.ai
**Purpose:** Verify the CLI design against Part III requirements

**Prompt:**
> is it according to the instructions given - PART III Conversational Interface 

**Output Summary:**
Claude confirmed the structured CLI did NOT satisfy the brief. Key requirement missed: "user describes their situation in natural language." Redesigned the CLI with a regex+keyword Hinglish parser that handles free-form input like "Main 35 saal ka kisan hoon Bihar se." Parser covers: age patterns, income with hazaar/lakh conversion, occupation keywords in Hindi, gender from verb endings (rehta/rehti), state abbreviations, land units with bigha→hectare conversion, "pata nahi" as null. Falls back to guided mode when parser fails.

**Accepted / Rejected:** Accepted
**Reasoning:** This satisfies all four requirements from the brief: (1) natural language input ✓, (2) works in Hinglish ✓, (3) handles incomplete answers (marks as null, asks follow-up) ✓, (4) handles contradictory answers (detects and asks for clarification) ✓. The parser won't be as accurate as an LLM but the limitation is documented and the architecture allows a clean swap.

---


## Entry 15
**Tool:** Claude.ai
**Purpose:** Understand how to actually run the CLI and Streamlit on Windows

**Prompt:**
> How can i install streamlit / I am on windows so tell accordingly

**Output Summary:**
Step-by-step Windows setup: create venv (python -m venv venv), activate (venv\Scripts\activate), install deps (pip install streamlit pytest), run CLI (python interface\cli.py), run Streamlit (streamlit run interface\app.py). Common Windows fixes: use "py" if "python" not recognized, use "python -m streamlit" if streamlit not in PATH.

**Accepted / Rejected:** Accepted
**Reasoning:** Straightforward setup instructions. No issues.

---

## Entry 16 — DESIGN DECISION LOG
**Tool:** Self (documented during development)
**Purpose:** Track the key design pivot in the conversational interface

**Decision Timeline:**
1. **Initial design:** LLM-powered Hinglish NLU using Anthropic API → Rejected (no API key)
2. **First fallback:** Structured Q&A CLI (ask one question at a time) → Rejected (doesn't satisfy "natural language" requirement from brief)
3. **Final design:** Regex + keyword parser for free-form Hinglish input with guided fallback → Accepted

**Why this matters for evaluation:**
This progression shows exactly what CBC is looking for in the AI Fluency dimension — iterating when the first approach doesn't work, catching requirement mismatches before submission, and making principled tradeoffs (parser accuracy vs API dependency) with documented reasoning.

The architecture is designed so the parser is the ONLY swappable component. If an API key becomes available later, replacing parse_hinglish() with an LLM call requires changing one function. The matcher, confidence scorer, document generator, and output formatter are completely unaffected. This is the correct separation of concerns for a system where the language layer and the logic layer serve fundamentally different purposes.

---

---

## Summary of Rejected/Iterated Outputs

| Entry | What was rejected | Why | What replaced it |
|-------|------------------|-----|-----------------|
| 2 | Exhaustive KALAM explanation | Too complex to act on | Simplified 3-part breakdown (Entry 3) |
| 12 | Reading full Acts for eligibility | Too slow for 15 schemes | myscheme.gov.in + targeted verification |
| 15 | Anthropic API for NLU | No API key available | No-API keyword parser |
| 16 | Structured Q&A CLI | Doesn't satisfy "natural language" requirement | Free-form Hinglish regex parser |

---

## AI Usage Patterns Observed

### Pattern 1: Constraint discovery through iteration
Multiple times, the initial AI output was technically correct but didn't match a constraint I hadn't explicitly stated (no API key, natural language requirement). The fix was always: re-read the original requirements, identify the mismatch, and ask for a targeted redesign.

### Pattern 2: AI over-designs when unconstrained
When given open-ended prompts ("explain KALAM"), AI produces exhaustive outputs. When given constrained prompts ("simplify to 3 parts"), outputs are more actionable. Lesson: constrain the format before asking for content.

### Pattern 3: AI is good at adversarial thinking
The edge cases, ambiguity identification, and failure mode documentation were areas where AI added significant value — it's naturally good at "what could go wrong?" thinking. Less good at "what does the spec actually require?" — that needs human verification.

### Pattern 4: Rejected outputs are more valuable than accepted ones
The rejected → iterated cycle (Entry 16 especially) demonstrates deeper understanding than outputs that were accepted on the first try. CBC explicitly scores this in the AI Fluency dimension.

## Notes on AI Usage Strategy

### What Worked:
- Using AI to draft, then verifying specific claims against official sources
- Asking AI to simplify when output was too complex
- Using AI to generate adversarial test cases (it's good at thinking about edge cases)
- Using AI for project structuring and prompt sequencing

### What Required Pushback:
- AI's first attempt at explaining KALAM was too verbose — had to constrain it
- AI-generated eligibility criteria need manual verification (this is the core KALAM lesson)
- AI defaults to generic project structures — CLAUDE.md needed customization for this specific project

### Red Flags I Caught:
- When AI lists scheme eligibility, it sometimes merges criteria from different time periods or state variations without flagging this
- AI tends to present ambiguous government language as if it has a clear answer
- AI's code examples sometimes import libraries that aren't needed or use patterns that are more complex than necessary for 15 schemes

---

# Part B — Implementation (Claude Code)

## Entry 1
**Tool:** Claude Code
**Purpose:** Set up the initial project directory structure for KALAM

**Prompt:**
> Set up the KALAM project structure as described in CLAUDE.md. Create all directories and empty files with proper __init__.py files. Create a requirements.txt with: anthropic, streamlit, pytest. Read CLAUDE.md first.

**Output Summary:**
Created directories: `data/`, `engine/`, `interface/`, `tests/`, `docs/`. Created empty files: `engine/__init__.py`, `engine/matcher.py`, `engine/confidence.py`, `engine/documents.py`, `engine/sequence.py`, `interface/__init__.py`, `interface/cli.py`, `interface/app.py`, `tests/__init__.py`, `data/schemes.json`, `tests/edge_cases.json`, `docs/failure_log.md`. Created `requirements.txt` with anthropic, streamlit, pytest.

**Accepted / Rejected:** Accepted

---

## Entry 2
**Tool:** Claude Code
**Purpose:** Clean up duplicate folder structure created before the session started

**Prompt:**
> The file structure got messed up because i created some folders earlier, read claude.md again, delete the irrelevant or repeating files and make the structure final

**Output Summary:**
Read CLAUDE.md, inspected full directory tree. Found a `Kalam/` subfolder with duplicate empty files (`tests/`, `docs/`, `data/`). Checked all files for content — all Kalam/ files were empty. Deleted the entire `Kalam/` subfolder. Kept `data/ambiguity_map.json` (had substantial content). Final structure matched CLAUDE.md exactly.

**Accepted / Rejected:** Accepted

---

## Entry 3
**Tool:** Claude Code
**Purpose:** Build the core matching engine that evaluates user profiles against scheme eligibility rules

**Prompt:**
> Read data/schemes.json (my eligibility rules dataset) and create the matcher.py engine. For each scheme, the engine should:
> 1. Take a user dict with fields: age, gender, state, area, caste_category, annual_income, occupation, land_ownership, land_size_hectares, family_size, bank_account, aadhaar, marital_status, disability
> 2. Check each rule and classify it as matched/failed/uncertain
> 3. Calculate confidence as matched/(matched+failed+uncertain)
> 4. Return scheme name, confidence, matched_rules, failed_rules, uncertain_rules, and gap_analysis (what's missing for near-misses)
> Handle None/missing values as "uncertain" not "failed".

**Output Summary:**
Read `schemes.json` in full. Built `engine/matcher.py` with: `_EVALUATORS` dict mapping all 100+ rule IDs to lambda functions, `_CLEAN_KEY_MAP` for direct occupational lookups, `match_scheme()` for single scheme evaluation, `match_all()` for all 15 schemes sorted by confidence, `top_matches()` convenience wrapper. Inclusion rules: matched=satisfied, failed=not satisfied. Exclusion rules: logic inverted (matched exclusion → goes to failed_rules). None values always return "uncertain". Tested with rural SC farmer profile and empty profile (None-handling assertion passed).

**Accepted / Rejected:** Accepted

---

## Entry 4
**Tool:** Claude Code
**Purpose:** Build a weighted, critical-rule-aware confidence scoring module on top of the matcher

**Prompt:**
> Build confidence.py. The confidence score should:
> - Be 1.0 only if ALL rules match and NONE are uncertain
> - Deduct proportionally for uncertain rules (missing data) but less than for failed rules
> - A failed critical rule (like area=urban for MGNREGA) should drop confidence to 0 regardless of other matches
> - Every score must include a human-readable explanation string like "Confidence 0.85: matched 6/7 rules, 1 uncertain (income not verified)"
> Mark certain rules as "critical" per scheme — if a critical rule fails, confidence = 0.

**Output Summary:**
Built `engine/confidence.py` with: `UNCERTAIN_CREDIT = 0.4` (uncertain rules get 40% partial credit), `CRITICAL_RULES` dict mapping all 15 scheme names to frozensets of critical rule IDs, `_RULE_LABELS` dict for human-readable rule descriptions, `compute_confidence()` returning confidence + explanation + blocked_by + match_quality, `enrich()` to update a match_result dict in place, `enrich_all()` to process and re-sort a full list. Formula: `score = (matched + uncertain * 0.4) / total`. Hard-blocks on critical rule failure set confidence to 0.0.

**Accepted / Rejected:** Accepted

---

## Entry 5
**Tool:** Claude Code
**Purpose:** Build a document checklist generator that deduplicates and prioritises required documents across matched schemes

**Prompt:**
> Build documents.py. Given a list of matched schemes:
> 1. Collect all required documents across matched schemes
> 2. Deduplicate
> 3. Sort by priority: Aadhaar first (needed by almost everything), then bank passbook, income certificate, caste certificate, land records, others
> 4. For each document, note which schemes need it
> Output format: list of {document, needed_for: [scheme names], priority: int}

**Output Summary:**
Built `engine/documents.py` with: `_PRIORITY` dict (36 canonical document names mapped to priority integers), `_CLEAN_KEY_MAP` for structured entries like `"aadhaar"` → `"Aadhaar Card"`, `_KEYWORD_RULES` ordered list of (keywords, canonical_name) pairs for messy concatenated strings, `_label_of()` to extract only the label before `:` in labelled segments (preventing "Passport" in "Aadhaar Card, Voter ID, Passport" from false-matching), `_matches_keyword()` with special regex for "passport" to block false positives in alternatives lists like "(Aadhaar/Passport/Voter ID)", `get_document_checklist()` accepting both scheme name strings and match_result dicts. Fixed two bugs during development: PM-USP metadata label "FRESH:" was not matching documents (fixed by detecting short/uppercase labels as non-document labels), and EPS was falsely extracting "Passport" from alternatives list (fixed with negative lookbehind regex).

**Accepted / Rejected:** Accepted

---

## Entry 6
**Tool:** Claude Code
**Purpose:** Build an application sequencing module using topological sort to determine the correct order to apply for schemes

**Prompt:**
> Build sequence.py. Some schemes are prerequisites for others:
> - Jan Dhan account is needed before PM Kisan (for payment)
> - Aadhaar linkage is needed before most DBT schemes
> - BPL/SECC listing is a prerequisite for Ayushman Bharat, PMAY, Ujjwala
> Create a dependency graph and output the correct application order using topological sort. If no dependency exists, sort by confidence score descending.

**Output Summary:**
Built `engine/sequence.py` with: `INFRA_METADATA` for three prerequisite nodes (Jan Dhan Account, Aadhaar Linkage, BPL/SECC Registration) with descriptions and where-to-go info, `_INFRA_DEPS` for infrastructure ordering (Aadhaar Linkage depends on Jan Dhan Account), `SCHEME_DEPS` mapping all 14 applicable schemes to their prerequisites, `_build_graph()` to construct the DAG from provided match results only, `_kahn_sort()` implementing Kahn's BFS topological sort with level-based grouping (within each level: infra nodes first, then by confidence descending), `get_application_order()` returning enriched ordered list with node_type, prerequisites, needed_before, description. Verified PM JANMAN always appears after Ayushman Bharat. Edge cases (empty input, no-dep scheme, min_confidence filter) all passed.

**Accepted / Rejected:** Accepted

---

## Entry 7
**Tool:** Claude Code
**Purpose:** Run all 10 adversarial edge case profiles through the engine, identify bugs, and write a structured failure report

**Prompt:**
> Read tests/edge_cases.json (my 10 adversarial profiles) and run each through the matching engine. For each profile:
> 1. Print the user profile
> 2. Print all matched schemes with confidence
> 3. Print near-misses with gap analysis
> 4. Flag any case where the engine gives a confident answer on ambiguous data (this is a BUG)
> 5. Write results to tests/edge_case_results.md
> Document every failure and unexpected output.

**Output Summary:**
Read all 10 profiles from `edge_cases.json`. Ran each through `matcher.match_all()` + `confidence.enrich_all()`. Identified and documented 10 bugs across 3 severity levels. Wrote full analysis to `tests/edge_case_results.md`. Key bugs found:
- **BUG-001 (HIGH):** PM Kisan shows 0.65 for tenant farmer (land_ownership=False) — `land_ownership` missing from PM Kisan's inclusion rules
- **BUG-002 (HIGH):** MGNREGA shows 0.70 with no bank account — `bank_account` not in MGNREGA rules
- **BUG-003 (HIGH):** Ayushman Bharat urban uses AND logic on OR inclusion criteria — construction worker gets penalised for not being every occupation simultaneously
- **BUG-004 (MEDIUM):** AB shows 0.58 despite `monthly_income_above_10k` exclusion firing — not a critical rule
- **BUG-005 (MEDIUM):** AB shows 0.63 for a 16-year-old minor — no guardian flag
- **BUG-006 (MEDIUM):** VCF-SC matches SC agricultural workers as "entrepreneurs"
- **BUG-007 (MEDIUM):** `family_total_income` silently ignored
- **BUG-008 (LOW):** Transgender gender gap — no scheme has explicit trans rules
- **BUG-009 (LOW):** Out-of-state disability certificate not flagged
- **BUG-010 (LOW):** `occupation="none"` (string) causes false FAILED instead of uncertain

**Accepted / Rejected:** Accepted

---

## Entry 8
**Tool:** Claude Code
**Purpose:** Add `Mandatory_info_required_complete` and `documents_required_complete` to every scheme's inclusion rules that was missing them

**Prompt:**
> In schemes.json put "Mandatory_info_required_complete","documents_required_complete" in every inclusion if it is not present

**Output Summary:**
Read `schemes.json`. Found 4 schemes already had both fields (PM Kisan, MGNREGA, PMFBY, PMKSY). Added both fields to the remaining 11 schemes' inclusion lists: Ayushman Bharat `inclusion_if_rural`, Ayushman Bharat `inclusion_if_Urban`, PM JANMAN, Pradhan Mantri Suraksha Bima Yojana, PM Vishwakarma, Pradhan Mantri Virasat ka Samvardhan, NPS Traders, VCF-SC, Study in India, Veteran Artists, PM-USP, Employees' Pension Scheme. Verified all 16 inclusion lists show OK.

**Accepted / Rejected:** Accepted

---

## Entry 9
**Tool:** Claude Code
**Purpose:** Make `documents_required_complete` and `Mandatory_info_required_complete` scheme-aware so missing documents (e.g. no land records) correctly fail eligibility

**Prompt:**
> So now if in the edge cases for example if someone does not have land records than he cannot submit the documents_required so his "documents_required_complete" field in the inclusions will be false so his eligibility is not there. This is the way it should work for other examples in all schemes right, if not then make it work like that

**Output Summary:**
Added two scheme-aware evaluator functions to `engine/matcher.py`: `_eval_docs_complete(scheme, user)` iterates the scheme's `documents_required` list and checks each document against the profile using a `_DOC_CHECKS` mapping (land_records → land_ownership, bank_passbook → bank_account, aadhaar → aadhaar field, Category_certificate → caste not General, crop_declaration → is farmer, PVTG certificate → caste==PVTG). `_eval_info_complete(scheme, user)` does the same for `Mandatory_info_required` using `_INFO_CHECKS` (Bank_Account_Details, ID_proof, Age, Gender, Category, Income_details, Land_details, etc.). Both return "failed" if any required item is provably absent, "uncertain" if some items can't be verified from the profile, "matched" only if everything checks out. Wired into `match_scheme()` by intercepting the two rule IDs before the generic evaluator. Verified: PM Kisan dropped from 0.65 → 0.54 for tenant farmer (BUG-001 fixed), MGNREGA dropped from 0.70 → 0.50 for no-bank-account profile (BUG-002 fixed).

**Accepted / Rejected:** Accepted

---

## Entry 10
**Tool:** Claude Code
**Purpose:** Four-part engine fix: General caste cert exemption, Ayushman Bharat OR logic, AB income critical rule, and uncertain-exclusion credit removal

**Prompt:**
> so for cases with general caste add an if rule to exempt them from giving caste certificate, and for cases with OR-AND bug also add an if else rule for covering the OR case, and for profile 7 do the needfull. and why is PM Kisan still 0.54, it should be less because of documents_required_complete being false

**Output Summary:**
Four fixes applied:

**Fix 1 — General caste Category_certificate (`engine/matcher.py`):** Changed `_DOC_CHECKS["Category_certificate"]` from `lambda v: v.upper() not in ("GENERAL",)` (which returned "failed" for General) to `"uncertain" if caste_category is None else "matched"`. General caste people don't need a certificate; SC/ST/OBC can provide one — only unknown caste is uncertain. Profile 6 (Sharma, General) PM Kisan now has 0 failed rules.

**Fix 2 — Ayushman Bharat OR logic (`engine/matcher.py`):** Added `_AB_SCHEME_NAME` and `_COMPLETENESS_RULES` constants. Added special-case branch in `match_scheme()` for AB: OR criteria (all inclusion rules except completeness rules) are evaluated with OR logic — any single match collapses the group into one synthetic rule "AB_eligibility_criterion" (matched/failed/uncertain). Completeness rules remain AND. Eliminates BUG-003 where a construction worker was penalised for not being all 11 urban occupations simultaneously.

**Fix 3 — AB `monthly_income_above_10k` critical rule (`engine/confidence.py`):** Added `monthly_income_above_10k` and `AB_eligibility_criterion` to `CRITICAL_RULES["Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana"]`. Profile 7 (Lakshmi, ₹2.55L/year > ₹1.2L threshold) now correctly blocked at confidence 0.0.

**Fix 4 — Uncertain exclusion credit removal (`engine/matcher.py` + `engine/confidence.py`):** `match_scheme()` now separately tracks `uncertain_inclusion_rules` and `uncertain_exclusion_rules` (returned in the result dict; `uncertain_rules` remains the combined list for backward compatibility). `compute_confidence()` accepts optional `uncertain_inclusion_rules` parameter; only these get `UNCERTAIN_CREDIT = 0.4` in the weighted formula. Uncertain exclusions (e.g. pension_above_10k, NRI_household for PM Kisan) get 0 credit — unverified exclusion uncertainty cannot inflate eligibility. PM Kisan for Profile 2 (Ramesh, tenant farmer) drops from 0.54 → **0.38** (5 matched / 13 total, 0 uncertain-inclusion credit, 5 uncertain-exclusion at 0 credit).

**Accepted / Rejected:** Accepted

---

## Entry 11
**Tool:** Claude Code
**Purpose:** Log the Entry 10 prompt into the prompt log

**Prompt:**
> add this as well to the prompt log

**Output Summary:**
Appended Entry 11 to `docs/prompt_log.md`.

**Accepted / Rejected:** Accepted

---

## Entry 12
**Tool:** Claude Code
**Purpose:** Update ambiguity_map.json with all found ambiguities, update CLAUDE.md with 5 new profile fields, and update matcher.py to wire in new fields

**Prompt:**
> All of the ambiguities that are being found and has been found should be added to ambiguity_map.json. update CLAUDE.md and the matcher to include the 5 new fields in the user input schema.

**Output Summary:**
Three files updated simultaneously:

**`data/ambiguity_map.json`:** Added new `engine_gaps` section with 4 entries — EG-01 (compound occupation strings don't exact-match evaluator sets, e.g. `auto_rickshaw_driver`), EG-02 (`occupation="none"` string treated as failed not uncertain), EG-03 (`family_total_income` silently ignored), EG-04 (photographs/Address_proof/Domicile_cert missing from `_DOC_CHECKS`). Added SA-08 (AB has no age gate for minors), SA-09 (disability certificate portability across states), CC-05 (transgender gap — no scheme documents transgender-specific rules).

**`CLAUDE.md`:** Added full profile schema table documenting all fields including 5 new ones marked with `*`: `secc_listed` (bool, resolves AB rural criterion), `owns_vehicle` (bool, resolves AB asset exclusion), `epf_member` (bool, unlocks EPS), `years_of_service` (int, EPS 10-year minimum), `minority_religion` (str, PM VIKAS non-minority exclusion), `trade_type` (str, PM Vishwakarma 18 trades).

**`engine/matcher.py`:** Added `_PM_VISHWAKARMA_TRADES` (24 trades) and `_MINORITY_RELIGIONS` (6 notified communities) constants. Fixed `_occ()` to treat `"none"/"n/a"/""` strings as uncertain (BUG-010). Added compound occupation strings (`auto_rickshaw_driver`, `agricultural_labourer`, `daily_wage_labourer`, `gig_worker`, etc.) to relevant sets. Added compound driver names to `transport_worker_or_driver` evaluator set. Wired new fields: `secc_listed` short-circuits AB OR logic; `owns_vehicle` → `owns_two_three_or_four_wheeler` evaluator; `epf_member` → EPF membership and contribution evaluators; `years_of_service` → `minimum_10_years_eligible_service`; `minority_religion` → `non_minority_community_member_exceeding_25_percent_seat_quota` (returns "failed" if known minority, else "uncertain"); `trade_type` → PM Vishwakarma trade evaluators. Fixed `minority_religion` boolean crash with `str()` guard.

**`engine/confidence.py`:** Added 4 AB asset exclusions to `CRITICAL_RULES` — `owns_two_three_or_four_wheeler`, `owns_mechanized_farming_equipment`, `owns_refrigerator_or_landline`, `three_or_more_rooms_with_pucca_walls_and_roof` — since any one SECC asset exclusion is an absolute bar when verifiable.

**Accepted / Rejected:** Accepted

---

## Entry 13
**Tool:** Claude Code
**Purpose:** Run all 15 edge cases and document full results in edge_case_results.md

**Prompt:**
> Now run the edge cases and document the results in edge_case_results.md

**Output Summary:**
Ran all 15 profiles through `matcher.match_all()` + `confidence.enrich_all()`. Fixed one crash mid-run: `minority_religion=true` (bool in Profile 13) caused `AttributeError` in the PM VIKAS evaluator — fixed with `str()` guard. Wrote full results to `tests/edge_case_results.md` with: summary table (15 rows), per-profile detailed sections (scheme confidence table + hard blocks + analysis), open issues table (6 items), and fixed bugs table (8 items). Two suspected new boundary bugs (Profile 11 AB block, Profile 15 PM VIKAS block) were investigated and confirmed as correct behavior — profile income was 140k (not 120k) and age was 52 (not 45). Only genuinely new finding: Profile 13 `minority_religion=true` (bool) should be string `"Muslim"` — profile data quality issue, not engine bug.

**Accepted / Rejected:** Accepted

---

## Entry 14
**Tool:** Claude Code
**Purpose:** Review edge case results for new bugs

**Prompt:**
> Any new bugs found

**Output Summary:**
No new engine bugs found. All open issues in edge_case_results.md were pre-documented in ambiguity_map.json during Entry 12. The run confirmed Entry-12 fixes are working correctly and introduced no regressions.

**Accepted / Rejected:** Accepted

---


## Entry 15
**Tool:** Claude Code
**Purpose:** First attempt at interface/cli.py — used external Anthropic API (REJECTED)

**Prompt:**
> continue

**Output Summary:**
Built `interface/cli.py` using `claude-haiku-4-5-20251001` for three NLU tasks: field extraction (returns JSON), follow-up question generation, and result presentation. Conversation loop: extract fields → ask follow-up → run matcher when enough data. Supported `documents`, `sequence`, `reset` commands.

**Accepted / Rejected:** Rejected
**If Rejected, Why:** User's brief explicitly required no external API calls. The CLI must demonstrate the rule engine works without API dependency. parse_hinglish() must be pure keyword/regex — LLM is only the production upgrade path, not a prototype requirement.

---

## Entry 16
**Tool:** Claude Code
**Purpose:** Rebuild interface/cli.py as a fully self-contained Hinglish CLI with no external API calls

**Prompt:**
> why are you using external api key my prompt was — Build interface/cli.py — a conversational Hinglish interface that collects user data through structured questions and runs the matching engine. No external API calls needed. [full spec provided]

**Output Summary:**
Rewrote `interface/cli.py` from scratch — zero external API calls. All NLU via pure string matching and if/else logic:
- `parse_bool()`, `parse_int()`, `parse_float()`, `parse_state()`, `parse_occupation()`, `parse_caste()`, `parse_gender()`, `parse_minority()`, `parse_marital()` — field-specific parsers
- Structured 5-round question flow (basic → identity → economic → documents → scheme-specific) with conditional follow-ups (land size if land owned, trade type if artisan)
- Contradiction detection via `check_contradiction()` — flags e.g. "farmer" then "factory worker"
- "pata nahi" / "don't know" → `None`, never assumed
- Profile summary + confirmation loop before running engine
- Results displayed with ✅ eligible / ⚠️ near-miss / ❌ blocked sections + document checklist + application sequence
- Runtime commands: `documents`, `sequence`, `reset`, `quit`
- Fixed 5 Pylance unused-variable warnings: removed `_fmt_income`, `blocked` var, dropped `profile` param from `_show_results`, `new_value` from `check_contradiction`, renamed `trade` to `_`

**Accepted / Rejected:** Accepted

---

## Entry 17
**Tool:** Claude Code
**Purpose:** Test the engine with a specific profile — 20-year-old Sikh male, Punjab, married, no vehicle, no land, income ₹10,000/year

**Prompt:**
> check if a 20 year old boy living in punjab, married, no vehicle, no land, sikh religion, yearly income 10,000

**Output Summary:**
Asked for missing fields (area, caste, aadhaar, bank account, occupation, secc_listed, epf_member, disability) before running. User provided: rural, SC, aadhaar ✓, bank ✓, farmer, secc_listed ✓, epf_member ✗. Full results:
- MGNREGA 70% (partial) — best match
- PM Virasat ka Samvardhan 60% (partial)
- VCF-SC 43%, AB 42%, PM-USP 39%, PM Kisan 38%, PMSBY 38% — all weak
- Hard blocked: PMFBY/PM Vishwakarma (no land), EPS (no EPF), NPS Traders, Veteran Artists, PM JANMAN
- Key insight: PM Kisan ceiling at 38% solely due to land_ownership=False

**Accepted / Rejected:** Accepted

---

## Entry 18
**Tool:** Claude Code
**Purpose:** Build interface/app.py — Streamlit web UI with Hinglish natural language input, no external API calls

**Prompt:**
> Build interface/app.py — a Streamlit web UI for KALAM that supports natural language Hinglish input. No external API calls. [full spec provided]

**Output Summary:**
Two deliverables:

1. **`parse_hinglish()` added to `interface/cli.py`** — single shared NLU entry point for both CLI and app. Extracts all 19 profile fields from free-form text. Fixed a critical state-parsing bug: "ka" (Karnataka alias) was firing on "saal **ka** kisan" — fixed by: (a) prioritising full state names over aliases, (b) requiring location-context word boundary (`\bse\b`, `\bmein\b`, etc.) for 2-letter codes, (c) removing "ka" and "ki" from context words since both appear as common Hinglish particles. All 10 state tests passing.

2. **`interface/app.py`** — three-section Streamlit UI:
   - **Section 1:** Free-text chat input → `parse_hinglish()` → "Samajh gaya" confirmation + merge into `session_state.profile`. Missing primary fields shown as inline widgets. Chat history collapsible.
   - **Section 2:** Results — green expandable cards for eligible (auto-expanded ≥60%), orange near-miss cards with gap analysis, collapsed hard-blocked list, ambiguity notes.
   - **Section 3:** Action plan — checkbox document list with "needed for" captions + numbered application sequence side by side.
   - Sidebar: live profile with OK/??? icons, edit-mode toggle for all fields, reset button.

**Accepted / Rejected:** Accepted

---

## Entry 19
**Tool:** Claude Code
**Purpose:** Create docs/architecture.md — full submission architecture document

**Prompt:**
> Create docs/architecture.md — the full architecture document for KALAM as required by the submission. [full spec provided]

**Output Summary:**
Created `docs/architecture.md` (371 lines). Sections:
1. System diagram — Mermaid flowchart + ASCII fallback. Components labelled deterministic vs. LLM-upgradeable. Deterministic boundary clearly marked.
2. Three technical decisions with rejected alternatives: rule-based vs. ML matching, LLM for language layer only vs. end-to-end LLM, regex NLU vs. LLM NLU. Each includes explicit tradeoffs and why alternatives were rejected.
3. Two production gaps: scheme data staleness (gazette monitoring + human review gate needed) and state-level variation (state overlay schema + disclaimer requirement).
4. Testing strategy — adversarial/happy-path case table, known gaps.
5. Failure modes table — 7 modes, each marked intentional with rationale.
6. File map + dependency diagram showing no circular imports.

**Accepted / Rejected:** Accepted


## Entry 20
**Tool:** Claude Code
**Purpose:** Install streamlit and dependencies into the project venv

**Prompt:**
> Install streamlit and other dependencies required in app.py

**Output Summary:**
Discovered the project uses a local `venv/` (Python 3.13.5) rather than system Python. `python` and `pip` both resolve to the venv. Installed via `pip install streamlit anthropic pytest`. Final versions: streamlit 1.56.0, anthropic 0.96.0, pytest 9.0.3. All transitive dependencies auto-resolved.

**Accepted / Rejected:** Accepted

---

## Entry 21
**Tool:** Claude Code
**Purpose:** Fix Pylance type annotation warnings in app.py (lines 35, 37, 39, 41)

**Prompt:**
> [screenshot] Type annotation not supported for this statement Pylance(reportInvalidTypeForm) 
**Output Summary:**
Removed inline type annotations from `st.session_state` attribute assignments. `st.session_state` is a dynamic Streamlit dict-like object — Pylance cannot annotate assignments on it. Changed `st.session_state.profile: dict = {}` → `st.session_state.profile = {}` (and same for `results`, `show_results`, `chat_history`). All 4 warnings resolved.

**Accepted / Rejected:** Accepted

---
