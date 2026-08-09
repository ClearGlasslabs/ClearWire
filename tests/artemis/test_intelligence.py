import unittest
from datetime import datetime, timezone

from lib.artemis.intelligence import (
    BearCase,
    ChangeProposal,
    Decision,
    Evidence,
    LifecycleStage,
    PolicyContext,
    PolicyEngine,
    PromotionGate,
    RevenueIndependence,
    Signal,
    append_audit_event,
    deduplicate_signals,
)


class IntelligenceTest(unittest.TestCase):
    def test_revenue_independence_maps_score_to_controlled_pilot(self):
        assessment = RevenueIndependence(4, 4, 3, 4, 4, 5, 4, 3, 4)
        self.assertEqual(assessment.score(), 0.7778)
        self.assertEqual(assessment.decision(), Decision.CONTROLLED_PILOT)

    def test_bear_case_requires_explicit_assumptions(self):
        with self.assertRaisesRegex(ValueError, "assumptions"):
            BearCase(3, 4, 2, 3, ()).exposure()

    def test_policy_engine_requires_compartment_and_human_approval(self):
        context = PolicyContext("analyst-7", frozenset({"ARCTIC-CIV"}), "CA", "operations", False)
        policy = PolicyEngine()
        self.assertTrue(policy.authorize("query", context, frozenset({"ARCTIC-CIV"})))
        self.assertFalse(policy.authorize("open_case", context, frozenset({"ARCTIC-CIV"})))
        self.assertFalse(policy.authorize("query", context, frozenset({"NATO-RESTRICTED"})))

    def test_promotion_gate_blocks_regression_and_missing_approval(self):
        proposal = ChangeProposal(
            "cp-1", "prompt", "v4", "v5", "Reduce false positives", ("feedback-1",),
            {"precision": 0.88, "recall": 0.80, "latency_p95_ms": 900, "operator_acceptance": 0.85},
            "medium", "eval-service", ("reviewer-a",),
        )
        approved, reasons = PromotionGate().evaluate(
            proposal,
            {"precision": 0.90, "recall": 0.80, "latency_p95_ms": 850, "operator_acceptance": 0.82},
        )
        self.assertFalse(approved)
        self.assertIn("precision regressed", reasons)
        self.assertIn("two-person approval is required", reasons)

    def test_signal_deduplication_keeps_higher_confidence_observation(self):
        evidence = Evidence(
            "Authority", "https://example.gov/program", datetime(2026, 8, 1, tzinfo=timezone.utc),
            datetime(2026, 8, 9, tzinfo=timezone.utc), "government", "Funding was approved.", 5, True, True,
        )
        def signal(identifier, confidence):
            return Signal(identifier, "Program", evidence, ("Canada",), ("Agency",), "Arctic", "Budget",
                LifecycleStage.FUNDED, "durable program", "buyer discovery", "level 2", 3, confidence,
                ("port authority",), ("monitoring",), "approved budget", (), "verify tender", "growth", datetime(2026, 9, 1, tzinfo=timezone.utc))
        result = deduplicate_signals((signal("s-1", 2), signal("s-2", 5)))
        self.assertEqual(tuple(item.signal_id for item in result), ("s-2",))

    def test_audit_events_are_hash_chained(self):
        first = append_audit_event("GENESIS", {"action": "observe"})
        second = append_audit_event(first["event_hash"], {"action": "score"})
        self.assertEqual(second["previous_hash"], first["event_hash"])
        self.assertNotEqual(second["event_hash"], first["event_hash"])


if __name__ == "__main__":
    unittest.main()
