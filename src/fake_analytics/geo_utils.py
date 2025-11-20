"""
Geographic utilities for country, timezone, and locale mapping.
Uses pytz for country-timezone mapping and provides locale mappings.
"""

import contextlib

try:
    import pytz

    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    pytz = None

LOCALE_MAP = {
    "US": "en-US",
    "GB": "en-GB",
    "CA": "en-CA",
    "AU": "en-AU",
    "NZ": "en-NZ",
    "IE": "en-IE",
    "ZA": "en-ZA",
    "SG": "en-SG",
    "MY": "en-MY",
    "IN": "en-IN",
    "PH": "en-PH",
    "HK": "en-HK",
    "DE": "de-DE",
    "AT": "de-AT",
    "CH": "de-CH",
    "FR": "fr-FR",
    "BE": "fr-BE",
    "ES": "es-ES",
    "MX": "es-MX",
    "AR": "es-AR",
    "CO": "es-CO",
    "CL": "es-CL",
    "IT": "it-IT",
    "PT": "pt-PT",
    "BR": "pt-BR",
    "NL": "nl-NL",
    "PL": "pl-PL",
    "RU": "ru-RU",
    "SE": "sv-SE",
    "NO": "nb-NO",
    "DK": "da-DK",
    "FI": "fi-FI",
    "GR": "el-GR",
    "CZ": "cs-CZ",
    "HU": "hu-HU",
    "RO": "ro-RO",
    "CN": "zh-CN",
    "TW": "zh-TW",
    "JP": "ja-JP",
    "KR": "ko-KR",
    "TH": "th-TH",
    "VN": "vi-VN",
    "ID": "id-ID",
    "MM": "my-MM",
    "KH": "km-KH",
    "LA": "lo-LA",
    "SA": "ar-SA",
    "AE": "ar-AE",
    "IL": "he-IL",
    "TR": "tr-TR",
    "IR": "fa-IR",
}


def get_timezone_for_country(country_code: str) -> str | None:
    """
    Get the primary timezone for a country code.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')

    Returns:
        str: Primary timezone (e.g., 'America/New_York') or None if not found
    """
    if not PYTZ_AVAILABLE:
        fallback_timezones = {
            "US": "America/New_York",
            "GB": "Europe/London",
            "CA": "America/Toronto",
            "AU": "Australia/Sydney",
            "DE": "Europe/Berlin",
            "FR": "Europe/Paris",
            "JP": "Asia/Tokyo",
            "CN": "Asia/Shanghai",
            "IN": "Asia/Kolkata",
            "BR": "America/Sao_Paulo",
            "MX": "America/Mexico_City",
            "RU": "Europe/Moscow",
        }
        return fallback_timezones.get(country_code.upper())

    try:
        timezones = pytz.country_timezones.get(country_code.upper())
        if timezones:
            return timezones[0]
    except (KeyError, AttributeError):
        pass

    return None


def get_all_timezones_for_country(country_code: str) -> list[str]:
    """
    Get all timezones for a country code.

    Args:
        country_code: ISO 3166-1 alpha-2 country code

    Returns:
        list[str]: List of timezones for the country, empty list if not found
    """
    if not PYTZ_AVAILABLE:
        primary = get_timezone_for_country(country_code)
        return [primary] if primary else []

    try:
        return pytz.country_timezones.get(country_code.upper(), [])
    except (KeyError, AttributeError):
        return []


def get_locale_for_country(country_code: str) -> str:
    """
    Get the locale string for a country code.

    Args:
        country_code: ISO 3166-1 alpha-2 country code

    Returns:
        str: Locale string (e.g., 'en-US') or 'en-US' as default
    """
    return LOCALE_MAP.get(country_code.upper(), "en-US")


def get_country_info(country_code: str) -> dict:
    """
    Get comprehensive country information including timezone and locale.

    Args:
        country_code: ISO 3166-1 alpha-2 country code

    Returns:
        dict: Contains 'timezone', 'locale', 'all_timezones', 'country_name'
    """
    country_code = country_code.upper()

    timezone = get_timezone_for_country(country_code)
    locale = get_locale_for_country(country_code)
    all_timezones = get_all_timezones_for_country(country_code)

    country_name = None
    if PYTZ_AVAILABLE:
        with contextlib.suppress(KeyError, AttributeError):
            country_name = pytz.country_names.get(country_code)

    return {
        "country_code": country_code,
        "country_name": country_name,
        "timezone": timezone or "UTC",
        "locale": locale,
        "all_timezones": all_timezones,
    }
