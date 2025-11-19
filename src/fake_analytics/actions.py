import asyncio
import json
import random

from playwright.async_api import (
    Page,
    Request,
    Response,
    WebSocket,
)
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
)


async def random_sleep(min_seconds=1.0, max_seconds=3.0):
    """Random sleep to simulate human pause"""
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


async def human_type(page: Page, selector: str, text: str):
    """Type text with variable delays between keystrokes"""
    locator = page.locator(selector).first
    await locator.wait_for(state="visible", timeout=10000)
    await locator.hover()
    await locator.click()
    for char in text:
        await locator.type(char, delay=random.randint(50, 200))
    await random_sleep(0.5, 1.5)


async def random_mouse_move(page: Page):
    """Randomly move mouse across the screen using Bezier-like steps"""
    width = page.viewport_size["width"]
    height = page.viewport_size["height"]

    for _ in range(random.randint(3, 7)):
        _start_x, _start_y = random.randint(0, width), random.randint(0, height)
        end_x, end_y = random.randint(0, width), random.randint(0, height)

        steps = random.randint(20, 50)
        await page.mouse.move(end_x, end_y, steps=steps)
        await asyncio.sleep(random.uniform(0.1, 0.5))


async def random_scroll(page: Page):
    """Scroll randomly up and down"""
    for _ in range(random.randint(3, 6)):
        scroll_amount = random.randint(100, 700)
        direction = random.choice([1, 1, 1, -1])
        await page.mouse.wheel(0, scroll_amount * direction)
        await asyncio.sleep(random.uniform(1.0, 3.0))


async def fill_form(page: Page, form_fields: dict, identity: dict) -> bool:
    """Fills a form based on a flexible mapping of fields to selectors."""
    if not form_fields:
        print("No form fields defined in the configuration.")
        return False

    all_fields_filled = True
    for field_name, selector in form_fields.items():
        if field_name not in identity:
            print(f"Warning: No data provided for form field '{field_name}'.")
            continue

        try:
            await human_type(page, selector, identity[field_name])
            print(f"Filled '{field_name}' field using selector '{selector}'.")
        except PlaywrightTimeoutError:
            print(f"Failed to locate field '{field_name}' with selector '{selector}'.")
            all_fields_filled = False
        except Exception as e:
            print(f"Selector {selector} for '{field_name}' failed with error: {e}")
            all_fields_filled = False

    return all_fields_filled


async def check_proxy_ip(page: Page, verbose: bool = False) -> dict:
    """Verify proxy IP connection and return geo info"""
    if verbose:
        print("Verifying proxy connection...")
    geo_info = {"country": "US", "timezone": "America/New_York", "locale": "en-US"}
    try:
        response = await page.goto(
            "http://ip-api.com/json/?fields=status,country,countryCode,timezone,query",
            timeout=60000,
            wait_until="commit",
        )
        if response and response.ok:
            content = await response.text()
            geo_data = json.loads(content)
            if geo_data.get("status") == "success":
                country_code = geo_data.get("countryCode", "US")
                timezone = geo_data.get("timezone", "America/New_York")
                country = geo_data.get("country", "United States")
                ip = geo_data.get("query", "unknown")

                if verbose:
                    print(f"Proxy IP: {ip}")
                    print(f"Detected Location: {country} ({country_code})")
                    print(f"Timezone: {timezone}")

                # Use geo_utils for locale mapping and timezone fallback
                from .geo_utils import get_locale_for_country, get_timezone_for_country

                # Use API timezone if available, otherwise fallback to country mapping
                final_timezone = timezone if timezone else get_timezone_for_country(country_code)
                locale = get_locale_for_country(country_code)

                geo_info = {
                    "country": country_code,
                    "country_name": country,
                    "timezone": final_timezone or "UTC",
                    "locale": locale,
                    "ip": ip,
                }
        else:
            # Fallback to simple IP check
            await page.goto("https://api.ipify.org?format=json", timeout=60000)
            content = await page.content()
            if verbose:
                print(f"Current IP Info (ipify): {await page.inner_text('body')}")
    except Exception as e:
        if verbose:
            print(f"Failed to verify IP: {e}")

    return geo_info


def setup_network_logging(page: Page):
    """Log interesting network requests to debug analytics blocking"""

    def on_request(request: Request):
        if request.resource_type not in ["image", "font", "stylesheet", "media"]:
            print(f" >> [REQ] {request.method} {request.url[:100]}")

    def on_response(response: Response):
        if response.request.resource_type not in [
            "image",
            "font",
            "stylesheet",
            "media",
        ]:
            status = response.status
            status_text = "OK" if 200 <= status < 300 else "FAILED"
            # Only log failures or API calls to reduce noise
            if status >= 400 or "api" in response.url or "genma" in response.url:
                print(f" << [RES] {status} {status_text} {response.url[:100]}")

    def on_request_failed(request: Request):
        if request.resource_type not in ["image", "font", "stylesheet"]:
            print(f" !! [FAIL] {request.failure} {request.url[:100]}")

    def on_websocket(ws: WebSocket):
        print(f" >> [WS] WebSocket opened: {ws.url}")

    # Listen to console errors too
    page.on(
        "console",
        lambda msg: (print(f"BROWSER CONSOLE: {msg.text}") if msg.type == "error" else None),
    )

    page.on("request", on_request)
    page.on("response", on_response)
    page.on("requestfailed", on_request_failed)
    page.on("websocket", on_websocket)
