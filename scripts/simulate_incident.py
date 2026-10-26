#!/usr/bin/env python3
"""
Epic Games Workshop: Incident Simulation Script
Used by workshop instructors and trainees to dynamically inject an active incident into telemetry data.
Pushes the anomaly record directly to Google Cloud BigQuery and updates local JSON mock data.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone

def push_to_bigquery(event, project_id, dataset_id="epic_liveops", table_id="matchmaking_telemetry"):
    """Inserts the incident record into the BigQuery telemetry table."""
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=project_id)
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        table = client.get_table(table_ref)
        
        errors = client.insert_rows_json(table, [event])
        if errors:
            print(f"⚠️ [BigQuery Error] Failed to insert incident record: {errors}")
            return False
        else:
            print(f"⚡ [BigQuery Live Ops] Successfully pushed incident record to `{table_ref}`!")
            return True
    except ImportError:
        print("ℹ️  [BigQuery] `google-cloud-bigquery` not installed. Skipping live BigQuery push.")
        return False
    except Exception as e:
        print(f"⚠️ [BigQuery Warning] Could not push to BigQuery: {e}")
        return False

def update_local_json(event, data_file="data/matchmaking_telemetry.json"):
    """Updates the local mock telemetry JSON file."""
    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    records = []
    if os.path.exists(data_file):
        try:
            with open(data_file, "r") as f:
                records = json.load(f)
        except Exception:
            records = []

    records.insert(0, event)
    with open(data_file, "w") as f:
        json.dump(records, f, indent=2)
    print(f"📁 [Local Telemetry] Updated '{data_file}' with active incident event.")

def inject_anomaly(shard_id="us-east-12", packet_loss=18.5, latency=420.0, project_id=None, force_live=False):
    """Generates an active incident event and pushes it to BigQuery and local JSON."""
    region = "EU" if "eu" in shard_id.lower() else "NA-EAST"
    
    new_event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "shard_id": shard_id,
        "region": region,
        "active_matches": 2450,
        "matchmaking_latency_ms": latency,
        "packet_loss_pct": packet_loss,
        "player_dropouts": 320,
        "eos_gateway_status": "CRITICAL"
    }

    print(f"\n🚨 [WAR GAME INCIDENT INJECTION] Shard: '{shard_id}' (Region: {region})")
    print(f"   Status: CRITICAL | Packet Loss: {packet_loss}% | Matchmaking Latency: {latency}ms\n")

    # Update local mock telemetry
    update_local_json(new_event)

    # Push to live BigQuery if project is specified or GCP_PROJECT environment variable is set
    target_project = project_id or os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
    if target_project or force_live:
        if target_project:
            push_to_bigquery(new_event, project_id=target_project)
        else:
            print("⚠️ [BigQuery Notice] `--live` was requested but neither `GCP_PROJECT` nor `--project` was set.")
    else:
        print("ℹ️  [Notice] `GCP_PROJECT` not set. Set `export GCP_PROJECT=your-project` or pass `--live` to push to BigQuery.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject a synthetic LiveOps incident into telemetry data.")
    parser.add_argument("shard_id", nargs="?", default="us-east-12", help="Server shard ID to trigger incident on (default: us-east-12)")
    parser.add_argument("--packet-loss", type=float, default=18.5, help="Packet loss percentage (default: 18.5)")
    parser.add_argument("--latency", type=float, default=420.0, help="Matchmaking latency in ms (default: 420.0)")
    parser.add_argument("--project", type=str, default=None, help="Google Cloud Project ID for BigQuery")
    parser.add_argument("--live", action="store_true", help="Push incident record to live BigQuery table")

    args = parser.parse_args()
    inject_anomaly(
        shard_id=args.shard_id,
        packet_loss=args.packet_loss,
        latency=args.latency,
        project_id=args.project,
        force_live=args.live
    )
