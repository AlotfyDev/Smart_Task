"""
MCP Local Server — stdio transport for local AI clients.

Entry point::

    smart-task-mcp-local [--db-path PATH]
    python -m smart_task.mcp_local [--db-path PATH]

Exposed functions:
    run_local_server(db_path)     — create repo, wm, server, run stdio loop
    create_local_server(repo,wm)  — build configured Server instance
    main()                        — CLI entry (argparse → run_local_server)
"""

from __future__ import annotations

import argparse
import logging
import signal

from smart_task.repository import TicketRepository
from smart_task.wave_manager import WaveManager

logger = logging.getLogger(__name__)

running = True


def _handle_signal(signum, frame):
    global running
    running = False


def run_local_server(db_path: str = "smart_task.db") -> None:
    repo = TicketRepository(db_path)
    wm = WaveManager(repo)
    server = create_local_server(repo, wm)
    server.run(transport="stdio")


def create_local_server(
    repo: TicketRepository, wm: WaveManager
) -> "Server":
    from smart_task.mcp_local.local_server import build_server
    return build_server(repo, wm)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="smart-task MCP local server (stdio)"
    )
    parser.add_argument(
        "--db-path",
        default="smart_task.db",
        help="Path to SQLite database (default: smart_task.db)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    run_local_server(args.db_path)
