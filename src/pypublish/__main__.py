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
    parser.add_argument('version', help='Version number (e.g., 0.2.0 or v0.2.0)')
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

    if args.delete_tag:
        delete_tag(args.version)
    else:
        publish_version(
            args.version,
            tag_only=args.tag_only,
            build_only=args.build_only,
            no_build=args.no_build,
            no_upload=args.no_upload
        )

if __name__ == "__main__":
    main()
