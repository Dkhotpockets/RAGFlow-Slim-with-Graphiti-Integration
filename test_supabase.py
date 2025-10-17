#!/usr/bin/env python3
"""Test Supabase connection and setup"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"Testing Supabase connection...")
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "Key: Not found")

try:
    # Create Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client created successfully!")
    
    # Try to list tables
    response = supabase.table("documents").select("*").limit(1).execute()
    print(f"✅ Successfully connected to Supabase!")
    print(f"   Documents table exists with {len(response.data)} records (showing max 1)")
    
except Exception as e:
    print(f"❌ Error connecting to Supabase: {e}")
    print("\nThis might mean:")
    print("1. The 'documents' table doesn't exist yet (we'll create it)")
    print("2. There's a network issue")
    print("3. The credentials are incorrect")
