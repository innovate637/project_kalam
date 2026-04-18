from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

# ---------------------------------------------------------------------------
# Infrastructure prerequisite nodes (not schemes — things the applicant must
# set up before any DBT or document-heavy scheme can be processed).
# ---------------------------------------------------------------------------
INFRA_METADATA: dict[str, dict] = {
    "Jan Dhan Account": {
        "description": "Open a Jan Dhan (zero-balance) savings account at any bank or post office.",
        "where": "Any bank branch, Business Correspondent, or Post Office.",
    },
    "Aadhaar Linkage": {
        "description": (
            "Seed Aadhaar to your Jan Dhan / savings account and registered mobile number. "
            "Required for DBT payments and e-KYC across all welfare schemes."
        ),
        "where": "Bank branch, Aadhaar Seva Kendra, or bank's mobile app.",
    },
    "BPL/SECC Registration": {
        "description": (
            "Ensure your household is listed in the BPL or SECC-2011 database. "
            "Gateway for Ayushman Bharat, PMAY, and PM Ujjwala Yojana."
        ),
        "where": "Gram Panchayat office, urban local body, or state government portal.",
    },
}

# Infrastructure ordering: Aadhaar Linkage requires an account to link to.
_INFRA_DEPS: dict[str, list[str]] = {
    "Aadhaar Linkage": ["Jan Dhan Account"],
}

# ---------------------------------------------------------------------------
# Scheme-level dependency graph.
# Key   = scheme that must wait.
# Value = list of nodes (infra or other schemes) that must come first.
# ---------------------------------------------------------------------------
SCHEME_DEPS: dict[str, list[str]] = {
    # Agriculture / farmer DBT — all need Jan Dhan + Aadhaar seeding for transfers
    "PM Kisan": [
        "Jan Dhan Account",
        "Aadhaar Linkage",
    ],
    "MGNREGA": [
        "Jan Dhan Account",
        "Aadhaar Linkage",
    ],
    "PM Fasal Bima Yojana (PMFBY)": [
        "Jan Dhan Account",
        "Aadhaar Linkage",
    ],
    "PM Krishi Sinchayee Yojana (PMKSY)": [
        "Aadhaar Linkage",
    ],
    # Health — Ayushman Bharat requires SECC/BPL listing and Aadhaar seeding
    "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana": [
        "Aadhaar Linkage",
        "BPL/SECC Registration",
    ],
    # PVTG scheme explicitly requires an Ayushman Bharat card as a document
    "PM Janjati Adivasi Nyaya Maha Abhiyan (PM JANMAN)": [
        "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana",
        "Aadhaar Linkage",
    ],
    # Insurance — needs a bank account for premium auto-debit
    "Pradhan Mantri Suraksha Bima Yojana": [
        "Jan Dhan Account",
        "Aadhaar Linkage",
    ],
    # MSME / artisan — Aadhaar + bank mandatory for PM Vishwakarma registration
    "PM Vishwakarma": [
        "Jan Dhan Account",
        "Aadhaar Linkage",
    ],
    # Minority skilling — Aadhaar-linked bank account needed for stipend DBT
    "Pradhan Mantri Virasat ka Samvardhan": [
        "Aadhaar Linkage",
    ],
    # Trader pension — Jan Dhan + Aadhaar mandatory for enrolment
    "National Pension Scheme For Traders And Self Employed Persons": [
        "Jan Dhan Account",
        "Aadhaar Linkage",
    ],
    # Scholarship — Aadhaar-seeded account required for disbursement
    "Pradhan Mantri Uchchatar Shiksha Protsahan (PM-USP)": [
        "Aadhaar Linkage",
    ],
    # EPS — employer registers through EPFO, Aadhaar seeding mandatory
    "Employees' Pension Scheme": [
        "Aadhaar Linkage",
    ],
    # VC fund — Aadhaar-based KYC required
    "Venture Capital Fund for Scheduled Castes": [
        "Aadhaar Linkage",
    ],
    # Culture scheme — Aadhaar-linked bank account for pension disbursement
    "Scheme For Financial Assistance For Veteran Artists": [
        "Aadhaar Linkage",
    ],
}


def _build_graph(
    scheme_names: set[str],
) -> tuple[dict[str, list[str]], set[str]]:
    """
    Build the full dependency dict and node set for the given schemes.

    Returns
    -------
    deps : dict[node → list[prerequisites]]
    all_nodes : every node that must appear in the output
    """
    deps: dict[str, list[str]] = {}
    all_nodes: set[str] = set(scheme_names)

    # Add scheme-level deps for matched schemes
    for scheme in scheme_names:
        prereqs = SCHEME_DEPS.get(scheme, [])
        if prereqs:
            deps[scheme] = prereqs
            all_nodes.update(prereqs)

    # Add infra-to-infra deps (Jan Dhan → Aadhaar Linkage) only if both nodes present
    for infra, infra_prereqs in _INFRA_DEPS.items():
        if infra in all_nodes:
            deps[infra] = infra_prereqs
            all_nodes.update(infra_prereqs)

    return deps, all_nodes


def _kahn_sort(
    all_nodes: set[str],
    deps: dict[str, list[str]],
    confidence_map: dict[str, float],
) -> list[list[str]]:
    """
    Kahn's BFS topological sort.  Returns nodes grouped by level so that
    within each level we can sort independently (prerequisites first, then
    by confidence descending).  Raises ValueError on a cycle.
    """
    in_degree: dict[str, int] = {n: 0 for n in all_nodes}
    dependents: dict[str, list[str]] = defaultdict(list)

    for node, prereqs in deps.items():
        for p in prereqs:
            if p in all_nodes:
                in_degree[node] += 1
                dependents[p].append(node)

    levels: list[list[str]] = []
    current = deque(n for n in all_nodes if in_degree[n] == 0)

    while current:
        # All nodes currently ready form one level
        level = list(current)
        current.clear()

        # Within each level: infra nodes first, then by confidence desc
        level.sort(
            key=lambda n: (
                0 if n in INFRA_METADATA else 1,
                -(confidence_map.get(n, 0.0)),
            )
        )
        levels.append(level)

        for node in level:
            for dep in dependents[node]:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    current.append(dep)

    processed = sum(len(lvl) for lvl in levels)
    if processed < len(all_nodes):
        unresolved = all_nodes - {n for lvl in levels for n in lvl}
        raise ValueError(f"Dependency cycle detected among: {sorted(unresolved)}")

    return levels


def get_application_order(
    match_results: list[dict[str, Any]],
    min_confidence: float = 0.0,
) -> list[dict[str, Any]]:
    """
    Return match results sorted by recommended application order.

    Prerequisites (Jan Dhan, Aadhaar Linkage, BPL/SECC) are injected as
    leading nodes wherever needed.  Schemes with no inter-dependencies are
    sorted by confidence descending.

    Parameters
    ----------
    match_results
        Output of matcher.match_all / confidence.enrich_all.
        Each dict must have a "scheme" key; "confidence" is used for
        tie-breaking.
    min_confidence
        Exclude schemes below this threshold (default: include all).

    Returns
    -------
    List of dicts, each containing:
        scheme          – node name
        node_type       – "prerequisite" | "scheme"
        order           – 1-indexed position
        prerequisites   – direct prerequisites of this node
        confidence      – float or None (for prerequisite nodes)
        match_quality   – from confidence.py or None
        explanation     – from confidence.py or ""
        description     – human-readable step description
        needed_before   – (prerequisite nodes only) which schemes unlock
    """
    # Filter and index match results
    filtered = [r for r in match_results if r.get("confidence", 0) >= min_confidence]
    scheme_names: set[str] = {r["scheme"].strip() for r in filtered}
    by_name: dict[str, dict] = {r["scheme"].strip(): r for r in filtered}
    confidence_map: dict[str, float] = {
        name: by_name[name].get("confidence", 0.0) for name in scheme_names
    }

    if not scheme_names:
        return []

    deps, all_nodes = _build_graph(scheme_names)
    levels = _kahn_sort(all_nodes, deps, confidence_map)

    # Flatten levels into a single ordered list with metadata
    ordered: list[dict[str, Any]] = []
    position = 1

    for level in levels:
        for node in level:
            direct_prereqs = [p for p in deps.get(node, []) if p in all_nodes]

            if node in INFRA_METADATA:
                meta = INFRA_METADATA[node]
                entry: dict[str, Any] = {
                    "scheme": node,
                    "node_type": "prerequisite",
                    "order": position,
                    "description": meta["description"],
                    "where": meta["where"],
                    "prerequisites": direct_prereqs,
                    "needed_before": sorted(
                        s for s in scheme_names
                        if node in SCHEME_DEPS.get(s, [])
                    ),
                    "confidence": None,
                    "match_quality": None,
                    "explanation": "",
                }
            else:
                match = by_name.get(node, {})
                entry = {
                    "scheme": node,
                    "node_type": "scheme",
                    "order": position,
                    "description": f"Apply for {node}",
                    "prerequisites": direct_prereqs,
                    "needed_before": [],
                    "confidence": match.get("confidence"),
                    "match_quality": match.get("match_quality"),
                    "explanation": match.get("explanation", ""),
                }

            ordered.append(entry)
            position += 1

    return ordered
