import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TARGET_URL = os.getenv("TARGET_URL", "https://genma.lovable.app/")
    CONVERSION_RATE = float(os.getenv("CONVERSION_RATE", "1.0"))
    PROXY_HOST = os.getenv("PROXY_HOST", "gw.dataimpulse.com:823")
    PROXY_USER = os.getenv("PROXY_USER")
    PROXY_PASS = os.getenv("PROXY_PASS")
    PROXY_COUNTRIES = os.getenv("PROXY_COUNTRIES", "")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.PROXY_USER:
            missing.append("PROXY_USER")
        if not cls.PROXY_PASS:
            missing.append("PROXY_PASS")

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        if not 0 <= cls.CONVERSION_RATE <= 1:
            raise ValueError("CONVERSION_RATE must be between 0 and 1.")

    @classmethod
    def get_proxy_config(cls):
        if not cls.PROXY_USER or not cls.PROXY_PASS:
            return None
        if cls.PROXY_COUNTRIES:
            countries_str = cls.PROXY_COUNTRIES.replace(" ", "")  # Remove spaces
            username_with_countries = f"{cls.PROXY_USER}__cr.{countries_str}"
            return {
                "server": f"http://{cls.PROXY_HOST}",
                "username": username_with_countries,
                "password": cls.PROXY_PASS,
            }
        else:
            return {
                "server": f"http://{cls.PROXY_HOST}",
                "username": cls.PROXY_USER,
                "password": cls.PROXY_PASS,
            }
