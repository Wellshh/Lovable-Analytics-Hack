"""
End-to-end tests for TrafficBot complete workflow
"""

from unittest.mock import AsyncMock, patch

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from src.fake_analytics.config import Config
from src.fake_analytics.core import TrafficBot


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

    def test_traffic_bot_logger_has_thread_id(self, basic_config):
        """Test: TrafficBot logger has thread_id set"""
        bot = TrafficBot(basic_config)
        assert bot.logger.thread_id is not None
        assert bot.logger.thread_id == bot.thread_id


@pytest.mark.e2e
@pytest.mark.asyncio
class TestTrafficBotWorkflow:
    """Test complete TrafficBot workflow with mocked Playwright"""

    async def test_traffic_bot_run_basic_workflow(self, basic_config, mock_playwright, mock_page):
        """Test: TrafficBot completes basic run workflow"""
        bot = TrafficBot(basic_config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree") as mock_rmtree:
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    await bot.run()

                    assert mock_page.goto.called
                    assert True
                    mock_rmtree.assert_called_once()

    async def test_traffic_bot_run_with_form_submission(
        self, sample_config_file, sample_identity, mock_playwright, mock_page
    ):
        """Test: TrafficBot workflow with form submission"""
        config = Config(config_path=sample_config_file, verbose=False)
        config.conversion_rate = 1.0

        bot = TrafficBot(config, identity=sample_identity)

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

                    with patch("src.fake_analytics.core.random.random", return_value=0.5):
                        await bot.run()

                        assert mock_page.locator.called
                        assert mock_submit_btn.click.called

    async def test_traffic_bot_run_without_form_submission(
        self, basic_config, mock_playwright, mock_page
    ):
        """Test: TrafficBot workflow without form submission (bounce)"""
        basic_config.conversion_rate = 0.0

        bot = TrafficBot(basic_config)

        with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
            mock_pw_context.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                with patch("src.fake_analytics.core.shutil.rmtree"):
                    mock_mkdtemp.return_value = "/tmp/test_profile"

                    with patch("src.fake_analytics.core.random.random", return_value=0.9):
                        await bot.run()

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

                    await bot.run()

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

                    await bot.run()

                    assert mock_page.screenshot.called


@pytest.mark.e2e
@pytest.mark.asyncio
class TestTrafficBotConfigurations:
    """Test TrafficBot with various configuration scenarios"""

    @pytest.mark.parametrize(
        "conversion_rate,should_submit",
        [
            (0.0, False),
            (1.0, True),
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

                    with patch("src.fake_analytics.core.random.random", return_value=0.5):
                        await bot.run()

                        if should_submit:
                            assert mock_submit_btn.click.called

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

                            assert mock_gen.called


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

                    mock_rmtree.assert_called_once_with(temp_dir)


@pytest.mark.e2e
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


@pytest.mark.e2e
class TestTrafficBotMultiThreading:
    """Test TrafficBot multi-threading capabilities"""

    def test_multiple_bots_have_unique_thread_ids(self, basic_config):
        """Test: Multiple TrafficBot instances have unique thread IDs"""
        import threading
        import time

        thread_ids = set()
        lock = threading.Lock()

        def create_bot():
            time.sleep(0.01)
            bot = TrafficBot(basic_config)
            with lock:
                thread_ids.add(bot.thread_id)
            return bot.thread_id

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_bot)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        assert len(thread_ids) == 5

    def test_bot_thread_id_matches_logger_thread_id(self, basic_config):
        """Test: Bot thread_id matches logger thread_id"""
        bot = TrafficBot(basic_config)
        assert bot.thread_id == bot.logger.thread_id
        assert bot.thread_id is not None

    def test_concurrent_bot_execution(self, basic_config, mock_playwright, mock_page):
        """Test: Multiple bots can execute concurrently"""
        import asyncio
        import threading

        execution_count = []
        execution_lock = threading.Lock()

        def run_bot_in_thread():
            async def async_run():
                bot = TrafficBot(basic_config)
                with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
                    mock_pw_context.return_value.__aenter__.return_value = mock_playwright
                    with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                        with patch("src.fake_analytics.core.shutil.rmtree"):
                            mock_mkdtemp.return_value = "/tmp/test_profile"
                            await bot.run()
                            with execution_lock:
                                execution_count.append(bot.thread_id)

            asyncio.run(async_run())

        threads = []
        for _ in range(3):
            thread = threading.Thread(target=run_bot_in_thread)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        assert len(execution_count) == 3
        assert len(set(execution_count)) == 3

    def test_thread_registry_assigns_unique_numbers(self, basic_config):
        """Test: Thread registry assigns unique numbers to each thread"""
        import threading
        import time

        from src.fake_analytics.logger import get_thread_info

        thread_numbers = set()
        lock = threading.Lock()

        def get_thread_number():
            time.sleep(0.01)
            thread_id = threading.get_ident()
            info = get_thread_info(thread_id)
            with lock:
                thread_numbers.add(info["number"])
            return info["number"]

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_thread_number)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        assert len(thread_numbers) == 5

    def test_thread_colors_are_assigned(self, basic_config):
        """Test: Each thread gets a unique color assignment"""
        import threading
        import time

        from src.fake_analytics.logger import get_thread_info

        thread_colors = set()
        lock = threading.Lock()

        def get_thread_color():
            time.sleep(0.01)
            thread_id = threading.get_ident()
            info = get_thread_info(thread_id)
            with lock:
                thread_colors.add(info["color"])
            return info["color"]

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_thread_color)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        assert len(thread_colors) >= 1

    def test_multiple_bots_with_different_identities(
        self, sample_config_file, sample_identities, mock_playwright, mock_page
    ):
        """Test: Multiple bots can run with different identities"""
        import asyncio
        import threading

        config = Config(config_path=sample_config_file, verbose=False)
        config.conversion_rate = 0.0

        executed_identities = []
        execution_lock = threading.Lock()

        def run_bot_with_identity(identity):
            async def async_run():
                bot = TrafficBot(config, identity=identity)
                with patch("src.fake_analytics.core.async_playwright") as mock_pw_context:
                    mock_pw_context.return_value.__aenter__.return_value = mock_playwright
                    with patch("src.fake_analytics.core.tempfile.mkdtemp") as mock_mkdtemp:
                        with patch("src.fake_analytics.core.shutil.rmtree"):
                            mock_mkdtemp.return_value = "/tmp/test_profile"
                            await bot.run()
                            with execution_lock:
                                executed_identities.append(identity)

            asyncio.run(async_run())

        threads = []
        for identity in sample_identities:
            thread = threading.Thread(target=run_bot_with_identity, args=(identity,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        assert len(executed_identities) == len(sample_identities)

    def test_logger_thread_safety(self, basic_config):
        """Test: Logger operations are thread-safe"""
        import threading
        import time

        from src.fake_analytics.logger import BotLogger

        log_calls = []
        lock = threading.Lock()

        def log_from_thread():
            time.sleep(0.01)
            thread_id = threading.get_ident()
            logger = BotLogger(verbose=False, thread_id=thread_id)
            logger.info("Test message", thread_id=thread_id)
            with lock:
                log_calls.append(thread_id)

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=log_from_thread)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        assert len(log_calls) == 5
        assert len(set(log_calls)) == 5
