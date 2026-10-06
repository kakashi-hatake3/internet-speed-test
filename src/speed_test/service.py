from typing import Optional

from src.speed_test.interfaces import (
    DownloaderInterface,
    ReporterInterface,
    SpeedCalculatorInterface,
)
from src.speed_test.models import TestReport


class SpeedTester:
    """
    Coordinates execution of download measurements and delegates calculation & reporting.
    Adheres to Open-Closed Principle (OCP) and Dependency Inversion Principle (DIP).
    """

    def __init__(
        self,
        downloader: DownloaderInterface,
        calculator: SpeedCalculatorInterface,
        reporter: Optional[ReporterInterface] = None,
    ):
        self._downloader = downloader
        self._calculator = calculator
        self._reporter = reporter

    def run(self, url: str, iterations: int = 10, timeout: float = 30.0) -> TestReport:
        if iterations <= 0:
            raise ValueError("Iterations count must be greater than zero.")

        report = TestReport(target_url=url)

        if self._reporter:
            self._reporter.report_start(url, iterations)

        for i in range(1, iterations + 1):
            result = self._downloader.download(url=url, iteration=i, timeout=timeout)
            report.results.append(result)

            if self._reporter:
                self._reporter.report_iteration(result)

        self._calculator.calculate(report)

        if self._reporter:
            self._reporter.report_summary(report)

        return report
