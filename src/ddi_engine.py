"""
Module 3 (rule-based side) — DDI Engine
Source data: data/ddi_knowledge_base.csv (see docs/data_sources_policy.md).

The engine returns literature-level pair records only. It does NOT read renal
function: renal status is assessed separately (renal.py) and displayed next to
the pair flag. No pair alert is escalated or changed by renal category in this
build.
"""
import csv

# Structured alert classes. UI badges, PDF text and batch columns are all
# derived from these values -- never from free-text fields.
ALERT_HIGH = "high_severity_interaction"
ALERT_MODERATE = "moderate_interaction"
ALERT_ANALYTICAL = "analytical_interference"
ALERT_NEGATIVE_SEARCH = "no_interaction_found_in_documented_search"
ALERT_NOT_IN_KB = "not_in_knowledge_base"

ALERT_LABELS = {
    ALERT_HIGH: "HIGH-SEVERITY INTERACTION: REVIEW REQUIRED",
    ALERT_MODERATE: "MODERATE INTERACTION: MONITORING REVIEW",
    ALERT_ANALYTICAL: "ASSAY/SPECIMEN LIMITATION: NOT A DRUG INTERACTION",
    ALERT_NEGATIVE_SEARCH: "NO INTERACTION FOUND IN DOCUMENTED SEARCH (NOT PROOF OF SAFETY)",
    ALERT_NOT_IN_KB: "NOT IN KNOWLEDGE BASE: STATUS UNKNOWN",
}


class DDIEngine:
    """Loads the DDI knowledge base and provides order-independent pair lookup."""

    def __init__(self, csv_path: str):
        self._lookup = {}
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = self._make_key(row["drug_a"], row["drug_b"])
                if key in self._lookup:
                    raise ValueError(
                        f"Duplicate DDI pair found: {row['drug_a']} + {row['drug_b']}"
                    )
                self._lookup[key] = row

    @staticmethod
    def _make_key(drug_a: str, drug_b: str) -> frozenset:
        return frozenset({drug_a.strip().lower(), drug_b.strip().lower()})

    def check_pair(self, drug_a: str, drug_b: str) -> dict:
        """
        Returns the literature-level DDI record for a drug pair, plus a
        structured `alert_class`.
        pair_found_in_kb=False means the pair is not in this project's sourced
        6-pair set — it does NOT mean an interaction has been ruled out. Only
        pairs explicitly marked interaction_present=NO with a documented negative
        search represent a checked absence, and even that is not proof of safety.
        """
        key = self._make_key(drug_a, drug_b)
        record = self._lookup.get(key)
        if record is None:
            return {
                "pair_found_in_kb": False,
                "drug_a": drug_a, "drug_b": drug_b,
                "alert_class": ALERT_NOT_IN_KB,
                "note": "Pair not present in knowledge base. This does NOT mean "
                        "an interaction has been ruled out — it means no "
                        "interaction was documented in this project's sourced "
                        "6-pair set. Only pairs marked interaction_present=NO "
                        "with a documented negative search represent a checked "
                        "absence.",
            }
        result = {"pair_found_in_kb": True, **record}
        result["alert_class"] = classify_record(result)
        return result

    def check_all_pairs(self, drug_list: list) -> list:
        """Check every pairwise combination in a patient's drug list."""
        results = []
        for i in range(len(drug_list)):
            for j in range(i + 1, len(drug_list)):
                results.append(self.check_pair(drug_list[i], drug_list[j]))
        return results


def classify_record(record: dict) -> str:
    """
    Maps a pair record to one structured alert class using only the structured
    fields interaction_present, interaction_category and severity.
    Raises on combinations the knowledge base should never contain, so a data
    error cannot silently become a reassuring label.
    """
    if not record.get("pair_found_in_kb"):
        return ALERT_NOT_IN_KB
    present = record.get("interaction_present", "").strip().upper()
    category = record.get("interaction_category", "").strip().lower()
    severity = record.get("severity", "").strip().lower()

    if category == "analytical_interference":
        return ALERT_ANALYTICAL
    if present == "YES":
        if severity == "high":
            return ALERT_HIGH
        if severity == "moderate":
            return ALERT_MODERATE
        raise ValueError(f"Unsupported severity '{record.get('severity')}' for a "
                         f"present interaction ({record.get('drug_a')}+{record.get('drug_b')})")
    if present == "NO" and category == "none":
        return ALERT_NEGATIVE_SEARCH
    raise ValueError(f"Unclassifiable knowledge-base row "
                     f"({record.get('drug_a')}+{record.get('drug_b')}): "
                     f"interaction_present={present!r}, category={category!r}")
