# Supabase integration for Ragflow Slim
# Contributor-safe, modular connection and document storage
import os
from typing import Optional
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "<your-supabase-url>")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "<your-supabase-key>")

# Only create client if valid credentials are provided
supabase: Optional[Client] = None
if SUPABASE_URL != "<your-supabase-url>" and SUPABASE_KEY != "<your-supabase-key>":
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None

def add_document_to_supabase(text, metadata=None, embedding=None):
    if supabase is None:
        raise RuntimeError("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_KEY environment variables.")
    data = {
        "text": text,
        "metadata": metadata or {},
        "embedding": embedding or {},
    }
    response = supabase.table("documents").insert(data).execute()
    return response

def search_documents_supabase(query_embedding, top_k=3):
    if supabase is None:
        raise RuntimeError("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_KEY environment variables.")
    # Placeholder: implement vector similarity search using Supabase functions or extensions
    # For now, return latest documents
    response = supabase.table("documents").select("*").order("created_at", desc=True).limit(top_k).execute()
    return response.data
