"""
Domain model dataclasses with JSON serialisation and validation support.

Exports
-------
- MicroTaskTicket          : individual micro-task ticket
- TaskWave                 : logical grouping of tickets
- TopicToTicketMapping     : relationship between a topic file and a ticket
"""

from smart_task.models.ticket import MicroTaskTicket
from smart_task.models.wave import TaskWave
from smart_task.models.mapping import TopicToTicketMapping

__all__ = ["MicroTaskTicket", "TaskWave", "TopicToTicketMapping"]
