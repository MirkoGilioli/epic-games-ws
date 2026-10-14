#!/usr/bin/env python3
"""
Epic Games Workshop: Incident Simulation Script
Used by workshop instructors to dynamically inject an active incident into telemetry data.
"""

import os
import sys
import json
from datetime import datetime, timezone

def inject_anomaly(shard_id="eu-west-03", packet_loss=18.5, latency=420.0):
    data_file = "data/matchmaking_telemetry.json"
    if not os.path.exists(data_file):
        print(f"Data file '{data_file}' not found. Run seed script first.")
        return

    with open(data_file, "r") as f:
        records = json.load(f)

    new_event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "shard_id": shard_id,
        "region": "EU" if "eu" in shard_id else "NA-EAST",
        "active_matches": 2450,
        "matchmaking_latency_ms": latency,
        "packet_loss_pct": packet_loss,
        "player_dropouts": 320,
        "eos_gateway_status": "CRITICAL"
    }

    records.insert(0, new_event)

    with open(data_file, "w") as f:
        json.dump(records, f, indent=2)

    print(f"🚨 [WAR GAME INCIDENT INJECTED] Shard '{shard_id}' is now CRITICAL!")
    print(f"   Packet Loss: {packet_loss}% | Matchmaking Latency: {latency}ms")

if __name__ == "__main__":
    shard = sys.argv[1] if len(sys.argv) > 1 else "eu-west-03"
    inject_anomaly(shard_id=shard)
