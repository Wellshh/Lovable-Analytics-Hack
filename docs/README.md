# Sphinx Documentation

This directory contains the Sphinx documentation for the Fake Analytics project.

## Building the Documentation

### Using Make (Linux/macOS)

```bash
cd docs
make html
```

The generated HTML documentation will be in `docs/_build/html/`.

### Using sphinx-build directly

```bash
cd docs
sphinx-build -b html . _build/html
```

### Using Poetry

```bash
poetry run sphinx-build -b html docs docs/_build/html
```

## Viewing the Documentation

After building, open `docs/_build/html/index.html` in your browser.

You can also use Python's built-in HTTP server to preview:

```bash
cd docs/_build/html
python3 -m http.server 8000
```

Then open http://localhost:8000 in your browser.

## Deployment

### GitHub Pages (Automatic)

The project includes a GitHub Actions workflow (`.github/workflows/docs.yml`) that automatically builds and deploys documentation to GitHub Pages when you push to `main` or `develop` branches.

To enable GitHub Pages:
1. Go to your repository Settings → Pages
2. Under "Source", select "GitHub Actions"
3. The documentation will be automatically deployed after the workflow runs

The documentation will be available at:
`https://<username>.github.io/<repository-name>/`

### Manual Deployment

You can manually deploy the `docs/_build/html/` directory to any static hosting service:
- GitHub Pages
- Netlify
- Vercel
- AWS S3
- Any web server

## Auto-generating from Docstrings

The documentation is automatically generated from docstrings in the source code using Sphinx's `autodoc` extension. To update the documentation:

1. Make sure your docstrings are properly formatted
2. Rebuild the documentation using one of the methods above

## Documentation Structure

- `index.rst` - Main documentation entry point
- `modules.rst` - API reference for all modules
- `conf.py` - Sphinx configuration file
