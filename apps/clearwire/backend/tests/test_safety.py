from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def scope(expires=None, precise=False):
    return {"scope_id":"scope-test-001","label":"Authorized Lab","expires_at":(expires or datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),"precise_location":precise}


def test_scan_requires_matching_scope_header():
    r = client.post('/api/v1/scans', json={"authorization":scope()}, headers={"x-authorization-scope":"wrong"})
    assert r.status_code == 403


def test_scan_rejects_expired_scope():
    expired = datetime.now(timezone.utc)-timedelta(minutes=1)
    r = client.post('/api/v1/scans', json={"authorization":scope(expired)}, headers={"x-authorization-scope":"scope-test-001"})
    assert r.status_code == 403


def test_scan_returns_pseudonymous_identifiers_and_no_payloads():
    r = client.post('/api/v1/scans', json={"authorization":scope()}, headers={"x-authorization-scope":"scope-test-001"})
    assert r.status_code == 200
    body = r.json()
    assert body['authorized_monitoring'] is True
    for item in body['observations']:
        assert len(item['identifier']) == 16
        assert 'password' not in item
        assert 'payload' not in item
        assert 'plaintext' not in item


def test_capabilities_explicitly_disable_interception():
    body = client.get('/api/v1/capabilities').json()
    assert body['passive_only'] is True
    assert body['packet_content_capture'] is False
    assert body['credential_interception'] is False
