# 🎮 Operation Zero Downtime: Spec-Driven Agent Engineering with Antigravity 2.0 & Google Cloud

Welcome to the hands-on technical workshop built for **Epic Games Reliability & Platform Engineers**.

In this 3-hour immersive session, you will step into the role of Core Reliability Engineers during a high-stakes *Fortnite Chapter Launch Event*. You will build, verify, deploy, and publish **Titan** — an Autonomous LiveOps Incident Agent powered by **Antigravity 2.0**, **Google Agent Development Kit (ADK)** (`google.antigravity`), **Gemini 3.7 Flash**, and **Google Cloud Agent Platform (Agent Engine)**.

---

## ⏱️ 3-Hour Workshop Schedule

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 00:00 - 00:15 (15m) │ Welcome, Mission Briefing & LiveOps Problem Statement │
│ 00:15 - 00:30 (15m) │ Intro to Antigravity & Spec-Driven Development (SDD)  │
│ 00:30 - 01:30 (60m) │ Phase 2: Hands-on Lab: Build Titan with Google ADK    │
│                     │         (Parallel Subagents, BQ MCP, Rich Artifacts)  │
│ 01:30 - 01:40 (10m) │ ☕ Bio Break & Lightning Q&A                         │
│ 01:40 - 02:05 (25m) │ Phase 3: Antigravity CLI — Cloud Deploy & Verification│
│ 02:05 - 02:40 (35m) │ Phase 4: Gemini Enterprise Publishing & Interaction   │
│ 02:40 - 03:00 (20m) │ Phase 5: War Game Challenge, AGY vs CLI & Wrap-up     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture Overview

```mermaid
flowchart LR
    subgraph Dev["1. Antigravity 2.0 IDE (Spec-Driven Dev)"]
        Spec["specs/titan_agent_spec.yaml"] --> Orchestrator["Antigravity 2.0 Primary Agent"]
        Orchestrator -->|Spawns Subagent 1 (Parallel Coding)| Sub1["Telemetry Tool Builder: BigQuery MCP"]
        Orchestrator -->|Spawns Subagent 2 (Parallel Coding)| Sub2["Crash Diagnostics Builder: Unreal Engine"]
        Sub1 --> Code["Google ADK Agent Core (google.antigravity)"]
        Sub2 --> Code
        Code --> Artifacts["Implementation Plan & Walkthrough"]
    end

    subgraph Deploy["2. Antigravity CLI & Cloud Deployment"]
        Artifacts --> CLI["agy deploy --target=agent-engine"]
        CLI --> AgentEngine["Google Cloud Agent Platform (Agent Engine)"]
        CLI --> Verify["agy test (Health & Anomaly Probes)"]
    end

    subgraph Enterprise["3. Gemini Enterprise Activation"]
        AgentEngine --> Catalog["Gemini Enterprise Agent Catalog"]
        Catalog --> LiveOps["LiveOps On-Call Engineer: @Titan-LiveOps"]
    end
```

---

## 🚀 Step-by-Step Hands-On Guide

### 📋 Prerequisites & Quickstart
1. Ensure your environment variables are configured:
   ```bash
   export GCP_PROJECT="your-epic-gcp-project"
   export GCP_REGION="us-central1"
   ```
2. Populate the dummy BigQuery telemetry tables (or local mock JSON files):
   ```bash
   python3 scripts/seed_bigquery_telemetry.py
   ```

---

### 🕒 Phase 1: Intro to Antigravity & Spec-Driven Development (00:00 – 00:30)
1. **The LiveOps Challenge:** Triaging high packet loss and matchmaking dropouts across Fortnite server shards.
2. **Spec-Driven Development (SDD):** Inspect `specs/titan_agent_spec.yaml`. Notice how strict input/output contracts eliminate hallucinations and enforce safety guardrails.

---

### 🕒 Phase 2: Hands-on Lab: Build Titan with Google ADK in Antigravity 2.0 (00:30 – 01:30)
In this phase, you will use **Google ADK (`google.antigravity`)** as the agent framework. You will orchestrate **Antigravity 2.0** to generate, test, and wire the agent modules from the specification!

1. **Step 1: Open Antigravity 2.0 IDE** and load the workspace.
2. **Step 2: Prompt Antigravity 2.0 to orchestrate parallel subagents:**
   > *"Read `specs/titan_agent_spec.yaml`. Spin out two parallel subagents to implement the codebase:
   > 1. Subagent 1 (`telemetry-tool-builder`): Implement `titan_agent/tools/telemetry_tool.py` using BigQuery MCP to query matchmaking metrics and flag anomalies.
   > 2. Subagent 2 (`crash-inspector-builder`): Implement `titan_agent/tools/crash_diagnostics.py` to match Unreal Engine crash signatures and fetch SRE runbooks.
   > Synthesize their output into `titan_agent/agent.py` using the Google ADK (`google.antigravity` Agent, LocalAgentConfig) and produce an interactive Implementation Plan artifact."*
3. **Step 3: Review Antigravity Artifacts:**
   * Inspect the generated **Implementation Plan** and **Walkthrough** in the Antigravity artifact viewer.
4. **Step 4: Run the test suite to verify your implementation:**
   ```bash
   python3 -m unittest discover -s tests -p "test_*.py"
   ```

---

### 🕒 Phase 3: Antigravity CLI (`agy`) — Cloud Deployment & Verification (01:40 – 02:05)
1. **Deploy to Google Cloud Agent Platform (Agent Engine):**
   ```bash
   bash cli/deploy_agent_engine.sh
   ```
2. **Automated Verification Probes (`agy test`):**
   ```bash
   python3 cli/verify_cloud_agent.py
   ```
   * Probe 1: Agent Engine runtime health check.
   * Probe 2: BigQuery MCP connection probe.
   * Probe 3: Synthetic EU-West packet loss triage probe.

---

### 🕒 Phase 4: Gemini Enterprise Integration & Publishing (02:05 – 02:40)
1. **Register the Agent:** Inspect `cli/gemini_enterprise_manifest.json` and publish Titan into the **Gemini Enterprise Agent Catalog**.
2. **Live Incident Interaction:**
   * In Gemini Enterprise chat, mention `@Titan-LiveOps`:
   > *"@Titan-LiveOps Shard EU-West-03 is showing 14% packet loss and matchmaking timeouts following the 30.10 update. Run an incident diagnosis and provide mitigation."*
   * Titan autonomously queries BigQuery via MCP, correlates the Unreal NetDriver buffer overflow, and returns a 1-click rollback command (`eos-admin routing rollback --rule-id=EOS-NET-3010-P2`).

---

### 🕒 Phase 5: War Game Finale & Wrap-up (02:40 – 03:00)
1. **Live War Game Challenge:**
   * Instructor runs `python3 scripts/simulate_incident.py us-east-12` to inject a live matchmaking outage.
   * Engineers query their `@Titan-LiveOps` agent in Gemini Enterprise to diagnose the root cause and execute the mitigation.
2. **Antigravity 2.0 vs. Antigravity CLI:**
   * Review when to use the interactive IDE vs. headless CLI in Epic's engineering workflows.

---

## 🧭 Tooling Comparison: Antigravity 2.0 vs. Antigravity CLI (`agy`)

| Feature | Antigravity 2.0 (IDE / GUI) | Antigravity CLI (`agy` / Terminal) |
| :--- | :--- | :--- |
| **Best For** | Exploratory coding, multi-agent orchestration, visual architecture | CI/CD pipelines, Unreal Engine build hooks, batch tasks |
| **Framework** | Google ADK (`google.antigravity`) | Google ADK (`google.antigravity`) runtime runner |
| **Subagents** | Visual branching and concurrent subagent coordination | Headless execution across background workers |
| **Artifacts** | Interactive Plans, Walkthroughs, Mermaid graphs, Carousels | JSON logs, test reports, structured diffs |
| **Operations** | Spec authoring and human-in-the-loop review | Packaging (`agy deploy`) & automated health verification (`agy test`) |
