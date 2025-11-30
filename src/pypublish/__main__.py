#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse

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

def build_package():
    """Build the package"""
    commands = [
        'rm -rf dist/ build/ *.egg-info',
        'python -m build'
    ]

    for command in commands:
        print(f"Executing: {command}")
        try:
            run_command(command)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {command}")
            print(f"Error: {e}")
            sys.exit(1)

    print("Successfully built package")

def upload_package():
    """Upload the package to PyPI"""
    command = 'twine upload dist/*'
    print(f"Executing: {command}")
    try:
        run_command(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error: {e}")
        sys.exit(1)

    print("Successfully uploaded package to PyPI")

def init_github_repo(repo_name=None, private=False):
    """Initialize git repo and create GitHub repository"""
    import os

    # Get repo name from current directory if not provided
    if repo_name is None:
        repo_name = os.path.basename(os.getcwd())

    # Check if git repo exists
    try:
        subprocess.run(['git', 'status'], capture_output=True, check=True)
        print("Git repository already exists")
    except subprocess.CalledProcessError:
        # Initialize git repo
        print("Initializing git repository...")
        run_command('git init')
        run_command('git add .')
        run_command('git commit -m "Initial commit"')

    # Create GitHub repo and push
    visibility = '--private' if private else '--public'
    command = f'gh repo create {repo_name} {visibility} --source=. --remote=origin --push'
    print(f"Executing: {command}")
    try:
        run_command(command)
        print(f"Successfully created GitHub repository: {repo_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating GitHub repository: {e}")
        sys.exit(1)

def publish_version(version, tag_only=False, build_only=False, no_build=False, no_upload=False):
    """Publish a new version with configurable steps"""
    if not version.startswith('v'):
        version = f'v{version}'

    # Create and push tag
    create_tag(version)

    if tag_only:
        return

    # Build package
    if not no_build:
        build_package()

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
  %(prog)s --init-repo              # Initialize git and create GitHub repo
  %(prog)s --init-repo myproject    # Initialize with custom repo name
  %(prog)s --init-repo --private    # Create private GitHub repo
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
    parser.add_argument('--init-repo', action='store_true',
                        help='Initialize git repo and create GitHub repository')
    parser.add_argument('--private', action='store_true',
                        help='Create private GitHub repository (use with --init-repo)')
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

    if args.init_repo:
        init_github_repo(repo_name=args.version, private=args.private)
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
