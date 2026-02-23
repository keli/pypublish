#!/usr/bin/env python3
import os
import sys
import re
import subprocess
import argparse

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

def run_command(command):
    """Execute a shell command and return the exit code"""
    process = subprocess.run(command, shell=True, check=True)
    return process.returncode

def delete_tag(version):
    """Delete a tag locally and from origin"""
    if not version.startswith('v'):
        version = f'v{version}'

    commands = [
        f'git tag -d {version}',
        f'git push origin --delete {version}'
    ]

    for command in commands:
        print(f"Executing: {command}")
        try:
            run_command(command)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {command}")
            print(f"Error: {e}")
            sys.exit(1)

    print(f"Successfully deleted tag {version} locally and from origin")

def create_tag(version):
    """Create and push a git tag"""
    if not version.startswith('v'):
        version = f'v{version}'

    commands = [
        f'git tag {version}',
        f'git push origin {version}'
    ]

    for command in commands:
        print(f"Executing: {command}")
        try:
            run_command(command)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {command}")
            print(f"Error: {e}")
            sys.exit(1)

    print(f"Successfully created and pushed tag {version}")

def build_package(env=None):
    """Build the package"""
    commands = [
        'rm -rf dist/ build/ *.egg-info',
        'python -m build'
    ]

    for command in commands:
        print(f"Executing: {command}")
        try:
            subprocess.run(command, shell=True, check=True, env=env)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {command}")
            print(f"Error: {e}")
            sys.exit(1)

    print("Successfully built package")

def detect_upload_tool():
    """Detect available upload tool, preferring twine"""
    has_twine = subprocess.run('twine --version', shell=True, capture_output=True).returncode == 0
    has_uv = subprocess.run('uv --version', shell=True, capture_output=True).returncode == 0
    if has_twine:
        return 'twine'
    if has_uv:
        return 'uv'
    return None

def upload_package():
    """Upload the package to PyPI"""
    tool = detect_upload_tool()
    if tool == 'uv':
        command = 'uv publish dist/*'
    elif tool == 'twine':
        command = 'twine upload dist/*'
    else:
        print("Error: neither 'uv' nor 'twine' is installed (run: pip install twine)")
        sys.exit(1)

    print(f"Executing: {command}")
    try:
        run_command(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error: {e}")
        sys.exit(1)

    print("Successfully uploaded package to PyPI")

def init_repo():
    """Initialize local git repository"""
    try:
        subprocess.run(['git', 'status'], capture_output=True, check=True)
        print("Git repository already exists")
    except subprocess.CalledProcessError:
        print("Initializing git repository...")
        run_command('git init')
        run_command('git add .')
        run_command('git commit -m "Initial commit"')

def create_github_repo(repo_name=None, private=False):
    """Create GitHub repository and push"""
    if repo_name is None:
        repo_name = os.path.basename(os.getcwd())

    visibility = '--private' if private else '--public'
    command = f'gh repo create {repo_name} {visibility} --source=. --remote=origin --push'
    print(f"Executing: {command}")
    try:
        run_command(command)
        print(f"Successfully created GitHub repository: {repo_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating GitHub repository: {e}")
        sys.exit(1)

PYPROJECT_TEMPLATE = '''\
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
dynamic = ["version"]
description = ""
readme = "README.md"
requires-python = ">=3.8"
license = {{text = "MIT"}}
dependencies = []

[tool.setuptools_scm]
local_scheme = "no-local-version"
version_scheme = "post-release"
'''

SCM_BUILD_SYSTEM = '''\
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"
'''

SCM_TOOL_CONFIG = '''\
[tool.setuptools_scm]
local_scheme = "no-local-version"
version_scheme = "post-release"
'''

def init_pyproject():
    """Add setuptools_scm config to pyproject.toml, or create it from template"""
    if not os.path.exists('pyproject.toml'):
        name = os.path.basename(os.getcwd())
        with open('pyproject.toml', 'w') as f:
            f.write(PYPROJECT_TEMPLATE.format(name=name))
        print("Created pyproject.toml")
        return

    with open('pyproject.toml', 'rb') as f:
        data = tomllib.load(f)
    with open('pyproject.toml', 'r') as f:
        content = f.read()

    changed = False

    # Add setuptools_scm to [build-system] requires
    build_requires = data.get('build-system', {}).get('requires', [])
    has_scm = any('setuptools_scm' in r for r in build_requires)
    if not has_scm:
        if '[build-system]' in content:
            # Patch the requires = [...] line (single-line only)
            def add_scm_to_requires(m):
                inner = m.group(1).rstrip()
                sep = ', ' if inner.strip() else ''
                return f'requires = [{inner}{sep}"setuptools_scm[toml]>=6.2"]'
            content = re.sub(r'requires\s*=\s*\[([^\]]*)\]', add_scm_to_requires, content, count=1)
        else:
            content += '\n' + SCM_BUILD_SYSTEM
        changed = True

    # Remove hardcoded version = "x.y.z" from [project]
    project = data.get('project', {})
    if 'version' in project and 'version' not in project.get('dynamic', []):
        content = re.sub(r'(?m)^\s*version\s*=\s*["\'][\d.][^"\']*["\'][ \t]*\n', '', content, count=1)
        print(f"Removed hardcoded version = \"{project['version']}\" from [project]")
        changed = True

    # Add "version" to dynamic
    dynamic = project.get('dynamic', [])
    if 'version' not in dynamic:
        if 'dynamic' in content:
            def add_version_to_dynamic(m):
                inner = m.group(1).rstrip()
                sep = ', ' if inner.strip() else ''
                return f'dynamic = [{inner}{sep}"version"]'
            content = re.sub(r'dynamic\s*=\s*\[([^\]]*)\]', add_version_to_dynamic, content, count=1)
        else:
            content = content.replace('[project]', '[project]\ndynamic = ["version"]', 1)
        changed = True

    # Add [tool.setuptools_scm] section
    if 'setuptools_scm' not in data.get('tool', {}):
        content += '\n' + SCM_TOOL_CONFIG
        changed = True

    if changed:
        with open('pyproject.toml', 'w') as f:
            f.write(content)
        print("Updated pyproject.toml with setuptools_scm configuration")
    else:
        print("pyproject.toml already has setuptools_scm configuration")

    # Hint about __version__ in source files
    version_in_src = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'dist', 'build'}]
        for fname in files:
            if fname.endswith('.py'):
                fpath = os.path.join(root, fname)
                with open(fpath) as f:
                    if re.search(r'^\s*__version__\s*=\s*["\'][\d.]+["\']', f.read(), re.MULTILINE):
                        version_in_src.append(fpath)
    if version_in_src:
        print("\nNote: hardcoded __version__ found in:")
        for p in version_in_src:
            print(f"  {p}")
        print("Consider replacing with:")
        print("  from importlib.metadata import version")
        print('  __version__ = version("<package-name>")')

def check_publish_environment():
    """Check that the environment is ready for publishing"""
    errors = []

    # Check pyproject.toml exists
    if not os.path.exists('pyproject.toml'):
        errors.append("pyproject.toml not found")
    else:
        content = open('pyproject.toml').read()
        if 'setuptools_scm' not in content:
            errors.append("pyproject.toml does not use setuptools_scm for versioning")

    # Check build is installed
    result = subprocess.run('python -m build --version', shell=True, capture_output=True)
    if result.returncode != 0:
        errors.append("'build' is not installed (run: pip install build)")

    # Check uv or twine is available for upload
    if detect_upload_tool() is None:
        errors.append("neither 'uv' nor 'twine' is installed (run: pip install twine)")

    if errors:
        for err in errors:
            print(f"Error: {err}")
        sys.exit(1)

def has_git_tags():
    """Return True if the repo has at least one tag"""
    result = subprocess.run('git tag', shell=True, capture_output=True, text=True)
    return bool(result.stdout.strip())

def publish_version(version, tag_only=False, build_only=False, no_build=False, no_upload=False):
    """Publish a new version with configurable steps"""
    if not version.startswith('v'):
        version = f'v{version}'

    if not no_build:
        check_publish_environment()

    # Check for existing tags before creating new one
    first_publish = not no_build and not has_git_tags()

    # Create and push tag
    create_tag(version)

    if tag_only:
        return

    # Build package
    if not no_build:
        env = os.environ.copy()
        if first_publish:
            bare_version = version.lstrip('v')
            print(f"No existing tags found, setting SETUPTOOLS_SCM_PRETEND_VERSION={bare_version}")
            env['SETUPTOOLS_SCM_PRETEND_VERSION'] = bare_version
        build_package(env=env)

    if build_only or no_upload:
        return

    # Upload to PyPI
    upload_package()

    print(f"Successfully published version {version}")

def main():
    parser = argparse.ArgumentParser(
        description='Publish or delete package versions',
        epilog='''
Examples:
  %(prog)s --init-pyproject         # Add setuptools_scm config to pyproject.toml
  %(prog)s --init-repo              # Initialize local git repo
  %(prog)s --init-repo --github     # Initialize git and create GitHub repo
  %(prog)s --init-repo --github myproject  # Initialize with custom repo name
  %(prog)s --github                 # Create GitHub repo (git already initialized)
  %(prog)s --github --private       # Create private GitHub repo
  %(prog)s 0.2.0                    # Full publish: tag, build, upload
  %(prog)s v0.2.0                   # Full publish: tag, build, upload
  %(prog)s 0.2.0 --tag-only         # Only create and push tag
  %(prog)s 0.2.0 --build-only       # Tag and build, don't upload
  %(prog)s 0.2.0 --no-build         # Tag and upload existing dist
  %(prog)s 0.2.0 --no-upload        # Tag and build, don't upload
  %(prog)s --delete-tag 0.2.0       # Delete tag locally and from origin
  %(prog)s --delete-tag v0.2.0      # Delete tag locally and from origin
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('version', nargs='?', help='Version number (e.g., 0.2.0 or v0.2.0) or repo name for --init-repo')
    parser.add_argument('--init-pyproject', action='store_true',
                        help='Add setuptools_scm config to pyproject.toml (creates it if missing)')
    parser.add_argument('--init-repo', action='store_true',
                        help='Initialize local git repository')
    parser.add_argument('--github', action='store_true',
                        help='Create GitHub repository and push (use with --init-repo)')
    parser.add_argument('--private', action='store_true',
                        help='Create private GitHub repository (use with --github)')
    parser.add_argument('--delete-tag', action='store_true',
                        help='Delete the tag locally and from origin instead of publishing')
    parser.add_argument('--tag-only', action='store_true',
                        help='Only create and push the git tag')
    parser.add_argument('--build-only', action='store_true',
                        help='Create tag and build package, but do not upload')
    parser.add_argument('--no-build', action='store_true',
                        help='Skip build step (use existing dist/)')
    parser.add_argument('--no-upload', action='store_true',
                        help='Skip upload step (same as --build-only)')

    args = parser.parse_args()

    if args.init_pyproject:
        init_pyproject()
    elif args.init_repo:
        init_repo()
        if args.github:
            create_github_repo(repo_name=args.version, private=args.private)
    elif args.github:
        create_github_repo(repo_name=args.version, private=args.private)
    elif args.delete_tag:
        if not args.version:
            parser.error('version is required for --delete-tag')
        delete_tag(args.version)
    else:
        if not args.version:
            parser.error('version is required')
        publish_version(
            args.version,
            tag_only=args.tag_only,
            build_only=args.build_only,
            no_build=args.no_build,
            no_upload=args.no_upload
        )

if __name__ == "__main__":
    main()
