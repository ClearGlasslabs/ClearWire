import unittest
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from lib.artemis.compliance import (
    ActionRisk,
    CompliancePolicyEngine,
    ContinuousControlMonitor,
    ControlDefinition,
    EvidenceArtifact,
    EvidenceStatus,
    ExecutiveEvidenceVault,
    IncidentEvent,
    IncidentEvidenceEngine,
    PolicyContext,
    Provenance,
    RiskEdge,
    RiskNode,
    SupplyChainRiskGraph,
    action_digest,
)


NOW = datetime(2026, 8, 10, 12, tzinfo=timezone.utc)


def artifact(expires_at=NOW + timedelta(days=1)):
    payload = {"mfa": True}
    return EvidenceArtifact(
        "ev-1",
        "tenant-ca-1",
        "IAM-01",
        NOW - timedelta(minutes=5),
        expires_at,
        Provenance("azure", "policy-7", NOW, sha256(b"source").hexdigest(), "2.1.0"),
        frozenset({"CANADA", "ENERGY"}),
        payload,
    )


class ComplianceCommandTest(unittest.TestCase):
    def test_control_monitor_only_accepts_current_evidence(self):
        control = ControlDefinition("IAM-01", "Privileged MFA", ("CCSPA-RISK",), ("identity_policy",), "v3", "ciso")
        fresh = ContinuousControlMonitor().evaluate(control, (artifact(),), NOW)
        stale = ContinuousControlMonitor().evaluate(control, (artifact(NOW),), NOW)
        self.assertTrue(fresh.passed)
        self.assertEqual(fresh.evidence_ids, ("ev-1",))
        self.assertFalse(stale.passed)
        self.assertEqual(artifact(NOW).status_at(NOW), EvidenceStatus.STALE)

    def test_supply_chain_graph_calculates_transitive_exposure(self):
        graph = SupplyChainRiskGraph(
            (
                RiskNode("vendor", "vendor", "Identity vendor", 2),
                RiskNode("service", "software", "Access service", 4),
                RiskNode("grid", "system", "Grid operations", 5),
            ),
            (RiskEdge("vendor", "service", "supplies"), RiskEdge("service", "grid", "supports")),
        )
        self.assertEqual({node.node_id for node in graph.impacted_assets("vendor")}, {"service", "grid"})
        self.assertEqual(graph.exposure_score("vendor"), 9)

    def test_incident_chronology_uses_event_time(self):
        later = IncidentEvent("e-2", NOW, NOW, "analyst", "contained", ("ev-2",))
        earlier = IncidentEvent("e-1", NOW - timedelta(hours=1), NOW + timedelta(minutes=2), "sensor", "detected", ("ev-1",))
        self.assertEqual(tuple(event.event_id for event in IncidentEvidenceEngine().chronology((later, earlier))), ("e-1", "e-2"))

    def test_operational_actions_require_payload_bound_approval(self):
        payload = {"case_id": "case-4"}
        base = dict(actor_id="operator-1", tenant_id="tenant-ca-1", compartments=frozenset({"CANADA", "ENERGY"}), purpose="operations")
        policy = CompliancePolicyEngine()
        self.assertFalse(policy.authorize("open_case", ActionRisk.OPERATIONAL, PolicyContext(**base), "tenant-ca-1", frozenset({"ENERGY"}), payload))
        approved = PolicyContext(**base, approved_action_hash=action_digest("open_case", payload))
        self.assertTrue(policy.authorize("open_case", ActionRisk.OPERATIONAL, approved, "tenant-ca-1", frozenset({"ENERGY"}), payload))
        self.assertFalse(policy.authorize("open_case", ActionRisk.OPERATIONAL, approved, "tenant-ca-1", frozenset({"ENERGY"}), {"case_id": "case-5"}))

    def test_evidence_vault_builds_deterministic_manifest(self):
        control = ControlDefinition("IAM-01", "Privileged MFA", ("CCSPA-RISK",), ("identity_policy",), "v3", "ciso")
        result = ContinuousControlMonitor().evaluate(control, (artifact(),), NOW)
        first = ExecutiveEvidenceVault().build_package("pkg-1", "regulator", NOW, (artifact(),), (result,))
        second = ExecutiveEvidenceVault().build_package("pkg-2", "regulator", NOW, (artifact(),), (result,))
        self.assertEqual(first.manifest_hash, second.manifest_hash)


if __name__ == "__main__":
    unittest.main()
