# 🎮 Operation Zero Downtime: Spec-Driven Agent Engineering with Antigravity 2.0 & Google Cloud

Welcome to the hands-on technical workshop built for **Epic Games Reliability & Platform Engineers**.

In this 3-hour immersive session, you will step into the role of Core Reliability Engineers during a high-stakes *Fortnite Chapter Launch Event*. You will build, verify, deploy, and publish **Titan** — an Autonomous LiveOps Incident Agent powered by **Antigravity 2.0**, **Google Agent Development Kit (ADK)**, **Gemini 3.7 Flash**, and **Google Cloud Agent Platform (Agent Engine)**.

---

## ⏱️ 3-Hour Workshop Schedule

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 00:00 - 00:15 (15m) │ Welcome, Mission Briefing & LiveOps Problem Statement │
│ 00:15 - 00:30 (15m) │ Intro to Antigravity & Spec-Driven Development (SDD)  │
│ 00:30 - 01:30 (60m) │ Phase 2: Hands-on Lab: Build Titan with Antigravity   │
│                     │         (Plan Review, Subagents & google-cli Skills)  │
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
    subgraph Dev["1. Antigravity 2.0 IDE (Human-in-the-Loop SDD)"]
        Spec["specs/titan_agent_spec.yaml"] --> Orchestrator["Antigravity 2.0 Primary Agent"]
        Skills[".agents/skills/google-agents-cli-adk-code"] --> Orchestrator
        Orchestrator --> Plan["Implementation Plan Artifact"]
        Plan -->|Student Comments & Approves| ApprovedPlan["Approved Plan"]
        ApprovedPlan -->|Spawns Subagent 1 (Parallel Coding)| Sub1["Telemetry Tool Builder: BigQuery MCP"]
        ApprovedPlan -->|Spawns Subagent 2 (Parallel Coding)| Sub2["Crash Diagnostics Builder: Unreal Engine"]
        Sub1 --> Code["titan_agent/ (Google ADK & Gemini 3.7 Flash)"]
        Sub2 --> Code
        Code --> Artifacts["Visual Walkthrough Artifact"]
    end

    subgraph Deploy["2. Antigravity CLI & Cloud Deployment"]
        Artifacts --> CLI["agy deploy --target=agent-engine (.agents/skills/google-agents-cli-deploy)"]
        CLI --> AgentEngine["Google Cloud Agent Platform (Agent Engine)"]
        CLI --> Verify["agy test (Health & Anomaly Probes)"]
    end

    subgraph Enterprise["3. Gemini Enterprise Activation"]
        AgentEngine --> Catalog["Gemini Enterprise Agent Catalog (.agents/skills/google-agents-cli-publish)"]
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
> The `titan_agent/` directory is intentionally empty at the start of Phase 2! You will use **Antigravity 2.0**, interactive **Implementation Plan review**, **parallel subagents**, and the imported **`.agents/skills/`** to construct the entire agent package.

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
3. **Explore Antigravity Skills:** Inspect `.agents/skills/` to see the imported `agents-cli` skills (`google-agents-cli-adk-code`, `google-agents-cli-workflow`, `google-agents-cli-deploy`, `google-agents-cli-publish`).

---

### 🕒 Phase 2: Hands-on Lab: Build Titan with Antigravity 2.0 & ADK Skills (00:30 – 01:30)
In this phase, you experience **human-in-the-loop plan review**, **Antigravity 2.0 subagent orchestration**, and **Google ADK skills**.

#### 📝 Step 1: Request the Implementation Plan (DO NOT BUILD YET)
Open the Antigravity 2.0 IDE and enter the initial prompt:

```markdown
Activate and use the skills in `.agents/skills/google-agents-cli-adk-code` and `.agents/skills/google-agents-cli-workflow`.
Read the spec contract in `specs/titan_agent_spec.yaml`.

Create a comprehensive Implementation Plan artifact for building the Titan LiveOps Agent using Google ADK (`google.antigravity` / ADK patterns) with Gemini 3.7 Flash. 
Do NOT write code or create files yet. Outline the proposed architecture, tool contracts, and subagent delegation strategy, then stop and wait for my review and feedback.
```

---

#### 🔍 Step 2: Review & Revise the Plan with Inline Comments
When Antigravity generates the **Implementation Plan artifact** (`implementation_plan.md`), click to view it in the Artifact Panel. Practice adding inline comments to guide the agent:

##### 💡 Example Comments to Add on the Artifact:
* **On the Telemetry Tool Section:**
  > *"Ensure we flag shard packet loss > 5% as WARNING and > 10% as CRITICAL anomalies, and query BigQuery via MCP with a local mock JSON fallback."*
* **On the Crash Diagnostics Section:**
  > *"Make sure the crash parser extracts engine build changelist CL349201 and maps NetDriver buffer overflow crashes directly to runbook `ERR_NET_CONGESTION_EOS`."*
* **On the Agent Architecture Section:**
  > *"Follow ADK patterns from `.agents/skills/google-agents-cli-adk-code` and ensure `handle_request()` outputs structured reports with markdown headers, severity tags (`[P1 INCIDENT REPORT]`), and 1-click rollback commands."*
* **On the Execution Strategy:**
  > *"When executing this plan, use TWO specialized parallel subagents: Subagent 1 (`telemetry-tool-builder`) for `telemetry_tool.py` and Subagent 2 (`crash-diagnostics-builder`) for `crash_diagnostics.py`, while the main agent builds `agent.py` and coordinates testing."*

---

#### 🚀 Step 3: Approve the Plan and Trigger Multi-Agent Build
Once your comments are placed, prompt Antigravity to incorporate the feedback and proceed:

```markdown
Review the implementation plan according to my comments and proceed with building the agent using Google ADK.
Use the main agent for titan_agent/agent.py and config, and launch two parallel specialized subagents to implement titan_agent/tools/telemetry_tool.py and titan_agent/tools/crash_diagnostics.py.
```

##### ⚡ What Happens Next in Antigravity:
1. **Primary Agent:** Sets up `titan_agent/config.py` and `titan_agent/requirements.txt` using ADK conventions from `.agents/skills/google-agents-cli-adk-code`.
2. **Subagent 1 (`telemetry-tool-builder`):** Codes and verifies `titan_agent/tools/telemetry_tool.py` with BigQuery MCP integration.
3. **Subagent 2 (`crash-diagnostics-builder`):** Codes and verifies `titan_agent/tools/crash_diagnostics.py` with Unreal Engine NetDriver signatures.
4. **Primary Agent:** Assembles `titan_agent/agent.py` with Google ADK, runs verification, and generates an interactive **Walkthrough Artifact**.

---

#### ✅ Step 4: Verify Your Agent with `adk run` in Antigravity 2.0
Now that Antigravity 2.0 has built the agent and tools, test Titan locally using the **Google ADK CLI (`adk run`)**:

1. **Run Titan with an incident prompt:**
   ```bash
   adk run titan_agent --prompt "@Titan-LiveOps Shard EU-West-03 is showing 14% packet loss and matchmaking timeouts following the 30.10 update. Run an incident diagnosis and provide mitigation."
   ```

   *(Alternatively, start an interactive multi-turn ADK session by running `adk run titan_agent`)*

2. **Verify the Agent Output:**
   * ✅ **Agent Initialization:** Gemini 3.7 Flash boots with the system instruction from `specs/titan_agent_spec.yaml`.
   * ✅ **Tool Invocations:** Titan calls `query_telemetry_metrics` (BigQuery MCP) to identify the EU-West anomaly and `lookup_unreal_crash_signature` for NetDriver buffer overflow.
   * ✅ **Structured Incident Report:** Titan returns a `[P1 INCIDENT REPORT]` with affected shards, root cause, and the 1-click rollback command:
     ```bash
     eos-admin routing rollback --rule-id=EOS-NET-3010-P2
     ```

3. **(Optional) Run Unit Tests:**
   ```bash
   python3 -m unittest discover -s tests -p "test_*.py"
   ```

---

### 🕒 Phase 3: Antigravity CLI (`agy`) — Cloud Deployment & Verification (01:40 – 02:05)
1. **Deploy to Google Cloud Agent Platform (Agent Engine):**
   * Antigravity leverages `.agents/skills/google-agents-cli-deploy` to package and deploy Titan:
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
1. **Register the Agent:**
   * Antigravity leverages `.agents/skills/google-agents-cli-publish` to register Titan into the **Gemini Enterprise Agent Catalog**:
   * Inspect `cli/gemini_enterprise_manifest.json`.
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
| **Framework** | Google ADK (`google.antigravity`) via `.agents/skills/google-agents-cli-adk-code` | Google ADK runtime runner & packaging |
| **Subagents** | Visual branching and concurrent subagent coordination | Headless execution across background workers |
| **Skills** | Native `.agents/skills/` automatic discovery & invocation | CLI workflow automation (`agy run`) |
| **Artifacts** | Interactive Plans, Walkthroughs, Mermaid graphs, Carousels | JSON logs, test reports, structured diffs |
| **Operations** | Spec authoring and human-in-the-loop review | Packaging (`agy deploy`) & automated health verification (`agy test`) |
