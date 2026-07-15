"""Backend tests for the hardcoded recipe details feature and /api/app payload.

Covers this iteration's changes:
- /api/app serves ~2.9MB HTML including 'kpRecipeDetailsData' and 'KP_RECIPE_DETAILS' with ~474 entries
- day-modal-open desktop popup class present in HTML
- Protein target line format present in HTML (cible XX–XX g)
- /api/recipe/detailed-steps still works as fallback for custom recipes
"""
import os
import re
import pytest
import requests

BASE_URL = os.environ.get(
    "EXPO_BACKEND_URL",
    os.environ.get(
        "EXPO_PUBLIC_BACKEND_URL",
        "https://body-metrics-bug.preview.emergentagent.com",
    ),
).rstrip("/")


@pytest.fixture(scope="module")
def app_html():
    r = requests.get(f"{BASE_URL}/api/app", timeout=60)
    assert r.status_code == 200, f"/api/app returned {r.status_code}"
    return r.text


class TestAppHtmlPayload:
    def test_app_status_200_and_size(self, app_html):
        # ~2.9MB expected
        size_mb = len(app_html.encode("utf-8")) / 1_000_000
        assert 2.5 <= size_mb <= 3.5, f"unexpected /api/app size: {size_mb:.2f}MB"

    def test_kp_recipe_details_data_script_present(self, app_html):
        assert 'id="kpRecipeDetailsData"' in app_html or "id='kpRecipeDetailsData'" in app_html, \
            "kpRecipeDetailsData script tag missing"

    def test_window_kp_recipe_details_defined(self, app_html):
        assert "KP_RECIPE_DETAILS" in app_html, "window.KP_RECIPE_DETAILS not found"

    def test_recipe_details_entry_count_near_474(self, app_html):
        # Extract the JSON script block; count top-level keys heuristically
        m = re.search(
            r'<script[^>]+id=["\']kpRecipeDetailsData["\'][^>]*>(.*?)</script>',
            app_html,
            re.DOTALL,
        )
        assert m, "kpRecipeDetailsData script block not extractable"
        payload = m.group(1).strip()
        # Try JSON parse first
        import json
        try:
            data = json.loads(payload)
            keys = len(data)
        except Exception:
            # Fallback: count "steps": arrays
            keys = payload.count('"steps"')
        assert 400 <= keys <= 600, f"expected ~474 recipe detail entries, got {keys}"

    def test_day_modal_open_desktop_class_present(self, app_html):
        assert "day-modal-open" in app_html, "desktop popup class 'day-modal-open' missing"
        assert "daySheet" in app_html, "#daySheet element missing"

    def test_protein_target_text_present(self, app_html):
        # French label 'cible' + 'g/kg' pattern from the review request
        assert "g/kg" in app_html, "protein target 'g/kg' text not found"
        # At least one 1,2 or 1,5 g/kg reference
        assert ("1,2" in app_html and "1,5" in app_html), "1.2-1.5 g/kg range not in HTML"

    def test_no_detailed_steps_call_hint_for_integrated_recipes(self, app_html):
        # openRecipe should reference KP_RECIPE_DETAILS lookup before calling network
        assert "KP_RECIPE_DETAILS" in app_html
        # Presence of the branding string for pre-embedded details
        assert "Préparation détaillée pas-à-pas" in app_html, \
            "expected marker '✨ Préparation détaillée pas-à-pas' missing"


class TestDetailedStepsFallback:
    """Fallback path still works for custom recipes (not in KP_RECIPE_DETAILS)."""
    def test_detailed_steps_custom_recipe(self):
        payload = {
            "name": "Test poulet rôti",
            "ingredients": ["200g poulet"],
            "id": "test_qa_1",
        }
        r = requests.post(
            f"{BASE_URL}/api/recipe/detailed-steps",
            json=payload,
            timeout=90,
        )
        assert r.status_code == 200, f"unexpected status: {r.status_code} body={r.text[:200]}"
        data = r.json()
        assert data.get("ok") is True, f"expected ok:true, got {data}"
        steps = data.get("steps") or []
        assert isinstance(steps, list) and len(steps) >= 3, \
            f"expected >=3 steps, got {len(steps)}: {steps}"
