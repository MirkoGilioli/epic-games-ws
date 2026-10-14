"""
Integration Tests for Titan LiveOps Agent Execution Loop
"""

import unittest
from titan_agent.agent import TitanLiveOpsAgent

class TestTitanAgent(unittest.TestCase):

    def test_agent_triage_eu_incident(self):
        agent = TitanLiveOpsAgent()
        prompt = "@Titan-LiveOps Shard EU-West-03 is showing 14% packet loss and matchmaking timeouts. Run diagnosis."
        
        assessment = agent.run_deterministic_triage(prompt)
        self.assertEqual(assessment["agent"], "titan-liveops-incident-agent")
        self.assertEqual(assessment["model"], "gemini-3.7-flash")
        self.assertEqual(assessment["incident_severity"], "P1 - CRITICAL")
        self.assertEqual(assessment["impacted_shard"], "eu-west-03")
        self.assertIn("eos-admin routing rollback", assessment["rollback_command"])

    def test_agent_handle_request_formatting(self):
        agent = TitanLiveOpsAgent()
        prompt = "@Titan-LiveOps EU-West-03 incident check"
        
        report = agent.handle_request(prompt)
        self.assertIn("[P1 INCIDENT REPORT]", report)
        self.assertIn("eu-west-03", report)
        self.assertIn("Recommended Mitigation Steps", report)
        self.assertIn("Gemini 3.7 Flash", report)

if __name__ == "__main__":
    unittest.main()
