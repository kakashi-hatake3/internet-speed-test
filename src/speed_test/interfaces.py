from abc import ABC, abstractmethod
from typing import Callable

from src.speed_test.models import DownloadResult, TestReport


class DownloaderInterface(ABC):
    """
    Interface for downloading resources from a target URL.
    Adheres to Interface Segregation Principle (ISP) and Dependency Inversion Principle (DIP).
    """

    @abstractmethod
    def download(self, url: str, iteration: int = 1, timeout: float = 30.0) -> DownloadResult:
        """
        Download resource and return measurement metrics.
        """
        pass


class SpeedCalculatorInterface(ABC):
    """
    Interface for computing performance metrics from download results.
    """

    @abstractmethod
    def calculate(self, report: TestReport) -> TestReport:
        """
        Calculates aggregated metrics and returns the populated TestReport.
        """
        pass


class ReporterInterface(ABC):
    """
    Interface for reporting progress and final metrics.
    """

    @abstractmethod
    def report_start(self, url: str, iterations: int) -> None:
        """Called before the test starts."""
        pass

    @abstractmethod
    def report_iteration(self, result: DownloadResult) -> None:
        """Called after each iteration finishes."""
        pass

    @abstractmethod
    def report_summary(self, report: TestReport) -> None:
        """Called when the entire test is complete."""
        pass


IterationCallback = Callable[[DownloadResult], None]
