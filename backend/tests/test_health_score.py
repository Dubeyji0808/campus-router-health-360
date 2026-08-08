from app import calculate_health_score


def test_health_score_on_bad_router_is_low():
    payload = {
        'latency_ms': 240,
        'packet_loss_pct': 12.5,
        'disconnects': 6,
        'connected_devices': 140,
        'signal_dbm': -72,
        'is_bad': True,
    }
    assert calculate_health_score(payload) < 40


def test_health_score_on_healthy_router_is_high():
    payload = {
        'latency_ms': 40,
        'packet_loss_pct': 0.8,
        'disconnects': 0,
        'connected_devices': 42,
        'signal_dbm': -55,
        'is_bad': False,
    }
    assert calculate_health_score(payload) > 70
