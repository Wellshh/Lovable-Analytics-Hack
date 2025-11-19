import csv
import random
from typing import Optional

from faker import Faker

# Default referers with weights (will be overridden by config if provided)
DEFAULT_REFERERS = {
    "https://www.facebook.com/": 4,
    "https://www.reddit.com/": 1,
    "https://www.google.com/": 2,
    "https://www.twitter.com/": 1,
    "https://www.linkedin.com/": 1,
}

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


class IdentityGenerator:
    """Generate realistic identities using Faker library"""

    def __init__(self, locale: str = "en_US"):
        """
        Initialize the identity generator with a specific locale.

        Args:
            locale: Faker locale (e.g., 'en_US', 'en_GB', 'fr_FR', 'zh_CN')
        """
        self.faker = Faker(locale)

    def generate_identity(self) -> dict:
        """
        Generate a realistic identity with name, email, and company.

        Returns:
            dict: Contains 'full_name', 'email', 'company', 'phone' (optional)
        """
        full_name = self.faker.name()

        # Generate professional email based on name
        # Sometimes use company domain, sometimes use public email
        if random.random() < 0.3:  # 30% chance of company email
            company = self.faker.company()
            company_domain = self._company_to_domain(company)
            email = self._name_to_email(full_name, company_domain)
        else:  # Public email domain
            public_domains = [
                "gmail.com",
                "yahoo.com",
                "hotmail.com",
                "outlook.com",
                "proton.me",
                "icloud.com",
                "aol.com",
            ]
            email = self._name_to_email(full_name, random.choice(public_domains))

        return {
            "full_name": full_name,
            "email": email,
            "company": self.faker.company(),
            "phone": self.faker.phone_number() if random.random() < 0.5 else None,
        }

    def _name_to_email(self, name: str, domain: str) -> str:
        """Convert a name to an email address"""
        # Remove titles and suffixes
        name_parts = name.lower().replace(".", "").replace(",", "").split()
        # Use first and last name
        if len(name_parts) >= 2:
            first = name_parts[0]
            last = name_parts[-1]

            # Various email patterns
            patterns = [
                f"{first}.{last}",
                f"{first}{last}",
                f"{first}_{last}",
                f"{first[0]}{last}",  # First initial + last name
                f"{first}{last[0]}",  # First name + last initial
            ]

            email_local = random.choice(patterns)

            # Sometimes add numbers
            if random.random() < 0.3:
                email_local += str(random.randint(1, 999))

            return f"{email_local}@{domain}"
        else:
            return f"{name_parts[0]}{random.randint(1, 999)}@{domain}"

    def _company_to_domain(self, company: str) -> str:
        """Convert company name to domain"""
        # Remove common suffixes and special characters
        domain = company.lower()
        for suffix in [
            " inc",
            " inc.",
            " corp",
            " corp.",
            " ltd",
            " ltd.",
            " llc",
            " llc.",
        ]:
            domain = domain.replace(suffix, "")

        # Remove special characters
        domain = "".join(c for c in domain if c.isalnum() or c == " ")
        domain = domain.replace(" ", "")

        # Add TLD
        tlds = ["com", "net", "org", "io", "co"]
        return f"{domain}.{random.choice(tlds)}"


# Global instance
_identity_generator = None


def get_identity_generator(locale: str = "en_US") -> IdentityGenerator:
    """Get or create the global identity generator"""
    global _identity_generator
    if _identity_generator is None:
        _identity_generator = IdentityGenerator(locale)
    return _identity_generator


def generate_identity(locale: str = "en_US") -> dict:
    """
    Generate a realistic identity using Faker.

    Args:
        locale: Faker locale (e.g., 'en_US', 'en_GB', 'fr_FR')

    Returns:
        dict: Contains 'full_name', 'email', 'company', 'phone'
    """
    generator = get_identity_generator(locale)
    return generator.generate_identity()


def get_referer(referers_config: Optional[dict] = None) -> str:
    """
    Get a random referer based on weights.

    Args:
        referers_config: Dict mapping referer URLs to weights

    Returns:
        str: Selected referer URL
    """
    if not referers_config:
        referers_config = DEFAULT_REFERERS

    # Extract URLs and weights
    urls = list(referers_config.keys())
    weights = list(referers_config.values())

    # Use random.choices with weights
    return random.choices(urls, weights=weights, k=1)[0]


REFERERS = list(DEFAULT_REFERERS.keys())  # For backward compatibility


def load_user_data(file_path: str) -> list[dict]:
    """
    Loads user data from a CSV file.
    The CSV file should have a header row with field names.

    Args:
        file_path: Path to CSV file

    Returns:
        list[dict]: List of user data dictionaries
    """
    if not file_path:
        return []

    from pathlib import Path

    try:
        with Path(file_path).open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError as e:
        raise ValueError(f"Data file not found at: {file_path}") from e
    except Exception as e:
        raise ValueError(f"Error reading data file: {e}") from e
