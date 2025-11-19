"""
Pytest configuration and shared fixtures for all tests.
"""

import json
import os
import shutil
import tempfile
from unittest.mock import AsyncMock, Mock

import pytest
from playwright.async_api import Browser, BrowserContext, Page

from src.fake_analytics.config import Config
from src.fake_analytics.logger import BotLogger


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    tmp_dir = tempfile.mkdtemp(prefix="fake_analytics_test_")
    yield tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def sample_config_data():
    """Provide sample configuration data as dict"""
    return {
        "target_url": "https://example.com",
        "conversion_rate": 0.5,
        "form_fields": {
            "full_name": "#name",
            "email": "#email",
            "company": "#company",
        },
        "submit_button": "button[type='submit']",
        "referers": {
            "https://www.google.com/": 3,
            "https://www.facebook.com/": 2,
        },
        "locale": "en_US",
    }


@pytest.fixture
def sample_config_file(temp_dir, sample_config_data):
    """Create a temporary JSON config file"""
    config_path = os.path.join(temp_dir, "test_config.json")
    with open(config_path, "w") as f:
        json.dump(sample_config_data, f)
    return config_path


@pytest.fixture
def sample_csv_data():
    """Provide sample CSV user data"""
    return [
        {"full_name": "John Doe", "email": "john@example.com", "company": "Acme Inc"},
        {
            "full_name": "Jane Smith",
            "email": "jane@example.com",
            "company": "Tech Corp",
        },
        {
            "full_name": "Bob Wilson",
            "email": "bob@example.com",
            "company": "StartUp Ltd",
        },
    ]


@pytest.fixture
def sample_csv_file(temp_dir, sample_csv_data):
    """Create a temporary CSV file with user data"""
    import csv

    csv_path = os.path.join(temp_dir, "test_users.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["full_name", "email", "company"])
        writer.writeheader()
        writer.writerows(sample_csv_data)
    return csv_path


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables"""
    test_env = {
        "TARGET_URL": "https://test.example.com",
        "CONVERSION_RATE": "0.7",
        "PROXY_HOST": "proxy.test.com:8080",
        "PROXY_USER": "testuser",
        "PROXY_PASS": "testpass",
        "PROXY_COUNTRIES": "US,GB,CA",
    }
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    return test_env


@pytest.fixture
def basic_config():
    """Create a basic Config instance with minimal setup"""
    # Mock environment to avoid loading real .env
    return Config(config_path=None, verbose=False)


# ============================================================================
# FIXTURES: Mocked Playwright Components
# ============================================================================


@pytest.fixture
def mock_page():
    """Create a mock Playwright Page object"""
    page = AsyncMock(spec=Page)
    page.viewport_size = {"width": 1440, "height": 900}
    page.goto = AsyncMock(return_value=Mock(ok=True))
    page.wait_for_load_state = AsyncMock()
    page.screenshot = AsyncMock()
    page.query_selector = AsyncMock()
    page.query_selector_all = AsyncMock(return_value=[])
    page.mouse = AsyncMock()
    page.mouse.move = AsyncMock()
    page.mouse.wheel = AsyncMock()
    page.locator = Mock()
    page.set_extra_http_headers = AsyncMock()
    page.add_init_script = AsyncMock()
    page.content = AsyncMock(return_value="<html><body>Test</body></html>")
    page.inner_text = AsyncMock(return_value="Test content")
    page.evaluate = AsyncMock()
    page.on = Mock()  # Event listener
    return page


@pytest.fixture
def mock_context():
    """Create a mock Playwright BrowserContext object"""
    context = AsyncMock(spec=BrowserContext)
    context.new_page = AsyncMock()
    context.close = AsyncMock()
    context.pages = []
    return context


@pytest.fixture
def mock_browser():
    """Create a mock Playwright Browser object"""
    browser = AsyncMock(spec=Browser)
    browser.new_context = AsyncMock()
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_playwright(mock_browser, mock_context, mock_page):
    """Create a complete mock Playwright instance"""
    playwright = AsyncMock()
    playwright.chromium.launch = AsyncMock(return_value=mock_browser)
    playwright.chromium.launch_persistent_context = AsyncMock(return_value=mock_context)

    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    mock_context.pages = [mock_page]

    return playwright


@pytest.fixture
def mock_logger():
    """Create a mock logger to capture log calls"""
    logger = Mock(spec=BotLogger)
    logger.verbose = False
    logger.info = Mock()
    logger.success = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    logger.proxy_config = Mock()
    logger.bot_start = Mock()
    logger.form_submission = Mock()
    logger.navigation = Mock()
    logger.page_loaded = Mock()
    logger.bounce = Mock()
    logger.screenshot = Mock()
    logger.completion = Mock()
    return logger


@pytest.fixture
def silent_logger():
    """Create a real logger but with verbose=False for silent operation"""
    return BotLogger(verbose=False)


# ============================================================================
# FIXTURES: Identity Data
# ============================================================================


@pytest.fixture
def sample_identity():
    """Provide a sample identity dict"""
    return {
        "full_name": "Test User",
        "email": "test.user@example.com",
        "company": "Test Company Inc",
        "phone": "+1-555-0123",
    }


@pytest.fixture
def sample_identities():
    """Provide multiple sample identities"""
    return [
        {
            "full_name": "Alice Johnson",
            "email": "alice.johnson@gmail.com",
            "company": "Tech Solutions",
            "phone": "+1-555-1001",
        },
        {
            "full_name": "Bob Smith",
            "email": "bob.smith@yahoo.com",
            "company": "Digital Corp",
            "phone": "+1-555-1002",
        },
        {
            "full_name": "Carol White",
            "email": "carol@techstartup.io",
            "company": "TechStartup",
            "phone": None,
        },
    ]


# ============================================================================
# FIXTURES: Parametrize Helpers
# ============================================================================


@pytest.fixture(params=["en_US", "en_GB", "fr_FR", "de_DE", "ja_JP"])
def locale_param(request):
    """Parametrized locale fixture for testing different locales"""
    return request.param


@pytest.fixture(params=[0.0, 0.3, 0.5, 0.7, 1.0])
def conversion_rate_param(request):
    """Parametrized conversion rate fixture"""
    return request.param


@pytest.fixture(params=[True, False])
def verbose_param(request):
    """Parametrized verbose flag fixture"""
    return request.param


# ============================================================================
# FIXTURES: Form Fields
# ============================================================================


@pytest.fixture
def sample_form_fields():
    """Provide sample form field mapping"""
    return {
        "full_name": "#name-input",
        "email": "input[name='email']",
        "company": "#company",
        "phone": "input[type='tel']",
        "message": "textarea[name='message']",
    }


@pytest.fixture
def mock_form_elements(mock_page):
    """Create mock form elements on a page"""
    # Create mock locators for each form field
    mock_locator = AsyncMock()
    mock_locator.first = AsyncMock()
    mock_locator.first.wait_for = AsyncMock()
    mock_locator.first.hover = AsyncMock()
    mock_locator.first.click = AsyncMock()
    mock_locator.first.type = AsyncMock()

    mock_page.locator.return_value = mock_locator
    return mock_locator


# ============================================================================
# FIXTURES: Proxy Configuration
# ============================================================================


@pytest.fixture
def proxy_config_basic():
    """Basic proxy configuration without countries"""
    return {
        "server": "http://proxy.example.com:8080",
        "username": "proxyuser",
        "password": "proxypass",
    }


@pytest.fixture
def proxy_config_with_countries():
    """Proxy configuration with country routing"""
    return {
        "server": "http://gw.dataimpulse.com:823",
        "username": "user__cr.US,GB,CA",
        "password": "secure_password",
    }


# ============================================================================
# PYTEST HOOKS
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests for individual modules")
    config.addinivalue_line("markers", "integration: Integration tests for module interactions")
    config.addinivalue_line("markers", "e2e: End-to-end functional tests")
    config.addinivalue_line("markers", "slow: Tests that take a long time to run")
    config.addinivalue_line("markers", "network: Tests that require network connectivity")
