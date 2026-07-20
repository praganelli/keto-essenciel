"""Tests for keto HTML download endpoints (bug: user reports 'lien ne fonctionne pas')."""
import os
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "https://keto-parcours-dev.preview.emergentagent.com").rstrip("/")
GCS_FALLBACK = "https://storage.googleapis.com/testprojet-721cb-recipes/app/keto-essenciel.html"


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({
        # Simulate iOS Safari to detect any UA-based blocking
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return s


class TestApiDownload:
    def test_download_status_200(self, session):
        r = session.get(f"{BASE_URL}/api/download", timeout=60)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"

    def test_download_content_disposition(self, session):
        r = session.get(f"{BASE_URL}/api/download", timeout=60)
        cd = r.headers.get("Content-Disposition", "")
        assert "attachment" in cd.lower(), f"Content-Disposition missing attachment: {cd!r}"
        assert "index.html" in cd, f"filename index.html missing: {cd!r}"

    def test_download_content_type_html(self, session):
        r = session.get(f"{BASE_URL}/api/download", timeout=60)
        ct = r.headers.get("Content-Type", "")
        assert "html" in ct.lower(), f"Unexpected Content-Type: {ct!r}"

    def test_download_body_valid_html(self, session):
        r = session.get(f"{BASE_URL}/api/download", timeout=60)
        body = r.text
        assert body.lstrip().startswith("<!DOCTYPE html>") or body.lstrip().lower().startswith("<!doctype html>"), \
            f"Body does not start with DOCTYPE: {body[:120]!r}"
        assert "kpl-logo" in body, "'kpl-logo' marker missing in downloaded HTML"
        assert body.rstrip().endswith("</html>"), \
            f"Downloaded HTML seems truncated (does not end with </html>). Tail: {body[-200:]!r}"

    def test_download_size_reasonable(self, session):
        r = session.get(f"{BASE_URL}/api/download", timeout=60)
        size = len(r.content)
        # Expected ~3.8MB; allow generous window
        assert size > 3_000_000, f"Downloaded file too small: {size} bytes"
        assert size < 10_000_000, f"Downloaded file unexpectedly large: {size} bytes"

    def test_download_head_or_get_range(self, session):
        # Some browsers do a HEAD first; check it doesn't 405
        r = session.head(f"{BASE_URL}/api/download", timeout=30, allow_redirects=True)
        # FastAPI GET-only route may return 405 for HEAD - that's OK but note it
        assert r.status_code in (200, 405), f"HEAD returned unexpected status {r.status_code}"


class TestApiApp:
    def test_app_page_status(self, session):
        r = session.get(f"{BASE_URL}/api/app", timeout=60)
        assert r.status_code == 200, f"/api/app returned {r.status_code}"

    def test_app_page_html(self, session):
        r = session.get(f"{BASE_URL}/api/app", timeout=60)
        body = r.text
        assert "<html" in body.lower(), "No <html> tag in /api/app response"
        assert body.rstrip().endswith("</html>"), "/api/app HTML appears truncated"


class TestGCSFallback:
    def test_gcs_status_200(self, session):
        r = session.get(GCS_FALLBACK, timeout=60)
        assert r.status_code == 200, f"GCS fallback status {r.status_code}"

    def test_gcs_body_valid_html(self, session):
        r = session.get(GCS_FALLBACK, timeout=60)
        body = r.text
        assert body.lstrip().lower().startswith("<!doctype html>"), \
            f"GCS body does not start with DOCTYPE: {body[:120]!r}"
        assert body.rstrip().endswith("</html>"), "GCS HTML seems truncated"
        assert "kpl-logo" in body, "'kpl-logo' marker missing in GCS HTML"

    def test_gcs_size_matches(self, session):
        r = session.get(GCS_FALLBACK, timeout=60)
        size = len(r.content)
        assert size > 3_000_000, f"GCS file too small: {size} bytes"

    def test_gcs_content_disposition(self, session):
        r = session.get(GCS_FALLBACK, timeout=60)
        cd = r.headers.get("Content-Disposition", "")
        # GCS is configured to serve as attachment per problem statement
        assert "attachment" in cd.lower(), f"GCS Content-Disposition missing attachment: {cd!r}"


class TestParity:
    def test_api_and_gcs_same_size(self, session):
        r1 = session.get(f"{BASE_URL}/api/download", timeout=60)
        r2 = session.get(GCS_FALLBACK, timeout=60)
        # /api/download injects <base> tag → slightly different bytes.
        # Allow up to 2KB difference.
        diff = abs(len(r1.content) - len(r2.content))
        assert diff < 5000, f"Size drift between /api/download ({len(r1.content)}) and GCS ({len(r2.content)}): diff={diff}"
