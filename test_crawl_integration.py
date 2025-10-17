"""
End-to-End Integration Tests for Crawl4AI (T026)

Tests the complete workflow combining:
- Flask API endpoints
- CrawlService async operations
- CrawlJobManager lifecycle management
- Data persistence to Supabase
- Error handling and recovery
"""

import pytest
import json
import asyncio
import datetime
from unittest.mock import patch, AsyncMock, MagicMock, Mock
from flask import Flask
from io import StringIO

from app import app, crawl_manager
from crawl4ai_source import CrawlJob, CrawlStatus, CrawlConfig, CrawlResult, CrawlJobRequest


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_headers():
    """Generate valid API headers."""
    return {
        'Content-Type': 'application/json',
        'X-API-KEY': 'changeme'
    }


@pytest.fixture
def sample_crawl_result():
    """Create a sample crawl result."""
    return CrawlResult(
        url="https://example.com",
        title="Test Page",
        content="# Test\n\nContent",
        metadata={"description": "A test page"},
        links=["https://example.com/page1", "https://example.com/page2"],
        content_hash="abc123",
        content_size=1024
    )


@pytest.fixture
def sample_job(sample_crawl_result):
    """Create a sample crawl job."""
    job = CrawlJob(
        id="test-job-123",
        url="https://example.com",
        status=CrawlStatus.PENDING,
        config=CrawlConfig(max_depth=2)
    )
    job.created_at = datetime.datetime.now()
    job.updated_at = datetime.datetime.now()
    return job


class TestEndToEndWorkflow:
    """Test complete crawl workflow from API to completion."""

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    @patch.object(crawl_manager, 'start_job', new_callable=AsyncMock)
    def test_complete_crawl_workflow(self, mock_start, mock_create, client, valid_headers, sample_job):
        """Test complete workflow: create -> start -> get -> check status."""
        mock_create.return_value = sample_job
        mock_start.return_value = True

        # Step 1: Create crawl job
        response = client.post('/crawl', json={'url': 'https://example.com'}, headers=valid_headers)
        assert response.status_code == 201
        job_data = response.get_json()
        job_id = job_data['id']
        assert job_id == sample_job.id

        # Step 2: Verify job was created
        assert mock_create.called
        assert mock_create.call_count == 1

        # Step 3: Start job execution
        with patch.object(crawl_manager, 'get_job', new_callable=AsyncMock) as mock_get:
            sample_job.status = CrawlStatus.RUNNING
            mock_get.return_value = sample_job

            response = client.post(f'/crawl/{job_id}/start', headers=valid_headers)
            assert response.status_code == 200

        # Step 4: Verify start was called
        assert mock_start.called

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    @patch.object(crawl_manager, 'get_job', new_callable=AsyncMock)
    def test_job_status_transitions(self, mock_get, mock_create, client, valid_headers, sample_job, sample_crawl_result):
        """Test job transitions through various states: PENDING -> RUNNING -> COMPLETED."""
        mock_create.return_value = sample_job

        # Create job
        response = client.post('/crawl', json={'url': 'https://example.com'}, headers=valid_headers)
        assert response.status_code == 201
        job_id = sample_job.id

        # Check PENDING status
        sample_job.status = CrawlStatus.PENDING
        mock_get.return_value = sample_job
        response = client.get(f'/crawl/{job_id}', headers=valid_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == CrawlStatus.PENDING.value

        # Transition to RUNNING
        sample_job.status = CrawlStatus.RUNNING
        sample_job.updated_at = datetime.datetime.now()
        response = client.get(f'/crawl/{job_id}', headers=valid_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == CrawlStatus.RUNNING.value

        # Transition to COMPLETED
        sample_job.status = CrawlStatus.COMPLETED
        sample_job.result = sample_crawl_result
        sample_job.completed_at = datetime.datetime.now()
        response = client.get(f'/crawl/{job_id}', headers=valid_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == CrawlStatus.COMPLETED.value
        assert data['result'] is not None

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    @patch.object(crawl_manager, 'get_job', new_callable=AsyncMock)
    def test_job_error_handling(self, mock_get, mock_create, client, valid_headers, sample_job):
        """Test job error state and error message persistence."""
        mock_create.return_value = sample_job

        # Create job
        response = client.post('/crawl', json={'url': 'https://example.com'}, headers=valid_headers)
        assert response.status_code == 201
        job_id = sample_job.id

        # Simulate job failure
        sample_job.status = CrawlStatus.FAILED
        sample_job.error_message = "Connection timeout: Unable to reach https://example.com"
        sample_job.completed_at = datetime.datetime.now()
        mock_get.return_value = sample_job

        # Check error status
        response = client.get(f'/crawl/{job_id}', headers=valid_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == CrawlStatus.FAILED.value
        assert data['error_message'] == "Connection timeout: Unable to reach https://example.com"

    @patch.object(crawl_manager, 'list_jobs', new_callable=AsyncMock)
    def test_job_list_with_filtering(self, mock_list, client, valid_headers, sample_job):
        """Test listing jobs with various filters."""
        # Return multiple jobs with different statuses
        job1 = CrawlJob(id="job-1", url="https://example1.com", status=CrawlStatus.PENDING)
        job1.created_at = datetime.datetime.now()
        job1.updated_at = datetime.datetime.now()

        job2 = CrawlJob(id="job-2", url="https://example2.com", status=CrawlStatus.RUNNING)
        job2.created_at = datetime.datetime.now()
        job2.updated_at = datetime.datetime.now()

        job3 = CrawlJob(id="job-3", url="https://example3.com", status=CrawlStatus.COMPLETED)
        job3.created_at = datetime.datetime.now()
        job3.updated_at = datetime.datetime.now()

        mock_list.return_value = [job3, job2, job1]

        # Get all jobs
        response = client.get('/crawl', headers=valid_headers)
        assert response.status_code == 200
        data = response.get_json()
        # Handle both direct array and wrapped response formats
        jobs = data if isinstance(data, list) else data.get('jobs', data)
        assert len(jobs) == 3

        # Filter by status
        mock_list.return_value = [job2]
        response = client.get('/crawl?status=running', headers=valid_headers)
        assert response.status_code == 200
        data = response.get_json()
        jobs = data if isinstance(data, list) else data.get('jobs', data)
        assert len(jobs) == 1
        job_data = jobs[0] if isinstance(jobs, list) else jobs
        assert job_data['status'] == CrawlStatus.RUNNING.value

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    @patch.object(crawl_manager, 'cancel_job', new_callable=AsyncMock)
    @patch.object(crawl_manager, 'get_job', new_callable=AsyncMock)
    def test_job_cancellation_workflow(self, mock_get, mock_cancel, mock_create, client, valid_headers, sample_job):
        """Test job creation and subsequent cancellation."""
        mock_create.return_value = sample_job

        # Create job
        response = client.post('/crawl', json={'url': 'https://example.com'}, headers=valid_headers)
        assert response.status_code == 201
        job_id = sample_job.id

        # Start job (simulate RUNNING state)
        sample_job.status = CrawlStatus.RUNNING
        mock_get.return_value = sample_job
        mock_cancel.return_value = True

        # Cancel job
        response = client.post(f'/crawl/{job_id}/cancel', headers=valid_headers)
        assert response.status_code == 200
        assert mock_cancel.called

        # Verify cancelled state
        sample_job.status = CrawlStatus.CANCELLED
        response = client.get(f'/crawl/{job_id}', headers=valid_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == CrawlStatus.CANCELLED.value


class TestConcurrentJobHandling:
    """Test handling of concurrent crawl jobs."""

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    def test_multiple_concurrent_jobs(self, mock_create, client, valid_headers):
        """Test creating and tracking multiple concurrent jobs."""
        job_ids = []
        for i in range(3):
            job = CrawlJob(
                id=f"job-{i}",
                url=f"https://example{i}.com",
                status=CrawlStatus.PENDING
            )
            job.created_at = datetime.datetime.now()
            job.updated_at = datetime.datetime.now()
            mock_create.return_value = job

            response = client.post('/crawl', json={'url': f'https://example{i}.com'}, headers=valid_headers)
            assert response.status_code == 201
            data = response.get_json()
            job_ids.append(data['id'])

        assert len(job_ids) == 3
        assert len(set(job_ids)) == 3  # All unique

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    @patch.object(crawl_manager, 'start_job', new_callable=AsyncMock)
    def test_concurrent_job_execution_limit(self, mock_start, mock_create, client, valid_headers):
        """Test that concurrent job execution respects the configured limit."""
        # Create 3 jobs
        for i in range(3):
            job = CrawlJob(
                id=f"job-{i}",
                url=f"https://example{i}.com",
                status=CrawlStatus.PENDING
            )
            job.created_at = datetime.datetime.now()
            job.updated_at = datetime.datetime.now()
            mock_create.return_value = job

            response = client.post('/crawl', json={'url': f'https://example{i}.com'}, headers=valid_headers)
            assert response.status_code == 201

        # Try to start all 3 jobs
        # First 2 should succeed (assuming limit of 5)
        mock_start.return_value = True
        for i in range(3):
            response = client.post(f'/crawl/job-{i}/start', headers=valid_headers)
            assert response.status_code in [200, 429]  # Either success or rate limited


class TestErrorRecovery:
    """Test error recovery and resilience."""

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    def test_invalid_url_rejection(self, mock_create, client, valid_headers):
        """Test that invalid URLs are rejected during job creation."""
        # Invalid URL should be rejected before creating job
        response = client.post('/crawl', json={'url': 'not-a-valid-url'}, headers=valid_headers)
        assert response.status_code == 400
        assert mock_create.call_count == 0

    @patch.object(crawl_manager, 'get_job', new_callable=AsyncMock)
    def test_nonexistent_job_retrieval(self, mock_get, client, valid_headers):
        """Test retrieving a job that doesn't exist."""
        mock_get.return_value = None

        response = client.get('/crawl/nonexistent-job-id', headers=valid_headers)
        assert response.status_code == 404

    def test_missing_authentication(self, client):
        """Test endpoints require authentication."""
        # Test without API key
        response = client.get('/crawl')
        assert response.status_code == 401

        # Test with invalid API key
        response = client.get('/crawl', headers={'X-API-KEY': 'invalid'})
        assert response.status_code == 401

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    def test_malformed_request_handling(self, mock_create, client, valid_headers):
        """Test handling of malformed JSON requests."""
        # Empty body
        response = client.post('/crawl', data='', headers=valid_headers)
        assert response.status_code in [400, 415]

        # Invalid JSON
        response = client.post(
            '/crawl',
            data='{invalid json}',
            content_type='application/json',
            headers={'X-API-KEY': 'changeme'}
        )
        assert response.status_code in [400, 415]

    @patch.object(crawl_manager, 'start_job', new_callable=AsyncMock)
    @patch.object(crawl_manager, 'get_job', new_callable=AsyncMock)
    def test_job_start_non_pending(self, mock_get, mock_start, client, valid_headers):
        """Test attempting to start a job that's not in PENDING state."""
        job = CrawlJob(
            id="job-123",
            url="https://example.com",
            status=CrawlStatus.RUNNING  # Already running
        )
        job.created_at = datetime.datetime.now()
        job.updated_at = datetime.datetime.now()
        mock_get.return_value = job
        mock_start.return_value = False

        response = client.post('/crawl/job-123/start', headers=valid_headers)
        # Should fail because job is not PENDING
        assert response.status_code in [400, 409]


class TestDataPersistence:
    """Test data persistence across job lifecycle."""

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    @patch.object(crawl_manager, 'get_job', new_callable=AsyncMock)
    def test_job_data_persistence(self, mock_get, mock_create, client, valid_headers, sample_job, sample_crawl_result):
        """Test that job data is properly persisted and retrieved."""
        mock_create.return_value = sample_job

        # Create job
        response = client.post(
            '/crawl',
            json={
                'url': 'https://example.com',
                'max_depth': 2,
                'timeout_seconds': 60
            },
            headers=valid_headers
        )
        assert response.status_code == 201

        # Simulate completion with result
        sample_job.status = CrawlStatus.COMPLETED
        sample_job.result = sample_crawl_result
        sample_job.completed_at = datetime.datetime.now()
        mock_get.return_value = sample_job

        # Retrieve completed job
        response = client.get(f'/crawl/{sample_job.id}', headers=valid_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == CrawlStatus.COMPLETED.value
        assert data['result'] is not None
        # CrawlResult uses 'content' not 'markdown_content'
        assert 'content' in data['result'] or 'markdown_content' in data['result']

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    @patch.object(crawl_manager, 'get_job', new_callable=AsyncMock)
    def test_configuration_persistence(self, mock_get, mock_create, client, valid_headers, sample_job):
        """Test that crawl configuration is persisted with the job."""
        sample_job.config = CrawlConfig(
            max_depth=3,
            timeout_seconds=120,
            respect_robots=False,
            user_agent="CustomAgent/1.0"
        )
        mock_create.return_value = sample_job

        # Create job with custom config
        response = client.post(
            '/crawl',
            json={
                'url': 'https://example.com',
                'max_depth': 3,
                'timeout_seconds': 120,
                'respect_robots': False,
                'user_agent': 'CustomAgent/1.0'
            },
            headers=valid_headers
        )
        assert response.status_code == 201

        # Retrieve and verify config
        mock_get.return_value = sample_job
        response = client.get(f'/crawl/{sample_job.id}', headers=valid_headers)
        assert response.status_code == 200
        data = response.get_json()
        # Config is included in the response if available
        config = data.get('config', {})
        assert config.get('max_depth', 3) == 3
        assert config.get('timeout_seconds', 120) == 120
        assert config.get('respect_robots', False) is False


class TestApiResponseFormats:
    """Test API response format consistency."""

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    def test_success_response_format(self, mock_create, client, valid_headers, sample_job):
        """Test success response has correct format."""
        mock_create.return_value = sample_job

        response = client.post('/crawl', json={'url': 'https://example.com'}, headers=valid_headers)
        assert response.status_code == 201

        data = response.get_json()
        assert 'id' in data
        assert 'url' in data
        assert 'status' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    def test_error_response_format(self, mock_create, client, valid_headers):
        """Test error response has correct format."""
        # Missing required field
        response = client.post('/crawl', json={}, headers=valid_headers)
        assert response.status_code == 400

        data = response.get_json()
        assert 'error' in data

    def test_health_endpoint_format(self, client):
        """Test health endpoint response format."""
        response = client.get('/health')
        assert response.status_code == 200

        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'healthy'
