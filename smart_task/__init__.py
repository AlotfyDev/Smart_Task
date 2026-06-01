"""
Smart Task — Micro-task ticket system for specification-driven implementation orchestration.

Public API
----------
- MicroTaskTicket, TaskWave, TopicToTicketMapping   : domain models
- SmartTaskConfig, load_config                      : configuration
- ensure_schema                                     : database schema initialisation
- TicketRepository                                  : SQLite-backed persistence
- WaveManager                                       : high-level wave orchestration
"""

from __future__ import annotations

from smart_task.config import SmartTaskConfig, load_config
from smart_task.models import MicroTaskTicket, TaskWave, TopicToTicketMapping
from smart_task.repository import TicketRepository
from smart_task.schema import ensure_schema
from smart_task.wave_manager import WaveManager

__all__ = [
    "MicroTaskTicket",
    "TaskWave",
    "TopicToTicketMapping",
    "SmartTaskConfig",
    "load_config",
    "ensure_schema",
    "TicketRepository",
    "WaveManager",
]
