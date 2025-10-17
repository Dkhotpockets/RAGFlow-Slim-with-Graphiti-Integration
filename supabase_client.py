# Supabase integration for Ragflow Slim
# Contributor-safe, modular connection and document storage
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "<your-supabase-url>")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "<your-supabase-key>")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_document_to_supabase(text, metadata=None, embedding=None):
    data = {
        "text": text,
        "metadata": metadata or {},
        "embedding": embedding or {},
    }
    response = supabase.table("documents").insert(data).execute()
    return response

def search_documents_supabase(query_embedding, top_k=3):
    # Placeholder: implement vector similarity search using Supabase functions or extensions
    # For now, return latest documents
    response = supabase.table("documents").select("*").order("created_at", desc=True).limit(top_k).execute()
    return response.data
