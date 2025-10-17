-- PostgreSQL migration for Supabase
-- Create documents table for RAGflow Slim
-- This table stores document chunks with embeddings for vector search

DO $$
BEGIN
	IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'documents') THEN
		CREATE TABLE public.documents (
			id BIGSERIAL PRIMARY KEY,
			text TEXT NOT NULL,
			metadata JSONB DEFAULT '{}'::jsonb,
			embedding JSONB DEFAULT '{}'::jsonb,
			created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
			updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
		);
	END IF;
END$$;

-- Create index only if it doesn't exist
DO $$
BEGIN
	IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_documents_created_at') THEN
		CREATE INDEX idx_documents_created_at ON public.documents(created_at DESC);
	END IF;
END$$;

-- Enable Row Level Security (RLS)
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations for service_role
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'Allow all operations for service role'
	) THEN
		CREATE POLICY "Allow all operations for service role" ON public.documents
			FOR ALL
			USING (true)
			WITH CHECK (true);
	END IF;
END$$;

COMMENT ON TABLE public.documents IS 'Stores document chunks with metadata and embeddings for RAG retrieval';
COMMENT ON COLUMN public.documents.text IS 'The actual text content of the document chunk';
COMMENT ON COLUMN public.documents.metadata IS 'JSON metadata including filename, chunk_id, etc.';
COMMENT ON COLUMN public.documents.embedding IS 'JSON representation of the embedding vector';
