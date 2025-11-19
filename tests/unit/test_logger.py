"""
Unit tests for logger.py module
"""

from unittest.mock import patch

import pytest

from src.fake_analytics.logger import (
    BotLogger,
    create_progress_bar,
    get_logger,
    print_config_generated,
    print_field_table,
)

# ============================================================================
# TEST: BotLogger Class
# ============================================================================


@pytest.mark.unit
class TestBotLogger:
    """Test BotLogger class"""

    def test_logger_initialization_default(self):
        """Test: BotLogger initializes with default verbose=False"""
        logger = BotLogger()
        assert logger.verbose is False
        assert logger.console is not None

    def test_logger_initialization_verbose(self):
        """Test: BotLogger initializes with verbose=True"""
        logger = BotLogger(verbose=True)
        assert logger.verbose is True

    @pytest.mark.parametrize("verbose", [True, False])
    def test_logger_verbose_parameter(self, verbose):
        """Test: BotLogger respects verbose parameter"""
        logger = BotLogger(verbose=verbose)
        assert logger.verbose == verbose

    def test_logger_has_required_methods(self):
        """Test: BotLogger has all required logging methods"""
        logger = BotLogger()

        required_methods = [
            "info",
            "success",
            "warning",
            "error",
            "debug",
            "proxy_config",
            "bot_start",
            "form_submission",
            "navigation",
            "page_loaded",
            "bounce",
            "screenshot",
            "completion",
        ]

        for method in required_methods:
            assert hasattr(logger, method)
            assert callable(getattr(logger, method))


# ============================================================================
# TEST: Logger Methods
# ============================================================================


@pytest.mark.unit
class TestBotLoggerMethods:
    """Test BotLogger logging methods"""

    @patch("src.fake_analytics.logger.console")
    def test_info_logs_message(self, mock_console):
        """Test: info method logs message"""
        logger = BotLogger()
        logger.console = mock_console

        logger.info("Test message")
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_success_logs_message(self, mock_console):
        """Test: success method logs message"""
        logger = BotLogger()
        logger.console = mock_console

        logger.success("Success message")
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_warning_logs_message(self, mock_console):
        """Test: warning method logs message"""
        logger = BotLogger()
        logger.console = mock_console

        logger.warning("Warning message")
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_error_logs_message(self, mock_console):
        """Test: error method logs message"""
        logger = BotLogger()
        logger.console = mock_console

        logger.error("Error message")
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_debug_logs_when_verbose_true(self, mock_console):
        """Test: debug logs message when verbose=True"""
        logger = BotLogger(verbose=True)
        logger.console = mock_console

        logger.debug("Debug message")
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_debug_does_not_log_when_verbose_false(self, mock_console):
        """Test: debug does not log when verbose=False"""
        logger = BotLogger(verbose=False)
        logger.console = mock_console

        logger.debug("Debug message")
        mock_console.print.assert_not_called()

    @patch("src.fake_analytics.logger.console")
    def test_proxy_config_logs_table(self, mock_console):
        """Test: proxy_config logs proxy configuration"""
        logger = BotLogger()
        logger.console = mock_console

        logger.proxy_config("http://proxy.com:8080", "user", "pass****")
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_bot_start_logs_panel(self, mock_console):
        """Test: bot_start logs startup information"""
        logger = BotLogger()
        logger.console = mock_console

        logger.bot_start("https://example.com", threads=5)
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_form_submission_logs_info(self, mock_console):
        """Test: form_submission logs submission info"""
        logger = BotLogger()
        logger.console = mock_console

        logger.form_submission("Test User", 12345)
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_navigation_logs_url(self, mock_console):
        """Test: navigation logs target URL"""
        logger = BotLogger()
        logger.console = mock_console

        logger.navigation("https://example.com")
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_page_loaded_logs_when_verbose(self, mock_console):
        """Test: page_loaded logs when verbose=True"""
        logger = BotLogger(verbose=True)
        logger.console = mock_console

        logger.page_loaded()
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_page_loaded_does_not_log_when_not_verbose(self, mock_console):
        """Test: page_loaded does not log when verbose=False"""
        logger = BotLogger(verbose=False)
        logger.console = mock_console

        logger.page_loaded()
        mock_console.print.assert_not_called()

    @patch("src.fake_analytics.logger.console")
    def test_bounce_logs_pid(self, mock_console):
        """Test: bounce logs process ID"""
        logger = BotLogger()
        logger.console = mock_console

        logger.bounce(67890)
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_screenshot_logs_path(self, mock_console):
        """Test: screenshot logs file path"""
        logger = BotLogger()
        logger.console = mock_console

        logger.screenshot("/path/to/screenshot.png")
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_completion_logs_panel(self, mock_console):
        """Test: completion logs completion panel"""
        logger = BotLogger()
        logger.console = mock_console

        logger.completion()
        mock_console.print.assert_called_once()


# ============================================================================
# TEST: Global Logger Function
# ============================================================================


@pytest.mark.unit
class TestGetLogger:
    """Test get_logger global function"""

    def test_get_logger_returns_bot_logger(self):
        """Test: get_logger returns BotLogger instance"""
        logger = get_logger()
        assert isinstance(logger, BotLogger)

    def test_get_logger_default_verbose_false(self):
        """Test: get_logger defaults to verbose=False"""
        logger = get_logger()
        assert logger.verbose is False

    def test_get_logger_with_verbose_true(self):
        """Test: get_logger creates logger with verbose=True"""
        logger = get_logger(verbose=True)
        assert logger.verbose is True

    def test_get_logger_is_singleton(self):
        """Test: get_logger returns same instance for same verbose value"""
        # Note: This test depends on implementation details
        # In real usage, get_logger might return different instances
        logger1 = get_logger(verbose=False)
        logger2 = get_logger(verbose=False)
        # They should be the same instance (singleton pattern)
        assert logger1 is logger2

    def test_get_logger_creates_new_for_different_verbose(self):
        """Test: get_logger creates new instance when verbose changes"""
        logger1 = get_logger(verbose=False)
        logger2 = get_logger(verbose=True)
        # Should have different verbose settings
        assert logger1.verbose != logger2.verbose


# ============================================================================
# TEST: Progress Bar Creation
# ============================================================================


@pytest.mark.unit
class TestCreateProgressBar:
    """Test create_progress_bar function"""

    def test_create_progress_bar_returns_progress_instance(self):
        """Test: create_progress_bar returns Progress instance"""
        from rich.progress import Progress

        progress = create_progress_bar()
        assert isinstance(progress, Progress)

    def test_create_progress_bar_returns_instance(self):
        """Test: create_progress_bar returns a Progress instance"""
        progress = create_progress_bar()
        assert progress is not None


# ============================================================================
# TEST: Field Table Printing
# ============================================================================


@pytest.mark.unit
class TestPrintFieldTable:
    """Test print_field_table function"""

    @patch("src.fake_analytics.logger.console")
    def test_print_field_table_with_valid_fields(self, mock_console):
        """Test: print_field_table prints table with valid fields"""
        fields = [
            {
                "tag": "input",
                "type": "text",
                "name": "username",
                "id": "user-id",
                "placeholder": "Enter name",
            },
            {
                "tag": "input",
                "type": "email",
                "name": "email",
                "id": "email-id",
                "placeholder": "Enter email",
            },
        ]

        print_field_table(fields)
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_print_field_table_with_empty_list(self, mock_console):
        """Test: print_field_table handles empty field list"""
        print_field_table([])
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_print_field_table_truncates_long_values(self, mock_console):
        """Test: print_field_table truncates long field values"""
        fields = [
            {
                "tag": "input",
                "type": "text",
                "name": "very_long_name_that_should_be_truncated_in_display",
                "id": "very_long_id_that_should_be_truncated_in_display",
                "placeholder": "very_long_placeholder_that_should_be_truncated_in_display",
            }
        ]

        print_field_table(fields)
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_print_field_table_handles_missing_keys(self, mock_console):
        """Test: print_field_table handles fields with missing keys"""
        fields = [
            {"tag": "input"},  # Missing other keys
            {"type": "email"},  # Missing other keys
        ]

        # Should not crash
        print_field_table(fields)
        mock_console.print.assert_called_once()


# ============================================================================
# TEST: Config Generated Printing
# ============================================================================


@pytest.mark.unit
class TestPrintConfigGenerated:
    """Test print_config_generated function"""

    @patch("src.fake_analytics.logger.console")
    def test_print_config_generated_with_valid_config(self, mock_console):
        """Test: print_config_generated prints config info"""
        config = {
            "target_url": "https://example.com",
            "conversion_rate": 0.5,
        }
        path = "/tmp/config.json"

        print_config_generated(config, path)
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    def test_print_config_generated_with_empty_config(self, mock_console):
        """Test: print_config_generated handles empty config"""
        config = {}
        path = "/tmp/empty.json"

        print_config_generated(config, path)
        mock_console.print.assert_called_once()

    @patch("src.fake_analytics.logger.console")
    @pytest.mark.parametrize(
        "path",
        ["/tmp/config.json", "config.json", "/home/user/test.json", "output.json"],
    )
    def test_print_config_generated_various_paths(self, mock_console, path):
        """Test: print_config_generated works with various paths"""
        config = {"test": "value"}
        print_config_generated(config, path)
        mock_console.print.assert_called_once()


# ============================================================================
# TEST: Logger Integration
# ============================================================================


@pytest.mark.unit
class TestLoggerIntegration:
    """Test logger integration scenarios"""

    def test_logger_verbose_mode_logs_more(self):
        """Test: Verbose logger logs debug messages, non-verbose does not"""
        with patch("src.fake_analytics.logger.console") as mock_console:
            verbose_logger = BotLogger(verbose=True)
            verbose_logger.console = mock_console
            verbose_logger.debug("Debug message")
            verbose_calls = mock_console.print.call_count

            mock_console.reset_mock()

            non_verbose_logger = BotLogger(verbose=False)
            non_verbose_logger.console = mock_console
            non_verbose_logger.debug("Debug message")
            non_verbose_calls = mock_console.print.call_count

            assert verbose_calls > non_verbose_calls

    @patch("src.fake_analytics.logger.console")
    def test_logger_handles_special_characters(self, mock_console):
        """Test: Logger handles special characters in messages"""
        logger = BotLogger()
        logger.console = mock_console

        # Should not crash with special characters
        logger.info("Test with émojis 🎉 and ünïcödé")
        logger.success("Success with 中文 characters")
        logger.error("Error with spëcîål çhars")

        assert mock_console.print.call_count == 3

    @patch("src.fake_analytics.logger.console")
    def test_logger_methods_accept_various_types(self, mock_console):
        """Test: Logger methods accept various data types in messages"""
        logger = BotLogger()
        logger.console = mock_console

        logger.info(f"Number: {123}")
        logger.success(f"Float: {45.67}")
        logger.warning(f"Boolean: {True}")

        assert mock_console.print.call_count == 3
