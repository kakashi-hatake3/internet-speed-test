import sys
from typing import TextIO

from src.speed_test.interfaces import ReporterInterface
from src.speed_test.models import DownloadResult, TestReport


class ConsoleReporter(ReporterInterface):
    """
    Formats and prints speed test progress and summary to the console.
    Single Responsibility: Visualization / formatting of results.
    """

    def __init__(self, stream: TextIO = sys.stdout):
        self._stream = stream

    def report_start(self, url: str, iterations: int) -> None:
        self._stream.write("\n" + "=" * 65 + "\n")
        self._stream.write("             ЗАМЕР СКОРОСТИ ИНТЕРНЕТ-СОЕДИНЕНИЯ\n")
        self._stream.write("=" * 65 + "\n")
        self._stream.write(f" Целевой URL:     {url}\n")
        self._stream.write(f" Число запросов:  {iterations}\n")
        self._stream.write("-" * 65 + "\n")
        header = (
            f"{'Запрос':<8} | {'Статус':<8} | {'Объем':<12} | "
            f"{'Время':<10} | {'Скорость':<12}\n"
        )
        self._stream.write(header)
        self._stream.write("-" * 65 + "\n")
        self._stream.flush()

    def report_iteration(self, result: DownloadResult) -> None:
        if result.is_success:
            status_text = f"HTTP {result.status_code}"
            size_mb = result.bytes_downloaded / (1024 * 1024)
            size_text = f"{size_mb:.2f} МБ"
            duration_text = f"{result.duration_seconds:.3f} с"
            speed_text = f"{result.speed_mb_per_sec:.2f} МБ/с"
        else:
            status_text = "ОШИБКА"
            size_text = f"{result.bytes_downloaded} Б"
            duration_text = f"{result.duration_seconds:.3f} с"
            err_msg = result.error or "Неизвестная ошибка"
            speed_text = err_msg[:12]

        line = (
            f"{result.iteration:<8} | {status_text:<8} | {size_text:<12} | "
            f"{duration_text:<10} | {speed_text:<12}\n"
        )
        self._stream.write(line)
        self._stream.flush()

    def report_summary(self, report: TestReport) -> None:
        self._stream.write("=" * 65 + "\n")
        self._stream.write("                     ИТОГОВЫЙ ОТЧЕТ\n")
        self._stream.write("=" * 65 + "\n")

        m = report.metrics
        if not m or m.successful_iterations == 0:
            self._stream.write(" Не удалось получить данные ни по одному запросу.\n")
            self._stream.write("=" * 65 + "\n\n")
            self._stream.flush()
            return

        total_mb = m.total_bytes / (1024 * 1024)
        avg_mb_per_req = total_mb / m.successful_iterations

        self._stream.write(
            f" Успешных запросов:         {m.successful_iterations} из {m.total_iterations}\n"
        )
        if m.failed_iterations > 0:
            self._stream.write(f" Неудачных запросов:        {m.failed_iterations}\n")
        self._stream.write(
            f" Общий объем скачанного:    {total_mb:.2f} МБ ({m.total_bytes:,} байт)\n"
        )
        self._stream.write(f" Средний объем на запрос:   {avg_mb_per_req:.2f} МБ\n")
        self._stream.write(f" Суммарное время передачи:  {m.total_duration_seconds:.3f} с\n")
        self._stream.write(
            f" Среднее время запроса:     {m.avg_duration_seconds:.3f} с "
            f"(мин: {m.min_duration_seconds:.3f} с, макс: {m.max_duration_seconds:.3f} с)\n"
        )
        self._stream.write("-" * 65 + "\n")
        self._stream.write(
            f" СРЕДНЯЯ СКОРОСТЬ:          {m.avg_speed_mbyte_per_sec:.2f} МБ/с "
            f"({m.avg_speed_mbit_per_sec:.2f} Мбит/с)\n"
        )
        self._stream.write("=" * 65 + "\n\n")
        self._stream.flush()
