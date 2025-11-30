# pypublish-cli

A CLI tool for publishing Python packages to PyPI.

## Installation

```bash
pip install pypublish-cli
```

## Usage

### Initialize GitHub repository

```bash
pypublish --init-repo              # Use current directory name as repo name
pypublish --init-repo myproject    # Specify custom repo name
pypublish --init-repo --private    # Create private repository
```

This will:
1. Initialize git repository (if not already initialized)
2. Add all files and create initial commit
3. Create GitHub repository using `gh` CLI
4. Push to GitHub

### Full publish workflow

```bash
pypublish 0.2.0              # Full publish: tag, build, upload
pypublish v0.2.0             # Full publish: tag, build, upload
```

This will:
1. Create a git tag
2. Push the tag to origin
3. Clean up old build artifacts
4. Build the package using `python -m build`
5. Upload to PyPI using `twine`

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

This will remove the tag both locally and from the remote repository.

## Requirements

- Python >= 3.7
- Git repository
- PyPI account configured with `twine`

## License

MIT
