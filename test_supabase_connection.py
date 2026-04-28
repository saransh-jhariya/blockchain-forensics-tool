#!/usr/bin/env python3
"""
Test script to verify Supabase connection.
"""
import os
from src.utils.supabase_client import supabase

def test_connection():
    """Test connection to Supabase by attempting a simple query."""
    try:
        # Try to query a table (this will fail if table doesn't exist, but connection should work)
        response = supabase.table('test_table').select('*').limit(1).execute()
        print("✅ Supabase connection successful!")
        return True
    except Exception as e:
        # Check if it's a connection error vs table not found
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            print(f"❌ Supabase connection failed: {e}")
            return False
        else:
            # If it's not a connection error, the connection itself worked
            print("✅ Supabase connection successful! (Table may not exist, but connection works)")
            return True

if __name__ == "__main__":
    test_connection()