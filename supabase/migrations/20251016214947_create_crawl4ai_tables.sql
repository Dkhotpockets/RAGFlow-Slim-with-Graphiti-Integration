-- PostgreSQL migration for Supabase
-- Create Crawl4AI integration tables for RAGflow Slim
-- This migration adds tables for web crawling jobs and content storage

DO $$
BEGIN
	-- Create crawl_jobs table if it doesn't exist
	IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'crawl_jobs') THEN
		CREATE TABLE public.crawl_jobs (
			id VARCHAR(36) PRIMARY KEY,
			url TEXT NOT NULL,
			status VARCHAR(20) NOT NULL DEFAULT 'pending',
			created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
			updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
			completed_at TIMESTAMP WITH TIME ZONE NULL,
			config JSONB NOT NULL,
			result JSONB NULL,
			error_message TEXT NULL
		);
	END IF;
END$$;

-- Create indexes for crawl_jobs table
DO $$
BEGIN
	-- Index for status queries
	IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_crawl_jobs_status') THEN
		CREATE INDEX idx_crawl_jobs_status ON public.crawl_jobs(status);
	END IF;

	-- Index for created_at queries
	IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_crawl_jobs_created_at') THEN
		CREATE INDEX idx_crawl_jobs_created_at ON public.crawl_jobs(created_at DESC);
	END IF;

	-- Index for URL queries (partial index for performance)
	IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_crawl_jobs_url') THEN
		CREATE INDEX idx_crawl_jobs_url ON public.crawl_jobs USING gin (to_tsvector('english', url));
	END IF;
END$$;

DO $$
BEGIN
	-- Create crawl_content table if it doesn't exist
	IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'crawl_content') THEN
		CREATE TABLE public.crawl_content (
			id VARCHAR(36) PRIMARY KEY,
			job_id VARCHAR(36) NOT NULL,
			url TEXT NOT NULL,
			title VARCHAR(500),
			content_hash VARCHAR(64) NOT NULL,
			content_size INTEGER NOT NULL,
			extracted_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
			FOREIGN KEY (job_id) REFERENCES crawl_jobs(id) ON DELETE CASCADE
		);
	END IF;
END$$;

-- Create indexes for crawl_content table
DO $$
BEGIN
	-- Index for job_id foreign key
	IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_crawl_content_job_id') THEN
		CREATE INDEX idx_crawl_content_job_id ON public.crawl_content(job_id);
	END IF;

	-- Unique index for content hash deduplication
	IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_crawl_content_content_hash') THEN
		CREATE UNIQUE INDEX idx_crawl_content_content_hash ON public.crawl_content(content_hash);
	END IF;

	-- Index for extracted_at queries
	IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'idx_crawl_content_extracted_at') THEN
		CREATE INDEX idx_crawl_content_extracted_at ON public.crawl_content(extracted_at DESC);
	END IF;
END$$;

-- Enable Row Level Security (RLS) for crawl_jobs
ALTER TABLE public.crawl_jobs ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for crawl_jobs
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'crawl_jobs' AND policyname = 'Allow all operations for service role'
	) THEN
		CREATE POLICY "Allow all operations for service role" ON public.crawl_jobs
			FOR ALL
			USING (true)
			WITH CHECK (true);
	END IF;
END$$;

-- Enable Row Level Security (RLS) for crawl_content
ALTER TABLE public.crawl_content ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for crawl_content
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'crawl_content' AND policyname = 'Allow all operations for service role'
	) THEN
		CREATE POLICY "Allow all operations for service role" ON public.crawl_content
			FOR ALL
			USING (true)
			WITH CHECK (true);
	END IF;
END$$;

-- Add table comments
COMMENT ON TABLE public.crawl_jobs IS 'Stores web crawling job definitions and status tracking';
COMMENT ON TABLE public.crawl_content IS 'Stores extracted content from web crawling operations';

-- Add column comments for crawl_jobs
COMMENT ON COLUMN public.crawl_jobs.id IS 'Unique identifier for the crawl job (UUID)';
COMMENT ON COLUMN public.crawl_jobs.url IS 'Target URL to be crawled';
COMMENT ON COLUMN public.crawl_jobs.status IS 'Current status of the crawl job (pending, running, completed, failed, cancelled)';
COMMENT ON COLUMN public.crawl_jobs.created_at IS 'Timestamp when the job was created';
COMMENT ON COLUMN public.crawl_jobs.updated_at IS 'Timestamp when the job was last updated';
COMMENT ON COLUMN public.crawl_jobs.completed_at IS 'Timestamp when the job completed (null if not completed)';
COMMENT ON COLUMN public.crawl_jobs.config IS 'JSON configuration for the crawl operation';
COMMENT ON COLUMN public.crawl_jobs.result IS 'JSON result data from the crawl operation (null if not completed)';
COMMENT ON COLUMN public.crawl_jobs.error_message IS 'Error message if the job failed (null if successful)';

-- Add column comments for crawl_content
COMMENT ON COLUMN public.crawl_content.id IS 'Unique identifier for the content entry (UUID)';
COMMENT ON COLUMN public.crawl_content.job_id IS 'Reference to the crawl job that extracted this content';
COMMENT ON COLUMN public.crawl_content.url IS 'URL where the content was extracted from';
COMMENT ON COLUMN public.crawl_content.title IS 'Page title extracted from the content';
COMMENT ON COLUMN public.crawl_content.content_hash IS 'SHA256 hash of the content for deduplication';
COMMENT ON COLUMN public.crawl_content.content_size IS 'Size of the content in bytes';
COMMENT ON COLUMN public.crawl_content.extracted_at IS 'Timestamp when the content was extracted';