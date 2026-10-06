from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class DownloadResult:
    iteration: int
    bytes_downloaded: int
    duration_seconds: float
    status_code: int
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.error is None and 200 <= self.status_code < 300

    @property
    def speed_bytes_per_sec(self) -> float:
        if self.duration_seconds <= 0:
            return 0.0
        return self.bytes_downloaded / self.duration_seconds

    @property
    def speed_mb_per_sec(self) -> float:
        # 1 MB = 10^6 bytes (decimal) or 1,000,000 bytes
        return self.speed_bytes_per_sec / (1024 * 1024)


@dataclass(frozen=True)
class AggregatedMetrics:
    total_iterations: int
    successful_iterations: int
    failed_iterations: int
    total_bytes: int
    total_duration_seconds: float
    avg_duration_seconds: float
    min_duration_seconds: float
    max_duration_seconds: float
    avg_speed_bytes_per_sec: float
    avg_speed_mbyte_per_sec: float  # МБ/с (Megabytes per second, 1 MB = 1024 * 1024 bytes)
    avg_speed_mbit_per_sec: float   # Мбит/с (Megabits per second)


@dataclass
class TestReport:
    target_url: str
    results: List[DownloadResult] = field(default_factory=list)
    metrics: Optional[AggregatedMetrics] = None
