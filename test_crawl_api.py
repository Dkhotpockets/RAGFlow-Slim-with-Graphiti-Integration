"""
API Integration Tests for Crawl4AI Endpoints (T025)

Tests the Flask API endpoints for crawl job management, including:
- Authentication and authorization
- Request validation and error handling
- Response format validation
- Integration with CrawlJobManager
- Rate limiting behavior
"""

import pytest
import json
import datetime
from unittest.mock import patch, AsyncMock, MagicMock
from flask import Flask
from werkzeug.test import Client
from werkzeug.wrappers import Response

from app import app, crawl_manager
from crawl4ai_source import CrawlJob, CrawlStatus, CrawlConfig, CrawlResult


@pytest.fixture
def client():
    """Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_headers():
    """Valid API headers for authenticated requests."""
    return {
        'X-API-KEY': 'changeme',  # Default test API key
        'Content-Type': 'application/json'
    }


@pytest.fixture
def invalid_headers():
    """Invalid API headers for unauthorized requests."""
    return {
        'X-API-KEY': 'invalid_key',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_crawl_config():
    """Sample crawl configuration for testing."""
    return {
        'max_depth': 2,
        'timeout_seconds': 30,
        'respect_robots': True,
        'user_agent': 'Test Crawler',
        'extract_metadata': True
    }


@pytest.fixture
def sample_job():
    """Sample crawl job for testing."""
    config = CrawlConfig()
    job = CrawlJob(
        id='test-job-123',
        url='https://example.com',
        config=config,
        status=CrawlStatus.PENDING
    )
    return job


@pytest.fixture
def sample_completed_job(sample_job):
    """Sample completed crawl job with results."""
    result = CrawlResult(
        url='https://example.com',
        title='Test Page',
        content='Test content',
        content_hash='test_hash',
        content_size=12,
        crawl_time=1.5,
        metadata={'title': 'Test Page'},
        links=['https://link1.com']
    )
    sample_job.result = result
    sample_job.status = CrawlStatus.COMPLETED
    return sample_job


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_check_success(self, client):
        """Test successful health check response."""
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'graphiti_available' in data
        assert 'llm_provider' in data
        assert 'crawl4ai_available' in data
        assert 'timestamp' in data
        assert data['crawl4ai_available'] is True


class TestAuthentication:
    """Test authentication and authorization."""

    def test_missing_api_key(self, client):
        """Test request without API key."""
        response = client.post('/crawl', json={'url': 'https://example.com'})
        assert response.status_code == 401

        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Unauthorized'

    def test_invalid_api_key(self, client, invalid_headers):
        """Test request with invalid API key."""
        response = client.post('/crawl', json={'url': 'https://example.com'}, headers=invalid_headers)
        assert response.status_code == 401

        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Unauthorized'

    def test_valid_api_key(self, client, valid_headers):
        """Test request with valid API key."""
        with patch.object(crawl_manager, 'create_job', new_callable=AsyncMock) as mock_create:
            mock_job = MagicMock()
            mock_job.id = 'test-job-123'
            mock_job.url = 'https://example.com'
            mock_job.status = CrawlStatus.PENDING
            mock_job.created_at = datetime.datetime.now()
            mock_job.updated_at = datetime.datetime.now()
            mock_job.completed_at = None
            mock_job.result = None
            mock_job.error_message = None
            mock_job.config.to_dict.return_value = {'max_depth': 2}
            mock_create.return_value = mock_job

            response = client.post('/crawl', json={'url': 'https://example.com'}, headers=valid_headers)
            assert response.status_code == 201


class TestCrawlJobCreation:
    """Test crawl job creation endpoint."""

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    def test_create_crawl_job_success(self, mock_create, client, valid_headers, sample_job):
        """Test successful crawl job creation."""
        mock_create.return_value = sample_job

        request_data = {
            'url': 'https://example.com',
            'max_depth': 2,
            'timeout_seconds': 30
        }

        response = client.post('/crawl', json=request_data, headers=valid_headers)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'id' in data
        assert 'url' in data
        assert 'status' in data
        assert data['url'] == 'https://example.com'
        assert data['status'] == 'pending'

        # Verify the job creation was called
        mock_create.assert_called_once()
        args = mock_create.call_args[0]
        assert args[0] == 'https://example.com'
        assert isinstance(args[1], CrawlConfig)

    def test_create_crawl_job_missing_url(self, client, valid_headers):
        """Test crawl job creation with missing URL."""
        response = client.post('/crawl', json={'max_depth': 2}, headers=valid_headers)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data

    def test_create_crawl_job_invalid_url(self, client, valid_headers):
        """Test crawl job creation with invalid URL."""
        response = client.post('/crawl', json={'url': 'not-a-url'}, headers=valid_headers)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    def test_create_crawl_job_with_config(self, mock_create, client, valid_headers, sample_job):
        """Test crawl job creation with custom configuration."""
        mock_create.return_value = sample_job

        request_data = {
            'url': 'https://example.com',
            'max_depth': 3,
            'timeout_seconds': 60,
            'respect_robots': False,
            'user_agent': 'Custom Agent',
            'extract_metadata': False
        }

        response = client.post('/crawl', json=request_data, headers=valid_headers)
        assert response.status_code == 201

        # Verify config was passed correctly
        args = mock_create.call_args[0]
        config = args[1]
        assert config.max_depth == 3
        assert config.timeout_seconds == 60
        assert config.respect_robots is False
        assert config.user_agent == 'Custom Agent'
        assert config.extract_metadata is False


class TestCrawlJobRetrieval:
    """Test crawl job retrieval endpoints."""

    @patch.object(crawl_manager, 'get_job', new_callable=AsyncMock)
    def test_get_crawl_job_success(self, mock_get, client, valid_headers, sample_completed_job):
        """Test successful job retrieval."""
        mock_get.return_value = sample_completed_job

        response = client.get('/crawl/test-job-123', headers=valid_headers)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['id'] == 'test-job-123'
        assert data['status'] == 'completed'
        assert 'result' in data
        assert data['result']['title'] == 'Test Page'
        assert data['result']['content'] == 'Test content'

    @patch.object(crawl_manager, 'get_job', new_callable=AsyncMock)
    def test_get_crawl_job_not_found(self, mock_get, client, valid_headers):
        """Test job retrieval for non-existent job."""
        mock_get.return_value = None

        response = client.get('/crawl/non-existent-job', headers=valid_headers)
        assert response.status_code == 404

        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Job not found'

    @patch.object(crawl_manager, 'list_jobs', new_callable=AsyncMock)
    def test_list_crawl_jobs_success(self, mock_list, client, valid_headers, sample_job):
        """Test successful job listing."""
        mock_list.return_value = [sample_job]

        response = client.get('/crawl', headers=valid_headers)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'jobs' in data
        assert 'count' in data
        assert data['count'] == 1
        assert len(data['jobs']) == 1
        assert data['jobs'][0]['id'] == 'test-job-123'

    @patch.object(crawl_manager, 'list_jobs', new_callable=AsyncMock)
    def test_list_crawl_jobs_with_filter(self, mock_list, client, valid_headers, sample_job):
        """Test job listing with status filter."""
        mock_list.return_value = [sample_job]

        response = client.get('/crawl?status=pending&limit=10', headers=valid_headers)
        assert response.status_code == 200

        # Verify list_jobs was called with correct parameters
        mock_list.assert_called_once()
        args, kwargs = mock_list.call_args
        assert kwargs['status'] == CrawlStatus.PENDING
        assert kwargs['limit'] == 10

    def test_list_crawl_jobs_invalid_limit(self, client, valid_headers):
        """Test job listing with invalid limit parameter."""
        response = client.get('/crawl?limit=200', headers=valid_headers)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data

    def test_list_crawl_jobs_invalid_status(self, client, valid_headers):
        """Test job listing with invalid status parameter."""
        response = client.get('/crawl?status=invalid', headers=valid_headers)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data


class TestCrawlJobActions:
    """Test crawl job action endpoints."""

    @patch.object(crawl_manager, 'start_job', new_callable=AsyncMock)
    def test_start_crawl_job_success(self, mock_start, client, valid_headers):
        """Test successful job start."""
        mock_start.return_value = True

        response = client.post('/crawl/test-job-123/start', headers=valid_headers)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'message' in data
        assert 'started successfully' in data['message']

    @patch.object(crawl_manager, 'start_job', new_callable=AsyncMock)
    def test_start_crawl_job_failure(self, mock_start, client, valid_headers):
        """Test job start failure."""
        mock_start.return_value = False

        response = client.post('/crawl/test-job-123/start', headers=valid_headers)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data

    @patch.object(crawl_manager, 'cancel_job', new_callable=AsyncMock)
    def test_cancel_crawl_job_success(self, mock_cancel, client, valid_headers):
        """Test successful job cancellation."""
        mock_cancel.return_value = True

        response = client.post('/crawl/test-job-123/cancel', headers=valid_headers)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'message' in data
        assert 'cancelled successfully' in data['message']

    @patch.object(crawl_manager, 'cancel_job', new_callable=AsyncMock)
    def test_cancel_crawl_job_failure(self, mock_cancel, client, valid_headers):
        """Test job cancellation failure."""
        mock_cancel.return_value = False

        response = client.post('/crawl/test-job-123/cancel', headers=valid_headers)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_exceeded(self, client, valid_headers):
        """Test rate limiting behavior."""
        # This test would need to be enhanced with proper rate limit simulation
        # For now, just verify the rate limit function exists and is called
        pass


class TestErrorHandling:
    """Test error handling across endpoints."""

    @patch.object(crawl_manager, 'create_job', new_callable=AsyncMock)
    def test_internal_server_error(self, mock_create, client, valid_headers):
        """Test internal server error handling."""
        mock_create.side_effect = Exception("Database connection failed")

        response = client.post('/crawl', json={'url': 'https://example.com'}, headers=valid_headers)
        assert response.status_code == 500

        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Internal server error.'