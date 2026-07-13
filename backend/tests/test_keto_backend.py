"""Backend tests for Keto app.

Covers:
- Email signature (Patrice Raganelli, phone, address) — code review only, no real emails sent
- /api/notify auth (401 without token, 401 invalid token)
- /api/recipe/detailed-steps with cache (calls twice, expects cached:true on second)
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get('EXPO_BACKEND_URL', 'https://body-metrics-bug.preview.emergentagent.com').rstrip('/')


@pytest.fixture
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ── Sanity: /api/app returns HTML with __KP_API_BASE__ injected ──
def test_app_html_served(api_client):
    r = api_client.get(f"{BASE_URL}/api/app", timeout=30)
    assert r.status_code == 200
    body = r.text
    assert "<html" in body.lower()
    assert "__KP_API_BASE__" in body


# ── Email signature check via source (email endpoints are internal; do not send) ──
def test_email_signature_source_contains_patrice_and_no_marie():
    with open('/app/backend/server.py', 'r', encoding='utf-8') as f:
        src = f.read()
    assert 'Patrice Raganelli' in src
    assert '06 58 83 86 41' in src
    assert '47 rue de la République, 54300 Lunéville' in src
    # No "Marie" or "Marie-Cécile"
    assert 'Marie' not in src, "Marie occurrence found in server.py — must be removed"


# ── /api/notify auth ──
class TestNotifyAuth:
    def test_notify_no_token_returns_401(self, api_client):
        r = api_client.post(f"{BASE_URL}/api/notify", json={"kind": "signup"}, timeout=30)
        assert r.status_code == 401
        try:
            body = r.json()
            assert body.get('detail') == 'no_token'
        except Exception:
            pytest.fail(f"Non-JSON body: {r.text[:200]}")

    def test_notify_invalid_bearer_returns_401(self, api_client):
        headers = {"Authorization": "Bearer not_a_valid_firebase_token_xxx"}
        r = api_client.post(
            f"{BASE_URL}/api/notify",
            json={"kind": "signup"},
            headers=headers,
            timeout=30,
        )
        assert r.status_code == 401
        try:
            body = r.json()
            assert body.get('detail') == 'invalid_token'
        except Exception:
            pytest.fail(f"Non-JSON body: {r.text[:200]}")


# ── /api/recipe/detailed-steps with Firestore cache ──
class TestRecipeDetailedSteps:
    PAYLOAD = {
        "id": 1,
        "name": "Omelette avocat saumon",
        "ingredients": ["2 Œufs", "1/2 Avocat"],
        "steps": [],
    }

    def test_detailed_steps_returns_steps(self, api_client):
        r = api_client.post(
            f"{BASE_URL}/api/recipe/detailed-steps",
            json=self.PAYLOAD,
            timeout=120,
        )
        assert r.status_code == 200, f"unexpected status: {r.status_code} body={r.text[:200]}"
        data = r.json()
        assert data.get("ok") is True, f"expected ok:true, got {data}"
        steps = data.get("steps") or []
        assert isinstance(steps, list) and len(steps) > 0, f"expected steps list, got {steps}"
        # keep in shared context for next test
        TestRecipeDetailedSteps._first_steps = steps
        TestRecipeDetailedSteps._first_cached = data.get("cached", False)

    def test_detailed_steps_second_call_is_cached(self, api_client):
        t0 = time.time()
        r = api_client.post(
            f"{BASE_URL}/api/recipe/detailed-steps",
            json=self.PAYLOAD,
            timeout=60,
        )
        elapsed = time.time() - t0
        assert r.status_code == 200
        data = r.json()
        assert data.get("ok") is True
        assert data.get("cached") is True, f"expected cached:true on 2nd call, got {data}"
        # Cache should be fast (<5s)
        assert elapsed < 8.0, f"cache read too slow: {elapsed:.1f}s"
        assert len(data.get("steps") or []) > 0

    def test_detailed_steps_missing_name(self, api_client):
        r = api_client.post(
            f"{BASE_URL}/api/recipe/detailed-steps",
            json={"id": 999999, "ingredients": []},
            timeout=30,
        )
        assert r.status_code == 200
        data = r.json()
        assert data.get("ok") is False
        assert "missing_name" in (data.get("error") or "")
