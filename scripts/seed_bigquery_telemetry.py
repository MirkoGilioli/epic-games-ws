#!/usr/bin/env python3
"""
Epic Games Workshop: BigQuery Dummy Telemetry Seeder
Generates and populates synthetic LiveOps telemetry for Fortnite & Unreal Engine.
Can seed live BigQuery or write offline JSON mocks for local development.
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone

def generate_telemetry_records():
    now = datetime.now(timezone.utc)
    return [
        {
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
            "shard_id": "eu-west-01",
            "region": "EU",
            "active_matches": 1420,
            "matchmaking_latency_ms": 24.5,
            "packet_loss_pct": 0.2,
            "player_dropouts": 2,
            "eos_gateway_status": "HEALTHY"
        },
        {
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
            "shard_id": "eu-west-02",
            "region": "EU",
            "active_matches": 1580,
            "matchmaking_latency_ms": 26.1,
            "packet_loss_pct": 0.4,
            "player_dropouts": 3,
            "eos_gateway_status": "HEALTHY"
        },
        {
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
            "shard_id": "eu-west-03",
            "region": "EU",
            "active_matches": 2100,
            "matchmaking_latency_ms": 342.8,
            "packet_loss_pct": 14.2,
            "player_dropouts": 185,
            "eos_gateway_status": "DEGRADED"
        },
        {
            "timestamp": (now - timedelta(minutes=10)).isoformat(),
            "shard_id": "eu-west-03",
            "region": "EU",
            "active_matches": 1950,
            "matchmaking_latency_ms": 312.0,
            "packet_loss_pct": 13.8,
            "player_dropouts": 160,
            "eos_gateway_status": "DEGRADED"
        },
        {
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
            "shard_id": "us-east-11",
            "region": "NA-EAST",
            "active_matches": 2300,
            "matchmaking_latency_ms": 19.8,
            "packet_loss_pct": 0.1,
            "player_dropouts": 1,
            "eos_gateway_status": "HEALTHY"
        },
        {
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
            "shard_id": "us-east-12",
            "region": "NA-EAST",
            "active_matches": 1890,
            "matchmaking_latency_ms": 85.4,
            "packet_loss_pct": 4.2,
            "player_dropouts": 450,
            "eos_gateway_status": "CRITICAL"
        }
    ]

def generate_crash_signatures():
    now = datetime.now(timezone.utc)
    return [
        {
            "crash_hash": "CRASH-UE5-NET-0842",
            "build_version": "Release-30.10-CL349201",
            "engine_module": "NetDriver / SocketSubsystemEOS",
            "callstack_summary": "UNetDriver::TickDispatch -> FSocketEOS::RecvFrom -> FatalPacketBufferOverflowException",
            "first_seen_timestamp": (now - timedelta(minutes=30)).isoformat(),
            "affected_clients": 1240,
            "related_error_code": "ERR_NET_CONGESTION_EOS"
        },
        {
            "crash_hash": "CRASH-UE5-CHAOS-9102",
            "build_version": "Release-30.10-CL349201",
            "engine_module": "ChaosPhysics / Replication",
            "callstack_summary": "FChaosReplicationSync::SerializePayload -> NullReference at 0x00007FFF0042",
            "first_seen_timestamp": (now - timedelta(minutes=45)).isoformat(),
            "affected_clients": 890,
            "related_error_code": "ERR_UE5_CHAOS_NULLPTR"
        }
    ]

def generate_runbooks():
    return [
        {
            "error_code": "ERR_NET_CONGESTION_EOS",
            "title": "EOS Gateway Packet Buffer Overrun Mitigation",
            "severity": "P1",
            "remediation_steps": "1. Drain incoming matchmaking queue on affected shard.\n2. Revert EOS routing rule patch to v30.10-baseline.\n3. Cycle NetDriver socket pools.",
            "rollback_command": "eos-admin routing rollback --rule-id=EOS-NET-3010-P2 --shard=eu-west-03"
        },
        {
            "error_code": "ERR_UE5_CHAOS_NULLPTR",
            "title": "Unreal Chaos Physics Replication Hotfix",
            "severity": "P1",
            "remediation_steps": "1. Disable experimental chaos packet compression in LiveOps remote config.\n2. Restart affected server instances.",
            "rollback_command": "epic-config-cli set --key=p.Chaos.ReplicationSync --value=0 --broadcast=global"
        }
    ]

def seed_local_mock_data(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    
    telemetry = generate_telemetry_records()
    crashes = generate_crash_signatures()
    runbooks = generate_runbooks()

    with open(os.path.join(output_dir, "matchmaking_telemetry.json"), "w") as f:
        json.dump(telemetry, f, indent=2)
    with open(os.path.join(output_dir, "unreal_crash_signatures.json"), "w") as f:
        json.dump(crashes, f, indent=2)
    with open(os.path.join(output_dir, "incident_runbooks.json"), "w") as f:
        json.dump(runbooks, f, indent=2)

    print(f"✅ Local dummy BigQuery datasets created in '{output_dir}/'")

def seed_live_bigquery(project_id, dataset_id="epic_liveops"):
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=project_id)
        dataset_ref = client.dataset(dataset_id)
        client.create_dataset(dataset_ref, exists_ok=True)

        telemetry = generate_telemetry_records()
        crashes = generate_crash_signatures()
        runbooks = generate_runbooks()

        # Telemetry Table
        schema_telemetry = [
            bigquery.SchemaField("timestamp", "TIMESTAMP"),
            bigquery.SchemaField("shard_id", "STRING"),
            bigquery.SchemaField("region", "STRING"),
            bigquery.SchemaField("active_matches", "INT64"),
            bigquery.SchemaField("matchmaking_latency_ms", "FLOAT64"),
            bigquery.SchemaField("packet_loss_pct", "FLOAT64"),
            bigquery.SchemaField("player_dropouts", "INT64"),
            bigquery.SchemaField("eos_gateway_status", "STRING"),
        ]
        table_telemetry_ref = f"{project_id}.{dataset_id}.matchmaking_telemetry"
        client.create_table(bigquery.Table(table_telemetry_ref, schema=schema_telemetry), exists_ok=True)
        table_telemetry = client.get_table(table_telemetry_ref)
        errors = client.insert_rows_json(table_telemetry, telemetry)
        if errors:
            print(f"Errors inserting telemetry: {errors}")

        # Crash Signatures Table
        schema_crashes = [
            bigquery.SchemaField("crash_hash", "STRING"),
            bigquery.SchemaField("build_version", "STRING"),
            bigquery.SchemaField("engine_module", "STRING"),
            bigquery.SchemaField("callstack_summary", "STRING"),
            bigquery.SchemaField("first_seen_timestamp", "TIMESTAMP"),
            bigquery.SchemaField("affected_clients", "INT64"),
            bigquery.SchemaField("related_error_code", "STRING"),
        ]
        table_crashes_ref = f"{project_id}.{dataset_id}.unreal_crash_signatures"
        client.create_table(bigquery.Table(table_crashes_ref, schema=schema_crashes), exists_ok=True)
        table_crashes = client.get_table(table_crashes_ref)
        errors = client.insert_rows_json(table_crashes, crashes)
        if errors:
            print(f"Errors inserting crashes: {errors}")

        # Incident Runbooks Table
        schema_runbooks = [
            bigquery.SchemaField("error_code", "STRING"),
            bigquery.SchemaField("title", "STRING"),
            bigquery.SchemaField("severity", "STRING"),
            bigquery.SchemaField("remediation_steps", "STRING"),
            bigquery.SchemaField("rollback_command", "STRING"),
        ]
        table_runbooks_ref = f"{project_id}.{dataset_id}.incident_runbooks"
        client.create_table(bigquery.Table(table_runbooks_ref, schema=schema_runbooks), exists_ok=True)
        table_runbooks = client.get_table(table_runbooks_ref)
        errors = client.insert_rows_json(table_runbooks, runbooks)
        if errors:
            print(f"Errors inserting runbooks: {errors}")

        print(f"🚀 Successfully seeded BigQuery dataset `{project_id}.{dataset_id}`!")
    except Exception as e:
        print(f"⚠️ Live BigQuery seeding encountered: {e}")
        print("Falling back to local mock data generation.")
        seed_local_mock_data()

if __name__ == "__main__":
    project = os.getenv("GCP_PROJECT", "")
    if "--live" in sys.argv and project:
        print(f"Connecting to GCP Project: {project}...")
        seed_live_bigquery(project)
    else:
        seed_local_mock_data()
