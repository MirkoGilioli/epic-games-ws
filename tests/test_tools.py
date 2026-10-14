"""
Unit Tests for Titan LiveOps Agent Tools
"""

import unittest
from titan_agent.tools.telemetry_tool import query_telemetry_metrics
from titan_agent.tools.crash_diagnostics import lookup_unreal_crash_signature, fetch_remediation_runbook

class TestTitanTools(unittest.TestCase):

    def test_telemetry_tool_query_all(self):
        result = query_telemetry_metrics()
        self.assertEqual(result["status"], "success")
        self.assertGreater(len(result["records"]), 0)

    def test_telemetry_tool_filter_shard(self):
        result = query_telemetry_metrics(shard_id="eu-west-03")
        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["shard_id"], "eu-west-03")
        self.assertGreaterEqual(len(result["anomalies_detected"]), 1)
        self.assertEqual(result["anomalies_detected"][0]["severity"], "CRITICAL")

    def test_crash_diagnostics_by_hash(self):
        result = lookup_unreal_crash_signature(crash_hash="CRASH-UE5-NET-0842")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["crash_signatures"]), 1)
        self.assertEqual(result["crash_signatures"][0]["related_error_code"], "ERR_NET_CONGESTION_EOS")

    def test_fetch_runbook_valid(self):
        result = fetch_remediation_runbook("ERR_NET_CONGESTION_EOS")
        self.assertEqual(result["status"], "success")
        self.assertIn("eos-admin routing rollback", result["runbook"]["rollback_command"])

    def test_fetch_runbook_invalid(self):
        result = fetch_remediation_runbook("ERR_UNKNOWN_CODE")
        self.assertEqual(result["status"], "not_found")

if __name__ == "__main__":
    unittest.main()
