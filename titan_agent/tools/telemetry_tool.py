"""
BigQuery MCP Telemetry Tool for Titan LiveOps Agent (STUDENT STARTER TEMPLATE)
=============================================================================
Phase 2 Lab Task: Use Antigravity 2.0 to implement this tool based on specs/titan_agent_spec.yaml.

Antigravity 2.0 Prompt Guide (Subagent 1 - Telemetry Tool Builder):
------------------------------------------------------------------
"Inspect specs/titan_agent_spec.yaml and mcp_servers/bigquery_mcp.json.
 Implement query_telemetry_metrics in titan_agent/tools/telemetry_tool.py to:
 1. Query matchmaking telemetry from BigQuery (or data/matchmaking_telemetry.json for local mock).
 2. Filter by shard_id if provided.
 3. Flag anomalies where packet_loss_pct > 5% or latency > 100ms.
 Return a structured dictionary conforming to the spec."
"""

from typing import Dict, Any, Optional

def query_telemetry_metrics(
    shard_id: Optional[str] = None,
    metric_name: Optional[str] = "all",
    time_window_minutes: int = 30
) -> Dict[str, Any]:
    """
    Queries matchmaking and server shard telemetry from BigQuery via MCP.
    
    Args:
        shard_id: Optional server shard filter (e.g. 'eu-west-03').
        metric_name: Metric to filter ('packet_loss_pct', 'matchmaking_latency_ms', etc.).
        time_window_minutes: Time window in minutes.
        
    Returns:
        Dict containing query status, records, and detected anomalies.
    """
    # TODO [Phase 2]: Implement this function using Antigravity 2.0
    raise NotImplementedError(
        "query_telemetry_metrics is not implemented yet. "
        "Use Antigravity 2.0 Subagent 1 to generate this implementation from specs/titan_agent_spec.yaml!"
    )
