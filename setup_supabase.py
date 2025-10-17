#!/usr/bin/env python3
"""Setup Supabase database table for documents"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"Setting up Supabase database...")

try:
    # Create Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase")
    
    # Read the SQL file
    with open('setup_supabase_table.sql', 'r') as f:
        sql_content = f.read()
    
    print("\n📝 SQL to execute:")
    print("-" * 60)
    print(sql_content)
    print("-" * 60)
    
    print("\n⚠️  Please execute this SQL in your Supabase SQL Editor:")
    print(f"   1. Go to: https://supabase.com/dashboard/project/ilgsekabtgymxwgxbkok/sql/new")
    print(f"   2. Copy the SQL from 'setup_supabase_table.sql'")
    print(f"   3. Paste and run it in the SQL Editor")
    print(f"   4. Or copy the SQL shown above")
    
    # Alternative: Try to create table using REST API (limited functionality)
    print("\n🔄 Attempting to create table via API...")
    
    # Note: Direct SQL execution via REST API is limited
    # The best approach is to use the Supabase SQL Editor in the dashboard
    
except Exception as e:
    print(f"❌ Error: {e}")
