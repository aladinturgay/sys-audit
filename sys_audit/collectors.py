import platform
import socket
from datetime import datetime, timezone


def _bytes_to_gb(value: int) -> float:
    return round(value / (1024 ** 3), 2)


def collect_os_info() -> dict:
    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor() or "unknown",
    }


def collect_memory_info() -> dict:
    try:
        import psutil
    except ImportError:
        return {"note": "Install psutil for memory details: pip install psutil"}

    memory = psutil.virtual_memory()
    return {
        "total_gb": _bytes_to_gb(memory.total),
        "available_gb": _bytes_to_gb(memory.available),
        "used_percent": memory.percent,
    }


def collect_disk_info() -> list[dict]:
    try:
        import psutil
    except ImportError:
        return [{"note": "Install psutil for disk details: pip install psutil"}]

    disks: list[dict] = []
    for part in psutil.disk_partitions(all=False):
        if part.fstype:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append(
                {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": _bytes_to_gb(usage.total),
                    "used_gb": _bytes_to_gb(usage.used),
                    "free_gb": _bytes_to_gb(usage.free),
                    "used_percent": usage.percent,
                }
            )
    return disks


def collect_network_info() -> list[dict]:
    try:
        import psutil
    except ImportError:
        return [{"note": "Install psutil for network details: pip install psutil"}]

    adapters: list[dict] = []
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for name, entries in addrs.items():
        adapter = {
            "name": name,
            "is_up": stats.get(name).isup if name in stats else None,
            "addresses": [],
        }
        for entry in entries:
            if entry.family.name in {"AF_INET", "AF_INET6"}:
                adapter["addresses"].append(
                    {"family": entry.family.name, "address": entry.address}
                )
        if adapter["addresses"]:
            adapters.append(adapter)

    return adapters


def build_report() -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "os": collect_os_info(),
        "memory": collect_memory_info(),
        "disks": collect_disk_info(),
        "network": collect_network_info(),
    }
