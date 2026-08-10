from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from artemis.evolution import (  # noqa: E402
    ArtifactVersions,
    CandidateKind,
    EvaluationReport,
    EvolutionController,
    FeedbackSignal,
    ReleaseStage,
    UpgradeCandidate,
    deterministic_variant,
    feedback_dataset_hash,
)


class EvolutionControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = EvolutionController()
        self.candidate = UpgradeCandidate(
            candidate_id="chg_01",
            kind=CandidateKind.PROMPT,
            base_version="p17",
            candidate_version="p18",
            changed_fields=frozenset({"triage_instructions"}),
            rationale="Separate approved funding from contracted spend",
        )
        self.report = EvaluationReport(
            dataset_hash="sha256:golden",
            sample_size=500,
            precision=0.94,
            recall=0.91,
            unsupported_claim_rate=0.01,
            policy_violations=0,
            cross_compartment_leaks=0,
            latency_p95_ms=420,
            operator_acceptance=0.88,
        )

    def test_requires_distinct_product_and_security_approvers(self) -> None:
        self.controller.attach_evaluation(self.candidate, self.report)
        self.controller.approve(self.candidate, "product_owner", "operator-1")

        with self.assertRaisesRegex(ValueError, "distinct"):
            self.controller.approve(self.candidate, "security_steward", "operator-1")

        self.controller.approve(self.candidate, "security_steward", "operator-2")
        self.assertEqual(self.candidate.stage, ReleaseStage.APPROVED)

    def test_rejects_candidate_that_changes_a_protected_guardrail(self) -> None:
        self.candidate.changed_fields = frozenset({"mission_goal", "triage_instructions"})

        with self.assertRaisesRegex(ValueError, "mission_goal"):
            self.controller.attach_evaluation(self.candidate, self.report)

    def test_enforces_ordered_promotion_and_supports_rollback(self) -> None:
        self.controller.attach_evaluation(self.candidate, self.report)
        self.controller.approve(self.candidate, "product_owner", "operator-1")
        self.controller.approve(self.candidate, "security_steward", "operator-2")

        with self.assertRaisesRegex(ValueError, "invalid release transition"):
            self.controller.promote(self.candidate, ReleaseStage.PRODUCTION)

        self.controller.promote(self.candidate, ReleaseStage.SHADOW)
        self.controller.promote(self.candidate, ReleaseStage.CANARY_5)
        self.controller.rollback(self.candidate)
        self.assertEqual(self.candidate.stage, ReleaseStage.ROLLED_BACK)

    def test_blocks_promotion_when_evaluation_detects_policy_violation(self) -> None:
        unsafe_report = EvaluationReport(**{**self.report.__dict__, "policy_violations": 1})
        self.controller.attach_evaluation(self.candidate, unsafe_report)
        self.controller.approve(self.candidate, "product_owner", "operator-1")
        self.controller.approve(self.candidate, "security_steward", "operator-2")

        with self.assertRaisesRegex(ValueError, "safety violations"):
            self.controller.promote(self.candidate, ReleaseStage.SHADOW)


class EvolutionDatasetTest(unittest.TestCase):
    def test_feedback_hash_is_stable_and_bound_to_artifact_versions(self) -> None:
        versions = ArtifactVersions("p17", "w9", "r4", "o3", "pol8", "ds21")
        first = FeedbackSignal("i-2", "actor", versions, "reject", "unsupported_claim")
        second = FeedbackSignal("i-1", "actor", versions, "accept", "correct")

        self.assertEqual(feedback_dataset_hash((first, second)), feedback_dataset_hash((second, first)))
        changed = FeedbackSignal("i-1", "actor", ArtifactVersions("p18", "w9", "r4", "o3", "pol8", "ds21"), "accept", "correct")
        self.assertNotEqual(feedback_dataset_hash((first, second)), feedback_dataset_hash((first, changed)))

    def test_variant_assignment_is_deterministic(self) -> None:
        assignments = {deterministic_variant("case-42", "prompt-p18", 5) for _ in range(10)}

        self.assertEqual(len(assignments), 1)


if __name__ == "__main__":
    unittest.main()
