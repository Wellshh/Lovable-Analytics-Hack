import asyncio
import json

import click
from playwright.async_api import async_playwright

from .logger import console, print_config_generated, print_field_table


async def discover_form_fields(url: str):
    """
    Launches a headless browser to discover form fields on a given URL.
    """
    click.echo(f"🔍 Discovering form fields on {url}...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            click.echo("Navigating to the page...")
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")

            try:
                await page.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                click.echo("Waiting for network idle timed out, continuing anyway...")

            await asyncio.sleep(2)

            click.echo("Searching for input, textarea, and select elements...")

            elements = await page.query_selector_all("input, textarea, select")

            if not elements:
                click.secho("No form fields found on the page.", fg="yellow")
                await browser.close()
                return

            console.print(
                f"[bold green]✅ Found {len(elements)} potential form fields[/bold green]"
            )

            field_details = []
            for _idx, element in enumerate(elements, 1):
                attrs = await element.evaluate(
                    """el => ({
                        tag: el.tagName.toLowerCase(),
                        type: el.type || el.getAttribute('type') || 'N/A',
                        name: el.name || el.getAttribute('name') || 'N/A',
                        id: el.id || el.getAttribute('id') || 'N/A',
                        placeholder: el.placeholder || el.getAttribute('placeholder') || 'N/A',
                        ariaLabel: el.getAttribute('aria-label') || 'N/A',
                        className: el.className || el.getAttribute('class') || 'N/A',
                        value: el.value || el.getAttribute('value') || 'N/A'
                    })"""
                )

                details = {
                    "tag": attrs.get("tag", "N/A"),
                    "type": attrs.get("type", "N/A"),
                    "name": attrs.get("name", "N/A"),
                    "id": attrs.get("id", "N/A"),
                    "placeholder": attrs.get("placeholder", "N/A"),
                    "aria-label": attrs.get("ariaLabel", "N/A"),
                    "class": attrs.get("className", "N/A"),
                }
                field_details.append(details)

            print_field_table(field_details)

            console.print("\n[bold cyan]💡 Suggested CSS Selectors:[/bold cyan]")
            for idx, item in enumerate(field_details, 1):
                selectors = []
                if item["id"] != "N/A":
                    selectors.append(f"#{item['id']}")
                if item["name"] != "N/A":
                    selectors.append(f"[name='{item['name']}']")
                if item["type"] != "N/A" and item["type"] != "text":
                    selectors.append(f"input[type='{item['type']}']")
                if item["placeholder"] != "N/A":
                    selectors.append(f"[placeholder='{item['placeholder']}']")

                if selectors:
                    console.print(f"  [green]Field {idx}:[/green] {', '.join(selectors)}")
                else:
                    console.print(
                        f"  [yellow]Field {idx}:[/yellow] (no reliable selector found, try using class or nth-child)"
                    )

            console.print(
                "\n[cyan]Use the selectors above to create your JSON configuration file for the 'run' command.[/cyan]"
            )

            if click.confirm(
                "\n🤔 Would you like to generate a JSON configuration file?",
                default=True,
            ):
                await generate_config_file(url, page, field_details)

            await browser.close()
    except Exception as e:
        click.secho(f"An error occurred during discovery: {e}", fg="red")
        import traceback

        click.echo(traceback.format_exc())


async def generate_config_file(url: str, page, field_details: list):
    """
    Generate a JSON configuration file based on discovered form fields.
    """
    try:
        click.echo("\n" + "=" * 80)
        click.secho("📋 Configuration File Generation", fg="cyan")
        click.echo("=" * 80)

        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('Send')",
            "button:has-text('Get')",
            "button:has-text('Sign')",
            "button:has-text('Sign up')",
            "button:has-text('Sign Up')",
        ]

        submit_button = None
        for selector in submit_selectors:
            try:
                btn = await page.query_selector(selector)
                if btn:
                    submit_button = selector
                    click.secho(f"✅ Found submit button: {selector}", fg="green")
                    break
            except Exception:
                continue

        if not submit_button:
            click.secho("⚠️  No submit button found automatically.", fg="yellow")
            if click.confirm(
                "Would you like to manually enter a submit button selector?",
                default=False,
            ):
                submit_button = click.prompt("Enter submit button selector", type=str)

        form_fields = {}
        field_mapping = {
            "full_name": ["name", "fullname", "full_name", "fullName"],
            "email": ["email", "mail", "e-mail"],
            "company": ["company", "organization", "org", "companyName"],
            "phone": ["phone", "tel", "telephone", "mobile"],
            "message": ["message", "msg", "comment", "comments", "feedback"],
        }

        click.echo("\n📝 Mapping form fields:")
        click.echo("-" * 80)

        for idx, field in enumerate(field_details, 1):
            field_name_lower = field["name"].lower() if field["name"] != "N/A" else ""
            field_id_lower = field["id"].lower() if field["id"] != "N/A" else ""

            selectors = []
            if field["id"] != "N/A":
                selectors.append(("ID", f"#{field['id']}"))
            if field["name"] != "N/A":
                selectors.append(("Name", f"[name='{field['name']}']"))
            if field["type"] != "N/A" and field["type"] != "text":
                selectors.append(("Type", f"input[type='{field['type']}']"))
            if field["placeholder"] != "N/A":
                selectors.append(("Placeholder", f"[placeholder='{field['placeholder']}']"))

            if not selectors:
                continue

            matched_standard_name = None
            for standard_name, possible_names in field_mapping.items():
                if any(
                    name in field_name_lower or name in field_id_lower for name in possible_names
                ):
                    matched_standard_name = standard_name
                    break

            field_display = f"Field {idx} ({field['tag']}, type={field['type']})"
            if field["name"] != "N/A":
                field_display += f" name='{field['name']}'"
            if field["id"] != "N/A":
                field_display += f" id='{field['id']}'"

            if matched_standard_name:
                click.echo(f"\n{field_display}")
                click.secho(f"  → Auto-matched to: {matched_standard_name}", fg="cyan")
                if click.confirm(
                    f"  Include this field as '{matched_standard_name}'?", default=True
                ):
                    best_selector = selectors[0][1]
                    form_fields[matched_standard_name] = best_selector
                    click.secho(
                        f"  ✅ Added: {matched_standard_name} = {best_selector}",
                        fg="green",
                    )
            else:
                click.echo(f"\n{field_display}")
                if click.confirm("  Include this field in the config?", default=True):
                    default_key = field["name"] if field["name"] != "N/A" else field["id"]
                    field_key = click.prompt(
                        "  Enter field name for config",
                        default=default_key,
                        type=str,
                    )
                    best_selector = selectors[0][1]
                    form_fields[field_key] = best_selector
                    click.secho(f"  ✅ Added: {field_key} = {best_selector}", fg="green")

        config = {
            "target_url": url,
            "conversion_rate": 0.3,
        }

        if form_fields:
            config["form_fields"] = form_fields

        if submit_button:
            config["submit_button"] = submit_button

        click.echo("\n" + "=" * 80)
        default_filename = "config.json"
        output_path = click.prompt(
            "📁 Enter the output file path",
            default=default_filename,
            type=click.Path(),
        )

        if not output_path.endswith(".json"):
            output_path += ".json"

        from pathlib import Path

        if Path(output_path).exists() and not click.confirm(
            f"⚠️  File '{output_path}' already exists. Overwrite?", default=False
        ):
            click.secho("Configuration file generation cancelled.", fg="yellow")
            return

        conversion_rate = click.prompt(
            "🎯 Enter conversion rate (0.0 to 1.0)",
            default=0.3,
            type=float,
        )
        if not 0 <= conversion_rate <= 1:
            click.secho(
                "⚠️  Conversion rate must be between 0 and 1, using default 0.3",
                fg="yellow",
            )
            conversion_rate = 0.3

        config["conversion_rate"] = conversion_rate

        with Path(output_path).open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print_config_generated(config, output_path)

        console.print("\n[bold]Generated configuration:[/bold]")
        console.print(json.dumps(config, indent=2, ensure_ascii=False))

        console.print(
            f"\n[bold cyan]💡 You can now use this config with:[/bold cyan]\n   [green]fake-analytics run --config {output_path}[/green]"
        )

    except Exception as e:
        click.secho(f"Error generating config file: {e}", fg="red")
        import traceback

        click.echo(traceback.format_exc())
