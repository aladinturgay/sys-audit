import argparse
import json
import sys
from pathlib import Path

from sys_audit import __version__
from sys_audit.collectors import build_report


def format_text_report(report: dict) -> str:
    lines = [
        "SysAudit Report",
        "===============",
        f"Generated: {report['generated_at']}",
        "",
        "System",
        f"  Hostname: {report['os']['hostname']}",
        f"  OS: {report['os']['platform']} {report['os']['release']}",
        f"  Architecture: {report['os']['architecture']}",
        "",
        "Memory",
    ]

    memory = report["memory"]
    if "total_gb" in memory:
        lines.extend(
            [
                f"  Total: {memory['total_gb']} GB",
                f"  Available: {memory['available_gb']} GB",
                f"  Used: {memory['used_percent']}%",
            ]
        )
    else:
        lines.append(f"  {memory.get('note', 'Unavailable')}")

    lines.append("")
    lines.append("Disks")
    for disk in report["disks"]:
        if "device" in disk:
            lines.append(
                f"  {disk['device']} ({disk['mountpoint']}) "
                f"- {disk['used_gb']}/{disk['total_gb']} GB ({disk['used_percent']}%)"
            )
        else:
            lines.append(f"  {disk.get('note', 'Unavailable')}")

    lines.append("")
    lines.append("Network")
    for adapter in report["network"]:
        if "name" in adapter:
            status = "up" if adapter.get("is_up") else "down"
            lines.append(f"  {adapter['name']} [{status}]")
            for addr in adapter["addresses"]:
                lines.append(f"    {addr['family']}: {addr['address']}")
        else:
            lines.append(f"  {adapter.get('note', 'Unavailable')}")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sys-audit",
        description="Collect local system information for IT support and inventory.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write JSON report to file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON report to stdout",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"sys-audit {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    report = build_report()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    elif not args.output:
        print(format_text_report(report))

    return 0


if __name__ == "__main__":
    sys.exit(main())
