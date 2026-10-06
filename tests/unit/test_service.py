from unittest.mock import Mock

import pytest

from src.speed_test.interfaces import (
    DownloaderInterface,
    ReporterInterface,
    SpeedCalculatorInterface,
)
from src.speed_test.models import DownloadResult
from src.speed_test.service import SpeedTester


@pytest.fixture
def mock_downloader():
    return Mock(spec=DownloaderInterface)


@pytest.fixture
def mock_calculator():
    return Mock(spec=SpeedCalculatorInterface)


@pytest.fixture
def mock_reporter():
    return Mock(spec=ReporterInterface)


def test_run_executes_specified_iterations_and_delegates(
    mock_downloader, mock_calculator, mock_reporter
):
    sample_result = DownloadResult(
        iteration=1,
        bytes_downloaded=1024,
        duration_seconds=0.1,
        status_code=200,
    )
    mock_downloader.download.return_value = sample_result

    tester = SpeedTester(
        downloader=mock_downloader,
        calculator=mock_calculator,
        reporter=mock_reporter,
    )

    url = "https://example.com/image.jpg"
    report = tester.run(url=url, iterations=10, timeout=15.0)

    mock_reporter.report_start.assert_called_once_with(url, 10)
    assert mock_downloader.download.call_count == 10
    assert len(report.results) == 10
    assert mock_reporter.report_iteration.call_count == 10
    mock_calculator.calculate.assert_called_once_with(report)
    mock_reporter.report_summary.assert_called_once_with(report)


def test_run_rejects_non_positive_iterations(mock_downloader, mock_calculator):
    tester = SpeedTester(
        downloader=mock_downloader,
        calculator=mock_calculator,
    )
    with pytest.raises(ValueError, match="Iterations count must be greater than zero."):
        tester.run(url="https://example.com/test", iterations=0)
