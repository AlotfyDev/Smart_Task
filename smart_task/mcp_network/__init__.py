"""
MCP Network Server — SSE transport over HTTP for remote AI clients.

Usage::

    smart-task-mcp-network [--host HOST] [--port PORT] [--db-path PATH]
    python -m smart_task.mcp_network [--host HOST] [--port PORT] [--db-path PATH]
"""

from __future__ import annotations

import argparse
import logging
import signal

from smart_task.mcp_network.network_server import create_sse_app
from smart_task.mcp_network.utils import find_free_port
from smart_task.repository import TicketRepository
from smart_task.wave_manager import WaveManager

logger = logging.getLogger("smart_task.mcp_network")

running = True


def _handle_signal(signum, frame):
    global running
    running = False


def run_network_server(db_path: str = "smart_task.db", host: str = "127.0.0.1", port: int = 8100) -> None:
    repo = TicketRepository(db_path)
    wm = WaveManager(repo)
    app = create_sse_app(repo, wm, host=host, port=port)
    logger.info("MCP Network server starting on %s:%s", host, port)
    app.run(transport="sse")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="smart-task MCP network server (SSE)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind address (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8100,
        help="Bind port; use 0 for OS-assigned ephemeral port (default: 8100)",
    )
    parser.add_argument(
        "--db-path",
        default="smart_task.db",
        help="Path to SQLite database (default: smart_task.db)",
    )

    args = parser.parse_args()

    port = args.port
    if port == 0:
        port = find_free_port()
        logger.info("Assigned ephemeral port: %d", port)

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    run_network_server(db_path=args.db_path, host=args.host, port=port)
