Fake Analytics
==============

Introduction
------------

This tool was originally created for faking analytics data for Lovable. If you ever encounter situations where there's no time for real customer discovery, user testing, or when you need to demonstrate a product concept quickly, this tool might be helpful.

**Important Note**: This tool is provided for **educational purposes only**. The author assumes no responsibility or liability for how this tool is used. Use at your own discretion and ensure compliance with all applicable laws, terms of service, and ethical guidelines in your jurisdiction.

Overview
--------

A powerful tool to simulate website analytics by generating realistic browser traffic using Playwright. This tool can simulate user behavior including page visits, mouse movements, scrolling, and form submissions.

Features
--------

* **Realistic Browser Simulation**: Uses Playwright with Chrome to simulate real browser behavior
* **Human-like Interactions**: Random mouse movements, scrolling, and typing delays
* **Realistic Data Generation**: Uses Faker library to generate authentic names, emails, and company names
* **Form Auto-filling**: Automatically discover and fill form fields with generated or custom user data
* **Proxy Support**: Configure proxy servers with country-specific routing
* **Multi-threaded**: Run multiple bot instances concurrently
* **CSV Data Import**: Load user identities from CSV files
* **Form Discovery**: Automatically discover form fields on any webpage
* **Weighted Referers**: Configure custom referer sources with weights to simulate realistic traffic patterns
* **Enhanced Logging**: Rich colored output with progress bars and formatted tables

Installation
------------

Prerequisites
~~~~~~~~~~~~~

* Python 3.10 or higher
* Poetry (recommended) or pip

Using Poetry
~~~~~~~~~~~~

.. code-block:: bash

    poetry install
    poetry run playwright install chromium

Using pip
~~~~~~~~~

.. code-block:: bash

    pip install -r requirements.txt
    playwright install chromium

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Create a ``.env`` file in the project root with the following variables:

.. code-block:: bash

    TARGET_URL=https://example.com
    CONVERSION_RATE=0.3
    PROXY_HOST=gw.dataimpulse.com:823
    PROXY_USER=your_proxy_username
    PROXY_PASS=your_proxy_password
    PROXY_COUNTRIES=US,GB,CA

Configuration File (JSON)
~~~~~~~~~~~~~~~~~~~~~~~~~

You can also use a JSON configuration file:

.. code-block:: json

    {
        "target_url": "https://example.com",
        "conversion_rate": 0.3,
        "locale": "en_US",
        "referers": {
            "https://www.facebook.com/": 4,
            "https://www.google.com/": 3,
            "https://www.reddit.com/": 2,
            "https://www.twitter.com/": 1
        },
        "form_fields": {
            "full_name": "#name",
            "email": "#email",
            "company": "#company"
        },
        "submit_button": "button[type='submit']"
    }

New configuration options:

* ``locale``: Language/region for data generation (e.g., "en_US", "en_GB", "fr_FR", "zh_CN")
* ``referers``: Dictionary mapping referer URLs to weights (higher = more likely to be selected)

Usage
-----

Basic Usage
~~~~~~~~~~~

Run a single bot instance:

.. code-block:: bash

    fake-analytics run --url https://example.com

Run multiple concurrent instances with verbose logging:

.. code-block:: bash

    fake-analytics run --url https://example.com --threads 5 --verbose
    # Or use short form
    fake-analytics run --url https://example.com --threads 5 -v

Using Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    fake-analytics run --config config.json

Using CSV Data
~~~~~~~~~~~~~~

Create a CSV file with user data (e.g., ``users.csv``):

.. code-block:: csv

    full_name,email,company
    John Doe,john@example.com,Acme Corp
    Jane Smith,jane@example.com,Tech Solutions

Then run:

.. code-block:: bash

    fake-analytics run --data-file users.csv

The number of threads will automatically match the number of records in the CSV file.

Form Discovery
~~~~~~~~~~~~~

Discover form fields on a webpage:

.. code-block:: bash

    fake-analytics discover --url https://example.com

This will output all input, textarea, and select elements with their attributes (name, id, type, etc.) to help you create your configuration file.

Command Line Options
--------------------

run
~~~

* ``--url``: The target URL to visit
* ``--threads``: Number of concurrent threads (default: 1)
* ``--config``: Path to a custom JSON config file
* ``--data-file``: Path to a CSV file with user data

discover
~~~~~~~~

* ``--url``: The URL to discover forms on (required)

How It Works
------------

1. **Browser Launch**: Each bot instance launches a Chrome browser with realistic settings
2. **Page Navigation**: Navigates to the target URL with random referer headers
3. **Human Simulation**: Performs random mouse movements and scrolling
4. **Form Interaction**: If conversion rate threshold is met, fills and submits forms
5. **Cleanup**: Closes browser and cleans up temporary profile directories

Behavior Simulation
-------------------

The tool simulates realistic human behavior:

* **Random Delays**: Variable typing speeds and pauses between actions
* **Mouse Movements**: Bezier-like mouse movements across the viewport
* **Scrolling**: Random scroll patterns up and down the page
* **Form Filling**: Human-like typing with delays between keystrokes
* **Realistic Data**: Uses Faker library to generate authentic user identities with proper name formats, company domains, and email patterns

Data Generation
~~~~~~~~~~~~~~~

The tool uses the Faker library to generate realistic data:

* **Names**: Context-appropriate names based on locale
* **Emails**: Professional-looking emails with both company and public domains
* **Companies**: Realistic company names
* **Phone Numbers**: Optional phone number generation
* **Multi-locale Support**: Generate data in different languages/regions (en_US, en_GB, fr_FR, zh_CN, etc.)

Proxy Configuration
-------------------

When proxy credentials are provided, the tool will:

* Route traffic through the specified proxy server
* Detect the proxy's geographic location
* Set appropriate timezone and locale based on proxy location
* Support country-specific routing via ``PROXY_COUNTRIES``

Example: ``PROXY_COUNTRIES=US,GB,CA`` will rotate between US, UK, and Canadian proxies.

Project Structure
-----------------

::

    fake_analytics/
    ├── __init__.py
    ├── actions.py      # Browser interaction functions
    ├── cli.py          # Command-line interface
    ├── config.py       # Configuration management
    ├── core.py         # Main TrafficBot class
    ├── data.py         # User data generation and loading
    └── discovery.py    # Form field discovery

Documentation
-------------

API documentation can be generated from docstrings using Sphinx.

Prerequisites
~~~~~~~~~~~~~

Install documentation dependencies:

.. code-block:: bash

    poetry install --with dev

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~~

Generate HTML documentation:

.. code-block:: bash

    cd docs
    make html

Or using sphinx-build directly:

.. code-block:: bash

    poetry run sphinx-build -b html docs docs/_build/html

The generated documentation will be in ``docs/_build/html/``. Open ``index.html`` in your browser to view it.

The documentation is automatically generated from docstrings in the source code. Make sure your docstrings follow Google or NumPy style format for best results.

License
-------

MIT License - see LICENSE file for details.
