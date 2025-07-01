#!/usr/bin/env python3
"""
Platform Agent Environment Cleaner
===================================

A cross-platform script to clean Python virtual environments and caches
for both macOS and Ubuntu systems. Designed to resolve SSL connection issues
and corrupted package caches.

Usage:
    python clean_environment.py              # Interactive mode
    python clean_environment.py --full       # Full cleanup including user caches
    python clean_environment.py --yes        # Auto-confirm all operations
    python clean_environment.py --backup-only # Only create backups
"""

import argparse
import os
import platform
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


class EnvironmentCleaner:
    def __init__(self, auto_confirm: bool = False, full_cleanup: bool = False, backup_only: bool = False):
        self.auto_confirm = auto_confirm
        self.full_cleanup = full_cleanup
        self.backup_only = backup_only
        self.system = platform.system()
        self.project_root = Path.cwd()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def print_header(self):
        """Print script header with system info"""
        print("🧹 Platform Agent Environment Cleaner")
        print("=" * 50)
        print(f"📍 Current directory: {self.project_root}")
        print(f"🖥️  Platform: {self.system} ({platform.platform()})")
        print()
        
    def confirm_project_directory(self) -> bool:
        """Verify we're in the correct project directory"""
        required_files = [
            "src/main.py",
            "src/ops_crew/crew.py", 
            "requirements.txt"
        ]
        
        missing_files = [f for f in required_files if not (self.project_root / f).exists()]
        
        if missing_files:
            print("❌ ERROR: This doesn't appear to be a Platform Agent project directory!")
            print(f"Missing files: {', '.join(missing_files)}")
            print("Please run this script from the project root directory.")
            return False
            
        return True
        
    def get_cleanup_targets(self) -> List[Tuple[Path, str, str]]:
        """Get list of files/directories to clean with descriptions"""
        targets = []
        
        # Project-level targets
        project_targets = [
            (".venv", "Virtual environment directory"),
            ("crew_memory", "CrewAI memory cache"),
            ("tools_cache.json", "MCP tools cache file"),
        ]
        
        for target, description in project_targets:
            path = self.project_root / target
            if path.exists():
                if path.is_file():
                    size = self._format_size(path.stat().st_size)
                else:
                    size = self._get_directory_size(path)
                targets.append((path, description, size))
                
        # Python cache files
        pycache_dirs = list(self.project_root.rglob("__pycache__"))
        if pycache_dirs:
            total_size = sum(self._get_directory_size_bytes(d) for d in pycache_dirs)
            targets.append((None, f"{len(pycache_dirs)} __pycache__ directories", self._format_size(total_size)))
            
        # User-level caches (if full cleanup requested)
        if self.full_cleanup:
            user_caches = self._get_user_cache_targets()
            targets.extend(user_caches)
            
        return targets
        
    def _get_user_cache_targets(self) -> List[Tuple[Path, str, str]]:
        """Get user-level cache directories"""
        targets = []
        home = Path.home()
        
        # UV cache
        uv_cache = home / ".cache" / "uv"
        if uv_cache.exists():
            size = self._get_directory_size(uv_cache)
            targets.append((uv_cache, "UV package manager cache", size))
            
        # Pip cache
        pip_cache = home / ".cache" / "pip"
        if pip_cache.exists():
            size = self._get_directory_size(pip_cache)
            targets.append((pip_cache, "Pip package cache", size))
            
        return targets
        
    def create_backups(self):
        """Create backups of important configuration files"""
        print("📦 Creating backups...")
        
        backup_files = [
            ".env",
            "requirements.txt",
            "uv.lock"
        ]
        
        for filename in backup_files:
            source = self.project_root / filename
            if source.exists():
                backup_name = f"{filename}.backup.{self.timestamp}"
                backup_path = self.project_root / backup_name
                shutil.copy2(source, backup_path)
                print(f"  ✓ {filename} → {backup_name}")
                
        print()
        
    def clean_python_caches(self):
        """Clean Python __pycache__ directories and .pyc files"""
        print("🗑️  Cleaning Python cache files...")
        
        # Remove __pycache__ directories
        pycache_dirs = list(self.project_root.rglob("__pycache__"))
        for cache_dir in pycache_dirs:
            try:
                shutil.rmtree(cache_dir)
            except Exception as e:
                print(f"  ⚠️  Warning: Could not remove {cache_dir}: {e}")
                
        # Remove .pyc files
        pyc_files = list(self.project_root.rglob("*.pyc"))
        for pyc_file in pyc_files:
            try:
                pyc_file.unlink()
            except Exception as e:
                print(f"  ⚠️  Warning: Could not remove {pyc_file}: {e}")
                
        total_cleaned = len(pycache_dirs) + len(pyc_files)
        if total_cleaned > 0:
            print(f"  ✓ Cleaned {len(pycache_dirs)} cache directories and {len(pyc_files)} .pyc files")
        else:
            print("  ✓ No Python cache files found")
            
    def clean_project_files(self, targets: List[Tuple[Path, str, str]]):
        """Clean project-level files and directories"""
        print("🧹 Cleaning project files...")
        
        project_targets = [t for t in targets if t[0] and t[0].is_relative_to(self.project_root)]
        
        for path, description, size in project_targets:
            if path and path.exists():
                try:
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path)
                    print(f"  ✓ Removed {path.name}/ ({size})")
                except Exception as e:
                    print(f"  ❌ Error removing {path}: {e}")
                    
    def clean_user_caches(self, targets: List[Tuple[Path, str, str]]):
        """Clean user-level cache directories"""
        if not self.full_cleanup:
            return
            
        print("🗑️  Cleaning user caches...")
        
        user_targets = [t for t in targets if t[0] and not t[0].is_relative_to(self.project_root)]
        
        for path, description, size in user_targets:
            if path and path.exists():
                try:
                    shutil.rmtree(path)
                    print(f"  ✓ Cleaned {description} ({size})")
                except Exception as e:
                    print(f"  ❌ Error cleaning {description}: {e}")
                    
    def display_targets(self, targets: List[Tuple[Path, str, str]]) -> int:
        """Display cleanup targets and return total size"""
        if not targets:
            print("ℹ️  No cleanup targets found.")
            return 0
            
        print("🔍 Found items to clean:")
        total_size_bytes = 0
        
        for path, description, size in targets:
            print(f"  ✓ {description} ({size})")
            if path and path.exists():
                if path.is_file():
                    total_size_bytes += path.stat().st_size
                else:
                    total_size_bytes += self._get_directory_size_bytes(path)
                    
        print()
        return total_size_bytes
        
    def _get_directory_size(self, path: Path) -> str:
        """Get formatted directory size"""
        size_bytes = self._get_directory_size_bytes(path)
        return self._format_size(size_bytes)
        
    def _get_directory_size_bytes(self, path: Path) -> int:
        """Get directory size in bytes"""
        total = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
        except (PermissionError, OSError):
            pass
        return total
        
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
        
    def get_user_confirmation(self, total_size_bytes: int) -> bool:
        """Get user confirmation for cleanup"""
        if self.auto_confirm:
            return True
            
        total_size = self._format_size(total_size_bytes)
        print(f"💾 Total space to be freed: {total_size}")
        print()
        
        response = input("❓ Proceed with cleanup? [y/N]: ").strip().lower()
        return response in ['y', 'yes']
        
    def print_next_steps(self):
        """Print instructions for rebuilding environment"""
        print("\n🚀 Next steps to rebuild environment:")
        print("  1. uv venv")
        
        if self.system == "Windows":
            print("  2. .venv\\Scripts\\activate")
        else:
            print("  2. source .venv/bin/activate")
            
        print("  3. uv pip install -r requirements.txt")
        print("  4. python src/main.py")
        print()
        print("📝 Note: Configuration files have been backed up with timestamp.")
        
    def run(self):
        """Main execution function"""
        self.print_header()
        
        # Verify project directory
        if not self.confirm_project_directory():
            sys.exit(1)
            
        # Get cleanup targets
        targets = self.get_cleanup_targets()
        total_size_bytes = self.display_targets(targets)
        
        if not targets:
            print("✅ Environment is already clean!")
            return
            
        # Create backups
        self.create_backups()
        
        # Backup-only mode
        if self.backup_only:
            print("✅ Backup completed! Use --full or run without --backup-only to clean.")
            return
            
        # Get confirmation
        if not self.get_user_confirmation(total_size_bytes):
            print("❌ Cleanup cancelled by user.")
            return
            
        print()
        
        # Perform cleanup
        self.clean_project_files(targets)
        self.clean_python_caches()
        self.clean_user_caches(targets)
        
        freed_size = self._format_size(total_size_bytes)
        print(f"\n✅ Environment cleanup completed!")
        print(f"💾 Total space freed: {freed_size}")
        
        # Show next steps
        self.print_next_steps()


def main():
    parser = argparse.ArgumentParser(
        description="Clean Platform Agent Python environment and caches",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clean_environment.py                # Interactive cleanup
  python clean_environment.py --full         # Include user-level caches  
  python clean_environment.py --yes          # Auto-confirm operations
  python clean_environment.py --backup-only  # Only create backups
        """
    )
    
    parser.add_argument('--full', action='store_true',
                       help='Include user-level caches (~/.cache/uv, ~/.cache/pip)')
    parser.add_argument('--yes', action='store_true',
                       help='Automatically confirm all operations')
    parser.add_argument('--backup-only', action='store_true',
                       help='Only create backups, do not clean')
    
    args = parser.parse_args()
    
    try:
        cleaner = EnvironmentCleaner(
            auto_confirm=args.yes,
            full_cleanup=args.full,
            backup_only=args.backup_only
        )
        cleaner.run()
        
    except KeyboardInterrupt:
        print("\n\n❌ Cleanup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()