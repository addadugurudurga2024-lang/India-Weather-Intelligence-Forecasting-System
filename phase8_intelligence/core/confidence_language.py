"""
Phase 8 Forecast Confidence Language Engine
Enforces controlled meteorological vocabulary for uncertainty and prediction intervals.
FORBIDDEN WORDS:
'guaranteed', 'certain', '100% accurate', 'perfect', 'flawless', 'absolute certainty'.
ALLOWED TERMINOLOGY:
'prediction interval', 'forecast uncertainty', 'calibrated model probability',
'expected range', 'empirical residual dispersion'.
"""

import re
from typing import List, Tuple
from phase8_intelligence.core.schemas import ConfidenceLanguageOutput


FORBIDDEN_TERMS = [
    "guaranteed",
    "guarantee",
    "certain",
    "certainty",
    "100% accurate",
    "perfect",
    "flawless",
    "absolute certainty",
    "foolproof",
]


class ConfidenceLanguageEngine:
    """Generates approved uncertainty phrasing and audits text for forbidden terms."""

    @staticmethod
    def audit_text(text: str) -> Tuple[bool, List[str]]:
        """Returns (is_clean, list_of_violations) using strict word boundaries."""
        lower = text.lower()
        violations = []
        for term in FORBIDDEN_TERMS:
            # Word boundary matching to ensure 'certain' does not match 'uncertain' or 'uncertainty'
            pattern = rf"\b{re.escape(term)}\b"
            if re.search(pattern, lower):
                violations.append(term)
        return len(violations) == 0, violations

    @staticmethod
    def generate_confidence_statement(
        t1_spread_c: float,
        t12_spread_c: float,
        ece: float = 0.0612,
    ) -> ConfidenceLanguageOutput:
        statement = (
            f"Forecast uncertainty is quantified using empirical validation residual quantiles. "
            f"Near-term (Day 1) nominal 80% prediction intervals exhibit an expected range of ±{t1_spread_c/2:.1f}°C, "
            f"expanding to ±{t12_spread_c/2:.1f}°C at Day 12 as forecast uncertainty compounds over time. "
            f"Rainfall probabilities are calibrated with an Expected Calibration Error (ECE) of {ece*100:.1f}%, "
            f"meaning predicted probabilities closely track observed historical precipitation frequencies."
        )

        # Audit generated statement
        is_clean, violations = ConfidenceLanguageEngine.audit_text(statement)
        if not is_clean:
            raise ValueError(f"Confidence generator introduced forbidden terms: {violations}")

        return ConfidenceLanguageOutput(
            near_term_confidence_descriptor="High near-term consistency (narrow residual quantiles)",
            extended_uncertainty_descriptor="Widening prediction interval dispersion toward Day 12",
            calibration_basis=f"Fold 2 walk-forward residual calibration (ECE: {ece*100:.2f}%)",
            statement=statement,
            forbidden_terms_checked=True,
        )
