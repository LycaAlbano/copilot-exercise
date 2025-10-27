import copy
import pytest

from fastapi.testclient import TestClient
import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    # Backup and restore the in-memory activities dict for test isolation
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


def test_get_activities():
    client = TestClient(app_module.app)
    r = client.get('/activities')
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    # Sanity: Chess Club exists in sample data
    assert 'Chess Club' in data


def test_signup_and_prevent_duplicate():
    client = TestClient(app_module.app)
    activity = 'Chess Club'
    email = 'tester@example.com'

    # Ensure test email not present
    before = client.get('/activities').json()[activity]['participants']
    assert email not in before

    # Sign up
    r = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert r.status_code == 200
    assert 'Signed up' in r.json().get('message', '')

    # Signing up again should fail with 400
    r2 = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert r2.status_code == 400


def test_unregister_participant():
    client = TestClient(app_module.app)
    activity = 'Programming Class'
    email = 'temp-remove@example.com'

    # Add participant first
    r = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert r.status_code == 200

    # Now remove
    r2 = client.delete(f"/activities/{activity}/participants", params={'email': email})
    assert r2.status_code == 200
    assert 'Unregistered' in r2.json().get('message', '')

    # Ensure removed
    after = client.get('/activities').json()[activity]['participants']
    assert email not in after
