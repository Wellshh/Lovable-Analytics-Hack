import json
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self, config_path=None, verbose=False):
        self.target_url = os.getenv("TARGET_URL", "https://genma.lovable.app/")
        self.conversion_rate = float(os.getenv("CONVERSION_RATE", "1.0"))
        self.proxy_host = os.getenv("PROXY_HOST", "gw.dataimpulse.com:823")
        self.proxy_user = os.getenv("PROXY_USER")
        self.proxy_pass = os.getenv("PROXY_PASS")
        self.proxy_countries = os.getenv("PROXY_COUNTRIES", "")
        self.use_proxy = bool(self.proxy_user and self.proxy_pass)
        self.verbose = verbose

        self.form_fields = None
        self.submit_button = None
        self.referers = None
        self.locale = "en_US"

        if config_path:
            self.load_from_file(config_path)

        self.validate()

    def load_from_file(self, path):
        """Load configuration from a JSON file."""
        from pathlib import Path

        try:
            with Path(path).open(encoding="utf-8") as f:
                config_data = json.load(f)

            self.target_url = config_data.get("target_url", self.target_url)
            self.conversion_rate = config_data.get("conversion_rate", self.conversion_rate)
            self.form_fields = config_data.get("form_fields")
            self.submit_button = config_data.get("submit_button")
            self.referers = config_data.get("referers")
            self.locale = config_data.get("locale", self.locale)

        except FileNotFoundError as e:
            raise ValueError(f"Configuration file not found at: {path}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {path}") from e

    def validate(self):
        if not 0 <= self.conversion_rate <= 1:
            raise ValueError("CONVERSION_RATE must be between 0 and 1.")

    def get_proxy_config(self):
        if not self.proxy_user or not self.proxy_pass:
            return None
        if self.proxy_countries:
            countries_str = self.proxy_countries.replace(" ", "")
            username_with_countries = f"{self.proxy_user}__cr.{countries_str}"
            return {
                "server": f"http://{self.proxy_host}",
                "username": username_with_countries,
                "password": self.proxy_pass,
            }
        else:
            return {
                "server": f"http://{self.proxy_host}",
                "username": self.proxy_user,
                "password": self.proxy_pass,
            }
