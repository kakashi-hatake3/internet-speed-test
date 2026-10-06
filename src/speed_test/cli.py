import argparse
import sys

from src.speed_test.calculator import SpeedCalculator
from src.speed_test.downloader import HttpDownloader
from src.speed_test.reporter import ConsoleReporter
from src.speed_test.service import SpeedTester

DEFAULT_TEST_URL = "https://speed.cloudflare.com/__down?bytes=10000000"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="speed-test",
        description=(
            "Замер скорости интернет-соединения путем последовательных "
            "запросов к целевому URL."
        ),
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=DEFAULT_TEST_URL,
        help=(
            f"URL адрес ресурса (по умолчанию Cloudflare 10MB: {DEFAULT_TEST_URL})."
        ),
    )
    parser.add_argument(
        "-u",
        "--url",
        dest="url_opt",
        help="Альтернативный флаг задания URL.",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=10,
        help="Количество последовательных запросов (по умолчанию: 10).",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=30.0,
        help="Таймаут одного запроса в секундах (по умолчанию: 30.0).",
    )
    return parser


def main(args=None) -> int:
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    target_url = parsed_args.url_opt or parsed_args.url
    if not target_url:
        parser.error("Не указан URL адрес для замера скорости.")

    if not (target_url.startswith("http://") or target_url.startswith("https://")):
        parser.error(f"URL должен начинаться с http:// или https://. Получено: '{target_url}'")

    if parsed_args.count <= 0:
        parser.error("Количество запросов должно быть больше 0.")

    downloader = HttpDownloader()
    calculator = SpeedCalculator()
    reporter = ConsoleReporter(stream=sys.stdout)

    tester = SpeedTester(
        downloader=downloader,
        calculator=calculator,
        reporter=reporter,
    )

    try:
        report = tester.run(
            url=target_url,
            iterations=parsed_args.count,
            timeout=parsed_args.timeout,
        )
        if report.metrics and report.metrics.successful_iterations > 0:
            return 0
        return 1
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\nКритическая ошибка: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
