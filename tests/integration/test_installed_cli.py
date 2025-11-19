"""
Integration tests that require the package to be installed.

These tests should be run after installing the package with:
    poetry install
    # or
    pip install -e .

Run with: pytest tests/integration -v
"""

import subprocess
import sys

import pytest


@pytest.mark.integration
@pytest.mark.slow
class TestInstalledCLI:
    """Test CLI commands with installed package"""

    def is_package_installed(self):
        """Check if fake-analytics is installed"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "fake-analytics"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except Exception:
            return False
        else:
            return result.returncode == 0

    def test_cli_version_command_installed(self):
        """Test: CLI --version works when package is installed"""
        if not self.is_package_installed():
            pytest.skip("Package not installed. Run: pip install -e . or poetry install")

        result = subprocess.run(
            ["fake-analytics", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        # Should succeed when package is installed
        assert result.returncode == 0
        # Output should contain version info
        assert len(result.stdout) > 0 or len(result.stderr) > 0

    def test_cli_help_command_installed(self):
        """Test: CLI --help works when package is installed"""
        if not self.is_package_installed():
            pytest.skip("Package not installed. Run: pip install -e . or poetry install")

        result = subprocess.run(
            ["fake-analytics", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        assert result.returncode == 0
        assert "Fake Analytics" in result.stdout

    def test_cli_run_help_installed(self):
        """Test: CLI run --help works when package is installed"""
        if not self.is_package_installed():
            pytest.skip("Package not installed. Run: pip install -e . or poetry install")

        result = subprocess.run(
            ["fake-analytics", "run", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        assert result.returncode == 0
        assert "traffic bot" in result.stdout.lower()

    def test_cli_discover_help_installed(self):
        """Test: CLI discover --help works when package is installed"""
        if not self.is_package_installed():
            pytest.skip("Package not installed. Run: pip install -e . or poetry install")

        result = subprocess.run(
            ["fake-analytics", "discover", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        assert result.returncode == 0
        assert "form fields" in result.stdout.lower()

    @pytest.mark.network
    def test_cli_discover_command_with_real_url(self):
        """Test: CLI discover command works with a real URL"""
        if not self.is_package_installed():
            pytest.skip("Package not installed. Run: pip install -e . or poetry install")

        # Use a simple test page
        result = subprocess.run(
            ["fake-analytics", "discover", "--url", "https://httpbin.org/forms/post"],
            capture_output=True,
            text=True,
            timeout=30,
            input="n\n",
            check=False,  # Answer "no" to config generation prompt
        )

        # Should complete (might succeed or fail due to page structure, but shouldn't crash)
        assert result.returncode in [0, 1]


@pytest.mark.integration
class TestCLIWithPoetry:
    """Test CLI using poetry run (development environment)"""

    def is_poetry_available(self):
        """Check if poetry is available"""
        try:
            result = subprocess.run(
                ["poetry", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except Exception:
            return False
        else:
            return result.returncode == 0

    def test_poetry_run_cli_help(self):
        """Test: poetry run fake-analytics --help works"""
        if not self.is_poetry_available():
            pytest.skip("Poetry not available")

        result = subprocess.run(
            ["poetry", "run", "fake-analytics", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        assert result.returncode == 0
        assert "Fake Analytics" in result.stdout

    def test_poetry_run_pytest(self):
        """Test: poetry run pytest works"""
        if not self.is_poetry_available():
            pytest.skip("Poetry not available")

        # Run a simple unit test to verify pytest works
        result = subprocess.run(
            [
                "poetry",
                "run",
                "pytest",
                "tests/unit/test_config.py::TestConfigInitialization::test_config_with_verbose_flag",
                "-v",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        # Should pass
        assert result.returncode == 0
        assert "PASSED" in result.stdout or "passed" in result.stdout


@pytest.mark.integration
class TestPackageStructure:
    """Test package structure and imports"""

    def test_package_imports(self):
        """Test: All main modules can be imported"""
        try:
            from src.fake_analytics import actions, cli, config, core, data, discovery, logger

            # All imports should succeed
            assert config is not None
            assert data is not None
            assert actions is not None
            assert core is not None
            assert logger is not None
            assert cli is not None
            assert discovery is not None
        except ImportError as e:
            pytest.fail(f"Failed to import module: {e}")

    def test_cli_module_has_required_functions(self):
        """Test: CLI module has required functions"""
        from src.fake_analytics.cli import cli, run_bot_instance

        assert callable(cli)
        assert callable(run_bot_instance)

    def test_config_class_available(self):
        """Test: Config class is available and instantiable"""
        from src.fake_analytics.config import Config

        config = Config(verbose=False)
        assert config is not None
        assert hasattr(config, "target_url")
        assert hasattr(config, "conversion_rate")

    def test_traffic_bot_class_available(self):
        """Test: TrafficBot class is available"""
        from src.fake_analytics.config import Config
        from src.fake_analytics.core import TrafficBot

        config = Config(verbose=False)
        bot = TrafficBot(config)
        assert bot is not None
        assert bot.config is config
