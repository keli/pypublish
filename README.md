# pypublish-cli

A CLI tool for publishing Python packages to PyPI.

## Installation

```bash
pip install pypublish-cli
```

## Usage

### Initialize pyproject.toml

```bash
pypublish --init-pyproject    # Add setuptools_scm config to pyproject.toml (creates it if missing)
```

### Initialize repository

```bash
pypublish --init-repo              # Initialize local git repo only
pypublish --init-repo --github     # Initialize git and create GitHub repo
pypublish --init-repo --github myproject  # Specify custom repo name
pypublish --init-repo --github --private  # Create private GitHub repo
pypublish --github                 # Create GitHub repo (git already initialized)
```

`--init-repo` will:
1. Initialize git repository (if not already initialized)
2. Add all files and create initial commit

`--github` additionally:
3. Create GitHub repository using `gh` CLI
4. Push to GitHub

### Full publish workflow

```bash
pypublish 0.2.0              # Full publish: tag, build, upload
pypublish v0.2.0             # Full publish: tag, build, upload
```

This will:
1. Validate the environment (pyproject.toml, build tools)
2. Create a git tag and push to origin
3. Clean up old build artifacts
4. Build the package using `python -m build`
5. Upload to PyPI using `uv publish` (if available) or `twine upload`

### Partial workflows

```bash
pypublish 0.2.0 --tag-only         # Only create and push tag
pypublish 0.2.0 --build-only       # Tag and build, don't upload
pypublish 0.2.0 --no-build         # Tag and upload existing dist/
pypublish 0.2.0 --no-upload        # Tag and build, don't upload
```

### Delete a tag

```bash
pypublish --delete-tag 0.2.0       # Delete tag locally and from origin
pypublish --delete-tag v0.2.0      # Delete tag locally and from origin
```

## Requirements

- Python >= 3.7
- `build` (`pip install build`)
- `uv` or `twine` for uploading (`pip install twine`)
- `gh` CLI for GitHub repository creation

## License

MIT
