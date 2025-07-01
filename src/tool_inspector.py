#!/usr/bin/env python3
"""
Tool Inspector CLI - Manual MCP Tool Discovery and Cache Management

This script provides a command-line interface for manually discovering and caching
MCP tools, useful for development, debugging, and CI/CD pipelines.

Usage:
    python src/tool_inspector.py --refresh    # Force refresh cache
    python src/tool_inspector.py --check      # Check cache status
    python src/tool_inspector.py --list       # List cached tools
"""

import argparse
import json
import pathlib
import sys
from datetime import datetime
from typing import Dict, List

# Add src to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from ops_crew.crew import OpsCrew


def refresh_cache() -> Dict:
    """Force refresh the tools cache"""
    print("🔍 Forcing tool discovery and cache refresh...")
    
    try:
        ops_crew = OpsCrew()
        discovery_crew = ops_crew.discovery_crew()
        result = discovery_crew.kickoff()
        
        print(f"✅ Tool discovery completed: {result}")
        
        # Read and return the updated cache
        cache_path = pathlib.Path("tools_cache.json")
        if cache_path.exists():
            cache_data = json.loads(cache_path.read_text())
            print(f"📋 Successfully cached {len(cache_data.get('tools', []))} tools")
            return cache_data
        else:
            print("❌ Cache file was not created")
            return {}
            
    except Exception as e:
        print(f"❌ Error during tool discovery: {e}")
        return {}


def check_cache_status() -> None:
    """Check the current cache status"""
    cache_path = pathlib.Path("tools_cache.json")
    
    if not cache_path.exists():
        print("❌ Cache file does not exist")
        print("💡 Run with --refresh to create cache")
        return
    
    try:
        cache_data = json.loads(cache_path.read_text())
        fetched_at = datetime.fromisoformat(cache_data.get("fetched_at", ""))
        tools_count = len(cache_data.get("tools", []))
        
        age = datetime.now() - fetched_at
        # Check if cache is older than 24 hours
        is_stale = age.total_seconds() > 24 * 3600
        
        print(f"📋 Cache Status:")
        print(f"   📅 Last updated: {fetched_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   ⏰ Age: {age}")
        print(f"   🔧 Tools cached: {tools_count}")
        print(f"   {'🔴 STALE' if is_stale else '🟢 FRESH'} (24h threshold)")
        
        if is_stale:
            print("💡 Run with --refresh to update cache")
            
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"❌ Cache file is corrupted: {e}")
        print("💡 Run with --refresh to rebuild cache")


def list_cached_tools() -> None:
    """List all tools in the cache with details"""
    cache_path = pathlib.Path("tools_cache.json")
    
    if not cache_path.exists():
        print("❌ Cache file does not exist")
        print("💡 Run with --refresh to create cache")
        return
    
    try:
        cache_data = json.loads(cache_path.read_text())
        tools = cache_data.get("tools", [])
        
        if not tools:
            print("📋 No tools found in cache")
            return
        
        print(f"📋 Cached Tools ({len(tools)} total):")
        print("=" * 80)
        
        # Group tools by prefix for better organization
        grouped_tools = {}
        for tool in tools:
            name = tool.get("name", "unknown")
            prefix = name.split("_")[0].lower() if "_" in name else "other"
            if prefix not in grouped_tools:
                grouped_tools[prefix] = []
            grouped_tools[prefix].append(tool)
        
        for prefix, tool_group in sorted(grouped_tools.items()):
            print(f"\n🔧 {prefix.upper()} Tools:")
            for tool in sorted(tool_group, key=lambda x: x.get("name", "")):
                name = tool.get("name", "unknown")
                desc = tool.get("description", "No description")
                params = tool.get("parameters", {})
                required = params.get("required", [])
                
                print(f"   • {name}")
                print(f"     📝 {desc}")
                if required:
                    print(f"     📋 Required params: {', '.join(required)}")
                print()
                
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ Error reading cache: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="MCP Tool Inspector - Discover and manage tool cache",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/tool_inspector.py --refresh    # Force cache refresh
  python src/tool_inspector.py --check      # Check cache status  
  python src/tool_inspector.py --list       # List all cached tools
        """
    )
    
    parser.add_argument("--refresh", action="store_true", 
                       help="Force refresh the tools cache")
    parser.add_argument("--check", action="store_true",
                       help="Check current cache status")
    parser.add_argument("--list", action="store_true",
                       help="List all cached tools with details")
    
    args = parser.parse_args()
    
    # Require at least one action
    if not any([args.refresh, args.check, args.list]):
        parser.print_help()
        return
    
    print("🔧 MCP Tool Inspector")
    print("=" * 50)
    
    if args.refresh:
        refresh_cache()
        print()
    
    if args.check:
        check_cache_status()
        print()
    
    if args.list:
        list_cached_tools()


if __name__ == "__main__":
    main() 