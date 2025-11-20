import asyncio
from concurrent.futures import ThreadPoolExecutor

import click

from .config import Config
from .core import TrafficBot
from .data import load_user_data
from .discovery import discover_form_fields
from .logger import get_logger


@click.group()
@click.version_option()
def cli():
    """
    Fake Analytics - A tool to simulate website analytics by generating realistic browser traffic.

    This tool uses Playwright to simulate real browser behavior including page visits,
    mouse movements, scrolling, and form submissions. It supports proxy configuration,
    multi-threaded execution, and custom user data from CSV files.

    \b
    Examples:
        # Run a single bot instance
        fake-analytics run --url https://example.com

        # Run multiple concurrent instances
        fake-analytics run --url https://example.com --threads 5

        # Use a configuration file
        fake-analytics run --config config.json

        # Use CSV data file
        fake-analytics run --data-file users.csv

        # Discover form fields on a webpage
        fake-analytics discover --url https://example.com
    """
    pass


def run_bot_instance(config, identity):
    """Wrapper function to run a single bot instance in an async event loop."""

    async def main():
        bot = TrafficBot(config, identity)
        await bot.run()

    asyncio.run(main())


@cli.command()
@click.option(
    "--url",
    help="The target URL to visit. This overrides the TARGET_URL environment variable and config file setting.",
    metavar="<URL>",
)
@click.option(
    "--threads",
    default=1,
    type=int,
    help="The number of concurrent bot instances to run. Each instance will simulate a separate user session. "
    "Note: If --data-file is provided, this option is ignored and the number of threads will match the number of records in the CSV file.",
    metavar="<N>",
    show_default=True,
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Enable verbose output including network request/response logs, browser console messages, and detailed debugging information.",
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, readable=True),
    help="Path to a custom JSON configuration file. The config file can contain:\n"
    "  - target_url: The URL to visit\n"
    "  - conversion_rate: Probability of form submission (0.0 to 1.0)\n"
    "  - form_fields: Mapping of field names to CSS selectors\n"
    "  - submit_button: CSS selector for the submit button\n"
    "\n"
    "Example config.json:\n"
    "  {\n"
    '    "target_url": "https://example.com",\n'
    '    "conversion_rate": 0.3,\n'
    '    "form_fields": {\n'
    '      "full_name": "#name",\n'
    '      "email": "#email",\n'
    '      "company": "#company"\n'
    "    },\n"
    '    "submit_button": "button[type=\\"submit\\"]"\n'
    "  }",
    metavar="<PATH>",
)
@click.option(
    "--data-file",
    "data_path",
    type=click.Path(exists=True, readable=True),
    help="Path to a CSV file containing user data. The CSV should have a header row with field names "
    "that match the form field names in your configuration. Each row represents one user identity.\n"
    "\n"
    "Example users.csv:\n"
    "  full_name,email,company\n"
    "  John Doe,john@example.com,Acme Corp\n"
    "  Jane Smith,jane@example.com,Tech Solutions\n"
    "\n"
    "When this option is used, the number of bot instances will automatically match the number of rows in the CSV file.",
    metavar="<PATH>",
)
def run(url, threads, verbose, config_path, data_path):
    """
    Run the traffic bot to simulate website visits and user interactions.

    This command launches one or more browser instances to simulate real user behavior.
    Each instance will:

    \b
    1. Launch a Chrome browser with realistic settings
    2. Navigate to the target URL with random referer headers
    3. Perform random mouse movements and scrolling
    4. Optionally fill and submit forms (based on conversion_rate)
    5. Clean up and close the browser

    \b
    Configuration Priority:
    1. Command-line options (--url, --config, --data-file)
    2. Configuration file (--config or default)
    3. Environment variables (.env file)
    4. Default values

    \b
    Environment Variables:
    The following environment variables can be set in a .env file:

    \b
      TARGET_URL          - Default target URL
      CONVERSION_RATE     - Probability of form submission (0.0-1.0)
      PROXY_HOST          - Proxy server host and port
      PROXY_USER          - Proxy username
      PROXY_PASS          - Proxy password
      PROXY_COUNTRIES     - Comma-separated list of country codes for proxy routing

    \b
    Examples:
      fake-analytics run --url https://example.com

      fake-analytics run --url https://example.com --threads 5

      fake-analytics run --config myconfig.json

      fake-analytics run --data-file users.csv --config config.json

      fake-analytics run --url https://example.com --threads 3 --config config.json
    """
    try:
        config = Config(config_path, verbose=verbose)
        logger = get_logger(verbose)

        if url:
            config.target_url = url

        user_data = load_user_data(data_path)

        if user_data:
            logger.info(f"Loaded {len(user_data)} user records from {data_path}")
            threads = len(user_data)
            logger.info(f"Running with {threads} threads based on the data file.")

        logger.bot_start(config.target_url, threads)

        with ThreadPoolExecutor(max_workers=threads) as executor:
            identities = user_data if user_data else [None] * threads

            futures = [
                executor.submit(run_bot_instance, config, identity) for identity in identities
            ]

            for future in futures:
                future.result()

        logger.completion()

    except ValueError:
        logger = get_logger(verbose)
        logger.exception("Configuration error")


@cli.command()
@click.option(
    "--url",
    required=True,
    help="The URL of the webpage to analyze for form fields. The tool will launch a headless browser, "
    "navigate to the URL, and scan for all input, textarea, and select elements.",
    metavar="<URL>",
)
def discover(url):
    """
    Discover form fields on a webpage to help create configuration files.

    This command launches a headless browser, navigates to the specified URL, and scans
    for all form-related elements (input, textarea, select). It then displays a formatted
    table showing the attributes of each field (tag, type, name, id, placeholder, aria-label).

    Use this command to identify the correct CSS selectors for your form fields when creating
    a configuration file for the 'run' command.

    \b
    Example:
      fake-analytics discover --url https://example.com/contact

    \b
    Output Format:
    The command will display a table with the following information for each field:
      - Tag: HTML tag name (input, textarea, select)
      - Type: Input type attribute (text, email, etc.)
      - Name: Name attribute value
      - ID: ID attribute value
      - Placeholder: Placeholder text
      - Aria-label: ARIA label attribute

    Use the 'name' or 'id' values from the output to create selectors in your config file.
    """
    asyncio.run(discover_form_fields(url))


if __name__ == "__main__":
    cli()
