# Epic Games Engineering & Safety Rules for Antigravity

1. **Spec-Driven Consistency:** All agent modifications must adhere to `specs/titan_agent_spec.yaml`.
2. **Model Standard:** Always use `gemini-3.7-flash` for low-latency incident response loops.
3. **Data Access Standard:** Never generate hardcoded SQL strings inside tool bodies; always leverage the **BigQuery MCP Server** interface.
4. **Crash Log Standard:** Unreal Engine crash signatures must always follow the standard format `CRASH-UE5-<SUBSYSTEM>-<ID>`.
5. **No Production Direct Writes:** LiveOps telemetry queries must remain read-only (`execute_sql_readonly`).
