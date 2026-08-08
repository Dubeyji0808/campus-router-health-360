from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_rankings_endpoint_returns_router_rows():
    response = client.get('/api/rankings')
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 1
    assert 'router_id' in payload[0]
    assert 'health_score' in payload[0]


def test_router_detail_endpoint_returns_expected_payload():
    response = client.get('/api/router/R-1042')
    assert response.status_code == 200
    payload = response.json()
    assert payload['router_id'] == 'R-1042'
    assert 'info' in payload
    assert 'metrics_timeseries' in payload
    assert 'complaints' in payload


def test_missing_router_returns_404():
    response = client.get('/api/router/NOT-REAL')
    assert response.status_code == 404


def test_copilot_endpoint_uses_router_context():
    response = client.post('/api/copilot', json={'question': 'Why is R-1042 performing badly?'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['router_id'] == 'R-1042'
    assert 'recommended_fix' in payload
    assert payload['recommended_fix'] in {'replace', 'firmware_update', 'user_education'}
