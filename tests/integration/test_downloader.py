import http.server
import socketserver
import threading

import pytest

from src.speed_test.downloader import HttpDownloader


class ChunkedDataHandler(http.server.BaseHTTPRequestHandler):
    payload = b"A" * (256 * 1024)  # 256 KB test payload

    def do_GET(self):
        if self.path == "/test-payload":
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(self.payload)))
            self.end_headers()
            self.wfile.write(self.payload)
        elif self.path == "/error-500":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Server Error")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        pass


@pytest.fixture(scope="module")
def local_http_server():
    server = socketserver.TCPServer(("127.0.0.1", 0), ChunkedDataHandler)
    port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


@pytest.fixture
def downloader():
    return HttpDownloader()


def test_successful_download(local_http_server, downloader):
    url = f"{local_http_server}/test-payload"
    res = downloader.download(url=url, iteration=1, timeout=5.0)

    assert res.is_success
    assert res.status_code == 200
    assert res.bytes_downloaded == 256 * 1024
    assert res.duration_seconds > 0
    assert res.speed_bytes_per_sec > 0
    assert res.error is None


def test_http_404_handling(local_http_server, downloader):
    url = f"{local_http_server}/non-existent"
    res = downloader.download(url=url, iteration=1, timeout=5.0)

    assert not res.is_success
    assert res.status_code == 404
    assert "404" in (res.error or "")


def test_http_500_handling(local_http_server, downloader):
    url = f"{local_http_server}/error-500"
    res = downloader.download(url=url, iteration=1, timeout=5.0)

    assert not res.is_success
    assert res.status_code == 500
    assert "500" in (res.error or "")


def test_connection_refused(downloader):
    url = "http://127.0.0.1:1"
    res = downloader.download(url=url, iteration=1, timeout=2.0)

    assert not res.is_success
    assert res.error is not None
