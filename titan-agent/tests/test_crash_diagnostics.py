"""Unit tests for Unreal Engine crash diagnostics and runbook lookup tools."""

from app.tools.crash_diagnostics import (
    _determine_error_code,
    _extract_changelist,
    fetch_remediation_runbook,
    lookup_unreal_crash_signature,
)


def test_extract_changelist():
    """Test extracting engine build changelist from various build version formats."""
    assert _extract_changelist("Release-30.10-CL349201") == "CL349201"
    assert _extract_changelist("Fortnite-Release-CL998877-Shipping") == "CL998877"
    assert _extract_changelist("CL123456") == "CL123456"
    assert _extract_changelist("Release-30.10-Baseline") is None
    assert _extract_changelist(None) is None
    assert _extract_changelist("") is None


def test_determine_error_code_netdriver():
    """Test mapping NetDriver buffer overflow crash heuristics to ERR_NET_CONGESTION_EOS."""
    # By crash hash
    entry_hash = {"crash_hash": "CRASH-UE5-NET-0842"}
    assert _determine_error_code(entry_hash) == "ERR_NET_CONGESTION_EOS"

    # By callstack
    entry_callstack = {
        "crash_hash": "CRASH-CUSTOM-001",
        "callstack_summary": "UNetDriver::TickDispatch -> FSocketEOS::RecvFrom -> FatalPacketBufferOverflowException",
    }
    assert _determine_error_code(entry_callstack) == "ERR_NET_CONGESTION_EOS"

    # By module and overflow
    entry_module = {
        "crash_hash": "CRASH-CUSTOM-002",
        "engine_module": "NetDriver / SocketSubsystemEOS",
        "callstack_summary": "Buffer overflow in recv queue",
    }
    assert _determine_error_code(entry_module) == "ERR_NET_CONGESTION_EOS"


def test_determine_error_code_chaos():
    """Test mapping Chaos Physics crash heuristics to ERR_UE5_CHAOS_NULLPTR."""
    # By crash hash
    entry_hash = {"crash_hash": "CRASH-UE5-CHAOS-9102"}
    assert _determine_error_code(entry_hash) == "ERR_UE5_CHAOS_NULLPTR"

    # By callstack
    entry_callstack = {
        "crash_hash": "CRASH-CUSTOM-003",
        "callstack_summary": "FChaosReplicationSync::SerializePayload -> NullReference at 0x00007FFF0042",
    }
    assert _determine_error_code(entry_callstack) == "ERR_UE5_CHAOS_NULLPTR"

    # By engine module
    entry_module = {
        "crash_hash": "CRASH-CUSTOM-004",
        "engine_module": "ChaosPhysics / Replication",
    }
    assert _determine_error_code(entry_module) == "ERR_UE5_CHAOS_NULLPTR"


def test_lookup_unreal_crash_signature_netdriver():
    """Test lookup for NetDriver crash signature."""
    result = lookup_unreal_crash_signature(crash_hash="CRASH-UE5-NET-0842")
    assert result["status"] == "success"
    assert len(result["matches"]) >= 1

    match = result["matches"][0]
    assert match["crash_hash"] == "CRASH-UE5-NET-0842"
    assert match["changelist"] == "CL349201"
    assert match["related_error_code"] == "ERR_NET_CONGESTION_EOS"
    assert match["affected_clients"] == 1240
    assert "SocketSubsystemEOS" in match["engine_module"]


def test_lookup_unreal_crash_signature_chaos():
    """Test lookup for Chaos Physics crash signature."""
    result = lookup_unreal_crash_signature(crash_hash="CRASH-UE5-CHAOS-9102")
    assert result["status"] == "success"
    assert len(result["matches"]) >= 1

    match = result["matches"][0]
    assert match["crash_hash"] == "CRASH-UE5-CHAOS-9102"
    assert match["changelist"] == "CL349201"
    assert match["related_error_code"] == "ERR_UE5_CHAOS_NULLPTR"
    assert match["affected_clients"] == 890


def test_lookup_unreal_crash_signature_by_build_version():
    """Test lookup by build version."""
    result = lookup_unreal_crash_signature(build_version="Release-30.10-CL349201")
    assert result["status"] == "success"
    assert len(result["matches"]) == 2
    for m in result["matches"]:
        assert m["changelist"] == "CL349201"


def test_lookup_unreal_crash_signature_unknown():
    """Test lookup for unknown crash hash returns not_found."""
    result = lookup_unreal_crash_signature(crash_hash="CRASH-NONEXISTENT-9999")
    assert result["status"] == "not_found"
    assert result["matches"] == []


def test_fetch_remediation_runbook_net_congestion():
    """Test fetching runbook for ERR_NET_CONGESTION_EOS."""
    result = fetch_remediation_runbook("ERR_NET_CONGESTION_EOS")
    assert result["status"] == "success"
    assert result["error_code"] == "ERR_NET_CONGESTION_EOS"
    assert result["severity"] == "P1"
    assert "EOS Gateway Packet Buffer Overrun Mitigation" in result["title"]
    assert "Drain incoming matchmaking queue" in result["remediation_steps"]
    assert "eos-admin routing rollback" in result["rollback_command"]


def test_fetch_remediation_runbook_chaos_nullptr():
    """Test fetching runbook for ERR_UE5_CHAOS_NULLPTR."""
    result = fetch_remediation_runbook("ERR_UE5_CHAOS_NULLPTR")
    assert result["status"] == "success"
    assert result["error_code"] == "ERR_UE5_CHAOS_NULLPTR"
    assert result["severity"] == "P1"
    assert "Unreal Chaos Physics Replication Hotfix" in result["title"]
    assert "Disable experimental chaos packet compression" in result["remediation_steps"]
    assert "epic-config-cli set --key=p.Chaos.ReplicationSync" in result["rollback_command"]


def test_fetch_remediation_runbook_unknown():
    """Test fetching runbook for unknown error code returns not_found."""
    result = fetch_remediation_runbook("ERR_UNKNOWN_CODE_999")
    assert result["status"] == "not_found"
    assert result["error_code"] == "ERR_UNKNOWN_CODE_999"
