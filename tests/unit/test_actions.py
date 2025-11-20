"""
Unit tests for actions.py module
"""

from unittest.mock import AsyncMock, Mock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from src.fake_analytics.actions import (
    check_proxy_ip,
    fill_form,
    human_type,
    random_mouse_move,
    random_scroll,
    random_sleep,
    setup_network_logging,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestRandomSleep:
    """Test random_sleep function"""

    async def test_random_sleep_completes(self):
        """Test: random_sleep completes without error"""
        await random_sleep(0.01, 0.02)  # Very short sleep for testing

    async def test_random_sleep_respects_range(self):
        """Test: random_sleep duration is within specified range"""
        import time

        min_sec = 0.05
        max_sec = 0.1

        start = time.time()
        await random_sleep(min_sec, max_sec)
        duration = time.time() - start

        # Allow small tolerance for execution overhead
        assert duration >= min_sec * 0.9
        assert duration <= max_sec * 1.2

    @pytest.mark.parametrize("min_sec,max_sec", [(0.01, 0.02), (0.1, 0.2), (0.5, 1.0), (1.0, 2.0)])
    async def test_random_sleep_with_different_ranges(self, min_sec, max_sec):
        """Test: random_sleep works with various time ranges"""
        # Should complete without error
        await random_sleep(min_sec, max_sec)


# TEST: Human Type


@pytest.mark.unit
@pytest.mark.asyncio
class TestHumanType:
    """Test human_type function for realistic typing"""

    async def test_human_type_basic_functionality(self, mock_page):
        """Test: human_type types text into an element"""
        mock_locator = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.wait_for = AsyncMock()
        mock_locator.hover = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.type = AsyncMock()

        mock_page.locator.return_value = mock_locator

        await human_type(mock_page, "#test-input", "Hello")

        mock_page.locator.assert_called_once_with("#test-input")
        mock_locator.wait_for.assert_called_once()
        mock_locator.hover.assert_called_once()
        mock_locator.click.assert_called_once()

        # Should call type for each character
        assert mock_locator.type.call_count == 5  # "Hello" = 5 chars

    async def test_human_type_with_empty_string(self, mock_page):
        """Test: human_type handles empty string"""
        mock_locator = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.wait_for = AsyncMock()
        mock_locator.hover = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.type = AsyncMock()

        mock_page.locator.return_value = mock_locator

        await human_type(mock_page, "#test", "")

        # Should not call type for empty string
        assert mock_locator.type.call_count == 0

    @pytest.mark.parametrize("text", ["A", "Test", "Hello World!", "test@email.com"])
    async def test_human_type_with_various_texts(self, mock_page, text):
        """Test: human_type handles various text inputs"""
        mock_locator = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.wait_for = AsyncMock()
        mock_locator.hover = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.type = AsyncMock()

        mock_page.locator.return_value = mock_locator

        await human_type(mock_page, "#input", text)

        assert mock_locator.type.call_count == len(text)

    async def test_human_type_timeout_propagates(self, mock_page):
        """Test: human_type propagates timeout errors"""
        mock_locator = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.wait_for = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))

        mock_page.locator.return_value = mock_locator

        with pytest.raises(PlaywrightTimeoutError):
            await human_type(mock_page, "#missing", "Text")


# TEST: Random Mouse Move


@pytest.mark.unit
@pytest.mark.asyncio
class TestRandomMouseMove:
    """Test random_mouse_move function"""

    async def test_random_mouse_move_executes(self, mock_page):
        """Test: random_mouse_move executes without error"""
        await random_mouse_move(mock_page)

        # Should have called mouse.move at least once
        assert mock_page.mouse.move.call_count > 0

    async def test_random_mouse_move_stays_in_viewport(self, mock_page):
        """Test: random_mouse_move coordinates stay within viewport"""
        move_calls = []

        async def capture_move(x, y, **_kwargs):
            move_calls.append((x, y))

        mock_page.mouse.move = capture_move

        await random_mouse_move(mock_page)

        # Check all coordinates are within viewport
        width = mock_page.viewport_size["width"]
        height = mock_page.viewport_size["height"]

        for x, y in move_calls:
            assert 0 <= x <= width
            assert 0 <= y <= height

    async def test_random_mouse_move_makes_multiple_moves(self, mock_page):
        """Test: random_mouse_move makes multiple movements"""
        move_count = 0

        async def count_moves(_x, _y, **_kwargs):
            nonlocal move_count
            move_count += 1

        mock_page.mouse.move = count_moves

        await random_mouse_move(mock_page)

        # Should make between 3 and 7 movements
        assert 3 <= move_count <= 7


# TEST: Random Scroll


@pytest.mark.unit
@pytest.mark.asyncio
class TestRandomScroll:
    """Test random_scroll function"""

    async def test_random_scroll_executes(self, mock_page):
        """Test: random_scroll executes without error"""
        await random_scroll(mock_page)

        # Should have called mouse.wheel at least once
        assert mock_page.mouse.wheel.call_count > 0

    async def test_random_scroll_makes_multiple_scrolls(self, mock_page):
        """Test: random_scroll makes multiple scroll actions"""
        scroll_count = 0

        async def count_scrolls(_x, _y):
            nonlocal scroll_count
            scroll_count += 1

        mock_page.mouse.wheel = count_scrolls

        await random_scroll(mock_page)

        # Should scroll 3 to 6 times
        assert 3 <= scroll_count <= 6

    async def test_random_scroll_uses_varying_amounts(self, mock_page):
        """Test: random_scroll uses varying scroll amounts"""
        scroll_amounts = []

        async def capture_scroll(_x, y):
            scroll_amounts.append(y)

        mock_page.mouse.wheel = capture_scroll

        await random_scroll(mock_page)

        # All scroll amounts should be in expected range
        for amount in scroll_amounts:
            assert 100 <= abs(amount) <= 700


# TEST: Fill Form


@pytest.mark.unit
@pytest.mark.asyncio
class TestFillForm:
    """Test fill_form function"""

    async def test_fill_form_with_valid_data(self, mock_page, sample_identity):
        """Test: fill_form successfully fills all fields"""
        form_fields = {
            "full_name": "#name",
            "email": "#email",
            "company": "#company",
        }

        mock_locator = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.wait_for = AsyncMock()
        mock_locator.hover = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.type = AsyncMock()

        mock_page.locator.return_value = mock_locator

        result = await fill_form(mock_page, form_fields, sample_identity)

        assert result is True
        # Should have called locator for each field
        assert mock_page.locator.call_count == len(form_fields)

    async def test_fill_form_with_none_form_fields(self, mock_page, sample_identity):
        """Test: fill_form returns False when form_fields is None"""
        result = await fill_form(mock_page, None, sample_identity)
        assert result is False

    async def test_fill_form_with_empty_form_fields(self, mock_page, sample_identity):
        """Test: fill_form returns False for empty form_fields dict"""
        result = await fill_form(mock_page, {}, sample_identity)
        # Empty form_fields returns False (as per implementation in actions.py)
        assert result is False

    async def test_fill_form_with_missing_identity_field(self, mock_page, capsys):
        """Test: fill_form skips fields not in identity"""
        form_fields = {
            "full_name": "#name",
            "nonexistent_field": "#missing",
        }
        identity = {"full_name": "Test User"}

        mock_locator = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.wait_for = AsyncMock()
        mock_locator.hover = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.type = AsyncMock()

        mock_page.locator.return_value = mock_locator

        await fill_form(mock_page, form_fields, identity)

        captured = capsys.readouterr()
        assert "No data provided for form field 'nonexistent_field'" in captured.out

    async def test_fill_form_handles_timeout_error(self, mock_page, sample_identity):
        """Test: fill_form handles timeout errors gracefully"""
        form_fields = {"full_name": "#name"}

        mock_locator = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.wait_for = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))

        mock_page.locator.return_value = mock_locator

        result = await fill_form(mock_page, form_fields, sample_identity)

        # Should return False due to timeout
        assert result is False

    async def test_fill_form_continues_after_one_field_fails(self, mock_page, sample_identity):
        """Test: fill_form continues filling other fields after one fails"""
        form_fields = {
            "full_name": "#name",
            "email": "#email",
        }

        call_count = 0

        def locator_side_effect(selector):
            nonlocal call_count
            call_count += 1
            mock_locator = AsyncMock()
            mock_locator.first = mock_locator

            if selector == "#name":
                # First field fails
                mock_locator.wait_for = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))
            else:
                # Second field succeeds
                mock_locator.wait_for = AsyncMock()
                mock_locator.hover = AsyncMock()
                mock_locator.click = AsyncMock()
                mock_locator.type = AsyncMock()

            return mock_locator

        mock_page.locator.side_effect = locator_side_effect

        result = await fill_form(mock_page, form_fields, sample_identity)

        # Should have tried both fields
        assert call_count == 2
        # Should return False because one field failed
        assert result is False

    @pytest.mark.parametrize(
        "form_fields,identity",
        [
            (
                {"email": "#email"},
                {"email": "test@example.com"},
            ),
            (
                {"full_name": "#name", "company": "#company"},
                {"full_name": "Test", "company": "TestCo"},
            ),
        ],
    )
    async def test_fill_form_with_various_field_combinations(
        self, mock_page, form_fields, identity
    ):
        """Test: fill_form works with various field combinations"""
        mock_locator = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.wait_for = AsyncMock()
        mock_locator.hover = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.type = AsyncMock()

        mock_page.locator.return_value = mock_locator

        result = await fill_form(mock_page, form_fields, identity)
        assert result is True


# TEST: Check Proxy IP


@pytest.mark.unit
@pytest.mark.asyncio
class TestCheckProxyIP:
    """Test check_proxy_ip function"""

    async def test_check_proxy_ip_returns_default_on_error(self, mock_page):
        """Test: check_proxy_ip returns default geo info on error"""
        mock_page.goto = AsyncMock(side_effect=Exception("Network error"))

        result = await check_proxy_ip(mock_page, verbose=False)

        assert isinstance(result, dict)
        assert "country" in result
        assert "timezone" in result
        assert "locale" in result
        assert result["country"] == "US"  # Default

    async def test_check_proxy_ip_with_successful_response(self, mock_page):
        """Test: check_proxy_ip parses successful API response"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = AsyncMock(
            return_value='{"status":"success","country":"United Kingdom","countryCode":"GB","timezone":"Europe/London","query":"1.2.3.4"}'
        )

        mock_page.goto = AsyncMock(return_value=mock_response)

        result = await check_proxy_ip(mock_page, verbose=False)

        assert result["country"] == "GB"
        assert result["timezone"] == "Europe/London"
        assert result["locale"] == "en-GB"
        assert result["ip"] == "1.2.3.4"

    @pytest.mark.parametrize(
        "country_code,expected_locale",
        [
            ("US", "en-US"),
            ("GB", "en-GB"),
            ("FR", "fr-FR"),
            ("DE", "de-DE"),
            ("JP", "ja-JP"),
            ("CN", "zh-CN"),
            ("TH", "th-TH"),
            ("BR", "pt-BR"),
        ],
    )
    async def test_check_proxy_ip_locale_mapping(self, mock_page, country_code, expected_locale):
        """Test: check_proxy_ip correctly maps country codes to locales"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = AsyncMock(
            return_value=f'{{"status":"success","countryCode":"{country_code}","timezone":"UTC","query":"1.1.1.1"}}'
        )

        mock_page.goto = AsyncMock(return_value=mock_response)

        result = await check_proxy_ip(mock_page, verbose=False)

        assert result["locale"] == expected_locale

    async def test_check_proxy_ip_verbose_mode(self, mock_page, capsys):
        """Test: check_proxy_ip prints debug info in verbose mode"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = AsyncMock(
            return_value='{"status":"success","country":"Canada","countryCode":"CA","timezone":"America/Toronto","query":"5.6.7.8"}'
        )

        mock_page.goto = AsyncMock(return_value=mock_response)

        await check_proxy_ip(mock_page, verbose=True)

        captured = capsys.readouterr()
        assert "Verifying proxy connection" in captured.out
        assert "5.6.7.8" in captured.out
        assert "Canada" in captured.out

    async def test_check_proxy_ip_fallback_to_ipify(self, mock_page):
        """Test: check_proxy_ip falls back to ipify when ip-api fails"""
        # First call fails, second call is fallback
        call_count = 0

        async def goto_side_effect(_url, **_kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # ip-api.com fails
                mock_resp = Mock()
                mock_resp.ok = False
                return mock_resp
            else:
                # ipify fallback
                mock_resp = Mock()
                mock_resp.ok = True
                return mock_resp

        mock_page.goto = AsyncMock(side_effect=goto_side_effect)
        mock_page.content = AsyncMock(return_value='{"ip":"9.9.9.9"}')
        mock_page.inner_text = AsyncMock(return_value='{"ip":"9.9.9.9"}')

        result = await check_proxy_ip(mock_page, verbose=True)

        # Should return default values
        assert "country" in result


# TEST: Setup Network Logging


@pytest.mark.unit
class TestSetupNetworkLogging:
    """Test setup_network_logging function"""

    def test_setup_network_logging_attaches_listeners(self, mock_page):
        """Test: setup_network_logging attaches event listeners to page"""
        setup_network_logging(mock_page)

        # Should have attached multiple event listeners
        assert mock_page.on.call_count >= 4

        # Check that required events are registered
        calls = [call[0][0] for call in mock_page.on.call_args_list]
        assert "request" in calls
        assert "response" in calls
        assert "requestfailed" in calls
        assert "console" in calls

    def test_setup_network_logging_does_not_crash(self, mock_page):
        """Test: setup_network_logging executes without error"""
        # Should not raise any exceptions
        setup_network_logging(mock_page)

    def test_setup_network_logging_with_websocket(self, mock_page):
        """Test: setup_network_logging registers websocket listener"""
        setup_network_logging(mock_page)

        calls = [call[0][0] for call in mock_page.on.call_args_list]
        assert "websocket" in calls
