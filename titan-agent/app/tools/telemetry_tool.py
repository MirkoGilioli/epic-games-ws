"""Telemetry Query and Anomaly Detection Tool for Epic Games LiveOps.

This module provides tools conforming to Google ADK conventions to inspect
matchmaking telemetry, server shard health, latency, and packet loss metrics,
identifying critical network and NetDriver anomalies across Fortnite/Titan server shards.
"""

from __future__ import annotations

import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Search candidate paths for matchmaking telemetry dataset
DATA_CANDIDATE_PATHS = [
    Path("/Users/mirko.gilioli/Code/epic_games_uat/data/matchmaking_telemetry.json"),
    Path(__file__).resolve().parent.parent.parent.parent / "data" / "matchmaking_telemetry.json",
    Path(__file__).resolve().parent.parent.parent / "data" / "matchmaking_telemetry.json",
    Path.cwd() / "data" / "matchmaking_telemetry.json",
    Path.cwd().parent / "data" / "matchmaking_telemetry.json",
]

EOS_SEVERITY_ORDER = {
    "CRITICAL": 3,
    "DEGRADED": 2,
    "HEALTHY": 1,
    "UNKNOWN": 0,
}


def _load_telemetry_data() -> list[dict[str, Any]]:
    """Loads raw matchmaking telemetry data from local JSON or BigQuery."""
    for candidate in DATA_CANDIDATE_PATHS:
        if candidate.is_file():
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception as e:
                logger.warning("Failed reading telemetry data from %s: %s", candidate, e)

    # Fallback to BigQuery if local files not available
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or "qwiklabs-asl-02-0c77412b489d"
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=project_id)
        query = (
            f"SELECT timestamp, shard_id, region, active_matches, matchmaking_latency_ms, "
            f"packet_loss_pct, player_dropouts, eos_gateway_status "
            f"FROM `{project_id}.epic_liveops.matchmaking_telemetry` "
            f"ORDER BY timestamp DESC"
        )
        rows = list(client.query(query, timeout=5).result())
        if rows:
            data = []
            for r in rows:
                data.append({
                    "timestamp": r.timestamp.isoformat() if hasattr(r.timestamp, "isoformat") else str(r.timestamp),
                    "shard_id": r.shard_id,
                    "region": r.region,
                    "active_matches": r.active_matches,
                    "matchmaking_latency_ms": r.matchmaking_latency_ms,
                    "packet_loss_pct": r.packet_loss_pct,
                    "player_dropouts": r.player_dropouts,
                    "eos_gateway_status": r.eos_gateway_status,
                })
            return data
    except Exception as bq_err:
        logger.debug("BigQuery load skipped/fallback: %s", bq_err)

    logger.error("No telemetry data source found across candidate paths or BigQuery.")
    return []


def _parse_iso_timestamp(ts_str: str) -> datetime.datetime | None:
    """Parses an ISO 8601 formatted timestamp string."""
    try:
        return datetime.datetime.fromisoformat(ts_str)
    except Exception:
        return None


def query_telemetry_metrics(
    shard_id: str | None = None,
    metric_name: str = "all",
    time_window_minutes: int = 30,
) -> dict[str, Any]:
    """Queries matchmaking telemetry metrics with shard packet loss anomaly detection.

    Simulates a read-only query interface against the `epic_liveops.matchmaking_telemetry`
    BigQuery dataset. Extracts telemetry records, aggregates summary metrics, and performs
    automated threshold checks:
      - Packet loss > 5%: WARNING anomaly
      - Packet loss > 10%: CRITICAL anomaly

    Args:
        shard_id: Optional server shard ID to filter by (e.g. 'eu-west-03', 'us-east-12').
            If None, queries across all server shards.
        metric_name: Target metric to focus on ('all', 'packet_loss_pct',
            'matchmaking_latency_ms', 'player_dropouts', 'active_matches',
            'eos_gateway_status'). Defaults to 'all'.
        time_window_minutes: Time window in minutes relative to the most recent record.
            Defaults to 30.

    Returns:
        A dictionary containing:
            - status: "success" if records were found, "no_data" otherwise.
            - shard_id: The requested shard filter (or None).
            - records: List of telemetry record dictionaries matching the criteria.
            - summary_stats: Dict of aggregated statistics including avg/max packet loss,
              average latency, total player dropouts, and highest EOS gateway status.
            - anomalies_detected: List of detected anomalies with severity, threshold breached,
              and descriptive details.
    """
    raw_data = _load_telemetry_data()

    if not raw_data:
        return {
            "status": "no_data",
            "shard_id": shard_id,
            "records": [],
            "summary_stats": {
                "avg_packet_loss_pct": None,
                "max_packet_loss_pct": None,
                "avg_latency_ms": None,
                "total_player_dropouts": 0,
                "max_eos_status": "UNKNOWN",
            },
            "anomalies_detected": [],
        }

    # 1. Filter by shard_id if provided
    matched_records = raw_data
    if shard_id is not None:
        target_shard = shard_id.strip().lower()
        matched_records = [
            r for r in matched_records
            if str(r.get("shard_id", "")).strip().lower() == target_shard
        ]

    if not matched_records:
        return {
            "status": "no_data",
            "shard_id": shard_id,
            "records": [],
            "summary_stats": {
                "avg_packet_loss_pct": None,
                "max_packet_loss_pct": None,
                "avg_latency_ms": None,
                "total_player_dropouts": 0,
                "max_eos_status": "UNKNOWN",
            },
            "anomalies_detected": [],
        }

    # 2. Time window filtering (relative to the latest record in matched dataset)
    if time_window_minutes is not None and time_window_minutes > 0:
        parsed_timestamps = [
            _parse_iso_timestamp(r.get("timestamp", ""))
            for r in matched_records
        ]
        valid_timestamps = [ts for ts in parsed_timestamps if ts is not None]
        if valid_timestamps:
            latest_ts = max(valid_timestamps)
            cutoff_ts = latest_ts - datetime.timedelta(minutes=time_window_minutes)
            matched_records = [
                r for r in matched_records
                if _parse_iso_timestamp(r.get("timestamp", "")) is None
                or _parse_iso_timestamp(r.get("timestamp", "")) >= cutoff_ts
            ]

    if not matched_records:
        return {
            "status": "no_data",
            "shard_id": shard_id,
            "records": [],
            "summary_stats": {
                "avg_packet_loss_pct": None,
                "max_packet_loss_pct": None,
                "avg_latency_ms": None,
                "total_player_dropouts": 0,
                "max_eos_status": "UNKNOWN",
            },
            "anomalies_detected": [],
        }

    # 3. Compute Summary Statistics
    packet_loss_values: list[float] = [
        float(r["packet_loss_pct"])
        for r in matched_records
        if "packet_loss_pct" in r and isinstance(r["packet_loss_pct"], (int, float))
    ]
    latency_values: list[float] = [
        float(r["matchmaking_latency_ms"])
        for r in matched_records
        if "matchmaking_latency_ms" in r and isinstance(r["matchmaking_latency_ms"], (int, float))
    ]
    dropout_values: list[int] = [
        int(r["player_dropouts"])
        for r in matched_records
        if "player_dropouts" in r and isinstance(r["player_dropouts"], (int, float))
    ]
    eos_statuses: list[str] = [
        str(r["eos_gateway_status"]).upper()
        for r in matched_records
        if "eos_gateway_status" in r and r["eos_gateway_status"]
    ]

    max_eos = "HEALTHY"
    if eos_statuses:
        max_eos = max(
            eos_statuses,
            key=lambda s: EOS_SEVERITY_ORDER.get(s, 0)
        )

    summary_stats = {
        "avg_packet_loss_pct": round(sum(packet_loss_values) / len(packet_loss_values), 2) if packet_loss_values else None,
        "max_packet_loss_pct": round(max(packet_loss_values), 2) if packet_loss_values else None,
        "avg_latency_ms": round(sum(latency_values) / len(latency_values), 2) if latency_values else None,
        "total_player_dropouts": sum(dropout_values) if dropout_values else 0,
        "max_eos_status": max_eos,
    }

    # 4. Anomaly Detection
    anomalies_detected: list[dict[str, Any]] = []
    for r in matched_records:
        pkt_loss = r.get("packet_loss_pct")
        current_shard = r.get("shard_id", "unknown")
        record_ts = r.get("timestamp")

        if isinstance(pkt_loss, (int, float)):
            if pkt_loss > 10.0:
                anomalies_detected.append({
                    "shard_id": current_shard,
                    "anomaly_type": "PACKET_LOSS",
                    "severity": "CRITICAL",
                    "value": pkt_loss,
                    "threshold_breached": 10.0,
                    "message": (
                        f"CRITICAL packet loss anomaly detected on shard '{current_shard}': "
                        f"{pkt_loss}% exceeds critical threshold (10.0%)."
                    ),
                    "timestamp": record_ts,
                })
            elif pkt_loss > 5.0:
                anomalies_detected.append({
                    "shard_id": current_shard,
                    "anomaly_type": "PACKET_LOSS",
                    "severity": "WARNING",
                    "value": pkt_loss,
                    "threshold_breached": 5.0,
                    "message": (
                        f"WARNING packet loss anomaly detected on shard '{current_shard}': "
                        f"{pkt_loss}% exceeds warning threshold (5.0%)."
                    ),
                    "timestamp": record_ts,
                })

    # 5. Metric Field Projection if metric_name is specified and not "all"
    clean_metric = metric_name.strip().lower()
    if clean_metric != "all":
        base_keys = {"timestamp", "shard_id", "region"}
        projected_records = []
        for r in matched_records:
            proj = {k: v for k, v in r.items() if k in base_keys or k.lower() == clean_metric}
            projected_records.append(proj)
        records_to_return = projected_records
    else:
        records_to_return = list(matched_records)

    return {
        "status": "success",
        "shard_id": shard_id,
        "records": records_to_return,
        "summary_stats": summary_stats,
        "anomalies_detected": anomalies_detected,
    }
