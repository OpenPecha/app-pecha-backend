#!/usr/bin/env python3
"""
Sprint Release Script with Timestamp Versioning
Automatically creates version tags and updates project version
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
import toml
import argparse


class SprintReleaser:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.pyproject_path = project_root / "pyproject.toml"
        
    def generate_timestamp_version(self) -> str:
        """Generate timestamp-based version: YYYY.MM.DD.HHMM"""
        now = datetime.now()
        return now.strftime("%Y.%m.%d.%H%M")
    
    def update_pyproject_version(self, version: str) -> None:
        """Update version in pyproject.toml"""
        if not self.pyproject_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at {self.pyproject_path}")
        
        # Read current pyproject.toml
        with open(self.pyproject_path, 'r') as f:
            data = toml.load(f)
        
        # Update version
        old_version = data['tool']['poetry']['version']
        data['tool']['poetry']['version'] = version
        
        # Write back
        with open(self.pyproject_path, 'w') as f:
            toml.dump(data, f)
        
        print(f"✅ Updated pyproject.toml version: {old_version} → {version}")
    
    def run_git_command(self, command: list) -> str:
        """Run git command and return output"""
        try:
            result = subprocess.run(
                command, 
                cwd=self.project_root,
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ Git command failed: {' '.join(command)}")
            print(f"Error: {e.stderr}")
            sys.exit(1)
    
    def check_git_status(self) -> None:
        """Check if working directory is clean"""
        status = self.run_git_command(['git', 'status', '--porcelain'])
        if status:
            print("❌ Working directory is not clean. Please commit or stash changes first.")
            print("Uncommitted changes:")
            print(status)
            sys.exit(1)
        print("✅ Working directory is clean")
    
    def create_git_tag(self, version: str, tag_type: str = "sprint") -> None:
        """Create and push git tag"""
        tag_name = f"{tag_type}-{version}"
        
        # Create annotated tag
        tag_message = f"{tag_type.title()} release {version}"
        self.run_git_command(['git', 'tag', '-a', tag_name, '-m', tag_message])
        print(f"✅ Created tag: {tag_name}")
        
        # Push tag to remote
        self.run_git_command(['git', 'push', 'origin', tag_name])
        print(f"✅ Pushed tag to remote: {tag_name}")
    
    def commit_version_update(self, version: str) -> None:
        """Commit the version update"""
        self.run_git_command(['git', 'add', 'pyproject.toml'])
        commit_message = f"chore: bump version to {version}"
        self.run_git_command(['git', 'commit', '-m', commit_message])
        print(f"✅ Committed version update: {version}")
    
    def get_current_branch(self) -> str:
        """Get current git branch"""
        return self.run_git_command(['git', 'branch', '--show-current'])
    
    def release_sprint(self, tag_type: str = "sprint", push_changes: bool = True) -> str:
        """Complete sprint release process"""
        print(f"🚀 Starting {tag_type} release process...")
        
        # Check git status
        self.check_git_status()
        
        # Get current branch
        current_branch = self.get_current_branch()
        print(f"📋 Current branch: {current_branch}")
        
        # Generate version
        version = self.generate_timestamp_version()
        print(f"📅 Generated version: {version}")
        
        # Update pyproject.toml
        self.update_pyproject_version(version)
        
        # Commit version update
        self.commit_version_update(version)
        
        # Create and push tag
        self.create_git_tag(version, tag_type)
        
        # Push commits to remote
        if push_changes:
            self.run_git_command(['git', 'push', 'origin', current_branch])
            print(f"✅ Pushed changes to {current_branch}")
        
        print(f"🎉 {tag_type.title()} release {version} completed successfully!")
        return version


def main():
    parser = argparse.ArgumentParser(description="Create sprint release with timestamp versioning")
    parser.add_argument(
        "--type", 
        choices=["sprint", "release", "hotfix"], 
        default="sprint",
        help="Type of release (default: sprint)"
    )
    parser.add_argument(
        "--no-push", 
        action="store_true",
        help="Don't push changes to remote"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true", 
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    # Find project root
    project_root = Path(__file__).parent.parent
    
    if args.dry_run:
        version = datetime.now().strftime("%Y.%m.%d.%H%M")
        print(f"🔍 DRY RUN - Would create {args.type} release:")
        print(f"   Version: {version}")
        print(f"   Tag: {args.type}-{version}")
        print(f"   Push changes: {not args.no_push}")
        return
    
    try:
        releaser = SprintReleaser(project_root)
        version = releaser.release_sprint(
            tag_type=args.type,
            push_changes=not args.no_push
        )
        
        print(f"\n📋 Release Summary:")
        print(f"   Version: {version}")
        print(f"   Tag: {args.type}-{version}")
        print(f"   Project: pecha-api")
        
    except Exception as e:
        print(f"❌ Release failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
