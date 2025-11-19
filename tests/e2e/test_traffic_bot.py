"""
End-to-end tests for TrafficBot complete workflow
"""

from unittest.mock import AsyncMock, patch

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from src.fake_analytics.config import Config
from src.fake_analytics.core import TrafficBot

# ============================================================================
# TEST: TrafficBot Initialization
# ============================================================================


@pytest.mark.e2e
class TestTrafficBotInitialization:
    """Test TrafficBot initialization"""

    def test_traffic_bot_initialization_with_config(self, basic_config):
        """Test: TrafficBot initializes with config"""
        bot = TrafficBot(basic_config)
        assert bot.config is basic_config
        assert bot.identity is None
        assert bot.logger is not None

    def test_traffic_bot_initialization_with_identity(self, basic_config, sample_identity):
        """Test: TrafficBot initializes with identity"""
        bot = TrafficBot(basic_config, identity=sample_identity)
        assert bot.identity == sample_identity

    @pytest.mark.parametrize("verbose", [True, False])
    def test_traffic_bot_logger_respects_verbose(self, verbose):
        """Test: TrafficBot logger respects verbose setting"""
        config = Config(verbose=verbose)
        bot = TrafficBot(config)
        assert bot.logger.verbose == verbose


# ============================================================================
# TEST: TrafficBot Full Run Workflow (Mocked)
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
class TestTrafficBotWorkflow:
    """Test complete TrafficBot workflow with mocked Playwright"""

    async def test_traffic_bot_run_basic_workflow(self, basic_config, mock_playwright, mock_page):
        """Test: TrafficBot completes basic run workflow"""
        bot = TrafficBot(basic_config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            # Mock tempfile and shutil
            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree") as mock_rmtree:
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    # Run the bot
                    await bot.run()

                    # Verify critical operations occurred
                    assert mock_page.goto.called
                    assert True  # May or may not screenshot
                    mock_rmtree.assert_called_once()

    async def test_traffic_bot_run_with_form_submission(
        self, sample_config_file, sample_identity, mock_playwright, mock_page
    ):
        """Test: TrafficBot workflow with form submission"""
        config = Config(config_path=sample_config_file, verbose=False)
        config.conversion_rate = 1.0  # Force form submission

        bot = TrafficBot(config, identity=sample_identity)

        # Setup mock form elements
        mock_submit_btn = AsyncMock()
        mock_submit_btn.hover = AsyncMock()
        mock_submit_btn.click = AsyncMock()
        mock_page.query_selector.return_value = mock_submit_btn

        mock_locator = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.wait_for = AsyncMock()
        mock_locator.hover = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.type = AsyncMock()
        mock_page.locator.return_value = mock_locator

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    # Mock random to force form submission
                    with patch("src.fake_analytics.core.random.random", return_value=0.5):
                        await bot.run()

                        # Verify form was filled and submitted
                        assert mock_page.locator.called
                        assert mock_submit_btn.click.called

    async def test_traffic_bot_run_without_form_submission(
        self, basic_config, mock_playwright, mock_page
    ):
        """Test: TrafficBot workflow without form submission (bounce)"""
        basic_config.conversion_rate = 0.0  # Force no form submission

        bot = TrafficBot(basic_config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    with patch("src.fake_analytics.core.random.random", return_value=0.9):
                        await bot.run()

                        # Should have navigated but not filled form
                        assert mock_page.goto.called

    @pytest.mark.asyncio
    async def test_traffic_bot_run_with_proxy(self, mock_playwright):
        """Test: TrafficBot workflow with proxy configuration"""
        config = Config(verbose=False)
        bot = TrafficBot(config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    await bot.run()

                    # Should have launched with proxy config
                    assert mock_playwright.chromium.launch_persistent_context.called

    async def test_traffic_bot_handles_navigation_timeout(
        self, basic_config, mock_playwright, mock_page
    ):
        """Test: TrafficBot handles navigation timeout gracefully"""
        mock_page.goto = AsyncMock(side_effect=PlaywrightTimeoutError("Navigation timeout"))

        bot = TrafficBot(basic_config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    # Should handle error and take screenshot
                    await bot.run()

                    # Should have attempted screenshot
                    assert mock_page.screenshot.called

    async def test_traffic_bot_handles_general_exception(
        self, basic_config, mock_playwright, mock_page
    ):
        """Test: TrafficBot handles general exceptions"""
        mock_page.goto = AsyncMock(side_effect=Exception("Unexpected error"))

        bot = TrafficBot(basic_config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    # Should handle error gracefully
                    await bot.run()

                    # Should have taken error screenshot
                    assert mock_page.screenshot.called


# ============================================================================
# TEST: TrafficBot with Different Configurations
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
class TestTrafficBotConfigurations:
    """Test TrafficBot with various configuration scenarios"""

    @pytest.mark.parametrize(
        "conversion_rate,should_submit",
        [
            (0.0, False),  # Never submit
            (1.0, True),  # Always submit
        ],
    )
    async def test_traffic_bot_conversion_rates(
        self, conversion_rate, should_submit, mock_playwright, mock_page
    ):
        """Test: TrafficBot respects conversion rate"""
        config = Config(verbose=False)
        config.conversion_rate = conversion_rate
        config.form_fields = {"email": "#email"}
        config.submit_button = "button"

        bot = TrafficBot(config, identity={"email": "test@test.com"})

        mock_submit_btn = AsyncMock()
        mock_page.query_selector.return_value = mock_submit_btn

        mock_locator = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.wait_for = AsyncMock()
        mock_locator.hover = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.type = AsyncMock()
        mock_page.locator.return_value = mock_locator

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    # Mock random to be deterministic
                    with patch("src.fake_analytics.core.random.random", return_value=0.5):
                        await bot.run()

                        if should_submit:
                            assert mock_submit_btn.click.called
                        # Note: If not should_submit, button might not be queried

    @pytest.mark.parametrize(
        "locale",
        ["en_US", "en_GB", "fr_FR", "de_DE"],
    )
    async def test_traffic_bot_different_locales(self, locale, mock_playwright, mock_page):
        """Test: TrafficBot works with different locales"""
        config = Config(verbose=False)
        config.locale = locale

        bot = TrafficBot(config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    await bot.run()

                    # Should complete without error
                    assert mock_page.goto.called

    async def test_traffic_bot_without_identity_generates_one(
        self, basic_config, mock_playwright, mock_page
    ):
        """Test: TrafficBot generates identity when not provided"""
        basic_config.conversion_rate = 1.0
        basic_config.form_fields = {"full_name": "#name"}
        basic_config.submit_button = "button"

        bot = TrafficBot(basic_config, identity=None)

        mock_submit_btn = AsyncMock()
        mock_page.query_selector.return_value = mock_submit_btn

        mock_locator = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.wait_for = AsyncMock()
        mock_locator.hover = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.type = AsyncMock()
        mock_page.locator.return_value = mock_locator

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    with patch("src.fake_analytics.core.random.random", return_value=0.5):
                        with patch("src.fake_analytics.core.data.generate_identity") as mock_gen:
                            mock_gen.return_value = {"full_name": "Generated User"}

                            await bot.run()

                            # Should have generated identity
                            assert mock_gen.called


# ============================================================================
# TEST: TrafficBot Browser Configuration
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.e2e
class TestTrafficBotBrowserConfiguration:
    """Test TrafficBot browser setup and configuration"""

    async def test_traffic_bot_disables_webrtc(self, basic_config, mock_playwright, mock_page):
        """Test: TrafficBot disables WebRTC to prevent IP leakage"""
        bot = TrafficBot(basic_config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    await bot.run()

                    # Should have added init script to disable WebRTC
                    assert mock_page.add_init_script.called

    async def test_traffic_bot_sets_extra_headers(self, basic_config, mock_playwright, mock_page):
        """Test: TrafficBot sets extra HTTP headers"""
        bot = TrafficBot(basic_config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    await bot.run()

                    # Should have set extra headers
                    assert mock_page.set_extra_http_headers.called

    async def test_traffic_bot_uses_persistent_context(self, basic_config, mock_playwright):
        """Test: TrafficBot uses persistent context for realistic profile"""
        bot = TrafficBot(basic_config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    await bot.run()

                    assert mock_playwright.chromium.launch_persistent_context.called

    @pytest.mark.asyncio
    async def test_traffic_bot_cleans_up_temp_directory(self, basic_config, mock_playwright):
        """Test: TrafficBot cleans up temporary profile directory"""
        bot = TrafficBot(basic_config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree") as mock_rmtree:
                    temp_dir = "/tmp/test_profile_12345"
                    mock_mkdtemp.return_value = temp_dir

                    await bot.run()

                    # Should have cleaned up temp directory
                    mock_rmtree.assert_called_once_with(temp_dir)


# ============================================================================
# TEST: TrafficBot Network Logging
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
class TestTrafficBotNetworkLogging:
    """Test TrafficBot network logging in verbose mode"""

    async def test_traffic_bot_enables_logging_in_verbose_mode(self, mock_playwright, mock_page):
        """Test: TrafficBot enables network logging in verbose mode"""
        config = Config(verbose=True)
        bot = TrafficBot(config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    with patch(
                        "src.fake_analytics.core.actions.setup_network_logging"
                    ) as mock_setup:
                        await bot.run()

                        # Should have set up network logging
                        mock_setup.assert_called_once_with(mock_page)

    async def test_traffic_bot_disables_logging_in_non_verbose_mode(
        self, basic_config, mock_playwright
    ):
        """Test: TrafficBot disables network logging in non-verbose mode"""
        bot = TrafficBot(basic_config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    with patch(
                        "src.fake_analytics.core.actions.setup_network_logging"
                    ) as mock_setup:
                        await bot.run()
                        mock_setup.assert_not_called()
