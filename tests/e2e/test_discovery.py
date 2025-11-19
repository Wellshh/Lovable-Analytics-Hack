"""
End-to-end tests for form field discovery functionality
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.fake_analytics.discovery import (
    discover_form_fields,
    generate_config_file,
)

# ============================================================================
# TEST: Form Field Discovery
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
class TestDiscoverFormFields:
    """Test discover_form_fields function"""

    async def test_discover_form_fields_navigates_to_url(self):
        """Test: discover_form_fields navigates to target URL"""
        url = "https://example.com"

        with patch("src.fake_analytics.discovery.async_playwright") as mock_pw:
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.query_selector_all = AsyncMock(return_value=[])
            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_browser.close = AsyncMock()

            mock_playwright = AsyncMock()
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_pw.return_value.__aenter__.return_value = mock_playwright

            await discover_form_fields(url)

            mock_page.goto.assert_called_once_with(
                url, timeout=60000, wait_until="domcontentloaded"
            )

    async def test_discover_form_fields_finds_input_elements(self):
        """Test: discover_form_fields finds input elements on page"""
        url = "https://example.com"

        # Create mock elements
        mock_element1 = AsyncMock()
        mock_element1.evaluate = AsyncMock(
            return_value={
                "tag": "input",
                "type": "text",
                "name": "username",
                "id": "user-id",
                "placeholder": "Enter username",
                "ariaLabel": "N/A",
                "className": "form-control",
            }
        )

        mock_element2 = AsyncMock()
        mock_element2.evaluate = AsyncMock(
            return_value={
                "tag": "input",
                "type": "email",
                "name": "email",
                "id": "email-id",
                "placeholder": "Enter email",
                "ariaLabel": "Email address",
                "className": "form-control",
            }
        )

        with patch("src.fake_analytics.discovery.async_playwright") as mock_pw:
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.query_selector_all = AsyncMock(return_value=[mock_element1, mock_element2])
            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_browser.close = AsyncMock()

            mock_playwright = AsyncMock()
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_pw.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.discovery.click.confirm", return_value=False):
                await discover_form_fields(url)

            # Should have queried for form elements
            mock_page.query_selector_all.assert_called_once_with("input, textarea, select")

    async def test_discover_form_fields_handles_no_elements(self):
        """Test: discover_form_fields handles pages with no form elements"""
        url = "https://example.com"

        with patch("src.fake_analytics.discovery.async_playwright") as mock_pw:
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.query_selector_all = AsyncMock(return_value=[])
            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_browser.close = AsyncMock()

            mock_playwright = AsyncMock()
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_pw.return_value.__aenter__.return_value = mock_playwright

            # Should complete without error
            await discover_form_fields(url)

    async def test_discover_form_fields_handles_timeout(self):
        """Test: discover_form_fields handles network timeout"""
        url = "https://slow-site.com"

        with patch("src.fake_analytics.discovery.async_playwright") as mock_pw:
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock(side_effect=Exception("Timeout"))
            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_browser.close = AsyncMock()

            mock_playwright = AsyncMock()
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_pw.return_value.__aenter__.return_value = mock_playwright

            # Should handle error gracefully
            await discover_form_fields(url)


# ============================================================================
# TEST: Config File Generation
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
class TestGenerateConfigFile:
    """Test generate_config_file function"""

    async def test_generate_config_file_finds_submit_button(self):
        """Test: generate_config_file finds submit button"""
        url = "https://example.com"
        mock_page = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=AsyncMock())

        field_details = []

        with patch("src.fake_analytics.discovery.click.confirm", return_value=False):
            with patch("src.fake_analytics.discovery.click.prompt", return_value="config.json"):
                with patch("os.path.exists", return_value=False):
                    with patch("builtins.open", create=True) as mock_open:
                        mock_file = MagicMock()
                        mock_open.return_value.__enter__.return_value = mock_file

                        await generate_config_file(url, mock_page, field_details)

                        # Should have checked for submit button
                        assert mock_page.query_selector.called

    async def test_generate_config_file_creates_json_file(self, temp_dir):
        """Test: generate_config_file creates JSON config file"""
        url = "https://example.com"
        mock_page = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=None)

        field_details = [
            {
                "tag": "input",
                "type": "text",
                "name": "username",
                "id": "user-id",
                "placeholder": "N/A",
            }
        ]

        import os

        output_path = os.path.join(temp_dir, "test_output.json")

        with patch("src.fake_analytics.discovery.click.confirm", side_effect=[False, True]):
            with patch(
                "src.fake_analytics.discovery.click.prompt",
                side_effect=[output_path, 0.3],
            ):
                await generate_config_file(url, mock_page, field_details)

                # File should have been created
                assert os.path.exists(output_path)

    async def test_generate_config_file_handles_existing_file(self, temp_dir):
        """Test: generate_config_file handles existing file"""
        url = "https://example.com"
        mock_page = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=None)

        field_details = []

        import os

        output_path = os.path.join(temp_dir, "existing.json")

        # Create existing file
        with open(output_path, "w") as f:
            f.write("{}")

        with patch("src.fake_analytics.discovery.click.confirm", side_effect=[False, False]):
            with patch("src.fake_analytics.discovery.click.prompt", return_value=output_path):
                # Should cancel when user doesn't want to overwrite
                await generate_config_file(url, mock_page, field_details)

    async def test_generate_config_file_validates_conversion_rate(self, temp_dir):
        """Test: generate_config_file validates conversion rate"""
        url = "https://example.com"
        mock_page = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=None)
        field_details = []

        import os

        output_path = os.path.join(temp_dir, "valid_rate.json")

        with patch("src.fake_analytics.discovery.click.confirm", side_effect=[False]):
            with patch(
                "src.fake_analytics.discovery.click.prompt",
                side_effect=[output_path, 1.5],  # Invalid rate > 1
            ):
                await generate_config_file(url, mock_page, field_details)

                # Should have created file with default rate
                assert os.path.exists(output_path)

                import json

                with open(output_path) as f:
                    config = json.load(f)
                    # Invalid rate should be replaced with default
                    assert config["conversion_rate"] == 0.3


# ============================================================================
# TEST: Discovery Integration
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
class TestDiscoveryIntegration:
    """Test discovery integration scenarios"""

    async def test_discovery_full_workflow(self, temp_dir):
        """Test: Complete discovery workflow from start to finish"""
        url = "https://example.com/form"

        # Mock form elements
        mock_element = AsyncMock()
        mock_element.evaluate = AsyncMock(
            return_value={
                "tag": "input",
                "type": "email",
                "name": "email",
                "id": "email-field",
                "placeholder": "Enter your email",
                "ariaLabel": "Email",
                "className": "input-field",
            }
        )

        mock_submit = AsyncMock()

        with patch("src.fake_analytics.discovery.async_playwright") as mock_pw:
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.query_selector_all = AsyncMock(return_value=[mock_element])
            mock_page.query_selector = AsyncMock(return_value=mock_submit)
            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_browser.close = AsyncMock()

            mock_playwright = AsyncMock()
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_pw.return_value.__aenter__.return_value = mock_playwright

            import os

            output_path = os.path.join(temp_dir, "discovered_config.json")

            with patch(
                "src.fake_analytics.discovery.click.confirm",
                side_effect=[True, True],  # Generate config, include field
            ):
                with patch(
                    "src.fake_analytics.discovery.click.prompt",
                    side_effect=[output_path, 0.5],
                ):
                    await discover_form_fields(url)

                    # Config file should be created
                    assert os.path.exists(output_path)

                    import json

                    with open(output_path) as f:
                        config = json.load(f)

                        assert config["target_url"] == url
                        assert config["conversion_rate"] == 0.5
                        assert "form_fields" in config

    async def test_discovery_with_multiple_field_types(self):
        """Test: Discovery handles multiple field types"""
        url = "https://example.com"

        # Create different element types
        input_elem = AsyncMock()
        input_elem.evaluate = AsyncMock(
            return_value={
                "tag": "input",
                "type": "text",
                "name": "name",
                "id": "name-id",
                "placeholder": "Name",
                "ariaLabel": "N/A",
                "className": "input",
            }
        )

        textarea_elem = AsyncMock()
        textarea_elem.evaluate = AsyncMock(
            return_value={
                "tag": "textarea",
                "type": "N/A",
                "name": "message",
                "id": "message-id",
                "placeholder": "Your message",
                "ariaLabel": "Message",
                "className": "textarea",
            }
        )

        select_elem = AsyncMock()
        select_elem.evaluate = AsyncMock(
            return_value={
                "tag": "select",
                "type": "N/A",
                "name": "country",
                "id": "country-id",
                "placeholder": "N/A",
                "ariaLabel": "Select country",
                "className": "select",
            }
        )

        with patch("src.fake_analytics.discovery.async_playwright") as mock_pw:
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.query_selector_all = AsyncMock(
                return_value=[input_elem, textarea_elem, select_elem]
            )
            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_browser.close = AsyncMock()

            mock_playwright = AsyncMock()
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_pw.return_value.__aenter__.return_value = mock_playwright

            with patch("src.fake_analytics.discovery.click.confirm", return_value=False):
                # Should handle all element types without error
                await discover_form_fields(url)

                # Should have found all 3 elements
                assert mock_page.query_selector_all.called
