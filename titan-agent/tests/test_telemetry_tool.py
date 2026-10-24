"""Unit tests for query_telemetry_metrics tool."""

from unittest.mock import patch
import pytest

from app.tools.telemetry_tool import query_telemetry_metrics


@pytest.fixture
def mock_telemetry_data():
    """Provides a controlled telemetry dataset for deterministic unit testing."""
    return [
        {
            "timestamp": "2026-10-16T04:43:08.031837+00:00",
            "shard_id": "eu-west-01",
            "region": "EU",
            "active_matches": 1420,
            "matchmaking_latency_ms": 24.5,
            "packet_loss_pct": 0.2,
            "player_dropouts": 2,
            "eos_gateway_status": "HEALTHY",
        },
        {
            "timestamp": "2026-10-16T04:43:08.031837+00:00",
            "shard_id": "eu-west-02",
            "region": "EU",
            "active_matches": 1580,
            "matchmaking_latency_ms": 26.1,
            "packet_loss_pct": 0.4,
            "player_dropouts": 3,
            "eos_gateway_status": "HEALTHY",
        },
        {
            "timestamp": "2026-10-16T04:43:08.031837+00:00",
            "shard_id": "eu-west-03",
            "region": "EU",
            "active_matches": 2100,
            "matchmaking_latency_ms": 342.8,
            "packet_loss_pct": 14.2,
            "player_dropouts": 185,
            "eos_gateway_status": "DEGRADED",
        },
        {
            "timestamp": "2026-10-16T04:38:08.031837+00:00",
            "shard_id": "eu-west-03",
            "region": "EU",
            "active_matches": 1950,
            "matchmaking_latency_ms": 312.0,
            "packet_loss_pct": 13.8,
            "player_dropouts": 160,
            "eos_gateway_status": "DEGRADED",
        },
        {
            "timestamp": "2026-10-16T04:43:08.031837+00:00",
            "shard_id": "us-east-11",
            "region": "NA-EAST",
            "active_matches": 2300,
            "matchmaking_latency_ms": 19.8,
            "packet_loss_pct": 0.1,
            "player_dropouts": 1,
            "eos_gateway_status": "HEALTHY",
        },
        {
            "timestamp": "2026-10-16T04:43:08.031837+00:00",
            "shard_id": "us-east-12",
            "region": "NA-EAST",
            "active_matches": 1890,
            "matchmaking_latency_ms": 85.4,
            "packet_loss_pct": 7.5,
            "player_dropouts": 450,
            "eos_gateway_status": "CRITICAL",
        },
    ]


def test_query_all_shards_real_or_fallback():
    """Tests querying with no shard filter across all available shards."""
    result = query_telemetry_metrics(shard_id=None, metric_name="all")
    assert result["status"] == "success"
    assert result["shard_id"] is None
    assert len(result["records"]) > 0
    assert "summary_stats" in result
    assert "anomalies_detected" in result
    assert result["summary_stats"]["avg_packet_loss_pct"] is not None


def test_query_filtering_by_shard_eu_west_03(mock_telemetry_data):
    """Tests filtering by specific shard 'eu-west-03'."""
    with patch("app.tools.telemetry_tool._load_telemetry_data", return_value=mock_telemetry_data):
        result = query_telemetry_metrics(shard_id="eu-west-03")
        assert result["status"] == "success"
        assert result["shard_id"] == "eu-west-03"
        assert len(result["records"]) == 2
        for r in result["records"]:
            assert r["shard_id"] == "eu-west-03"

        stats = result["summary_stats"]
        assert stats["total_player_dropouts"] == 345
        assert stats["max_eos_status"] == "DEGRADED"
        assert stats["avg_packet_loss_pct"] == 14.0


def test_query_filtering_by_shard_us_east_12(mock_telemetry_data):
    """Tests filtering by shard 'us-east-12'."""
    with patch("app.tools.telemetry_tool._load_telemetry_data", return_value=mock_telemetry_data):
        result = query_telemetry_metrics(shard_id="us-east-12")
        assert result["status"] == "success"
        assert result["shard_id"] == "us-east-12"
        assert len(result["records"]) == 1
        assert result["summary_stats"]["max_eos_status"] == "CRITICAL"
        assert result["summary_stats"]["total_player_dropouts"] == 450


def test_query_non_existent_shard(mock_telemetry_data):
    """Tests querying a non-existent shard returns 'no_data' status."""
    with patch("app.tools.telemetry_tool._load_telemetry_data", return_value=mock_telemetry_data):
        result = query_telemetry_metrics(shard_id="ap-southeast-99")
        assert result["status"] == "no_data"
        assert result["shard_id"] == "ap-southeast-99"
        assert result["records"] == []
        assert result["anomalies_detected"] == []
        assert result["summary_stats"]["avg_packet_loss_pct"] is None


def test_anomaly_thresholds(mock_telemetry_data):
    """Tests that packet loss > 5% produces WARNING and > 10% produces CRITICAL."""
    with patch("app.tools.telemetry_tool._load_telemetry_data", return_value=mock_telemetry_data):
        result = query_telemetry_metrics(shard_id=None)
        anomalies = result["anomalies_detected"]
        assert len(anomalies) == 3

        # eu-west-03 has 14.2% and 13.8% -> CRITICAL (> 10%)
        critical_anomalies = [a for a in anomalies if a["severity"] == "CRITICAL"]
        assert len(critical_anomalies) == 2
        for ca in critical_anomalies:
            assert ca["shard_id"] == "eu-west-03"
            assert ca["anomaly_type"] == "PACKET_LOSS"
            assert ca["threshold_breached"] == 10.0
            assert ca["value"] > 10.0

        # us-east-12 has 7.5% -> WARNING (> 5% and <= 10%)
        warning_anomalies = [a for a in anomalies if a["severity"] == "WARNING"]
        assert len(warning_anomalies) == 1
        wa = warning_anomalies[0]
        assert wa["shard_id"] == "us-east-12"
        assert wa["anomaly_type"] == "PACKET_LOSS"
        assert wa["threshold_breached"] == 5.0
        assert wa["value"] == 7.5


def test_metric_filtering_packet_loss_pct(mock_telemetry_data):
    """Tests projection when filtering by metric_name='packet_loss_pct'."""
    with patch("app.tools.telemetry_tool._load_telemetry_data", return_value=mock_telemetry_data):
        result = query_telemetry_metrics(shard_id="eu-west-01", metric_name="packet_loss_pct")
        assert result["status"] == "success"
        record = result["records"][0]
        assert "packet_loss_pct" in record
        assert "shard_id" in record
        assert "timestamp" in record
        assert "active_matches" not in record
        assert "matchmaking_latency_ms" not in record


def test_metric_filtering_matchmaking_latency_ms(mock_telemetry_data):
    """Tests projection when filtering by metric_name='matchmaking_latency_ms'."""
    with patch("app.tools.telemetry_tool._load_telemetry_data", return_value=mock_telemetry_data):
        result = query_telemetry_metrics(shard_id="eu-west-02", metric_name="matchmaking_latency_ms")
        assert result["status"] == "success"
        record = result["records"][0]
        assert "matchmaking_latency_ms" in record
        assert record["matchmaking_latency_ms"] == 26.1
        assert "packet_loss_pct" not in record


def test_metric_filtering_player_dropouts(mock_telemetry_data):
    """Tests projection when filtering by metric_name='player_dropouts'."""
    with patch("app.tools.telemetry_tool._load_telemetry_data", return_value=mock_telemetry_data):
        result = query_telemetry_metrics(shard_id="us-east-11", metric_name="player_dropouts")
        assert result["status"] == "success"
        record = result["records"][0]
        assert "player_dropouts" in record
        assert record["player_dropouts"] == 1
        assert "matchmaking_latency_ms" not in record


def test_metric_filtering_all(mock_telemetry_data):
    """Tests returning all fields when metric_name='all'."""
    with patch("app.tools.telemetry_tool._load_telemetry_data", return_value=mock_telemetry_data):
        result = query_telemetry_metrics(shard_id="eu-west-01", metric_name="all")
        assert result["status"] == "success"
        record = result["records"][0]
        assert "packet_loss_pct" in record
        assert "matchmaking_latency_ms" in record
        assert "player_dropouts" in record
        assert "active_matches" in record
        assert "eos_gateway_status" in record


def test_time_window_filtering(mock_telemetry_data):
    """Tests filtering records outside time_window_minutes."""
    with patch("app.tools.telemetry_tool._load_telemetry_data", return_value=mock_telemetry_data):
        # With window of 2 minutes, the record from 04:38 should be filtered out
        result = query_telemetry_metrics(shard_id="eu-west-03", time_window_minutes=2)
        assert result["status"] == "success"
        assert len(result["records"]) == 1
        assert result["records"][0]["timestamp"] == "2026-10-16T04:43:08.031837+00:00"


def test_empty_data_source():
    """Tests behavior when telemetry data source is empty."""
    with patch("app.tools.telemetry_tool._load_telemetry_data", return_value=[]):
        result = query_telemetry_metrics(shard_id="eu-west-01")
        assert result["status"] == "no_data"
        assert result["records"] == []
        assert result["anomalies_detected"] == []

