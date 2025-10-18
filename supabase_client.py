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
    """
    Search documents using vector similarity with Supabase pgvector.

    Requires pgvector extension and a match_documents RPC function in Supabase.
    Falls back to latest documents if vector search fails.

    Args:
        query_embedding: The query embedding vector (list of floats)
        top_k: Number of results to return

    Returns:
        List of matching documents with similarity scores
    """
    if supabase is None:
        raise RuntimeError("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_KEY environment variables.")

    try:
        # Try vector similarity search using pgvector RPC function
        # This requires a match_documents function in Supabase:
        # CREATE OR REPLACE FUNCTION match_documents(
        #   query_embedding vector(1536),
        #   match_threshold float,
        #   match_count int
        # )
        # RETURNS TABLE (id bigint, text text, metadata jsonb, embedding vector, similarity float)
        # AS $$
        #   SELECT id, text, metadata, embedding,
        #   1 - (embedding <=> query_embedding) AS similarity
        #   FROM documents
        #   WHERE 1 - (embedding <=> query_embedding) > match_threshold
        #   ORDER BY embedding <=> query_embedding
        #   LIMIT match_count;
        # $$ LANGUAGE SQL STABLE;

        response = supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.0,  # Include all results
                'match_count': top_k
            }
        ).execute()

        if response.data:
            return response.data
        else:
            # Fallback if no results
            response = supabase.table("documents").select("*").order("created_at", desc=True).limit(top_k).execute()
            return response.data

    except Exception as e:
        # Fallback to latest documents if vector search not available
        import logging
        logging.warning(f"Vector search failed, falling back to latest documents: {e}")
        response = supabase.table("documents").select("*").order("created_at", desc=True).limit(top_k).execute()
        return response.data
