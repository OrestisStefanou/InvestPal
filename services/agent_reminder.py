import asyncio
from abc import ABC, abstractmethod

from models.agent_reminder import AgentReminder
from repos.agent_reminders import AgentRemindersTable


class AgentReminderNotFoundError(Exception):
    pass


class AgentReminderService(ABC):
    @abstractmethod
    async def create_agent_reminder(
        self,
        reminder_description: str,
        due_date: str | None = None,
    ) -> AgentReminder:
        pass

    @abstractmethod
    async def get_agent_reminders(
        self,
    ) -> list[AgentReminder]:
        pass

    @abstractmethod
    async def delete_agent_reminder(
        self,
        reminder_id: str,
    ) -> None:
        pass

    @abstractmethod
    async def update_agent_reminder(
        self,
        reminder_id: str,
        reminder_description: str | None = None,
        due_date: str | None = None,
    ) -> AgentReminder:
        pass


class TursoAgentReminderService(AgentReminderService):
    def __init__(self, table: AgentRemindersTable):
        self._table = table

    async def create_agent_reminder(
        self,
        reminder_description: str,
        due_date: str | None = None,
    ) -> AgentReminder:
        row = await asyncio.to_thread(
            self._table.create_reminder,
            description=reminder_description,
            due_date=due_date,
        )
        return AgentReminder(
            id=row.id,
            description=row.description,
            created_at=row.created_at,
            due_date=row.due_date,
        )

    async def get_agent_reminders(
        self,
    ) -> list[AgentReminder]:
        rows = await asyncio.to_thread(self._table.get_reminders)
        return [
            AgentReminder(
                id=row.id,
                description=row.description,
                created_at=row.created_at,
                due_date=row.due_date,
            )
            for row in rows
        ]

    async def delete_agent_reminder(
        self,
        reminder_id: str,
    ) -> None:
        deleted = await asyncio.to_thread(self._table.delete_reminder, reminder_id)
        if not deleted:
            raise AgentReminderNotFoundError(f"Agent reminder not found for reminder_id: {reminder_id}")

    async def update_agent_reminder(
        self,
        reminder_id: str,
        reminder_description: str | None = None,
        due_date: str | None = None,
    ) -> AgentReminder:
        row = await asyncio.to_thread(
            self._table.update_reminder,
            reminder_id=reminder_id,
            description=reminder_description,
            due_date=due_date,
        )
        if not row:
            raise AgentReminderNotFoundError(f"Agent reminder not found for reminder_id: {reminder_id}")

        return AgentReminder(
            id=row.id,
            description=row.description,
            created_at=row.created_at,
            due_date=row.due_date,
        )
