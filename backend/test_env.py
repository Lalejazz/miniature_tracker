#!/usr/bin/env python3
"""
Simple script to test if DATABASE_URL is readable on Render.
"""
import os

print("=== ENVIRONMENT TEST ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT_SET')}")
print(f"All env vars starting with DATABASE:")
for key, value in os.environ.items():
    if 'DATABASE' in key.upper():
        print(f"  {key}: {value}")

# Test database import
print("\n=== DATABASE IMPORT TEST ===")
try:
    from app.database import get_database
    db = get_database()
    print(f"Database type: {type(db).__name__}")
    
    if hasattr(db, 'database_url'):
        print(f"Database URL: {getattr(db, 'database_url', 'None')}")
    
except Exception as e:
    print(f"Error: {e}")

print("\n=== ASYNCPG TEST ===")
try:
    import asyncpg
    print("✅ asyncpg imported successfully")
except ImportError:
    print("❌ asyncpg not available") 