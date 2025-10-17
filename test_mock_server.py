import requests
import time

from mock_server import MockServer


def test_mock_server_root():
    srv = MockServer(port=8001)
    srv.start()
    try:
        resp = requests.get('http://127.0.0.1:8001/')
        assert resp.status_code == 200
        assert 'Mock' in resp.text
    finally:
        srv.stop()


def test_mock_server_robots():
    srv = MockServer(port=8002)
    srv.start()
    try:
        resp = requests.get('http://127.0.0.1:8002/robots.txt')
        assert resp.status_code == 200
        assert 'User-agent' in resp.text
    finally:
        srv.stop()
