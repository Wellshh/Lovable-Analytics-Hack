"""
Unit tests for config.py module
"""

import json
import os

import pytest

from src.fake_analytics.config import Config

# ============================================================================
# TEST: Config Initialization
# ============================================================================


@pytest.mark.unit
class TestConfigInitialization:
    """Test Config class initialization"""

    def test_config_default_initialization(self, monkeypatch):
        """Test: Config initializes with default values from environment"""
        # Set minimal environment
        monkeypatch.setenv("TARGET_URL", "https://default.com")
        monkeypatch.delenv("PROXY_USER", raising=False)
        monkeypatch.delenv("PROXY_PASS", raising=False)

        config = Config()

        assert config.target_url == "https://default.com"
        assert config.conversion_rate == 1.0
        assert config.use_proxy is False
        assert config.verbose is False
        assert config.locale == "en_US"

    def test_config_with_verbose_flag(self):
        """Test: Config respects verbose flag"""
        config = Config(verbose=True)
        assert config.verbose is True

    @pytest.mark.parametrize(
        "conversion_rate,expected",
        [(0.0, 0.0), (0.5, 0.5), (1.0, 1.0), (0.123, 0.123)],
    )
    def test_config_conversion_rate_values(self, monkeypatch, conversion_rate, expected):
        """Test: Config handles various valid conversion rates"""
        monkeypatch.setenv("CONVERSION_RATE", str(conversion_rate))
        config = Config()
        assert config.conversion_rate == expected

    def test_config_proxy_enabled_when_credentials_present(self, monkeypatch):
        """Test: Proxy is enabled when username and password are provided"""
        monkeypatch.setenv("PROXY_USER", "testuser")
        monkeypatch.setenv("PROXY_PASS", "testpass")
        config = Config()
        assert config.use_proxy is True

    def test_config_proxy_disabled_when_credentials_missing(self, monkeypatch):
        """Test: Proxy is disabled when credentials are missing"""
        monkeypatch.delenv("PROXY_USER", raising=False)
        monkeypatch.delenv("PROXY_PASS", raising=False)
        config = Config()
        assert config.use_proxy is False


# ============================================================================
# TEST: Config File Loading
# ============================================================================


@pytest.mark.unit
class TestConfigFileLoading:
    """Test loading configuration from JSON files"""

    def test_load_config_from_valid_file(self, sample_config_file, sample_config_data):
        """Test: Config loads successfully from valid JSON file"""
        config = Config(config_path=sample_config_file)

        assert config.target_url == sample_config_data["target_url"]
        assert config.conversion_rate == sample_config_data["conversion_rate"]
        assert config.form_fields == sample_config_data["form_fields"]
        assert config.submit_button == sample_config_data["submit_button"]
        assert config.referers == sample_config_data["referers"]
        assert config.locale == sample_config_data["locale"]

    def test_load_config_file_not_found(self):
        """Test: Config raises ValueError when file not found"""
        with pytest.raises(ValueError, match="Configuration file not found"):
            Config(config_path="/nonexistent/path/config.json")

    def test_load_config_invalid_json(self, temp_dir):
        """Test: Config raises ValueError for invalid JSON"""
        invalid_json_path = os.path.join(temp_dir, "invalid.json")
        with open(invalid_json_path, "w") as f:
            f.write("{ invalid json content")

        with pytest.raises(ValueError, match="Invalid JSON"):
            Config(config_path=invalid_json_path)

    def test_config_file_overrides_defaults(
        self, sample_config_file, monkeypatch, sample_config_data
    ):
        """Test: Config file values override environment defaults"""
        monkeypatch.setenv("TARGET_URL", "https://env.com")
        monkeypatch.setenv("CONVERSION_RATE", "0.9")

        config = Config(config_path=sample_config_file)

        # File values should override env vars
        assert config.target_url == sample_config_data["target_url"]
        assert config.conversion_rate == sample_config_data["conversion_rate"]

    def test_config_partial_file(self, temp_dir, monkeypatch):
        """Test: Config uses defaults for missing keys in file"""
        partial_config = {"target_url": "https://partial.com"}
        config_path = os.path.join(temp_dir, "partial.json")
        with open(config_path, "w") as f:
            json.dump(partial_config, f)

        monkeypatch.setenv("CONVERSION_RATE", "0.8")
        config = Config(config_path=config_path)

        assert config.target_url == "https://partial.com"
        assert config.conversion_rate == 0.8  # From env
        assert config.form_fields is None  # Default
        assert config.locale == "en_US"  # Default


# ============================================================================
# TEST: Config Validation
# ============================================================================


@pytest.mark.unit
class TestConfigValidation:
    """Test config validation logic"""

    @pytest.mark.parametrize("invalid_rate", [-0.1, -1.0, 1.1, 2.0, 100.0, -100.0])
    def test_validate_rejects_invalid_conversion_rate(self, monkeypatch, invalid_rate):
        """Test: Validation rejects conversion rates outside [0, 1]"""
        monkeypatch.setenv("CONVERSION_RATE", str(invalid_rate))
        with pytest.raises(ValueError, match="CONVERSION_RATE must be between 0 and 1"):
            Config()

    @pytest.mark.parametrize("valid_rate", [0.0, 0.001, 0.5, 0.999, 1.0])
    def test_validate_accepts_valid_conversion_rate(self, monkeypatch, valid_rate):
        """Test: Validation accepts conversion rates within [0, 1]"""
        monkeypatch.setenv("CONVERSION_RATE", str(valid_rate))
        config = Config()
        assert config.conversion_rate == valid_rate


# ============================================================================
# TEST: Proxy Configuration
# ============================================================================


@pytest.mark.unit
class TestProxyConfiguration:
    """Test proxy configuration generation"""

    def test_get_proxy_config_returns_none_without_credentials(self, monkeypatch):
        """Test: get_proxy_config returns None when credentials missing"""
        monkeypatch.delenv("PROXY_USER", raising=False)
        monkeypatch.delenv("PROXY_PASS", raising=False)
        config = Config()
        assert config.get_proxy_config() is None

    def test_get_proxy_config_basic(self, monkeypatch):
        """Test: get_proxy_config returns basic config without countries"""
        monkeypatch.setenv("PROXY_HOST", "proxy.example.com:8080")
        monkeypatch.setenv("PROXY_USER", "testuser")
        monkeypatch.setenv("PROXY_PASS", "testpass")
        monkeypatch.setenv("PROXY_COUNTRIES", "")

        config = Config()
        proxy_config = config.get_proxy_config()

        assert proxy_config is not None
        assert proxy_config["server"] == "http://proxy.example.com:8080"
        assert proxy_config["username"] == "testuser"
        assert proxy_config["password"] == "testpass"

    def test_get_proxy_config_with_countries(self, monkeypatch):
        """Test: get_proxy_config adds country routing to username"""
        monkeypatch.setenv("PROXY_HOST", "gw.dataimpulse.com:823")
        monkeypatch.setenv("PROXY_USER", "user123")
        monkeypatch.setenv("PROXY_PASS", "pass123")
        monkeypatch.setenv("PROXY_COUNTRIES", "US, GB, CA")

        config = Config()
        proxy_config = config.get_proxy_config()

        assert proxy_config is not None
        assert proxy_config["username"] == "user123__cr.US,GB,CA"
        assert "__cr." in proxy_config["username"]

    def test_get_proxy_config_strips_country_spaces(self, monkeypatch):
        """Test: get_proxy_config removes spaces from country list"""
        monkeypatch.setenv("PROXY_USER", "user")
        monkeypatch.setenv("PROXY_PASS", "pass")
        monkeypatch.setenv("PROXY_COUNTRIES", "US , GB , CA")

        config = Config()
        proxy_config = config.get_proxy_config()

        # Should remove spaces between countries
        assert proxy_config["username"] == "user__cr.US,GB,CA"

    @pytest.mark.parametrize(
        "countries,expected_suffix",
        [
            ("US", "user__cr.US"),
            ("US,GB", "user__cr.US,GB"),
            ("US,GB,CA,AU", "user__cr.US,GB,CA,AU"),
            ("TH,MM,CN", "user__cr.TH,MM,CN"),
        ],
    )
    def test_get_proxy_config_various_countries(self, monkeypatch, countries, expected_suffix):
        """Test: get_proxy_config handles various country combinations"""
        monkeypatch.setenv("PROXY_USER", "user")
        monkeypatch.setenv("PROXY_PASS", "pass")
        monkeypatch.setenv("PROXY_COUNTRIES", countries)

        config = Config()
        proxy_config = config.get_proxy_config()

        assert proxy_config["username"] == expected_suffix


# ============================================================================
# TEST: Config Properties
# ============================================================================


@pytest.mark.unit
class TestConfigProperties:
    """Test config property access and modification"""

    def test_config_attributes_are_accessible(self, sample_config_file):
        """Test: All config attributes are accessible"""
        config = Config(config_path=sample_config_file)

        # Check all attributes exist and are accessible
        assert hasattr(config, "target_url")
        assert hasattr(config, "conversion_rate")
        assert hasattr(config, "form_fields")
        assert hasattr(config, "submit_button")
        assert hasattr(config, "referers")
        assert hasattr(config, "locale")
        assert hasattr(config, "proxy_host")
        assert hasattr(config, "proxy_user")
        assert hasattr(config, "proxy_pass")
        assert hasattr(config, "proxy_countries")
        assert hasattr(config, "use_proxy")
        assert hasattr(config, "verbose")

    def test_config_can_be_modified(self):
        """Test: Config attributes can be modified after initialization"""
        config = Config()
        original_url = config.target_url

        config.target_url = "https://modified.com"
        assert config.target_url == "https://modified.com"
        assert config.target_url != original_url

    def test_config_form_fields_default_none(self, monkeypatch):
        """Test: form_fields defaults to None when not in config"""
        monkeypatch.delenv("PROXY_USER", raising=False)
        monkeypatch.delenv("PROXY_PASS", raising=False)
        config = Config()
        assert config.form_fields is None

    def test_config_submit_button_default_none(self):
        """Test: submit_button defaults to None when not in config"""
        config = Config()
        assert config.submit_button is None
