import asyncio
import os
import random
import shutil
import tempfile
import threading

from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
)
from playwright.async_api import (
    async_playwright,
)

from . import actions, data
from .config import Config
from .logger import get_logger


class TrafficBot:
    def __init__(self, config: Config, identity: dict | None = None):
        self.config = config
        self.identity = identity
        self.thread_id = threading.get_ident()
        self.logger = get_logger(config.verbose, thread_id=self.thread_id)

    async def run(self):
        self.logger.info("Starting Traffic Bot...", "bold cyan", self.thread_id)
        proxy_config = self.config.get_proxy_config()
        use_proxy = self.config.use_proxy

        if proxy_config and use_proxy:
            masked = (
                proxy_config["password"][:2] + "****" if proxy_config.get("password") else "None"
            )
            username_display = proxy_config.get("username", "None")

            if "__cr." in username_display:
                parts = username_display.split("__cr.")
                if len(parts) == 2:
                    username_display = f"{parts[0]}__cr.****"

            self.logger.proxy_config(
                proxy_config["server"], username_display, masked, self.thread_id
            )
        else:
            self.logger.warning("Running without proxy (Local IP mode)", self.thread_id)
            use_proxy = False

        referer = data.get_referer(self.config.referers)
        user_agent = data.USER_AGENT

        self.logger.debug(f"Configuration: Referer={referer}", self.thread_id)
        self.logger.debug(f"User-Agent: {user_agent}", self.thread_id)

        async with async_playwright() as p:
            args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--ignore-certificate-errors",
                "--ignore-ssl-errors",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ]

            is_ci = os.getenv("CI") == "true"
            headless_mode = is_ci

            geo_info = {
                "country": "US",
                "timezone": "America/New_York",
                "locale": "en-US",
            }

            if use_proxy and proxy_config:
                self.logger.debug("Detecting proxy IP location...", self.thread_id)
                temp_browser = await p.chromium.launch(headless=True, args=args)
                temp_proxy_config = {"server": proxy_config["server"]}
                if proxy_config.get("username"):
                    temp_proxy_config["username"] = proxy_config["username"]
                if proxy_config.get("password"):
                    temp_proxy_config["password"] = proxy_config["password"]

                temp_context = await temp_browser.new_context(proxy=temp_proxy_config)
                temp_page = await temp_context.new_page()
                try:
                    geo_info = await actions.check_proxy_ip(temp_page, verbose=self.config.verbose)
                finally:
                    await temp_context.close()
                    await temp_browser.close()

            self.logger.debug(
                f"Using timezone: {geo_info.get('timezone', 'America/New_York')}, locale: {geo_info.get('locale', 'en-US')}",
                self.thread_id,
            )

            launch_kwargs = {
                "headless": headless_mode,
                "args": args,
                "user_agent": user_agent,
                "viewport": {"width": 1440, "height": 900},
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

            user_data_dir = tempfile.mkdtemp(prefix="chrome_profile_")
            self.logger.debug(f"Created temporary profile at: {user_data_dir}", self.thread_id)

            try:
                context = await p.chromium.launch_persistent_context(user_data_dir, **launch_kwargs)

                page = context.pages[0] if context.pages else await context.new_page()

                await page.set_extra_http_headers({"Referer": referer, "DNT": "0"})

                await page.add_init_script(
                    """
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition = function(success, error) {
                            if (error) error({ code: 1, message: "User denied Geolocation" });
                        };
                        navigator.geolocation.watchPosition = function(success, error) {
                            if (error) error({ code: 1, message: "User denied Geolocation" });
                            return 1;
                        };
                    }

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

                if self.config.verbose:
                    actions.setup_network_logging(page)

                try:
                    self.logger.navigation(self.config.target_url, self.thread_id)
                    await page.goto(
                        self.config.target_url,
                        timeout=120000,
                        wait_until="domcontentloaded",
                    )

                    self.logger.debug("Waiting for network idle...", self.thread_id)
                    try:
                        await page.wait_for_load_state("networkidle", timeout=60000)
                    except PlaywrightTimeoutError:
                        self.logger.debug("Network idle wait timed out.", self.thread_id)

                    await asyncio.sleep(random.uniform(5, 8))

                    self.logger.page_loaded(self.thread_id)

                    await actions.random_sleep(2, 5)
                    await actions.random_mouse_move(page)
                    await actions.random_scroll(page)

                    should_convert = random.random() <= self.config.conversion_rate
                    if should_convert and self.config.form_fields:
                        identity_to_use = (
                            self.identity
                            if self.identity
                            else data.generate_identity(self.config.locale)
                        )

                        self.logger.form_submission(
                            identity_to_use.get("full_name", "Unknown"), self.thread_id
                        )

                        form_completed = await actions.fill_form(
                            page, self.config.form_fields, identity_to_use
                        )
                        if form_completed and self.config.submit_button:
                            submit_btn = await page.query_selector(self.config.submit_button)
                            if submit_btn:
                                await actions.random_mouse_move(page)
                                await submit_btn.hover()
                                await asyncio.sleep(1.0)
                                await submit_btn.click()
                                self.logger.success("Form submitted.", self.thread_id)

                                await asyncio.sleep(15)
                                screenshot_path = f"success_screenshot_{self.thread_id}.png"
                                await page.screenshot(path=screenshot_path)
                                self.logger.screenshot(screenshot_path, self.thread_id)
                            else:
                                self.logger.warning(
                                    f"Submit button not found with selector: {self.config.submit_button}",
                                    self.thread_id,
                                )
                        else:
                            self.logger.warning(
                                "Form not submitted. Check completion status or submit button config.",
                                self.thread_id,
                            )
                    else:
                        self.logger.bounce(self.thread_id)

                    self.logger.debug("Final dwell time...", self.thread_id)
                    await actions.random_sleep(8, 12)

                except Exception as e:
                    self.logger.error(f"Error: {e}", self.thread_id)
                    error_path = f"error_screenshot_{self.thread_id}.png"
                    await page.screenshot(path=error_path)
                    self.logger.screenshot(error_path, self.thread_id)
                finally:
                    await context.close()
            finally:
                try:
                    shutil.rmtree(user_data_dir)
                    self.logger.debug(f"Removed temporary profile: {user_data_dir}", self.thread_id)
                except Exception as e:
                    self.logger.debug(f"Failed to remove temporary profile: {e}", self.thread_id)
