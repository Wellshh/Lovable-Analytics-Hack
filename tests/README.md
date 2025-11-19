# Fake Analytics Test Suite

This directory contains comprehensive unit and end-to-end tests for the fake-analytics project.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and pytest configuration
├── unit/                    # Unit tests for individual modules
│   ├── test_config.py       # Config class tests
│   ├── test_data.py         # Data generation and CSV loading tests
│   ├── test_actions.py      # Browser actions tests (async)
│   └── test_logger.py       # Logger functionality tests
├── integration/             # Integration tests (require installed package)
│   ├── test_installed_cli.py     # CLI tests with installed package
│   ├── test_real_discovery.py    # Real discovery tests (no mocks, from .env)
│   └── test_real_traffic_bot.py  # Real traffic bot tests (no mocks, from .env)
└── e2e/                     # End-to-end integration tests
    ├── test_traffic_bot.py  # TrafficBot workflow tests
    ├── test_cli.py          # CLI command tests (mocked)
    └── test_discovery.py    # Form field discovery tests
```

## Running Tests

### Install Test Dependencies

```bash
# Using Poetry
poetry install --with dev

# Using pip
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-xdist
```

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run with detailed output
pytest -vv
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only end-to-end tests
pytest -m e2e

# Run only integration tests (require installed package)
pytest -m integration

# Run integration tests with poetry
poetry run pytest tests/integration -v

# Run real integration tests (requires .env config)
pytest tests/integration/test_real_*.py -v -s

# Exclude slow tests
pytest -m "not slow"

# Run network tests only
pytest -m network -v
```

### Run Specific Test Files

```bash
# Run config tests
pytest tests/unit/test_config.py

# Run data tests
pytest tests/unit/test_data.py

# Run actions tests
pytest tests/unit/test_actions.py

# Run CLI tests
pytest tests/e2e/test_cli.py
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest tests/unit/test_config.py::TestConfigInitialization

# Run a specific test function
pytest tests/unit/test_data.py::TestIdentityGenerator::test_generate_identity_returns_dict

# Run tests matching a keyword
pytest -k "config"
pytest -k "identity"
```

### Run Tests in Parallel

```bash
# Run tests using multiple CPUs
pytest -n auto

# Run tests using 4 workers
pytest -n 4
```

### Coverage Reports

```bash
# Run tests with coverage report
pytest --cov=src/fake_analytics

# Generate HTML coverage report
pytest --cov=src/fake_analytics --cov-report=html

# Open HTML coverage report
open htmlcov/index.html

# Generate XML coverage report (for CI/CD)
pytest --cov=src/fake_analytics --cov-report=xml
```

### Stop on First Failure

```bash
# Stop after first failure
pytest -x

# Stop after N failures
pytest --maxfail=3
```

### Run Tests with Output

```bash
# Show print statements
pytest -s

# Show all output including passed tests
pytest -v -s
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual functions/classes
- `@pytest.mark.integration` - Integration tests between modules
- `@pytest.mark.e2e` - End-to-end functional tests
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.network` - Tests requiring network connectivity
- `@pytest.mark.asyncio` - Asynchronous tests

## Fixtures

Common fixtures are defined in `conftest.py`:

### Configuration Fixtures
- `temp_dir` - Temporary directory for test files
- `sample_config_data` - Sample configuration dictionary
- `sample_config_file` - Temporary JSON config file
- `sample_csv_file` - Temporary CSV data file
- `mock_env_vars` - Mock environment variables
- `basic_config` - Basic Config instance

### Playwright Fixtures
- `mock_page` - Mocked Playwright Page object
- `mock_context` - Mocked BrowserContext
- `mock_browser` - Mocked Browser
- `mock_playwright` - Complete mocked Playwright instance

### Logger Fixtures
- `mock_logger` - Mocked logger for testing
- `silent_logger` - Real logger with verbose=False

### Data Fixtures
- `sample_identity` - Sample user identity
- `sample_identities` - Multiple sample identities
- `sample_form_fields` - Sample form field mapping

### Parametrized Fixtures
- `locale_param` - Different locale values
- `conversion_rate_param` - Different conversion rates
- `verbose_param` - True/False verbose values

## Writing New Tests

### Unit Test Example

```python
import pytest
from src.fake_analytics.config import Config

@pytest.mark.unit
class TestMyFeature:
    """Test my new feature"""

    def test_feature_works(self):
        """Test: Feature works as expected"""
        # Arrange
        config = Config()

        # Act
        result = config.some_method()

        # Assert
        assert result is not None
```

### Async Test Example

```python
import pytest
from src.fake_analytics.actions import human_type

@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncFeature:
    """Test async feature"""

    async def test_async_function(self, mock_page):
        """Test: Async function completes"""
        await human_type(mock_page, "#input", "text")
        assert mock_page.locator.called
```

### Parametrized Test Example

```python
import pytest

@pytest.mark.unit
class TestParametrized:
    """Test with parameters"""

    @pytest.mark.parametrize(
        "input_value,expected",
        [
            (0.0, 0.0),
            (0.5, 0.5),
            (1.0, 1.0),
        ]
    )
    def test_various_inputs(self, input_value, expected):
        """Test: Function handles various inputs"""
        result = process(input_value)
        assert result == expected
```

## Continuous Integration

Tests are designed to run in CI/CD environments:

```bash
# CI environment detection
export CI=true

# Run tests with CI-friendly output
pytest --tb=short --color=yes

# Generate coverage report for CI
pytest --cov=src/fake_analytics --cov-report=xml --cov-report=term
```

## Test Best Practices

1. **Arrange-Act-Assert** - Structure tests clearly
2. **One assertion per test** - Keep tests focused (when practical)
3. **Descriptive names** - Use clear, descriptive test names
4. **Use fixtures** - Reuse common test setup
5. **Mock external dependencies** - Don't rely on network/filesystem
6. **Test edge cases** - Test boundary conditions
7. **Use parametrize** - Test multiple inputs efficiently
8. **Mark tests appropriately** - Use markers for organization

## Troubleshooting

### Tests Fail with Import Errors

```bash
# Ensure package is installed in development mode
pip install -e .
# or
poetry install
```

### Async Tests Not Running

```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Check asyncio_mode in pyproject.toml
# Should be: asyncio_mode = "auto"
```

### Coverage Not Working

```bash
# Install pytest-cov
pip install pytest-cov

# Run with explicit coverage
pytest --cov=src/fake_analytics --cov-report=term-missing
```

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Playwright Python documentation](https://playwright.dev/python/)
