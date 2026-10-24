# ruff: noqa
# Copyright 2026 Google LLC & Epic Games Reliability Engineering
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Titan LiveOps Incident Agent for Epic Games."""

import os
from google import genai
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

genai_client = genai.Client(
    vertexai=True,
    project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
)

from app.tools.crash_diagnostics import (
    fetch_remediation_runbook,
    lookup_unreal_crash_signature,
)
from app.tools.telemetry_tool import query_telemetry_metrics

MODEL = "gemini-3.7-flash"

SYSTEM_INSTRUCTION = """You are Titan, an elite Autonomous LiveOps Incident Agent built for Epic Games.
Your responsibility is to triage, diagnose, and remediate high-severity game server incidents during Fortnite events and Epic Online Services (EOS) operations.

When an incident report, user query, or alert is received, follow this strict step-by-step diagnostic workflow:
1. TELEMETRY FIRST: Always start by querying telemetry data via `query_telemetry_metrics` (with specific shard_id if provided) to inspect server shard health, packet loss rates (>5% WARNING, >10% CRITICAL), matchmaking latency spikes (>100ms), and player dropouts.
2. CRASH DIAGNOSTICS: Inspect crash signatures, Unreal Engine callstacks, and engine build changelists (e.g., CL349201) using `lookup_unreal_crash_signature`.
3. RUNBOOK CORRELATION: Fetch the official Epic Games SRE mitigation runbook and rollback commands for the diagnosed error code using `fetch_remediation_runbook`.
4. STRUCTURED INCIDENT ASSESSMENT: Produce a comprehensive, clear report formatted exactly as:

[<P1|P2|P3> INCIDENT REPORT]
- Incident Severity: <P1|P2|P3>
- Root Cause Summary: <Clear technical explanation correlating telemetry anomalies with Unreal Engine NetDriver/Chaos Physics or EOS gateway routing issues>
- Impacted Shards / Regions: <List of impacted shards (e.g. eu-west-03, us-east-12) and regions>
- Recommended Mitigation / 1-Click Rollback Script: <Exact remediation CLI command from the runbook (e.g., eos-admin routing rollback ... or epic-config-cli set ...)>

CRITICAL SAFETY GUARDRAILS:
- Never execute automated rollbacks directly on production shards without human operator sign-off; always provide the exact rollback command for operator review.
- All telemetry and database queries must remain read-only.
- Always maintain technical precision regarding Unreal Engine subsystems (NetDriver, Chaos Physics, SocketSubsystemEOS).
"""

root_agent = Agent(
    name="titan_agent",
    model=Gemini(
        model=MODEL,
        client=genai_client,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=4096,
    ),
    tools=[
        query_telemetry_metrics,
        lookup_unreal_crash_signature,
        fetch_remediation_runbook,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
