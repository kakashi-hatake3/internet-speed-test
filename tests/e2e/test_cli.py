import http.server
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

import pytest


class DummyFileHandler(http.server.BaseHTTPRequestHandler):
    data = b"0" * (512 * 1024)  # 512 KB payload

    def do_GET(self):
        if self.path == "/speed-test-img.jpg":
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(self.data)))
            self.end_headers()
            self.wfile.write(self.data)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


@pytest.fixture(scope="module")
def local_e2e_server():
    server = socketserver.TCPServer(("127.0.0.1", 0), DummyFileHandler)
    port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


@pytest.fixture
def project_root():
    return Path(__file__).resolve().parent.parent.parent


def test_e2e_successful_run(local_e2e_server, project_root):
    main_script = project_root / "main.py"
    url = f"{local_e2e_server}/speed-test-img.jpg"
    result = subprocess.run(
        [sys.executable, str(main_script), url, "--count", "10"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Stderr: {result.stderr}"
    stdout = result.stdout

    assert "ЗАМЕР СКОРОСТИ ИНТЕРНЕТ-СОЕДИНЕНИЯ" in stdout
    assert "ИТОГОВЫЙ ОТЧЕТ" in stdout
    assert "Успешных запросов:         10 из 10" in stdout
    assert "СРЕДНЯЯ СКОРОСТЬ:" in stdout
    assert "МБ/с" in stdout

    for i in range(1, 11):
        assert f"{i:<8} | HTTP 200" in stdout


def test_e2e_invalid_url_scheme(project_root):
    main_script = project_root / "main.py"
    result = subprocess.run(
        [sys.executable, str(main_script), "ftp://example.com/test.jpg"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "URL должен начинаться с http:// или https://" in result.stderr


def test_e2e_target_server_error(local_e2e_server, project_root):
    main_script = project_root / "main.py"
    url = f"{local_e2e_server}/non-existent.jpg"
    result = subprocess.run(
        [sys.executable, str(main_script), url, "--count", "3"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Не удалось получить данные ни по одному запросу" in result.stdout
