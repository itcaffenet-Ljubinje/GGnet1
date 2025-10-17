#!/usr/bin/env python3
"""
ggNet RAM Cache Manager

Simple in-memory cache manager that simulates FIFO behavior for image caching.
Collects statistics and can serve metrics via HTTP endpoint.

Usage:
    # As library
    from ram_cache_manager import RAMCacheManager
    cache = RAMCacheManager(max_size_mb=512)
    cache.put("image1", data)
    data = cache.get("image1")
    
    # As HTTP service
    python ram_cache_manager.py --port 8081 --size 1024
"""

import sys
import time
import threading
from pathlib import Path
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class CacheEntry:
    """Represents a cached item"""
    key: str
    size_bytes: int
    data: Any
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    
    def touch(self):
        """Update last accessed time and increment counter"""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    puts: int = 0
    current_entries: int = 0
    current_size_bytes: int = 0
    max_size_bytes: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    @property
    def utilization(self) -> float:
        """Calculate cache utilization percentage"""
        return (self.current_size_bytes / self.max_size_bytes * 100) if self.max_size_bytes > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary"""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "puts": self.puts,
            "current_entries": self.current_entries,
            "current_size_mb": round(self.current_size_bytes / (1024 * 1024), 2),
            "max_size_mb": round(self.max_size_bytes / (1024 * 1024), 2),
            "hit_rate_percent": round(self.hit_rate, 2),
            "utilization_percent": round(self.utilization, 2)
        }


class RAMCacheManager:
    """
    Simple FIFO (First-In-First-Out) RAM cache manager
    
    Features:
    - Fixed maximum size limit
    - FIFO eviction policy
    - Thread-safe operations
    - Statistics tracking
    - Simulates image caching behavior
    """
    
    def __init__(self, max_size_mb: int = 512):
        """
        Initialize cache manager
        
        Args:
            max_size_mb: Maximum cache size in megabytes
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        self.stats = CacheStats(max_size_bytes=self.max_size_bytes)
        
        print(f"✅ RAM Cache initialized: {max_size_mb} MB")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found
        """
        with self.lock:
            entry = self.cache.get(key)
            
            if entry:
                entry.touch()
                self.stats.hits += 1
                return entry.data
            else:
                self.stats.misses += 1
                return None
    
    def put(self, key: str, data: Any, size_bytes: Optional[int] = None) -> bool:
        """
        Put item into cache
        
        Args:
            key: Cache key
            data: Data to cache
            size_bytes: Size in bytes (estimated from data if not provided)
            
        Returns:
            True if successfully cached, False otherwise
        """
        with self.lock:
            # Estimate size if not provided
            if size_bytes is None:
                if isinstance(data, (str, bytes)):
                    size_bytes = len(data)
                elif isinstance(data, Path):
                    size_bytes = data.stat().st_size if data.exists() else 0
                else:
                    size_bytes = sys.getsizeof(data)
            
            # Check if item is too large
            if size_bytes > self.max_size_bytes:
                print(f"⚠️  Item too large for cache: {key} ({size_bytes} bytes)")
                return False
            
            # Remove existing entry if updating
            if key in self.cache:
                old_entry = self.cache.pop(key)
                self.stats.current_size_bytes -= old_entry.size_bytes
                self.stats.current_entries -= 1
            
            # Evict items if necessary (FIFO)
            while self.stats.current_size_bytes + size_bytes > self.max_size_bytes:
                if not self.cache:
                    break
                self._evict_oldest()
            
            # Add new entry
            entry = CacheEntry(
                key=key,
                size_bytes=size_bytes,
                data=data
            )
            
            self.cache[key] = entry
            self.stats.current_size_bytes += size_bytes
            self.stats.current_entries += 1
            self.stats.puts += 1
            
            return True
    
    def _evict_oldest(self):
        """Evict the oldest (first) item from cache"""
        if not self.cache:
            return
        
        # Pop first item (FIFO)
        key, entry = self.cache.popitem(last=False)
        self.stats.current_size_bytes -= entry.size_bytes
        self.stats.current_entries -= 1
        self.stats.evictions += 1
        
        print(f"🗑️  Evicted: {key} ({entry.size_bytes} bytes)")
    
    def remove(self, key: str) -> bool:
        """
        Remove item from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if removed, False if not found
        """
        with self.lock:
            if key in self.cache:
                entry = self.cache.pop(key)
                self.stats.current_size_bytes -= entry.size_bytes
                self.stats.current_entries -= 1
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.stats.current_size_bytes = 0
            self.stats.current_entries = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return self.stats.to_dict()
    
    def get_entries(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all cached entries"""
        with self.lock:
            entries = {}
            for key, entry in self.cache.items():
                entries[key] = {
                    "size_bytes": entry.size_bytes,
                    "size_mb": round(entry.size_bytes / (1024 * 1024), 2),
                    "created_at": datetime.fromtimestamp(entry.created_at).isoformat(),
                    "last_accessed": datetime.fromtimestamp(entry.last_accessed).isoformat(),
                    "access_count": entry.access_count,
                    "age_seconds": round(time.time() - entry.created_at, 2)
                }
            return entries
    
    def __len__(self) -> int:
        """Return number of cached items"""
        return len(self.cache)
    
    def __contains__(self, key: str) -> bool:
        """Check if key is in cache"""
        return key in self.cache


# HTTP Metrics Server (Optional)
def run_metrics_server(cache: RAMCacheManager, port: int = 8081):
    """
    Run simple HTTP server for cache metrics
    
    Args:
        cache: RAMCacheManager instance
        port: HTTP port
    """
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    class MetricsHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/metrics":
                # Metrics endpoint
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                
                metrics = {
                    "stats": cache.get_stats(),
                    "entries": cache.get_entries(),
                    "timestamp": datetime.now().isoformat()
                }
                
                self.wfile.write(json.dumps(metrics, indent=2).encode())
            
            elif self.path == "/":
                # Simple HTML dashboard
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                
                stats = cache.get_stats()
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>ggNet RAM Cache Metrics</title>
                    <meta http-equiv="refresh" content="5">
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .stat {{ margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 5px; }}
                        .label {{ font-weight: bold; }}
                        .value {{ float: right; }}
                        h1 {{ color: #2563eb; }}
                    </style>
                </head>
                <body>
                    <h1>ggNet RAM Cache Metrics</h1>
                    <p><em>Auto-refreshes every 5 seconds</em></p>
                    
                    <h2>Statistics</h2>
                    <div class="stat"><span class="label">Hits:</span><span class="value">{stats['hits']}</span></div>
                    <div class="stat"><span class="label">Misses:</span><span class="value">{stats['misses']}</span></div>
                    <div class="stat"><span class="label">Hit Rate:</span><span class="value">{stats['hit_rate_percent']}%</span></div>
                    <div class="stat"><span class="label">Evictions:</span><span class="value">{stats['evictions']}</span></div>
                    <div class="stat"><span class="label">Current Entries:</span><span class="value">{stats['current_entries']}</span></div>
                    <div class="stat"><span class="label">Cache Size:</span><span class="value">{stats['current_size_mb']} / {stats['max_size_mb']} MB</span></div>
                    <div class="stat"><span class="label">Utilization:</span><span class="value">{stats['utilization_percent']}%</span></div>
                    
                    <p><a href="/metrics">JSON Metrics</a></p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            # Suppress request logging
            pass
    
    server = HTTPServer(("0.0.0.0", port), MetricsHandler)
    print(f"🌐 Metrics server running at http://0.0.0.0:{port}")
    print(f"   Dashboard: http://localhost:{port}/")
    print(f"   JSON API: http://localhost:{port}/metrics")
    print(f"   Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")


# Demo / Testing
def demo():
    """Demonstration of cache functionality"""
    print("=" * 60)
    print("ggNet RAM Cache Manager Demo")
    print("=" * 60)
    print()
    
    # Create cache with 10 MB limit
    cache = RAMCacheManager(max_size_mb=10)
    
    # Simulate caching some images
    print("\n📥 Adding items to cache...")
    cache.put("image1", b"A" * (3 * 1024 * 1024), size_bytes=3 * 1024 * 1024)  # 3 MB
    cache.put("image2", b"B" * (4 * 1024 * 1024), size_bytes=4 * 1024 * 1024)  # 4 MB
    cache.put("image3", b"C" * (2 * 1024 * 1024), size_bytes=2 * 1024 * 1024)  # 2 MB
    
    print(f"\n📊 Cache stats:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test retrieval
    print("\n🔍 Testing retrieval...")
    result = cache.get("image1")
    print(f"   image1 found: {result is not None}")
    
    result = cache.get("nonexistent")
    print(f"   nonexistent found: {result is not None}")
    
    # Add item that causes eviction
    print("\n📥 Adding large item (will cause eviction)...")
    cache.put("image4", b"D" * (5 * 1024 * 1024), size_bytes=5 * 1024 * 1024)  # 5 MB
    
    # Check what's still in cache
    print("\n📋 Cached entries:")
    entries = cache.get_entries()
    for key, info in entries.items():
        print(f"   {key}: {info['size_mb']} MB, accessed {info['access_count']} times")
    
    print(f"\n📊 Final stats:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Demo complete!")


# CLI Entry Point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ggNet RAM Cache Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run demo
  python ram_cache_manager.py --demo
  
  # Run metrics server
  python ram_cache_manager.py --serve --port 8081 --size 1024
        """
    )
    
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--serve", action="store_true", help="Run metrics HTTP server")
    parser.add_argument("--port", type=int, default=8081, help="HTTP port (default: 8081)")
    parser.add_argument("--size", type=int, default=512, help="Cache size in MB (default: 512)")
    
    args = parser.parse_args()
    
    if args.demo:
        demo()
    elif args.serve:
        cache = RAMCacheManager(max_size_mb=args.size)
        run_metrics_server(cache, port=args.port)
    else:
        parser.print_help()

