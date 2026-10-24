"""Unreal Engine crash diagnostics and remediation runbook tools for Titan LiveOps Agent."""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Search paths for data files
DATA_DIRS = [
    Path("/Users/mirko.gilioli/Code/epic_games_uat/data"),
    Path(__file__).resolve().parents[3] / "data",
    Path(__file__).resolve().parents[2] / "data",
    Path("data"),
    Path("../data"),
]


def _resolve_data_file(filename: str) -> Path | None:
    """Resolve a data file path from known locations."""
    for data_dir in DATA_DIRS:
        candidate = data_dir / filename
        if candidate.is_file():
            return candidate
    return None


def _load_crash_signatures_data() -> list[dict[str, Any]]:
    """Loads crash signatures from local file or BigQuery."""
    file_path = _resolve_data_file("unreal_crash_signatures.json")
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            logger.warning("Failed to read unreal_crash_signatures.json: %s", e)

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or "qwiklabs-asl-02-0c77412b489d"
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=project_id)
        query = (
            f"SELECT crash_hash, build_version, engine_module, callstack_summary, "
            f"first_seen_timestamp, affected_clients, related_error_code "
            f"FROM `{project_id}.epic_liveops.unreal_crash_signatures`"
        )
        rows = list(client.query(query, timeout=5).result())
        if rows:
            data = []
            for r in rows:
                data.append({
                    "crash_hash": r.crash_hash,
                    "build_version": r.build_version,
                    "engine_module": r.engine_module,
                    "callstack_summary": r.callstack_summary,
                    "first_seen_timestamp": r.first_seen_timestamp.isoformat() if hasattr(r.first_seen_timestamp, "isoformat") else str(r.first_seen_timestamp),
                    "affected_clients": r.affected_clients,
                    "related_error_code": r.related_error_code,
                })
            return data
    except Exception as bq_err:
        logger.debug("BigQuery crash signatures query skipped/fallback: %s", bq_err)
    return []


def _load_runbooks_data() -> list[dict[str, Any]]:
    """Loads incident runbooks from local file or BigQuery."""
    file_path = _resolve_data_file("incident_runbooks.json")
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            logger.warning("Failed to read incident_runbooks.json: %s", e)

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or "qwiklabs-asl-02-0c77412b489d"
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=project_id)
        query = (
            f"SELECT error_code, title, severity, remediation_steps, rollback_command "
            f"FROM `{project_id}.epic_liveops.incident_runbooks`"
        )
        rows = list(client.query(query, timeout=5).result())
        if rows:
            data = []
            for r in rows:
                steps = r.remediation_steps
                if isinstance(steps, str):
                    try:
                        steps = json.loads(steps)
                    except Exception:
                        steps = [steps]
                data.append({
                    "error_code": r.error_code,
                    "title": r.title,
                    "severity": r.severity,
                    "remediation_steps": steps,
                    "rollback_command": r.rollback_command,
                })
            return data
    except Exception as bq_err:
        logger.debug("BigQuery runbooks query skipped/fallback: %s", bq_err)
    return []


def _extract_changelist(build_version: str | None) -> str | None:
    """Extract engine build changelist (e.g. 'CL349201') from build version string."""
    if not build_version:
        return None
    match = re.search(r"(CL\d+)", build_version, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def _determine_error_code(entry: dict[str, Any]) -> str | None:
    """Determine the related error code based on crash signature heuristics."""
    crash_hash = str(entry.get("crash_hash", ""))
    engine_module = str(entry.get("engine_module", ""))
    callstack = str(entry.get("callstack_summary", ""))
    combined = f"{crash_hash} {engine_module} {callstack}".lower()

    if (
        "crash-ue5-net-0842" in combined
        or "fatalpacketbufferoverflowexception" in combined
        or "socketsubsystemeos" in combined
        or ("netdriver" in combined and "overflow" in combined)
    ):
        return "ERR_NET_CONGESTION_EOS"

    if (
        "crash-ue5-chaos-9102" in combined
        or "fchaosreplicationsync" in combined
        or "chaosphysics" in combined
        or "chaos" in combined
        or "nullreference" in combined
    ):
        return "ERR_UE5_CHAOS_NULLPTR"

    return entry.get("related_error_code")


def lookup_unreal_crash_signature(
    crash_hash: str | None = None,
    build_version: str | None = None,
) -> dict[str, Any]:
    """Look up known Unreal Engine crash signatures by hash or build version.

    Args:
        crash_hash: Optional crash hash or substring (e.g. 'CRASH-UE5-NET-0842', 'CRASH-UE5-CHAOS-9102').
        build_version: Optional engine build version (e.g. 'Release-30.10-CL349201').

    Returns:
        A dictionary containing matched crash signatures and associated metadata.
    """
    data = _load_crash_signatures_data()
    if not data:
        return {
            "status": "not_found",
            "matches": [],
            "error": "unreal_crash_signatures data source not available",
        }

    matches: list[dict[str, Any]] = []
    norm_crash_hash = crash_hash.strip().lower() if crash_hash else None
    norm_build_ver = build_version.strip().lower() if build_version else None

    for entry in data:
        entry_hash = str(entry.get("crash_hash", "")).strip().lower()
        entry_build = str(entry.get("build_version", "")).strip().lower()

        if norm_crash_hash and norm_crash_hash not in entry_hash:
            continue

        if norm_build_ver and norm_build_ver not in entry_build:
            continue

        build_str = entry.get("build_version")
        changelist = _extract_changelist(build_str)
        related_error_code = _determine_error_code(entry)

        matched_record = {
            "crash_hash": entry.get("crash_hash"),
            "build_version": entry.get("build_version"),
            "changelist": changelist,
            "engine_module": entry.get("engine_module"),
            "callstack_summary": entry.get("callstack_summary"),
            "affected_clients": entry.get("affected_clients"),
            "related_error_code": related_error_code,
        }
        if "first_seen_timestamp" in entry:
            matched_record["first_seen_timestamp"] = entry["first_seen_timestamp"]

        matches.append(matched_record)

    if not matches:
        return {
            "status": "not_found",
            "matches": [],
        }

    return {
        "status": "success",
        "matches": matches,
    }


def fetch_remediation_runbook(error_code: str) -> dict[str, Any]:
    """Fetch an incident remediation runbook for a specific error code.

    Args:
        error_code: The error code key (e.g. 'ERR_NET_CONGESTION_EOS', 'ERR_UE5_CHAOS_NULLPTR').

    Returns:
        A dictionary containing the runbook remediation steps and rollback commands.
    """
    data = _load_runbooks_data()
    if not data:
        return {
            "status": "not_found",
            "error_code": error_code,
            "error": "incident_runbooks data source not available",
        }

    norm_code = error_code.strip().lower()
    for entry in data:
        entry_code = str(entry.get("error_code", "")).strip().lower()
        if entry_code == norm_code:
            return {
                "status": "success",
                "error_code": entry.get("error_code"),
                "title": entry.get("title"),
                "severity": entry.get("severity"),
                "remediation_steps": entry.get("remediation_steps"),
                "rollback_command": entry.get("rollback_command"),
            }

    return {
        "status": "not_found",
        "error_code": error_code,
        "message": f"No remediation runbook found for error code '{error_code}'.",
    }
