import uuid

from fastapi.testclient import TestClient

from app.auth import get_password_hash, verify_password
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    assert response.json()['service'] == 'PocketSmart AI'


def test_landing_page():
    response = client.get('/')
    assert response.status_code == 200
    assert 'PocketSmart AI' in response.text


def test_register_page():
    response = client.get('/register')
    assert response.status_code == 200
    assert 'Register' in response.text or 'Sign up' in response.text


def test_login_page():
    response = client.get('/login')
    assert response.status_code == 200
    assert 'Login' in response.text or 'Sign in' in response.text


def test_long_password_is_truncated_for_bcrypt():
    long_password = 'a' * 200
    hashed = get_password_hash(long_password)
    assert verify_password(long_password, hashed) is True
    assert len(hashed) > 0


def test_home_planner_generation_does_not_crash():
    email = f"planner-{uuid.uuid4().hex[:8]}@example.com"
    register_response = client.post(
        '/register',
        data={
            'name': 'Planner Tester',
            'email': email,
            'password': 'strongpass123',
        },
        follow_redirects=False,
    )
    assert register_response.status_code in (200, 303)

    login_response = client.post(
        '/token',
        json={'email': email, 'password': 'strongpass123'},
    )
    assert login_response.status_code == 200
    token = login_response.json()['access_token']

    response = client.post(
        '/api/generate-home',
        json={
            'total_budget': 150000,
            'rooms': 'Living room, bedroom',
            'required_items': '2 sofas',
            'interior_style': 'Minimal modern',
            'location': 'Bengaluru',
            'priorities': 'comfort',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    payload = response.json()
    assert 'summary' in payload
    assert 'budget_allocation' in payload
    assert 'recommendations' in payload


def test_trip_planner_generation_succeeds():
    email = f"trip-{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        '/register',
        data={
            'name': 'Trip User',
            'email': email,
            'password': 'strongpass123',
        },
        follow_redirects=False,
    )

    login_response = client.post(
        '/token',
        json={'email': email, 'password': 'strongpass123'},
    )
    assert login_response.status_code == 200
    token = login_response.json()['access_token']

    response = client.post(
        '/api/generate-trip',
        json={
            'total_budget': 45000,
            'destination': 'Goa',
            'trip_type': 'Beach getaway',
            'travelers': 2,
            'days': 4,
            'season': 'Summer',
            'travel_style': 'Budget-friendly',
            'preferences': 'Beach, food, sightseeing',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    payload = response.json()
    assert 'summary' in payload
    assert 'budget_allocation' in payload
    assert 'recommendations' in payload
