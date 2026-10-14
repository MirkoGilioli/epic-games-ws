"""
Unreal Engine Crash Diagnostics & Runbook Tool for Titan LiveOps Agent
Inspects crash stack traces, matches engine build tags, and provides SRE mitigation commands.
"""

import json
import os
from typing import Dict, Any, Optional

def lookup_unreal_crash_signature(
    crash_hash: Optional[str] = None,
    build_version: Optional[str] = None
) -> Dict[str, Any]:
    """
    Looks up Unreal Engine crash logs, stack traces, and engine modules.
    
    Args:
        crash_hash: Crash signature identifier (e.g. 'CRASH-UE5-NET-0842').
        build_version: Engine build release tag (e.g. 'Release-30.10-CL349201').
        
    Returns:
        Crash details, affected client counts, and correlated error codes.
    """
    mock_file = "data/unreal_crash_signatures.json"
    if os.path.exists(mock_file):
        with open(mock_file, "r") as f:
            crashes = json.load(f)
    else:
        crashes = [
            {
                "crash_hash": "CRASH-UE5-NET-0842",
                "build_version": "Release-30.10-CL349201",
                "engine_module": "NetDriver / SocketSubsystemEOS",
                "callstack_summary": "UNetDriver::TickDispatch -> FSocketEOS::RecvFrom -> FatalPacketBufferOverflowException",
                "affected_clients": 1240,
                "related_error_code": "ERR_NET_CONGESTION_EOS"
            }
        ]

    matched = crashes
    if crash_hash:
        matched = [c for c in crashes if crash_hash.lower() in c.get("crash_hash", "").lower()]
    elif build_version:
        matched = [c for c in crashes if build_version.lower() in c.get("build_version", "").lower()]

    return {
        "status": "success",
        "matches_found": len(matched),
        "crash_signatures": matched
    }

def fetch_remediation_runbook(error_code: str) -> Dict[str, Any]:
    """
    Fetches official Epic Games SRE mitigation runbooks and rollback commands.
    
    Args:
        error_code: SRE Incident error code (e.g. 'ERR_NET_CONGESTION_EOS').
        
    Returns:
        Mitigation steps and executable rollback command.
    """
    mock_file = "data/incident_runbooks.json"
    if os.path.exists(mock_file):
        with open(mock_file, "r") as f:
            runbooks = json.load(f)
    else:
        runbooks = [
            {
                "error_code": "ERR_NET_CONGESTION_EOS",
                "title": "EOS Gateway Packet Buffer Overrun Mitigation",
                "severity": "P1",
                "remediation_steps": "1. Drain incoming matchmaking queue.\n2. Revert EOS routing rule patch.\n3. Cycle NetDriver socket pools.",
                "rollback_command": "eos-admin routing rollback --rule-id=EOS-NET-3010-P2 --shard=eu-west-03"
            }
        ]

    for rb in runbooks:
        if rb.get("error_code", "").upper() == error_code.upper():
            return {
                "status": "success",
                "runbook": rb
            }

    return {
        "status": "not_found",
        "message": f"No official runbook found for error code '{error_code}'. Escalate to Core NetDriver team."
    }
