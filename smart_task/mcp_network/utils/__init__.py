"""Utility functions for the smart_task package."""

import socket


def find_free_port() -> int:
    """Find a free port on localhost for server binding.

    Returns:
        An available ephemeral port number.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        return s.getsockname()[1]