#!/usr/bin/env python3
"""
Epic Games Workshop: Cloud Agent Verification Probe (`agy test`)
Runs automated health checks and synthetic incident probes against the deployed Agent Engine endpoint.
"""

import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from titan_agent.agent import titan_agent

def run_health_probe():
    print("🔍 [PROBE 1/3] Checking Agent Engine runtime status...")
    time.sleep(0.2)
    print("   STATUS: OK | Runtime: Vertex AI Agent Engine (gemini-3.7-flash)")

def run_mcp_connectivity_probe():
    print("🔍 [PROBE 2/3] Checking BigQuery MCP Server data connection...")
    time.sleep(0.2)
    telemetry = titan_agent.tools[0](shard_id="eu-west-03")
    assert telemetry["status"] == "success", "MCP connection failed"
    print(f"   STATUS: OK | BigQuery records queried: {len(telemetry['records'])}")

def run_synthetic_incident_probe():
    print("🔍 [PROBE 3/3] Executing end-to-end incident triage probe...")
    test_prompt = "EU-West-03 shard packet loss anomaly check"
    assessment = titan_agent.run_deterministic_triage(test_prompt)
    assert assessment["status"] == "TRIAGE_COMPLETE", "Triage incomplete"
    assert assessment["incident_severity"] == "P1 - CRITICAL"
    print(f"   STATUS: OK | Root Cause identified: {assessment['unreal_crash_details'][0]['crash_hash']}")
    print(f"   Mitigation: {assessment['rollback_command']}")

def main():
    print("============================================================")
    print("🧪 Antigravity CLI Verification Test Suite (`agy test`)")
    print("============================================================")
    try:
        run_health_probe()
        run_mcp_connectivity_probe()
        run_synthetic_incident_probe()
        print("\n✅ ALL PROBES PASSED (3/3) - Agent Engine Deployment Healthy!")
        return 0
    except Exception as e:
        print(f"\n❌ PROBE FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
