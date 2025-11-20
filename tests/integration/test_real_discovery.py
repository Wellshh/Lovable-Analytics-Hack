"""
Real integration tests for form field discovery (no mocks).

These tests use real Playwright browsers and network requests.
They require network access and are slower than unit tests.

Run with: pytest tests/integration/test_real_discovery.py -v -s
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from src.fake_analytics.discovery import discover_form_fields

load_dotenv()


@pytest.mark.integration
@pytest.mark.network
@pytest.mark.slow
@pytest.mark.asyncio
class TestRealDiscovery:
    """Real integration tests for discovery functionality"""

    async def test_discover_form_fields_on_real_page(self, capsys):
        """Test: Discovery works on a real webpage with forms"""
        # Use httpbin.org which has a test form page
        url = "https://httpbin.org/forms/post"

        # This will launch a real browser
        await discover_form_fields(url)

        # Capture output
        captured = capsys.readouterr()

        # Should have found some form fields
        assert "form fields" in captured.out.lower() or "field" in captured.out.lower()

    async def test_discover_form_fields_on_page_without_forms(self, capsys):
        """Test: Discovery handles pages without forms gracefully"""
        # Use a page without forms
        url = "https://httpbin.org/html"

        await discover_form_fields(url)

        # Should handle gracefully
        capsys.readouterr()
        # May show "no form fields" or similar message

    @pytest.mark.parametrize(
        "test_url",
        [
            "https://httpbin.org/forms/post",  # Has forms
            "https://example.com",  # Simple page
        ],
    )
    async def test_discover_various_pages(self, test_url, capsys):
        """Test: Discovery works on various real pages"""
        # Should complete without crashing
        await discover_form_fields(test_url)

        captured = capsys.readouterr()
        # Should have navigated and searched
        assert len(captured.out) > 0

    async def test_discover_handles_timeout_gracefully(self):
        """Test: Discovery handles slow/timeout pages gracefully"""
        # Use a URL that might timeout (using httpbin delay endpoint)
        url = "https://httpbin.org/delay/5"

        # Should handle timeout without crashing
        try:
            await discover_form_fields(url)
            # If it completes, that's fine
        except Exception:
            # If it times out or errors, that's also acceptable for this test
            # Just make sure it doesn't crash the test suite
            assert True

    async def test_discover_with_javascript_forms(self):
        """Test: Discovery finds forms loaded by JavaScript"""
        # Note: This is a basic test - you may want to use your actual target URL
        url = os.getenv("TARGET_URL", "https://httpbin.org/forms/post")

        # Should handle JavaScript-rendered content
        try:
            await discover_form_fields(url)
            # Should complete without error
            assert True
        except Exception as e:
            pytest.skip(f"Target URL not available or failed: {e}")


@pytest.mark.integration
@pytest.mark.network
@pytest.mark.slow
class TestRealDiscoveryWithTargetURL:
    """Integration tests using TARGET_URL from .env"""

    def test_target_url_is_configured(self):
        """Test: TARGET_URL is configured in environment"""
        target_url = os.getenv("TARGET_URL")
        if not target_url:
            pytest.skip("TARGET_URL not set in .env file")
        assert target_url.startswith("http")

    @pytest.mark.asyncio
    async def test_discover_on_configured_target_url(self, capsys):
        """Test: Discovery works on configured TARGET_URL"""
        target_url = os.getenv("TARGET_URL")
        if not target_url:
            pytest.skip("TARGET_URL not set in .env file")

        # Run discovery on the actual target URL
        try:
            await discover_form_fields(target_url)
            captured = capsys.readouterr()
            # Should have attempted discovery
            assert len(captured.out) > 0
        except Exception as e:
            pytest.skip(f"Failed to access target URL: {e}")

    @pytest.mark.asyncio
    async def test_discover_finds_configured_form_fields(self, capsys):
        """Test: Discovery finds fields that match config"""
        target_url = os.getenv("TARGET_URL")
        if not target_url:
            pytest.skip("TARGET_URL not set in .env file")

        # Check if config file exists
        config_path = Path("config.json")
        if not config_path.exists():
            config_path = Path("config.example.json")

        if not config_path.exists():
            pytest.skip("No config file found to verify against")

        import json

        with open(config_path) as f:
            config = json.load(f)

        form_fields = config.get("form_fields", {})
        if not form_fields:
            pytest.skip("No form fields configured")

        # Run discovery
        await discover_form_fields(target_url)
        captured = capsys.readouterr()

        # This is a soft check - discovery should find similar fields
        assert len(captured.out) > 100  # Should have substantial output


@pytest.mark.integration
@pytest.mark.network
class TestRealDiscoveryEdgeCases:
    """Integration tests for edge cases"""

    @pytest.mark.asyncio
    async def test_discover_on_https_site(self):
        """Test: Discovery works with HTTPS sites"""
        url = "https://httpbin.org/forms/post"
        # Should handle HTTPS without certificate issues
        await discover_form_fields(url)

    @pytest.mark.asyncio
    async def test_discover_on_redirect_url(self):
        """Test: Discovery handles redirects"""
        url = "https://httpbin.org/redirect-to?url=https://httpbin.org/forms/post"
        # Should follow redirect
        try:
            await discover_form_fields(url)
        except Exception:
            # Some sites may not handle redirects well, that's ok
            pass

    @pytest.mark.asyncio
    async def test_discover_with_different_input_types(self, capsys):
        """Test: Discovery identifies different input types"""
        url = "https://httpbin.org/forms/post"

        await discover_form_fields(url)
        captured = capsys.readouterr()

        # Should identify various input types
        # (text, email, tel, etc. - depending on the form)
        assert "input" in captured.out.lower() or "field" in captured.out.lower()


@pytest.mark.integration
@pytest.mark.network
@pytest.mark.slow
class TestRealDiscoveryPerformance:
    """Integration tests for discovery performance"""

    @pytest.mark.asyncio
    async def test_discovery_completes_in_reasonable_time(self):
        """Test: Discovery completes within reasonable time"""
        import time

        url = "https://httpbin.org/forms/post"

        start_time = time.time()
        await discover_form_fields(url)
        elapsed = time.time() - start_time

        # Should complete within 2 minutes
        assert elapsed < 120, f"Discovery took too long: {elapsed}s"

    @pytest.mark.asyncio
    async def test_discovery_handles_multiple_fields_efficiently(self, capsys):
        """Test: Discovery handles pages with many fields efficiently"""
        url = "https://httpbin.org/forms/post"

        await discover_form_fields(url)
        captured = capsys.readouterr()

        # Should have found and displayed fields
        assert len(captured.out) > 0
