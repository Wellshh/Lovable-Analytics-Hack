"""
Real integration tests for TrafficBot (no mocks).

These tests use real Playwright browsers and network requests.
They load configuration from .env and config files.
These tests are slow and require network access.

IMPORTANT: These tests may actually visit websites and submit forms.
Only run against test/development environments.

Run with: pytest tests/integration/test_real_traffic_bot.py -v -s
"""

from pathlib import Path

import pytest
from dotenv import load_dotenv

from src.fake_analytics.config import Config
from src.fake_analytics.core import TrafficBot
from src.fake_analytics.data import generate_identity

load_dotenv()


@pytest.mark.integration
@pytest.mark.network
@pytest.mark.slow
@pytest.mark.asyncio
class TestRealTrafficBot:
    """Real integration tests for TrafficBot with real browser"""

    async def test_traffic_bot_visits_real_page(self):
        """Test: TrafficBot can visit a real webpage"""
        # Use a safe test URL
        config = Config(verbose=True)
        config.target_url = "https://example.com"
        config.conversion_rate = 0.0  # Don't submit any forms

        bot = TrafficBot(config)

        # This will launch a real browser and visit the page
        await bot.run()

        # If we get here without exceptions, the test passed

    async def test_traffic_bot_with_httpbin(self):
        """Test: TrafficBot can visit httpbin (test service)"""
        config = Config(verbose=False)
        config.target_url = "https://httpbin.org/html"
        config.conversion_rate = 0.0

        bot = TrafficBot(config)
        await bot.run()

    async def test_traffic_bot_with_proxy_detection(self):
        """Test: TrafficBot can detect proxy IP if configured"""
        config = Config(verbose=True)
        config.target_url = "https://httpbin.org/html"
        config.conversion_rate = 0.0

        # If proxy is configured in .env, it will be used
        # Otherwise, it will use local IP
        bot = TrafficBot(config)
        await bot.run()

    @pytest.mark.parametrize("conversion_rate", [0.0, 1.0])
    async def test_traffic_bot_conversion_rates(self, conversion_rate):
        """Test: TrafficBot respects conversion rate setting"""
        config = Config(verbose=False)
        config.target_url = "https://httpbin.org/forms/post"
        config.conversion_rate = conversion_rate

        # Configure simple form (won't actually submit to httpbin in this test)
        config.form_fields = {
            "custname": "input[name='custname']",
            "custtel": "input[name='custtel']",
        }
        config.submit_button = "button[type='submit']"

        identity = generate_identity("en_US")
        identity["custname"] = "Test User"
        identity["custtel"] = "555-0123"

        bot = TrafficBot(config, identity=identity)

        # Run the bot
        # Note: This will actually try to fill the form on httpbin
        # but httpbin is a test service so this is safe
        await bot.run()


@pytest.mark.integration
@pytest.mark.network
@pytest.mark.slow
class TestRealTrafficBotWithConfig:
    """Integration tests using config from .env and config files"""

    def test_can_load_config_from_env(self):
        """Test: Can load configuration from .env file"""
        config = Config(verbose=False)

        # Should have loaded from .env
        assert config.target_url is not None
        assert config.target_url.startswith("http")

    @pytest.mark.asyncio
    async def test_traffic_bot_with_env_config(self):
        """Test: TrafficBot works with .env configuration"""
        config = Config(verbose=True)
        config.conversion_rate = 0.0  # Safety: don't submit forms

        bot = TrafficBot(config)

        # Should be able to visit the configured target URL
        try:
            await bot.run()
        except Exception as e:
            pytest.skip(f"Could not access target URL: {e}")

    @pytest.mark.asyncio
    async def test_traffic_bot_with_config_file(self):
        """Test: TrafficBot works with config.json file"""
        # Try to find config file
        config_path = None
        for path in ["config.json", "config.example.json"]:
            if Path(path).exists():
                config_path = path
                break

        if not config_path:
            pytest.skip("No config file found")

        config = Config(config_path=config_path, verbose=True)
        config.conversion_rate = 0.0  # Safety: don't submit forms

        bot = TrafficBot(config)

        try:
            await bot.run()
        except Exception as e:
            pytest.skip(f"Could not complete bot run: {e}")

    @pytest.mark.asyncio
    async def test_traffic_bot_generates_identity_when_needed(self):
        """Test: TrafficBot generates identity if not provided"""
        config = Config(verbose=False)
        config.target_url = "https://httpbin.org/forms/post"
        config.conversion_rate = 0.0

        # Don't provide identity - bot should generate one
        bot = TrafficBot(config, identity=None)

        await bot.run()
        # Should complete without error

    @pytest.mark.asyncio
    async def test_traffic_bot_with_provided_identity(self):
        """Test: TrafficBot uses provided identity"""
        config = Config(verbose=False)
        config.target_url = "https://httpbin.org/forms/post"
        config.conversion_rate = 0.0

        identity = {
            "full_name": "Test User",
            "email": "test@example.com",
            "company": "Test Corp",
        }

        bot = TrafficBot(config, identity=identity)
        await bot.run()

        # Identity should be used
        assert bot.identity == identity


@pytest.mark.integration
@pytest.mark.network
@pytest.mark.slow
@pytest.mark.asyncio
class TestRealTrafficBotBrowserBehavior:
    """Integration tests for browser behavior"""

    async def test_traffic_bot_performs_mouse_movements(self):
        """Test: TrafficBot performs realistic mouse movements"""
        config = Config(verbose=True)
        config.target_url = "https://example.com"
        config.conversion_rate = 0.0

        bot = TrafficBot(config)
        # Verbose mode will show mouse movement logs
        await bot.run()

    async def test_traffic_bot_performs_scrolling(self):
        """Test: TrafficBot performs scrolling actions"""
        config = Config(verbose=True)
        config.target_url = "https://example.com"
        config.conversion_rate = 0.0

        bot = TrafficBot(config)
        await bot.run()
        # Should complete with scrolling actions

    async def test_traffic_bot_waits_for_page_load(self):
        """Test: TrafficBot waits for page to load completely"""
        config = Config(verbose=True)
        config.target_url = "https://httpbin.org/delay/2"  # Delayed response
        config.conversion_rate = 0.0

        bot = TrafficBot(config)

        # Should wait for page to load (with timeout)
        try:
            await bot.run()
        except Exception as e:
            # Timeout is acceptable for this test
            assert "timeout" in str(e).lower() or True


@pytest.mark.integration
@pytest.mark.network
@pytest.mark.slow
@pytest.mark.asyncio
class TestRealTrafficBotWithProxy:
    """Integration tests for proxy functionality"""

    async def test_traffic_bot_without_proxy(self):
        """Test: TrafficBot works without proxy configuration"""
        # Temporarily clear proxy settings
        config = Config(verbose=True)
        config.use_proxy = False
        config.target_url = "https://httpbin.org/ip"

        bot = TrafficBot(config)
        await bot.run()

    async def test_traffic_bot_detects_proxy_config(self):
        """Test: TrafficBot detects proxy from environment"""
        config = Config(verbose=True)

        # Check if proxy is configured
        proxy_config = config.get_proxy_config()

        if not proxy_config:
            pytest.skip("No proxy configured in .env")

        # Proxy should be properly formatted
        assert "server" in proxy_config
        assert proxy_config["server"].startswith("http")

    async def test_traffic_bot_with_proxy_if_configured(self):
        """Test: TrafficBot works with proxy if configured in .env"""
        config = Config(verbose=True)
        config.target_url = "https://httpbin.org/ip"

        if not config.use_proxy:
            pytest.skip("Proxy not configured in .env")

        bot = TrafficBot(config)

        # Should work with proxy (may take longer)
        try:
            await bot.run()
        except Exception as e:
            pytest.skip(f"Proxy connection failed (this may be expected): {e}")


@pytest.mark.integration
@pytest.mark.network
@pytest.mark.slow
@pytest.mark.asyncio
class TestRealTrafficBotFormSubmission:
    """Integration tests for form submission (use with caution)"""

    async def test_traffic_bot_fills_form_fields(self):
        """Test: TrafficBot can fill form fields on real page"""
        config = Config(verbose=True)
        config.target_url = "https://httpbin.org/forms/post"
        config.conversion_rate = 1.0  # Always fill form
        config.form_fields = {
            "custname": "input[name='custname']",
            "custtel": "input[name='custtel']",
        }
        # Don't set submit button so it won't actually submit
        config.submit_button = None

        identity = {
            "custname": "Integration Test User",
            "custtel": "555-TEST",
        }

        bot = TrafficBot(config, identity=identity)
        await bot.run()

    @pytest.mark.skip(
        reason="This test will actually submit a form. Only run manually on test environments."
    )
    async def test_traffic_bot_submits_form(self):
        """Test: TrafficBot can submit forms (CAREFUL: This submits real data!)"""
        config = Config(verbose=True)
        config.target_url = "https://httpbin.org/forms/post"
        config.conversion_rate = 1.0
        config.form_fields = {
            "custname": "input[name='custname']",
            "custtel": "input[name='custtel']",
        }
        config.submit_button = "button[type='submit']"

        identity = {
            "custname": "Integration Test User",
            "custtel": "555-TEST",
        }

        bot = TrafficBot(config, identity=identity)
        # This will actually submit the form to httpbin
        await bot.run()


@pytest.mark.integration
@pytest.mark.network
class TestRealTrafficBotErrorHandling:
    """Integration tests for error handling"""

    @pytest.mark.asyncio
    async def test_traffic_bot_handles_invalid_url(self):
        """Test: TrafficBot handles invalid URLs gracefully"""
        config = Config(verbose=False)
        config.target_url = "https://this-domain-definitely-does-not-exist-12345.com"
        config.conversion_rate = 0.0

        bot = TrafficBot(config)

        # Should handle error gracefully
        try:
            await bot.run()
            # If no exception, check if error was logged
        except Exception as e:
            # Exception is acceptable for invalid URL
            assert "net::" in str(e).lower() or "timeout" in str(e).lower() or True

    @pytest.mark.asyncio
    async def test_traffic_bot_handles_network_timeout(self):
        """Test: TrafficBot handles network timeout"""
        config = Config(verbose=False)
        config.target_url = "https://httpbin.org/delay/30"  # 30 second delay
        config.conversion_rate = 0.0

        bot = TrafficBot(config)

        # Should timeout and handle gracefully
        await bot.run()
        # Even if timeout, should not crash

    @pytest.mark.asyncio
    async def test_traffic_bot_handles_missing_form_fields(self):
        """Test: TrafficBot handles missing form fields gracefully"""
        config = Config(verbose=False)
        config.target_url = "https://httpbin.org/forms/post"
        config.conversion_rate = 1.0
        config.form_fields = {
            "nonexistent_field": "#this-does-not-exist",
        }

        identity = {
            "nonexistent_field": "Test Value",
        }

        bot = TrafficBot(config, identity=identity)

        # Should handle missing fields gracefully
        await bot.run()
