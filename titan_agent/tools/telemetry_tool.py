"""
BigQuery MCP Telemetry Tool for Titan LiveOps Agent
Queries shard health, packet loss, and latency metrics via BigQuery MCP protocol.
"""

import json
import os
from typing import Dict, Any, Optional

def query_telemetry_metrics(
    shard_id: Optional[str] = None,
    metric_name: Optional[str] = "all",
    time_window_minutes: int = 30
) -> Dict[str, Any]:
    """
    Queries matchmaking and server shard telemetry from BigQuery.
    
    Args:
        shard_id: Server shard identifier (e.g., 'eu-west-03').
        metric_name: Specific metric ('packet_loss_pct', 'matchmaking_latency_ms', 'player_dropouts', 'all').
        time_window_minutes: Analysis time window in minutes.
        
    Returns:
        Structured telemetry metrics and detected anomaly flags.
    """
    mock_file = "data/matchmaking_telemetry.json"
    
    # Check if local mock file exists (Lab environment fallback)
    if os.path.exists(mock_file):
        with open(mock_file, "r") as f:
            records = json.load(f)
    else:
        # Fallback inline dataset
        records = [
            {
                "timestamp": "2026-10-14T15:00:00Z",
                "shard_id": "eu-west-03",
                "region": "EU",
                "active_matches": 2100,
                "matchmaking_latency_ms": 342.8,
                "packet_loss_pct": 14.2,
                "player_dropouts": 185,
                "eos_gateway_status": "DEGRADED"
            },
            {
                "timestamp": "2026-10-14T15:00:00Z",
                "shard_id": "eu-west-01",
                "region": "EU",
                "active_matches": 1420,
                "matchmaking_latency_ms": 24.5,
                "packet_loss_pct": 0.2,
                "player_dropouts": 2,
                "eos_gateway_status": "HEALTHY"
            }
        ]

    # Filter by shard_id if requested
    filtered = records
    if shard_id:
        filtered = [r for r in records if shard_id.lower() in r.get("shard_id", "").lower()]

    anomalies = []
    for r in filtered:
        if r.get("packet_loss_pct", 0) > 5.0 or r.get("matchmaking_latency_ms", 0) > 100.0 or r.get("player_dropouts", 0) > 100:
            anomalies.append({
                "shard_id": r.get("shard_id"),
                "status": r.get("eos_gateway_status"),
                "packet_loss_pct": r.get("packet_loss_pct"),
                "latency_ms": r.get("matchmaking_latency_ms"),
                "dropouts": r.get("player_dropouts"),
                "severity": "CRITICAL" if r.get("packet_loss_pct", 0) > 10.0 else "WARNING"
            })

    return {
        "status": "success",
        "time_window_minutes": time_window_minutes,
        "total_shards_evaluated": len(filtered),
        "records": filtered,
        "anomalies_detected": anomalies
    }
