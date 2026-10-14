-- Epic Games BigQuery LiveOps Dummy Telemetry Dataset
-- Dataset: epic_liveops

CREATE SCHEMA IF NOT EXISTS `epic_liveops`
OPTIONS (
  location = "US",
  description = "Synthetic LiveOps Telemetry for Fortnite Matchmaking & Unreal Engine Diagnostics"
);

-- 1. Matchmaking & Shard Telemetry Table
CREATE OR REPLACE TABLE `epic_liveops.matchmaking_telemetry` (
  timestamp TIMESTAMP,
  shard_id STRING,
  region STRING,
  active_matches INT64,
  matchmaking_latency_ms FLOAT64,
  packet_loss_pct FLOAT64,
  player_dropouts INT64,
  eos_gateway_status STRING
);

INSERT INTO `epic_liveops.matchmaking_telemetry` (timestamp, shard_id, region, active_matches, matchmaking_latency_ms, packet_loss_pct, player_dropouts, eos_gateway_status)
VALUES
  (TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE), 'eu-west-01', 'EU', 1420, 24.5, 0.2, 2, 'HEALTHY'),
  (TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE), 'eu-west-02', 'EU', 1580, 26.1, 0.4, 3, 'HEALTHY'),
  (TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE), 'eu-west-03', 'EU', 2100, 342.8, 14.2, 185, 'DEGRADED'),
  (TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 10 MINUTE), 'eu-west-03', 'EU', 1950, 312.0, 13.8, 160, 'DEGRADED'),
  (TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE), 'us-east-11', 'NA-EAST', 2300, 19.8, 0.1, 1, 'HEALTHY'),
  (TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE), 'us-east-12', 'NA-EAST', 1890, 85.4, 4.2, 450, 'CRITICAL'),
  (TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 15 MINUTE), 'us-east-12', 'NA-EAST', 1950, 78.2, 3.8, 380, 'CRITICAL'),
  (TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE), 'ap-northeast-01', 'ASIA', 1100, 32.1, 0.5, 4, 'HEALTHY');

-- 2. Unreal Engine Crash Signatures Table
CREATE OR REPLACE TABLE `epic_liveops.unreal_crash_signatures` (
  crash_hash STRING,
  build_version STRING,
  engine_module STRING,
  callstack_summary STRING,
  first_seen_timestamp TIMESTAMP,
  affected_clients INT64,
  related_error_code STRING
);

INSERT INTO `epic_liveops.unreal_crash_signatures` (crash_hash, build_version, engine_module, callstack_summary, first_seen_timestamp, affected_clients, related_error_code)
VALUES
  (
    'CRASH-UE5-NET-0842',
    'Release-30.10-CL349201',
    'NetDriver / SocketSubsystemEOS',
    'UNetDriver::TickDispatch -> FSocketEOS::RecvFrom -> FatalPacketBufferOverflowException',
    TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 MINUTE),
    1240,
    'ERR_NET_CONGESTION_EOS'
  ),
  (
    'CRASH-UE5-CHAOS-9102',
    'Release-30.10-CL349201',
    'ChaosPhysics / Replication',
    'FChaosReplicationSync::SerializePayload -> NullReference at 0x00007FFF0042',
    TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 45 MINUTE),
    890,
    'ERR_UE5_CHAOS_NULLPTR'
  );

-- 3. LiveOps SRE Runbooks Table
CREATE OR REPLACE TABLE `epic_liveops.incident_runbooks` (
  error_code STRING,
  title STRING,
  severity STRING,
  remediation_steps STRING,
  rollback_command STRING
);

INSERT INTO `epic_liveops.incident_runbooks` (error_code, title, severity, remediation_steps, rollback_command)
VALUES
  (
    'ERR_NET_CONGESTION_EOS',
    'EOS Gateway Packet Buffer Overrun Mitigation',
    'P1',
    '1. Drain incoming matchmaking queue on affected shard.\n2. Revert EOS routing rule patch to v30.10-baseline.\n3. Cycle NetDriver socket pools.',
    'eos-admin routing rollback --rule-id=EOS-NET-3010-P2 --shard=eu-west-03'
  ),
  (
    'ERR_UE5_CHAOS_NULLPTR',
    'Unreal Chaos Physics Replication Hotfix',
    'P1',
    '1. Disable experimental chaos packet compression in LiveOps remote config.\n2. Restart affected server instances.',
    'epic-config-cli set --key=p.Chaos.ReplicationSync --value=0 --broadcast=global'
  );
