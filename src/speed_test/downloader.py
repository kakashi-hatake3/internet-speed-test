import time
import urllib.error
import urllib.request

from src.speed_test.interfaces import DownloaderInterface
from src.speed_test.models import DownloadResult


class HttpDownloader(DownloaderInterface):
    """
    Downloads resources over HTTP/HTTPS and measures transfer performance.
    Disables client caching via headers and streams the body in chunks.
    """

    CHUNK_SIZE = 64 * 1024  # 64 KB chunks

    def __init__(self, user_agent: str = "SpeedTestClient/1.0"):
        self._user_agent = user_agent

    def download(self, url: str, iteration: int = 1, timeout: float = 30.0) -> DownloadResult:
        req = urllib.request.Request(
            url=url,
            headers={
                "User-Agent": self._user_agent,
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

        bytes_count = 0
        status_code = 0
        start_time = time.perf_counter()

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status_code = getattr(response, "status", 200)
                while True:
                    chunk = response.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    bytes_count += len(chunk)

            elapsed = max(time.perf_counter() - start_time, 1e-9)
            return DownloadResult(
                iteration=iteration,
                bytes_downloaded=bytes_count,
                duration_seconds=elapsed,
                status_code=status_code,
                error=None,
            )

        except urllib.error.HTTPError as err:
            elapsed = max(time.perf_counter() - start_time, 1e-9)
            return DownloadResult(
                iteration=iteration,
                bytes_downloaded=bytes_count,
                duration_seconds=elapsed,
                status_code=err.code,
                error=f"HTTP Error {err.code}: {err.reason}",
            )
        except urllib.error.URLError as err:
            elapsed = max(time.perf_counter() - start_time, 1e-9)
            return DownloadResult(
                iteration=iteration,
                bytes_downloaded=bytes_count,
                duration_seconds=elapsed,
                status_code=0,
                error=f"Network Error: {err.reason}",
            )
        except Exception as err:
            elapsed = max(time.perf_counter() - start_time, 1e-9)
            return DownloadResult(
                iteration=iteration,
                bytes_downloaded=bytes_count,
                duration_seconds=elapsed,
                status_code=0,
                error=f"Error: {str(err)}",
            )
