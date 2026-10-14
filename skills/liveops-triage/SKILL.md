---
name: liveops-triage
description: Autonomous incident triage skill for Epic Games LiveOps, Fortnite server shards, and Unreal Engine NetDriver diagnostics.
---

# LiveOps Triage Skill for Epic Games

This skill instructs Antigravity agents on how to triage and diagnose high-concurrency game server anomalies.

## Workflow Rules

1. **Telemetry First:** Always start by querying `epic_liveops.matchmaking_telemetry` via the BigQuery MCP server.
2. **Correlation Matrix:** Correlate shard packet loss spikes (>5%) and latency spikes (>100ms) with `epic_liveops.unreal_crash_signatures`.
3. **Safety Guardrail:** Never execute automated rollbacks directly on production shards without human confirmation. Always provide the exact `eos-admin` or `epic-config-cli` command for operator sign-off.
4. **Artifact Standard:** Always format findings with an interactive Implementation Plan or visual Walkthrough containing:
   - Root Cause Summary
   - Shard Impact Analysis
   - Rollback Script Block
