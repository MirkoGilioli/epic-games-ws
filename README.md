# 🎮 Operation Zero Downtime: Spec-Driven Agent Engineering with Antigravity 2.0 & Google Cloud

Welcome to the hands-on technical workshop built for **Epic Games Reliability & Platform Engineers**.

In this 3-hour immersive session, you will step into the role of Core Reliability Engineers during a high-stakes *Fortnite Chapter Launch Event*. You will build, verify, deploy, and publish **Titan** — an Autonomous LiveOps Incident Agent powered by **Antigravity 2.0**, **Google Agent Development Kit (ADK)** (`google.antigravity`), **Gemini 3.7 Flash**, and **Google Cloud Agent Platform (Agent Engine)**.

---

## ⏱️ 3-Hour Workshop Schedule

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 00:00 - 00:15 (15m) │ Welcome, Mission Briefing & LiveOps Problem Statement │
│ 00:15 - 00:30 (15m) │ Intro to Antigravity & Spec-Driven Development (SDD)  │
│ 00:30 - 01:30 (60m) │ Phase 2: Hands-on Lab: Build Titan with Antigravity   │
│                     │         (Parallel Subagents + agents-cli Skills)      │
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
    subgraph Dev["1. Antigravity 2.0 IDE (Spec-Driven Dev + Subagents)"]
        Spec["specs/titan_agent_spec.yaml"] --> Orchestrator["Antigravity 2.0 Primary Agent"]
        Skills[".agents/skills/ (google-agents-cli-adk-code)"] --> Orchestrator
        Orchestrator -->|Spawns Subagent 1 (Parallel Coding)| Sub1["Telemetry Tool Builder: BigQuery MCP"]
        Orchestrator -->|Spawns Subagent 2 (Parallel Coding)| Sub2["Crash Diagnostics Builder: Unreal Engine"]
        Sub1 --> Code["titan_agent/ (Google ADK & Gemini 3.7 Flash)"]
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

## 📂 Project Repository Structure (Starting State for Phase 2)

```
├── .agents/
│   ├── rules/
│   │   └── epic_engineering_rules.md            # Epic coding & safety rules
│   └── skills/
│       ├── google-agents-cli-adk-code/          # ADK API patterns & code recipes
│       ├── google-agents-cli-deploy/            # Agent Engine & Cloud Run deployment
│       ├── google-agents-cli-eval/              # Evaluation & benchmarking skills
│       ├── google-agents-cli-observability/     # Cloud Trace & BigQuery logging
│       ├── google-agents-cli-publish/           # Gemini Enterprise publishing
│       ├── google-agents-cli-scaffold/          # Project templates & structure
│       ├── google-agents-cli-workflow/          # SDD lifecycle & workflow
│       └── liveops-triage/                      # Epic Games Fortnite & NetDriver triage
├── data/                                        # Mock fallback telemetry & crash DB
├── mcp_servers/
│   └── bigquery_mcp.json                        # BigQuery MCP server config
├── specs/
│   ├── incident_scenarios.yaml                  # Incident test cases (EU-West / US-East)
│   └── titan_agent_spec.yaml                    # SDD Contract (ADK Agent & Tool Schemas)
├── tests/
│   ├── test_agent.py                            # End-to-end agent integration test
│   └── test_tools.py                            # Tool unit tests
└── README.md
```

> [!NOTE]
> The `titan_agent/` directory is intentionally empty at the start of Phase 2! You will use **Antigravity 2.0** and its **parallel subagents** to construct the entire agent package from `specs/titan_agent_spec.yaml` and `.agents/skills/`.

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
3. **Explore Antigravity Skills:** Inspect `.agents/skills/` to see the imported `agents-cli` skills that equip Antigravity with Google ADK patterns, deployment pipelines, and evaluation workflows.

---

### 🕒 Phase 2: Hands-on Lab: Build Titan with Antigravity 2.0 (00:30 – 01:30)
In this phase, you experience **Antigravity 2.0 subagent orchestration** in action.

1. **Step 1: Open Antigravity 2.0 IDE** and load this repository.
2. **Step 2: Instruct Antigravity to build Titan from the specification:**
   
   Enter this prompt in Antigravity 2.0:
   ```markdown
   Read `specs/titan_agent_spec.yaml` and use the Google ADK skills in `.agents/skills/google-agents-cli-adk-code` and `.agents/skills/google-agents-cli-workflow`.

   Create an interactive Implementation Plan, then spin out TWO parallel coding subagents:
   1. Subagent 1 (`telemetry-tool-builder`): Create `titan_agent/tools/telemetry_tool.py` using BigQuery MCP to query shard telemetry and flag anomalies exceeding threshold (packet loss > 5%, latency > 120ms).
   2. Subagent 2 (`crash-diagnostics-builder`): Create `titan_agent/tools/crash_diagnostics.py` to match Unreal Engine crash signatures (NetDriver buffer overflow, CL349201) and retrieve SRE runbooks.

   Assemble their work into `titan_agent/` with:
   - `titan_agent/agent.py` using Google ADK (`google.antigravity` Agent, LocalAgentConfig) with Gemini 3.7 Flash.
   - `titan_agent/config.py` and `titan_agent/requirements.txt`.

   Finally, generate a Walkthrough artifact and run the test suite to verify!
   ```

3. **Step 3: Watch Antigravity 2.0 Subagents in Real-Time:**
   * Antigravity creates an **Implementation Plan Artifact**.
   * Antigravity branches into two simultaneous subagents coding both tools in parallel.
   * Antigravity merges the tools into the Google ADK agent and generates a **Walkthrough Artifact**.

4. **Step 4: Verify Your Agent:**
   Run the test suite in the terminal:
   ```bash
   python3 -m unittest discover -s tests -p "test_*.py"
   ```
   * All unit tests for tools and agent integration will pass!

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
| **Skills** | Native `.agents/skills/` automatic discovery & invocation | CLI workflow automation (`agy run`) |
| **Artifacts** | Interactive Plans, Walkthroughs, Mermaid graphs, Carousels | JSON logs, test reports, structured diffs |
| **Operations** | Spec authoring and human-in-the-loop review | Packaging (`agy deploy`) & automated health verification (`agy test`) |
