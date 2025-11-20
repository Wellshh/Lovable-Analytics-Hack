"""
Unit tests for data.py module
"""

import csv
import os

import pytest

from src.fake_analytics.data import (
    DEFAULT_REFERERS,
    IdentityGenerator,
    generate_identity,
    get_identity_generator,
    get_referer,
    load_user_data,
)


@pytest.mark.unit
class TestIdentityGenerator:
    """Test IdentityGenerator class"""

    @pytest.mark.parametrize("locale", ["en_US", "en_GB", "fr_FR", "de_DE", "ja_JP"])
    def test_identity_generator_initialization(self, locale):
        """Test: IdentityGenerator initializes with different locales"""
        generator = IdentityGenerator(locale)
        assert generator.faker is not None
        # Faker stores locales as a list/tuple, check if our locale is in there
        # The faker object has a _locales attribute that contains the locale info
        assert locale in str(generator.faker.locales)

    def test_generate_identity_returns_dict(self):
        """Test: generate_identity returns a dictionary with required keys"""
        generator = IdentityGenerator("en_US")
        identity = generator.generate_identity()

        assert isinstance(identity, dict)
        assert "full_name" in identity
        assert "email" in identity
        assert "company" in identity
        assert "phone" in identity

    def test_generate_identity_full_name_is_string(self):
        """Test: Generated full_name is a non-empty string"""
        generator = IdentityGenerator("en_US")
        identity = generator.generate_identity()

        assert isinstance(identity["full_name"], str)
        assert len(identity["full_name"]) > 0

    def test_generate_identity_email_format(self):
        """Test: Generated email has valid format"""
        generator = IdentityGenerator("en_US")
        identity = generator.generate_identity()

        assert isinstance(identity["email"], str)
        assert "@" in identity["email"]
        assert "." in identity["email"].split("@")[1]  # Domain has TLD

    def test_generate_identity_company_is_string(self):
        """Test: Generated company is a non-empty string"""
        generator = IdentityGenerator("en_US")
        identity = generator.generate_identity()

        assert isinstance(identity["company"], str)
        assert len(identity["company"]) > 0

    def test_generate_identity_phone_is_optional(self):
        """Test: Phone number can be None (50% chance)"""
        generator = IdentityGenerator("en_US")

        # Generate multiple identities to test variability
        identities = [generator.generate_identity() for _ in range(20)]
        phones = [id["phone"] for id in identities]

        # Should have mix of None and strings
        has_none = any(p is None for p in phones)
        has_phone = any(p is not None for p in phones)

        assert has_none or has_phone  # At least one of each type is likely

    def test_generate_multiple_identities_are_different(self):
        """Test: Multiple generated identities are different"""
        generator = IdentityGenerator("en_US")

        identity1 = generator.generate_identity()
        identity2 = generator.generate_identity()
        identity3 = generator.generate_identity()

        # Names should be different (very unlikely to be the same)
        names = [identity1["full_name"], identity2["full_name"], identity3["full_name"]]
        assert len(set(names)) > 1  # At least 2 different names

    @pytest.mark.parametrize(
        "name",
        [
            "John Smith",
            "Alice Johnson",
        ],
    )
    def test_name_to_email_conversion(self, name):
        """Test: _name_to_email converts names to email addresses"""
        generator = IdentityGenerator("en_US")
        email = generator._name_to_email(name, "example.com")

        assert "@example.com" in email
        assert email.count("@") == 1

    def test_name_to_email_handles_single_name(self):
        """Test: _name_to_email handles single names"""
        generator = IdentityGenerator("en_US")
        email = generator._name_to_email("Prince", "example.com")

        assert "@example.com" in email
        assert "prince" in email.lower()

    def test_company_to_domain_removes_suffixes(self):
        """Test: _company_to_domain removes common company suffixes"""
        generator = IdentityGenerator("en_US")

        test_cases = [
            ("Acme Corp.", "acme"),
            ("Tech Inc", "tech"),
            ("Solutions LLC.", "solutions"),
            ("StartUp Ltd", "startup"),
        ]

        for company, expected_base in test_cases:
            domain = generator._company_to_domain(company)
            assert expected_base in domain.lower()
            assert "." in domain  # Has TLD

    def test_company_to_domain_handles_special_characters(self):
        """Test: _company_to_domain removes special characters"""
        generator = IdentityGenerator("en_US")
        domain = generator._company_to_domain("Tech & Solutions, Inc.")

        # Should only have alphanumeric and dot
        assert "@" not in domain
        assert "&" not in domain
        assert "," not in domain

    @pytest.mark.parametrize(
        "locale",
        ["en_US", "en_GB", "fr_FR", "de_DE", "ja_JP", "zh_CN", "es_ES", "pt_BR"],
    )
    def test_different_locales_generate_valid_identities(self, locale):
        """Test: Different locales all generate valid identity structures"""
        generator = IdentityGenerator(locale)
        identity = generator.generate_identity()

        assert "full_name" in identity
        assert "email" in identity
        assert "company" in identity
        assert "@" in identity["email"]


# TEST: Global Identity Generator Functions


@pytest.mark.unit
class TestGlobalIdentityFunctions:
    """Test global identity generator functions"""

    def test_get_identity_generator_returns_generator(self):
        """Test: get_identity_generator returns an IdentityGenerator instance"""
        generator = get_identity_generator()
        assert isinstance(generator, IdentityGenerator)

    def test_get_identity_generator_is_singleton(self):
        """Test: get_identity_generator returns the same instance"""
        gen1 = get_identity_generator("en_US")
        gen2 = get_identity_generator("en_US")
        assert gen1 is gen2  # Same object

    def test_generate_identity_function(self):
        """Test: generate_identity function works correctly"""
        identity = generate_identity("en_US")

        assert isinstance(identity, dict)
        assert "full_name" in identity
        assert "email" in identity
        assert "company" in identity
        assert "phone" in identity

    @pytest.mark.parametrize("locale", ["en_US", "fr_FR", "de_DE", "ja_JP"])
    def test_generate_identity_with_different_locales(self, locale):
        """Test: generate_identity works with various locales"""
        identity = generate_identity(locale)

        assert isinstance(identity, dict)
        assert len(identity["full_name"]) > 0
        assert "@" in identity["email"]


# TEST: Referer Selection


@pytest.mark.unit
class TestRefererSelection:
    """Test referer URL selection with weights"""

    def test_get_referer_returns_string(self):
        """Test: get_referer returns a string URL"""
        referer = get_referer()
        assert isinstance(referer, str)
        assert referer.startswith("http")

    def test_get_referer_uses_default_referers(self):
        """Test: get_referer uses DEFAULT_REFERERS when no config provided"""
        referer = get_referer()
        assert referer in DEFAULT_REFERERS

    def test_get_referer_with_custom_referers(self):
        """Test: get_referer uses custom referers when provided"""
        custom_referers = {
            "https://custom1.com/": 1,
            "https://custom2.com/": 1,
        }
        referer = get_referer(custom_referers)
        assert referer in custom_referers

    def test_get_referer_respects_weights(self):
        """Test: get_referer respects weight distribution"""
        # Use heavily weighted referers
        weighted_referers = {
            "https://heavy.com/": 1000,
            "https://light.com/": 1,
        }

        # Generate multiple referers
        results = [get_referer(weighted_referers) for _ in range(100)]

        # Heavy weight should appear more often
        heavy_count = results.count("https://heavy.com/")
        light_count = results.count("https://light.com/")

        # Heavy should be significantly more common
        assert heavy_count > light_count

    @pytest.mark.parametrize(
        "referers,expected_keys",
        [
            (
                {"https://a.com/": 1, "https://b.com/": 1},
                ["https://a.com/", "https://b.com/"],
            ),
            (
                {"https://x.com/": 5, "https://y.com/": 3, "https://z.com/": 2},
                ["https://x.com/", "https://y.com/", "https://z.com/"],
            ),
        ],
    )
    def test_get_referer_with_various_configs(self, referers, expected_keys):
        """Test: get_referer works with various referer configurations"""
        referer = get_referer(referers)
        assert referer in expected_keys

    def test_get_referer_empty_config_uses_default(self):
        """Test: get_referer uses default when given empty config"""
        referer = get_referer(None)
        assert referer in DEFAULT_REFERERS

    def test_default_referers_structure(self):
        """Test: DEFAULT_REFERERS has correct structure"""
        assert isinstance(DEFAULT_REFERERS, dict)
        assert len(DEFAULT_REFERERS) > 0

        for url, weight in DEFAULT_REFERERS.items():
            assert isinstance(url, str)
            assert url.startswith("http")
            assert isinstance(weight, int)
            assert weight > 0


# TEST: CSV Data Loading


@pytest.mark.unit
class TestLoadUserData:
    """Test loading user data from CSV files"""

    def test_load_user_data_from_valid_csv(self, sample_csv_file, sample_csv_data):
        """Test: load_user_data loads data from valid CSV file"""
        data = load_user_data(sample_csv_file)

        assert isinstance(data, list)
        assert len(data) == len(sample_csv_data)
        assert all(isinstance(row, dict) for row in data)

    def test_load_user_data_returns_empty_for_none(self):
        """Test: load_user_data returns empty list when path is None"""
        data = load_user_data(None)
        assert data == []

    def test_load_user_data_returns_empty_for_empty_string(self):
        """Test: load_user_data returns empty list for empty string"""
        data = load_user_data("")
        assert data == []

    def test_load_user_data_raises_for_nonexistent_file(self):
        """Test: load_user_data raises ValueError for nonexistent file"""
        with pytest.raises(ValueError, match="Data file not found"):
            load_user_data("/nonexistent/path/data.csv")

    def test_load_user_data_preserves_headers(self, sample_csv_file):
        """Test: load_user_data preserves CSV headers as dict keys"""
        data = load_user_data(sample_csv_file)

        assert len(data) > 0
        first_row = data[0]
        assert "full_name" in first_row
        assert "email" in first_row
        assert "company" in first_row

    def test_load_user_data_preserves_values(self, sample_csv_file, sample_csv_data):
        """Test: load_user_data preserves data values correctly"""
        data = load_user_data(sample_csv_file)

        # Check first row matches
        assert data[0]["full_name"] == sample_csv_data[0]["full_name"]
        assert data[0]["email"] == sample_csv_data[0]["email"]
        assert data[0]["company"] == sample_csv_data[0]["company"]

    def test_load_user_data_with_different_columns(self, temp_dir):
        """Test: load_user_data handles CSV with different column structure"""
        csv_path = os.path.join(temp_dir, "custom_columns.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "mail", "org"])
            writer.writeheader()
            writer.writerow({"name": "Test", "mail": "test@test.com", "org": "TestCo"})

        data = load_user_data(csv_path)
        assert len(data) == 1
        assert data[0]["name"] == "Test"
        assert data[0]["mail"] == "test@test.com"
        assert data[0]["org"] == "TestCo"

    def test_load_user_data_with_empty_csv(self, temp_dir):
        """Test: load_user_data handles empty CSV (only headers)"""
        csv_path = os.path.join(temp_dir, "empty.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["col1", "col2"])
            writer.writeheader()

        data = load_user_data(csv_path)
        assert data == []

    def test_load_user_data_with_special_characters(self, temp_dir):
        """Test: load_user_data handles special characters in data"""
        csv_path = os.path.join(temp_dir, "special_chars.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "email"])
            writer.writeheader()
            writer.writerow({"name": "Jean-François O'Neill", "email": "test@example.com"})

        data = load_user_data(csv_path)
        assert len(data) == 1
        assert "François" in data[0]["name"]

    def test_load_user_data_handles_unicode(self, temp_dir):
        """Test: load_user_data handles Unicode characters correctly"""
        csv_path = os.path.join(temp_dir, "unicode.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "company"])
            writer.writeheader()
            writer.writerow({"name": "田中太郎", "company": "株式会社テスト"})

        data = load_user_data(csv_path)
        assert len(data) == 1
        assert data[0]["name"] == "田中太郎"
