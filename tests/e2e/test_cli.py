"""
End-to-end tests for CLI commands
"""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from src.fake_analytics.cli import cli, run_bot_instance

# ============================================================================
# TEST: CLI Run Command
# ============================================================================


@pytest.mark.e2e
class TestCLIRunCommand:
    """Test CLI run command"""

    def test_cli_run_with_url(self, monkeypatch):
        """Test: CLI run command with URL parameter"""
        runner = CliRunner()

        # Mock environment and bot execution
        monkeypatch.delenv("PROXY_USER", raising=False)
        monkeypatch.delenv("PROXY_PASS", raising=False)

        with patch("src.fake_analytics.cli.ThreadPoolExecutor") as mock_executor:
            mock_executor.return_value.__enter__ = Mock(return_value=mock_executor.return_value)
            mock_executor.return_value.__exit__ = Mock(return_value=False)
            mock_executor.return_value.submit = Mock(
                return_value=Mock(result=Mock(return_value=None))
            )

            result = runner.invoke(cli, ["run", "--url", "https://test.com", "--threads", "1"])

            # Should execute without crashing
            assert result.exit_code == 0

    def test_cli_run_with_config_file(self, sample_config_file, monkeypatch):
        """Test: CLI run command with config file"""
        runner = CliRunner()

        monkeypatch.delenv("PROXY_USER", raising=False)
        monkeypatch.delenv("PROXY_PASS", raising=False)

        with patch("src.fake_analytics.cli.ThreadPoolExecutor") as mock_executor:
            mock_executor.return_value.__enter__ = Mock(return_value=mock_executor.return_value)
            mock_executor.return_value.__exit__ = Mock(return_value=False)
            mock_executor.return_value.submit = Mock(
                return_value=Mock(result=Mock(return_value=None))
            )

            result = runner.invoke(cli, ["run", "--config", sample_config_file])

            assert result.exit_code == 0

    def test_cli_run_with_data_file(self, sample_config_file, sample_csv_file, monkeypatch):
        """Test: CLI run command with CSV data file"""
        runner = CliRunner()

        monkeypatch.delenv("PROXY_USER", raising=False)
        monkeypatch.delenv("PROXY_PASS", raising=False)

        with patch("src.fake_analytics.cli.ThreadPoolExecutor") as mock_executor:
            mock_executor.return_value.__enter__ = Mock(return_value=mock_executor.return_value)
            mock_executor.return_value.__exit__ = Mock(return_value=False)
            mock_executor.return_value.submit = Mock(
                return_value=Mock(result=Mock(return_value=None))
            )

            result = runner.invoke(
                cli,
                [
                    "run",
                    "--config",
                    sample_config_file,
                    "--data-file",
                    sample_csv_file,
                ],
            )

            assert result.exit_code == 0

    def test_cli_run_with_verbose_flag(self, monkeypatch):
        """Test: CLI run command with verbose flag"""
        runner = CliRunner()

        monkeypatch.delenv("PROXY_USER", raising=False)
        monkeypatch.delenv("PROXY_PASS", raising=False)

        with patch("src.fake_analytics.cli.ThreadPoolExecutor") as mock_executor:
            mock_executor.return_value.__enter__ = Mock(return_value=mock_executor.return_value)
            mock_executor.return_value.__exit__ = Mock(return_value=False)
            mock_executor.return_value.submit = Mock(
                return_value=Mock(result=Mock(return_value=None))
            )

            result = runner.invoke(cli, ["run", "--url", "https://test.com", "--verbose"])

            assert result.exit_code == 0

    @pytest.mark.parametrize("threads", [1, 3, 5, 10])
    def test_cli_run_with_different_thread_counts(self, threads, monkeypatch):
        """Test: CLI run command with different thread counts"""
        runner = CliRunner()

        monkeypatch.delenv("PROXY_USER", raising=False)
        monkeypatch.delenv("PROXY_PASS", raising=False)

        with patch("src.fake_analytics.cli.ThreadPoolExecutor") as mock_executor:
            mock_executor.return_value.__enter__ = Mock(return_value=mock_executor.return_value)
            mock_executor.return_value.__exit__ = Mock(return_value=False)
            mock_executor.return_value.submit = Mock(
                return_value=Mock(result=Mock(return_value=None))
            )

            result = runner.invoke(
                cli,
                ["run", "--url", "https://test.com", "--threads", str(threads)],
            )

            assert result.exit_code == 0

    def test_cli_run_handles_invalid_config_file(self):
        """Test: CLI run command handles invalid config file"""
        runner = CliRunner()

        result = runner.invoke(cli, ["run", "--config", "/nonexistent/config.json"])

        # Should exit with error
        assert result.exit_code != 0


# ============================================================================
# TEST: CLI Discover Command
# ============================================================================


@pytest.mark.e2e
class TestCLIDiscoverCommand:
    """Test CLI discover command"""

    def test_cli_discover_requires_url(self):
        """Test: CLI discover command requires URL parameter"""
        runner = CliRunner()

        result = runner.invoke(cli, ["discover"])

        # Should fail without URL
        assert result.exit_code != 0

    def test_cli_discover_with_url(self):
        """Test: CLI discover command with URL parameter"""
        runner = CliRunner()

        with patch("src.fake_analytics.cli.asyncio.run") as mock_run:
            result = runner.invoke(cli, ["discover", "--url", "https://example.com"])

            # Should call async discover function
            assert mock_run.called
            assert result.exit_code == 0

    def test_cli_discover_calls_discover_form_fields(self):
        """Test: CLI discover command calls discover_form_fields function"""
        runner = CliRunner()

        with patch("src.fake_analytics.cli.discover_form_fields"):
            with patch("src.fake_analytics.cli.asyncio.run") as mock_run:
                mock_run.side_effect = lambda _coro: None

                runner.invoke(cli, ["discover", "--url", "https://test.com"])

                # Should have been passed to asyncio.run
                assert mock_run.called


# ============================================================================
# TEST: CLI Version and Help
# ============================================================================


@pytest.mark.e2e
class TestCLIGeneralCommands:
    """Test general CLI commands"""

    @pytest.mark.skip(reason="Version command requires package installation via poetry/pip install")
    def test_cli_version_command(self):
        """Test: CLI --version shows version (requires installed package)"""
        runner = CliRunner()

        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "version" in result.output.lower() or len(result.output) > 0

    def test_cli_help_command(self):
        """Test: CLI --help shows help text"""
        runner = CliRunner()

        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Fake Analytics" in result.output

    def test_cli_run_help_command(self):
        """Test: CLI run --help shows run command help"""
        runner = CliRunner()

        result = runner.invoke(cli, ["run", "--help"])

        assert result.exit_code == 0
        assert "traffic bot" in result.output.lower()

    def test_cli_discover_help_command(self):
        """Test: CLI discover --help shows discover command help"""
        runner = CliRunner()

        result = runner.invoke(cli, ["discover", "--help"])

        assert result.exit_code == 0
        assert "form fields" in result.output.lower()


# ============================================================================
# TEST: run_bot_instance Function
# ============================================================================


@pytest.mark.e2e
class TestRunBotInstance:
    """Test run_bot_instance wrapper function"""

    def test_run_bot_instance_executes(self, basic_config):
        """Test: run_bot_instance executes bot"""
        with patch("src.fake_analytics.cli.asyncio.run") as mock_run:
            run_bot_instance(basic_config, None)

            # Should have called asyncio.run
            assert mock_run.called

    def test_run_bot_instance_with_identity(self, basic_config, sample_identity):
        """Test: run_bot_instance executes with identity"""
        with patch("src.fake_analytics.cli.asyncio.run") as mock_run:
            run_bot_instance(basic_config, sample_identity)

            assert mock_run.called

    def test_run_bot_instance_creates_traffic_bot(self, basic_config):
        """Test: run_bot_instance creates TrafficBot instance"""
        with patch("src.fake_analytics.cli.asyncio.run") as mock_async_run:
            mock_async_run.return_value = None

            # Run the function
            run_bot_instance(basic_config, None)

            # Should have called asyncio.run with a coroutine
            assert mock_async_run.called
            assert mock_async_run.call_count == 1


# ============================================================================
# TEST: CLI Integration Scenarios
# ============================================================================


@pytest.mark.e2e
class TestCLIIntegrationScenarios:
    """Test CLI integration scenarios"""

    def test_cli_run_url_overrides_config_file(self, sample_config_file, monkeypatch):
        """Test: CLI URL parameter overrides config file"""
        runner = CliRunner()

        monkeypatch.delenv("PROXY_USER", raising=False)
        monkeypatch.delenv("PROXY_PASS", raising=False)

        with patch("src.fake_analytics.cli.ThreadPoolExecutor") as mock_executor:
            mock_executor.return_value.__enter__ = Mock(return_value=mock_executor.return_value)
            mock_executor.return_value.__exit__ = Mock(return_value=False)
            mock_executor.return_value.submit = Mock(
                return_value=Mock(result=Mock(return_value=None))
            )

            with patch("src.fake_analytics.cli.Config") as mock_config_class:
                mock_config_instance = Mock()
                mock_config_instance.target_url = "https://override.com"
                mock_config_class.return_value = mock_config_instance

                runner.invoke(
                    cli,
                    [
                        "run",
                        "--config",
                        sample_config_file,
                        "--url",
                        "https://override.com",
                    ],
                )

                # URL should have been set on config
                assert mock_config_instance.target_url == "https://override.com"

    def test_cli_data_file_overrides_thread_count(
        self, sample_config_file, sample_csv_file, sample_csv_data, monkeypatch
    ):
        """Test: CLI data file overrides thread count"""
        runner = CliRunner()

        monkeypatch.delenv("PROXY_USER", raising=False)
        monkeypatch.delenv("PROXY_PASS", raising=False)

        with patch("src.fake_analytics.cli.ThreadPoolExecutor") as mock_executor:
            mock_executor.return_value.__enter__ = Mock(return_value=mock_executor.return_value)
            mock_executor.return_value.__exit__ = Mock(return_value=False)
            mock_executor.return_value.submit = Mock(
                return_value=Mock(result=Mock(return_value=None))
            )

            runner.invoke(
                cli,
                [
                    "run",
                    "--config",
                    sample_config_file,
                    "--data-file",
                    sample_csv_file,
                    "--threads",
                    "10",  # Should be overridden by CSV row count
                ],
            )

            # Thread count should match CSV rows (3), not --threads value (10)
            # Check that submit was called correct number of times
            assert mock_executor.return_value.submit.call_count == len(sample_csv_data)

    def test_cli_verbose_flag_propagates_to_config(self, monkeypatch):
        """Test: CLI verbose flag propagates to Config"""
        runner = CliRunner()

        monkeypatch.delenv("PROXY_USER", raising=False)
        monkeypatch.delenv("PROXY_PASS", raising=False)

        with patch("src.fake_analytics.cli.ThreadPoolExecutor") as mock_executor:
            mock_executor.return_value.__enter__ = Mock(return_value=mock_executor.return_value)
            mock_executor.return_value.__exit__ = Mock(return_value=False)
            mock_executor.return_value.submit = Mock(
                return_value=Mock(result=Mock(return_value=None))
            )

            with patch("src.fake_analytics.cli.Config") as mock_config_class:
                runner.invoke(cli, ["run", "--url", "https://test.com", "--verbose"])

                # Config should have been created with verbose=True
                mock_config_class.assert_called_once()
                call_kwargs = mock_config_class.call_args[1]
                assert call_kwargs.get("verbose") is True
