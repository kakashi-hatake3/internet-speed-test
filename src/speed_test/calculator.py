from src.speed_test.interfaces import SpeedCalculatorInterface
from src.speed_test.models import AggregatedMetrics, TestReport


class SpeedCalculator(SpeedCalculatorInterface):
    """
    Calculates statistical and performance metrics from raw download results.
    Strictly follows Single Responsibility Principle (SRP).
    """

    BYTES_IN_MIB = 1024 * 1024
    BITS_IN_BYTE = 8

    def calculate(self, report: TestReport) -> TestReport:
        successful_results = [r for r in report.results if r.is_success]

        total_iterations = len(report.results)
        successful_iterations = len(successful_results)
        failed_iterations = total_iterations - successful_iterations

        if not successful_results:
            report.metrics = AggregatedMetrics(
                total_iterations=total_iterations,
                successful_iterations=0,
                failed_iterations=failed_iterations,
                total_bytes=0,
                total_duration_seconds=0.0,
                avg_duration_seconds=0.0,
                min_duration_seconds=0.0,
                max_duration_seconds=0.0,
                avg_speed_bytes_per_sec=0.0,
                avg_speed_mbyte_per_sec=0.0,
                avg_speed_mbit_per_sec=0.0,
            )
            return report

        total_bytes = sum(r.bytes_downloaded for r in successful_results)
        durations = [r.duration_seconds for r in successful_results]
        total_duration = sum(durations)
        avg_duration = total_duration / successful_iterations
        min_duration = min(durations)
        max_duration = max(durations)

        # Average transfer rate: total bytes downloaded divided by total active transfer time
        avg_speed_bytes_per_sec = total_bytes / total_duration if total_duration > 0 else 0.0
        avg_speed_mbyte_per_sec = avg_speed_bytes_per_sec / self.BYTES_IN_MIB
        avg_speed_mbit_per_sec = (avg_speed_bytes_per_sec * self.BITS_IN_BYTE) / (1_000_000)

        report.metrics = AggregatedMetrics(
            total_iterations=total_iterations,
            successful_iterations=successful_iterations,
            failed_iterations=failed_iterations,
            total_bytes=total_bytes,
            total_duration_seconds=total_duration,
            avg_duration_seconds=avg_duration,
            min_duration_seconds=min_duration,
            max_duration_seconds=max_duration,
            avg_speed_bytes_per_sec=avg_speed_bytes_per_sec,
            avg_speed_mbyte_per_sec=avg_speed_mbyte_per_sec,
            avg_speed_mbit_per_sec=avg_speed_mbit_per_sec,
        )
        return report
