import pytest

from src.speed_test.calculator import SpeedCalculator
from src.speed_test.models import DownloadResult, TestReport


@pytest.fixture
def calculator():
    return SpeedCalculator()


def test_calculate_with_empty_results(calculator):
    report = TestReport(target_url="http://example.com/test.jpg", results=[])
    res = calculator.calculate(report)

    assert res.metrics is not None
    m = res.metrics
    assert m.total_iterations == 0
    assert m.successful_iterations == 0
    assert m.failed_iterations == 0
    assert m.total_bytes == 0
    assert m.avg_speed_mbyte_per_sec == 0.0
    assert m.avg_speed_mbit_per_sec == 0.0


def test_calculate_with_all_failed_results(calculator):
    report = TestReport(
        target_url="http://example.com/test.jpg",
        results=[
            DownloadResult(
                iteration=1,
                bytes_downloaded=0,
                duration_seconds=1.0,
                status_code=404,
                error="Not Found",
            ),
            DownloadResult(
                iteration=2,
                bytes_downloaded=0,
                duration_seconds=2.0,
                status_code=500,
                error="Server Error",
            ),
        ],
    )
    res = calculator.calculate(report)

    assert res.metrics is not None
    m = res.metrics
    assert m.total_iterations == 2
    assert m.successful_iterations == 0
    assert m.failed_iterations == 2
    assert m.total_bytes == 0
    assert m.avg_speed_mbyte_per_sec == 0.0


def test_calculate_with_successful_results(calculator):
    one_mb = 1024 * 1024
    report = TestReport(
        target_url="http://example.com/test.jpg",
        results=[
            DownloadResult(
                iteration=1,
                bytes_downloaded=one_mb,
                duration_seconds=1.0,
                status_code=200,
            ),
            DownloadResult(
                iteration=2,
                bytes_downloaded=one_mb * 2,
                duration_seconds=1.0,
                status_code=200,
            ),
            DownloadResult(
                iteration=3,
                bytes_downloaded=0,
                duration_seconds=0.5,
                status_code=500,
                error="Error",
            ),
        ],
    )
    res = calculator.calculate(report)

    assert res.metrics is not None
    m = res.metrics
    assert m.total_iterations == 3
    assert m.successful_iterations == 2
    assert m.failed_iterations == 1
    assert m.total_bytes == one_mb * 3
    assert pytest.approx(m.total_duration_seconds, rel=1e-4) == 2.0
    assert pytest.approx(m.avg_duration_seconds, rel=1e-4) == 1.0
    assert pytest.approx(m.min_duration_seconds, rel=1e-4) == 1.0
    assert pytest.approx(m.max_duration_seconds, rel=1e-4) == 1.0
    assert pytest.approx(m.avg_speed_mbyte_per_sec, rel=1e-4) == 1.5

    expected_mbits = (one_mb * 3 * 8) / (2.0 * 1_000_000)
    assert pytest.approx(m.avg_speed_mbit_per_sec, rel=1e-4) == expected_mbits
