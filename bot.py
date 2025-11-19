import asyncio
import json
import random
import os
import shutil
import tempfile
from playwright.async_api import (
    async_playwright,
    Page,
    Request,
    Response,
    TimeoutError as PlaywrightTimeoutError,
    WebSocket,
)

# from playwright_stealth import stealth_async # Disabled for clean test
from config import Config
from fake_useragent import UserAgent


class TrafficBot:
    def __init__(self):
        self.ua = UserAgent(
            os="linux"
        )  # Force linux/desktop UA to avoid mobile inconsistencies
        self.referers = [
            "https://www.facebook.com/",  # Primary source (weighted)
            "https://www.facebook.com/",
            "https://www.facebook.com/",
            "https://www.facebook.com/",
            "https://www.reddit.com/",
            # "https://twitter.com/",
            # "https://x.com/",
            # "https://www.linkedin.com/",
        ]
        self.email_domains = [
            "gmail.com",
            "hotmail.com",
            "outlook.com",
            "yahoo.com",
            "proton.me",
            "icloud.com",
            "aol.com",
        ]
        self.company_suffixes = [
            "Labs",
            "Studio",
            "Solutions",
            "Digital",
            "Analytics",
            "Partners",
            "Collective",
        ]
        self.first_names = [
            "Alex",
            "Bella",
            "Carlos",
            "Diana",
            "Ethan",
            "Fiona",
            "Gabriel",
            "Hannah",
            "Isaac",
            "Julia",
            "Kevin",
            "Lara",
            "Mason",
            "Nina",
            "Owen",
            "Pablo",
            "Quinn",
            "Riley",
            "Sofia",
            "Tyler",
            "Valerie",
        ]
        self.last_names = [
            "Anderson",
            "Bennett",
            "Chang",
            "Diaz",
            "Evans",
            "Foster",
            "Garcia",
            "Hughes",
            "Ibarra",
            "Jackson",
            "Kelley",
            "Lopez",
            "Mitchell",
            "Nguyen",
            "Owens",
            "Parker",
            "Quintana",
            "Reed",
            "Sullivan",
            "Turner",
            "Valdez",
        ]

    async def random_sleep(self, min_seconds=1.0, max_seconds=3.0):
        """Random sleep to simulate human pause"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def human_type(self, page: Page, selector: str, text: str):
        """Type text with variable delays between keystrokes"""
        locator = page.locator(selector).first
        await locator.wait_for(state="visible", timeout=10000)
        await locator.hover()
        await locator.click()
        # Type with occasional mistakes and corrections could be added here
        for char in text:
            await locator.type(char, delay=random.randint(50, 200))
        await self.random_sleep(0.5, 1.5)

    async def random_mouse_move(self, page: Page):
        """Randomly move mouse across the screen using Bezier-like steps"""
        width = page.viewport_size["width"]
        height = page.viewport_size["height"]

        # Perform multiple random movements
        for _ in range(random.randint(3, 7)):
            start_x, start_y = random.randint(0, width), random.randint(0, height)
            end_x, end_y = random.randint(0, width), random.randint(0, height)

            # Simple smooth movement simulation
            steps = random.randint(20, 50)
            await page.mouse.move(end_x, end_y, steps=steps)
            await asyncio.sleep(random.uniform(0.1, 0.5))

    async def random_scroll(self, page: Page):
        """Scroll randomly up and down"""
        for _ in range(random.randint(3, 6)):
            scroll_amount = random.randint(100, 700)
            direction = random.choice([1, 1, 1, -1])  # Mostly scroll down
            await page.mouse.wheel(0, scroll_amount * direction)
            await asyncio.sleep(random.uniform(1.0, 3.0))

    def generate_identity(self) -> dict:
        """Generate a realistic identity and email address"""
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        suffix = random.choice(self.company_suffixes)
        number_suffix = str(random.randint(1, 97)) if random.random() < 0.35 else ""
        separator = random.choice([".", "_", ""])
        email = f"{first}{separator}{last}{number_suffix}@{random.choice(self.email_domains)}"
        email = email.lower()
        company = f"{last} {suffix}"
        return {
            "company": company,
            "email": email,
            "full_name": f"{first} {last}",
        }

    async def fill_visibility_form(self, page: Page, identity: dict) -> bool:
        """Fill the Genma visibility form if fields are available"""
        field_definitions = [
            {
                "name": "company",
                "value": identity["company"],
                "selectors": [
                    "input[placeholder='Your Company Name']",
                    "input[placeholder*='Company']",
                    "input[name='company']",
                    "input[name*='company']",
                ],
            },
            {
                "name": "email",
                "value": identity["email"],
                "selectors": [
                    "input[placeholder='Your Email']",
                    "input[placeholder*='Email']",
                    "input[name='email']",
                    "input[type='email']",
                ],
            },
        ]

        for field in field_definitions:
            filled = False
            for selector in field["selectors"]:
                try:
                    await self.human_type(page, selector, field["value"])
                    print(f"Filled {field['name']} field.")
                    filled = True
                    break
                except PlaywrightTimeoutError:
                    continue
                except Exception as e:
                    print(f"Selector {selector} failed with error: {e}")
                    continue

            if not filled:
                print(f"Failed to locate {field['name']} field.")
                return False

        return True

    async def check_proxy_ip(self, page: Page) -> dict:
        """Verify proxy IP connection and return geo info"""
        print("Verifying proxy connection...")
        geo_info = {"country": "US", "timezone": "America/New_York", "locale": "en-US"}
        try:
            # Try ip-api.com for detailed geo info
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

                    print(f"Proxy IP: {ip}")
                    print(f"Detected Location: {country} ({country_code})")
                    print(f"Timezone: {timezone}")

                    # Map country to locale (complete list including all DataImpulse countries)
                    locale_map = {
                        "US": "en-US",
                        "GB": "en-GB",
                        "CA": "en-CA",
                        "AU": "en-AU",
                        "SG": "en-SG",
                        "MY": "en-MY",
                        "TH": "th-TH",  # Thailand
                        "MM": "my-MM",  # Myanmar (Burmese)
                        "CN": "zh-CN",  # China
                        "DE": "de-DE",  # Germany
                        "JP": "ja-JP",  # Japan
                        "IN": "en-IN",
                        "FR": "fr-FR",
                        "ES": "es-ES",
                        "IT": "it-IT",
                        "KR": "ko-KR",
                        "TW": "zh-TW",
                        "BR": "pt-BR",
                        "MX": "es-MX",
                        "NL": "nl-NL",
                        "SE": "sv-SE",
                    }

                    geo_info = {
                        "country": country_code,
                        "country_name": country,
                        "timezone": timezone,
                        "locale": locale_map.get(country_code, "en-US"),
                        "ip": ip,
                    }
            else:
                # Fallback to simple IP check
                await page.goto("https://api.ipify.org?format=json", timeout=60000)
                content = await page.content()
                print(f"Current IP Info (ipify): {await page.inner_text('body')}")
        except Exception as e:
            print(f"Failed to verify IP: {e}")

        return geo_info

    def setup_network_logging(self, page: Page):
        """Log interesting network requests to debug analytics blocking"""

        # Log ALL non-static requests to find hidden API calls
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
            # ws.on("framesent", lambda payload: print(f" -> WS SENT: {payload}"))
            # ws.on("framereceived", lambda payload: print(f" <- WS RECV: {payload}"))

        # Listen to console errors too
        page.on(
            "console",
            lambda msg: (
                print(f"BROWSER CONSOLE: {msg.text}") if msg.type == "error" else None
            ),
        )

        page.on("request", on_request)
        page.on("response", on_response)
        page.on("requestfailed", on_request_failed)
        page.on("websocket", on_websocket)

    async def run(self):
        print("Starting Traffic Bot...")
        Config.validate()

        proxy_config = Config.get_proxy_config()
        # Enable proxy for production use
        use_proxy = True

        if proxy_config and use_proxy:
            # Mask password for logging
            masked = (
                proxy_config["password"][:2] + "****"
                if proxy_config.get("password")
                else "None"
            )
            username_display = proxy_config.get("username", "None")
            # Mask countries in username if it's DataImpulse format (contains __cr.)
            if "__cr." in username_display:
                # Show: user__cr.**** instead of full countries list
                parts = username_display.split("__cr.")
                if len(parts) == 2:
                    username_display = f"{parts[0]}__cr.****"
            print(
                f"Proxy Config: Server={proxy_config['server']}, User={username_display}, Pass={masked}"
            )
        else:
            print("WARNING: Running without proxy (Local IP mode)")
            use_proxy = False  # Force disable if no proxy config

        referer = random.choice(self.referers)

        # Use user's ACTUAL UA (or a very standard one) to avoid mismatch
        # This UA is from a standard Mac Chrome, safer for local testing
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        print(f"Configuration: Referer={referer}, UA={user_agent}")

        async with async_playwright() as p:
            args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--ignore-certificate-errors",
                "--ignore-ssl-errors",
                "--disable-web-security",  # DISABLE CORS
                "--disable-features=IsolateOrigins,site-per-process",  # DISABLE ISOLATION
                # f"--user-agent={user_agent}",  # Don't enforce UA at launch in persistent mode, let it default or use context
            ]

            is_ci = os.getenv("CI") == "true"
            headless_mode = is_ci

            # Default geo settings
            geo_info = {
                "country": "US",
                "timezone": "America/New_York",
                "locale": "en-US",
            }

            # If using proxy, detect IP location first to set correct timezone/locale
            if use_proxy and proxy_config:
                print("Detecting proxy IP location...")
                temp_browser = await p.chromium.launch(headless=True, args=args)
                temp_proxy_config = {"server": proxy_config["server"]}
                if proxy_config.get("username"):
                    temp_proxy_config["username"] = proxy_config["username"]
                if proxy_config.get("password"):
                    temp_proxy_config["password"] = proxy_config["password"]

                temp_context = await temp_browser.new_context(proxy=temp_proxy_config)
                temp_page = await temp_context.new_page()
                try:
                    geo_info = await self.check_proxy_ip(temp_page)
                finally:
                    await temp_context.close()
                    await temp_browser.close()

            print(
                f"Using timezone: {geo_info.get('timezone', 'America/New_York')}, locale: {geo_info.get('locale', 'en-US')}"
            )

            launch_kwargs = {
                "headless": headless_mode,
                "args": args,
                "user_agent": user_agent,
                "viewport": {"width": 1440, "height": 900},  # Standard Mac resolution
                "locale": geo_info.get("locale", "en-US"),
                "timezone_id": geo_info.get("timezone", "America/New_York"),
            }

            if use_proxy and proxy_config:
                proxy_kwargs = {
                    "server": proxy_config["server"],
                    "bypass": "*.supabase.co,supabase.co",
                }
                if proxy_config.get("username"):
                    proxy_kwargs["username"] = proxy_config["username"]
                if proxy_config.get("password"):
                    proxy_kwargs["password"] = proxy_config["password"]

                launch_kwargs["proxy"] = proxy_kwargs

            # Create a temporary directory for the user profile
            user_data_dir = tempfile.mkdtemp(prefix="chrome_profile_")
            print(f"Created temporary profile at: {user_data_dir}")

            try:
                # Use persistent_context to simulate real user profile
                context = await p.chromium.launch_persistent_context(
                    user_data_dir, **launch_kwargs
                )

                page = context.pages[0] if context.pages else await context.new_page()

                # Set extra headers manually since persistent context constructor doesn't take extra_http_headers easily in all versions
                await page.set_extra_http_headers({"Referer": referer, "DNT": "0"})

                # CRITICAL: Disable Geolocation API to prevent location leakage
                await page.add_init_script(
                    """
                    // Override geolocation API
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition = function(success, error) {
                            if (error) error({ code: 1, message: "User denied Geolocation" });
                        };
                        navigator.geolocation.watchPosition = function(success, error) {
                            if (error) error({ code: 1, message: "User denied Geolocation" });
                            return 1;
                        };
                    }
                    
                    // Disable WebRTC to prevent IP leakage
                    const noop = () => {};
                    if (window.RTCPeerConnection) {
                        window.RTCPeerConnection = undefined;
                    }
                    if (window.webkitRTCPeerConnection) {
                        window.webkitRTCPeerConnection = undefined;
                    }
                    if (window.mozRTCPeerConnection) {
                        window.mozRTCPeerConnection = undefined;
                    }
                """
                )

                # 1. Disable Stealth for a clean run (sometimes stealth injection IS the fingerprint)
                # await stealth_async(page)

                # 2. Disable Custom Hardware Spoofing
                # await self.inject_stealth_scripts(page)

                # 3. Setup Diagnostic Logging
                self.setup_network_logging(page)

                try:

                    print(f"Navigating to {Config.TARGET_URL}")
                    await page.goto(
                        Config.TARGET_URL,
                        timeout=120000,
                        wait_until="domcontentloaded",
                    )

                    print("Waiting for network idle...")
                    try:
                        await page.wait_for_load_state("networkidle", timeout=60000)
                    except PlaywrightTimeoutError:
                        print("Network idle wait timed out.")

                    # Wait for analytics initialization
                    await asyncio.sleep(random.uniform(5, 8))

                    # Manually accept cookies if selector known (optional)
                    # await self.accept_cookies(page)

                    print("Page loaded.")

                    # Interaction
                    await self.random_sleep(2, 5)
                    await self.random_mouse_move(page)
                    await self.random_scroll(page)

                    # Form Logic
                    print("Looking for form...")
                    should_convert = random.random() <= Config.CONVERSION_RATE
                    if should_convert:
                        identity = self.generate_identity()
                        print(f"Submitting as {identity['full_name']}...")

                        form_completed = await self.fill_visibility_form(page, identity)
                        if form_completed:
                            submit_btn = await page.query_selector(
                                "button[type='submit'], button:has-text('Get My Genma Analysis'), button:has-text('Get report')"
                            )
                            if submit_btn:
                                await self.random_mouse_move(page)
                                await submit_btn.hover()
                                await asyncio.sleep(
                                    1.0
                                )  # Deliberate pause before click
                                await submit_btn.click()
                                print("Form submitted.")

                                # Capture screenshot
                                await asyncio.sleep(15)  # Long wait for processing
                                await page.screenshot(path="success_screenshot.png")
                                print("Screenshot saved.")
                            else:
                                print("Submit button not found.")
                        else:
                            print("Form fields not found.")
                    else:
                        print("Simulating bounce.")

                    print("Final dwell time...")
                    await self.random_sleep(8, 12)

                except Exception as e:
                    print(f"Error: {e}")
                    await page.screenshot(path="error_screenshot.png")
                finally:
                    await context.close()
                    # browser object is not available in persistent context mode as context IS the browser
                    # await browser.close()
            finally:
                # Clean up the temporary directory
                try:
                    shutil.rmtree(user_data_dir)
                    print(f"Removed temporary profile: {user_data_dir}")
                except Exception as e:
                    print(f"Failed to remove temporary profile: {e}")


if __name__ == "__main__":
    bot = TrafficBot()
    asyncio.run(bot.run())
