"""Unit test for agent configuration, tool registration, and evaluation dataset validation."""

import json
from pathlib import Path
import pytest
from app.agent import root_agent, MODEL, SYSTEM_INSTRUCTION
from app.tools import query_telemetry_metrics, lookup_unreal_crash_signature, fetch_remediation_runbook


def test_agent_model_and_configuration():
    assert MODEL == "gemini-3.7-flash"
    assert root_agent.name == "titan_agent"
    assert len(root_agent.tools) == 3
    tool_names = [t.__name__ for t in root_agent.tools]
    assert "query_telemetry_metrics" in tool_names
    assert "lookup_unreal_crash_signature" in tool_names
    assert "fetch_remediation_runbook" in tool_names


def test_agent_instruction_contains_guardrails_and_workflow():
    assert "TELEMETRY FIRST" in SYSTEM_INSTRUCTION
    assert "CRASH DIAGNOSTICS" in SYSTEM_INSTRUCTION
    assert "RUNBOOK CORRELATION" in SYSTEM_INSTRUCTION
    assert "[<P1|P2|P3> INCIDENT REPORT]" in SYSTEM_INSTRUCTION
    assert "Recommended Mitigation / 1-Click Rollback Script" in SYSTEM_INSTRUCTION
    assert "Never execute automated rollbacks directly on production shards without human operator sign-off" in SYSTEM_INSTRUCTION


def test_evalset_jsonl_validity():
    evalset_path = Path(__file__).resolve().parent.parent / "eval" / "evalset.jsonl"
    assert evalset_path.is_file(), "eval/evalset.jsonl must exist"

    with open(evalset_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    assert len(lines) == 2, "Must contain 2 scenario cases"
    for line in lines:
        case = json.loads(line)
        assert "eval_case_id" in case
        assert "prompt" in case
        assert "reference" in case
        assert "expected_tool_trajectory" in case
        assert case["expected_tool_trajectory"] == [
            "query_telemetry_metrics",
            "lookup_unreal_crash_signature",
            "fetch_remediation_runbook"
        ]


def test_eval_dataset_json_validity():
    dataset_path = Path(__file__).resolve().parent / "eval" / "datasets" / "incident_scenarios.json"
    assert dataset_path.is_file(), "tests/eval/datasets/incident_scenarios.json must exist"

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "eval_cases" in data
    cases = data["eval_cases"]
    assert len(cases) == 2
    assert cases[0]["eval_case_id"] == "scenario-01-eu-packet-loss"
    assert cases[1]["eval_case_id"] == "scenario-02-us-east-crash-loop"


def test_end_to_end_tool_chain():
    # 1. Telemetry query
    telemetry_res = query_telemetry_metrics(shard_id="eu-west-03")
    assert telemetry_res["status"] == "success"
    assert any(a["severity"] == "CRITICAL" for a in telemetry_res["anomalies_detected"])

    # 2. Crash signature query
    crash_res = lookup_unreal_crash_signature(crash_hash="CRASH-UE5-NET-0842")
    assert crash_res["status"] == "success"
    match = crash_res["matches"][0]
    assert match["changelist"] == "CL349201"
    assert match["related_error_code"] == "ERR_NET_CONGESTION_EOS"

    # 3. Remediation runbook
    runbook_res = fetch_remediation_runbook(error_code=match["related_error_code"])
    assert runbook_res["status"] == "success"
    assert "eos-admin routing rollback" in runbook_res["rollback_command"]
