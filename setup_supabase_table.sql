-- Create documents table for RAGflow Slim
-- This table stores document chunks with embeddings for vector search

CREATE TABLE IF NOT EXISTS public.documents (
    id BIGSERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create an index on created_at for faster sorting
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON public.documents(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations with service_role
CREATE POLICY "Allow all operations for service role" ON public.documents
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Optional: If you want to use vector embeddings with pgvector extension in the future
-- CREATE EXTENSION IF NOT EXISTS vector;
-- ALTER TABLE public.documents ADD COLUMN embedding_vector vector(1536);
-- CREATE INDEX ON public.documents USING ivfflat (embedding_vector vector_cosine_ops);

COMMENT ON TABLE public.documents IS 'Stores document chunks with metadata and embeddings for RAG retrieval';
COMMENT ON COLUMN public.documents.text IS 'The actual text content of the document chunk';
COMMENT ON COLUMN public.documents.metadata IS 'JSON metadata including filename, chunk_id, etc.';
COMMENT ON COLUMN public.documents.embedding IS 'JSON representation of the embedding vector';
