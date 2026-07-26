import datetime as dt
import logging
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import (
    CurrentContext,
    Depends,
)
from fastmcp.server.context import Context
from fastmcp.server.lifespan import lifespan
from fastmcp.server.middleware import (
    Middleware,
    MiddlewareContext,
)

from config import settings
from models.agent_reminder import AgentReminder
from models.agent_workflow import (
    AgentWorkflow,
    WorkflowResult,
    WorkflowStatus,
)
from models.user_context import (
    UserConversationNote,
    UserProfileNote,
)
from services.agent_reminder import (
    AgentReminderService,
    TursoAgentReminderService,
)
from repos.agent_reminders import AgentRemindersTable
from services.agent_workflows.results import (
    TursoWorkflowResultService,
    WorkflowResultService,
)
from services.agent_workflows.workflow import (
    AgentWorkflowService,
    TursoAgentWorkflowService,
)
from repos.agent_workflows import AgentWorkflowsTable
from services.agents.prompts import INVESTMENT_ADVISOR_PROMPT
from services.agents.skills import (
    SkillName,
    skill_descriptions,
    skills,
)
from services.agents.tools import SkillDefinition
from services.user_context import (
    UserConversationNotesService,
    UserProfileService,
)
from repos.user_conversation_notes import UserConversationNotesTable
from repos.user_profile_notes import UserProfileNotesTable
from repos.db import init_db


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        tool_name = context.message.name
        args = context.message.arguments
        logger.info("Calling tool %s with arguments %s", tool_name, args)
        result = await call_next(context)
        logger.info(
            "Tool call %s with arguments %s returned result %s", tool_name, args, result
        )
        return result


@lifespan
async def db_lifespan(server):
    # Initialize Turso/SQLite database schema
    init_db(settings.TURSO_DB_PATH)
    yield {}


def get_user_profile_notes_table(ctx: Context = CurrentContext()) -> UserProfileNotesTable:
    return UserProfileNotesTable(db_path=settings.TURSO_DB_PATH)


def get_user_profile_service(
    table: UserProfileNotesTable = Depends(get_user_profile_notes_table),
) -> UserProfileService:
    return UserProfileService(table=table)


def get_user_conversation_notes_table() -> UserConversationNotesTable:
    return UserConversationNotesTable(db_path=settings.TURSO_DB_PATH)


def get_user_conversation_notes_service(
    table: UserConversationNotesTable = Depends(get_user_conversation_notes_table),
) -> UserConversationNotesService:
    return UserConversationNotesService(table=table)



def get_agent_reminder_service() -> AgentReminderService:
    table = AgentRemindersTable(db_path=settings.TURSO_DB_PATH)
    return TursoAgentReminderService(table=table)


def get_agent_workflows_table() -> AgentWorkflowsTable:
    return AgentWorkflowsTable(db_path=settings.TURSO_DB_PATH)


def get_agent_workflow_service(
    table: AgentWorkflowsTable = Depends(get_agent_workflows_table),
) -> AgentWorkflowService:
    return TursoAgentWorkflowService(table=table)


def get_workflow_result_service(
    table: AgentWorkflowsTable = Depends(get_agent_workflows_table),
) -> WorkflowResultService:
    return TursoWorkflowResultService(table=table)


mcp_app = FastMCP("InvestPal MCP Server", lifespan=db_lifespan)
mcp_app.add_middleware(LoggingMiddleware())


@mcp_app.tool(
    name="createUserProfileNote",
    description="Create a new user profile note.",
)
async def create_user_profile_note(
    note: Annotated[str, "The content of the note"],
    user_profile_service: UserProfileService = Depends(get_user_profile_service),
) -> UserProfileNote:
    return await user_profile_service.create_user_profile_note(note=note)


@mcp_app.tool(
    name="getUserProfileNotes",
    description="Get the list of active user profile notes.",
)
async def get_user_profile_notes(
    user_profile_service: UserProfileService = Depends(get_user_profile_service),
) -> list[UserProfileNote]:
    return await user_profile_service.get_user_profile_notes()


@mcp_app.tool(
    name="markUserProfileNoteAsOutdated",
    description="Mark a user profile note as outdated.",
)
async def mark_user_profile_note_as_outdated(
    note_id: Annotated[str, "The ID of the note to mark as outdated"],
    user_profile_service: UserProfileService = Depends(get_user_profile_service),
) -> str:
    await user_profile_service.mark_note_as_outdated(note_id=note_id)
    return f"Note {note_id} marked as outdated successfully"


@mcp_app.tool(
    name="getCurrentDatetime",
    description="Get the current datetime.",
)
async def get_current_datetime() -> str:
    return dt.datetime.now().isoformat()


@mcp_app.tool(
    name="getUserConversationNotes",
    description=(
        "Retrieve conversation notes, ordered by most recent first. "
        "Allows the agent to recall specific details from past conversations."
    ),
)
async def get_user_conversation_notes(
    limit: Annotated[
        int | None,
        "Maximum number of notes to return, ordered by most recent first. Defaults to 5. Pass None to return all notes.",
    ] = 5,
    user_conversation_notes_service: UserConversationNotesService = Depends(
        get_user_conversation_notes_service
    ),
) -> list[UserConversationNote]:
    return await user_conversation_notes_service.get_user_conversation_notes(
        limit=limit
    )


@mcp_app.tool(
    name="createUserConversationNote",
    description=(
        "Store a conversation note, by default against today's date. A date can hold any "
        "number of notes, so this adds a note rather than replacing existing ones. "
        "Keep notes short and concise."
    ),
)
async def create_user_conversation_note(
    note: Annotated[str, "A short, concise note about the conversation"],
    date: Annotated[
        str | None,
        "The date of the conversation in YYYY-MM-DD format. Defaults to today, so only pass it when recording a note for a different date.",
    ] = None,
    user_conversation_notes_service: UserConversationNotesService = Depends(
        get_user_conversation_notes_service
    ),
) -> UserConversationNote:
    return await user_conversation_notes_service.create_user_conversation_note(
        note=note,
        date=date,
    )


@mcp_app.tool(
    name="createAgentReminder",
    description="Create a new reminder for the user.",
)
async def create_agent_reminder(
    reminder_description: Annotated[str, "The description of the reminder"],
    due_date: Annotated[
        str | None, "Optional due date for the reminder in YYYY-MM-DD format"
    ] = None,
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
) -> AgentReminder:
    return await agent_reminder_service.create_agent_reminder(
        reminder_description=reminder_description,
        due_date=due_date,
    )


@mcp_app.tool(
    name="getAgentReminders",
    description="Get all reminders for the user.",
)
async def get_agent_reminders(
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
) -> list[AgentReminder]:
    return await agent_reminder_service.get_agent_reminders()


@mcp_app.tool(
    name="updateAgentReminder",
    description="Update an existing reminder for the user.",
)
async def update_agent_reminder(
    reminder_id: Annotated[str, "The unique id of the reminder to update"],
    reminder_description: Annotated[
        str | None,
        "New description for the reminder. If omitted, the existing description is kept.",
    ] = None,
    due_date: Annotated[
        str | None,
        "New due date for the reminder in YYYY-MM-DD format. If omitted, the existing due date is kept.",
    ] = None,
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
) -> AgentReminder:
    return await agent_reminder_service.update_agent_reminder(
        reminder_id=reminder_id,
        reminder_description=reminder_description,
        due_date=due_date,
    )


@mcp_app.tool(
    name="deleteAgentReminder",
    description="Delete a reminder for the user.",
)
async def delete_agent_reminder(
    reminder_id: Annotated[str, "The unique id of the reminder to delete"],
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
) -> None:
    await agent_reminder_service.delete_agent_reminder(
        reminder_id=reminder_id,
    )


@mcp_app.tool(
    name="createAgentWorkflow",
    description="""Create a new scheduled workflow for the user. An agent will execute the description autonomously on the given schedule.
    The description must state only WHAT goal to achieve — not HOW. Do not include tool names, user data, or implementation steps.
    The execution agent has its own tools and will independently access the user's profile.
    """,
)
async def create_agent_workflow(
    name: Annotated[str, "A short human-readable name for the workflow"],
    description: Annotated[
        str,
        "Goal-only description of what the agent should achieve on each run. No tool names, no user data, no implementation steps — just the intent.",
    ],
    schedule: Annotated[
        str, "Cron expression for the schedule, e.g. '0 0 1 * *' for monthly on the 1st"
    ],
    agent_workflow_service: AgentWorkflowService = Depends(get_agent_workflow_service),
) -> AgentWorkflow:
    return await agent_workflow_service.create_workflow(
        name=name,
        description=description,
        schedule=schedule,
    )


@mcp_app.tool(
    name="getAgentWorkflows",
    description="Get all scheduled workflows.",
)
async def get_agent_workflows(
    agent_workflow_service: AgentWorkflowService = Depends(get_agent_workflow_service),
) -> list[AgentWorkflow]:
    return await agent_workflow_service.get_workflows()


@mcp_app.tool(
    name="updateAgentWorkflow",
    description="Update an existing scheduled workflow. Only fields provided will be changed.",
)
async def update_agent_workflow(
    workflow_id: Annotated[str, "The unique id of the workflow to update"],
    name: Annotated[str | None, "New name. If omitted, existing name is kept."] = None,
    description: Annotated[
        str | None,
        "Updated goal-only description. No tool names, no user data, no implementation steps. If omitted, existing description is kept.",
    ] = None,
    schedule: Annotated[
        str | None, "New cron schedule. If omitted, existing schedule is kept."
    ] = None,
    status: Annotated[
        WorkflowStatus | None,
        "New status: 'active' or 'paused'. If omitted, existing status is kept.",
    ] = None,
    agent_workflow_service: AgentWorkflowService = Depends(get_agent_workflow_service),
) -> AgentWorkflow:
    return await agent_workflow_service.update_workflow(
        workflow_id=workflow_id,
        name=name,
        description=description,
        schedule=schedule,
        status=status,
    )


@mcp_app.tool(
    name="deleteAgentWorkflow",
    description="Delete a scheduled workflow.",
)
async def delete_agent_workflow(
    workflow_id: Annotated[str, "The unique id of the workflow to delete"],
    agent_workflow_service: AgentWorkflowService = Depends(get_agent_workflow_service),
) -> None:
    await agent_workflow_service.delete_workflow(workflow_id=workflow_id)


@mcp_app.tool(
    name="getWorkflowResults",
    description="Get the results of all past workflow runs, ordered by most recent first. Use this when the user asks what the agent has done on their behalf since the last conversation.",
)
async def get_workflow_results(
    limit: Annotated[
        int | None,
        "Maximum number of results to return. Defaults to 10. Pass None to return all.",
    ] = 10,
    workflow_result_service: WorkflowResultService = Depends(
        get_workflow_result_service
    ),
) -> list[WorkflowResult]:
    return await workflow_result_service.get_results(limit=limit)


@mcp_app.tool(
    name="storeWorkflowResult",
    description=(
        "Store the result of a workflow run. This also marks the run as finished: it sets "
        "the workflow's last run, advances its next run from its cron schedule, and clears "
        "the running lock."
    ),
)
async def store_workflow_result(
    workflow_id: Annotated[str, "The unique ID of the workflow"],
    workflow_name: Annotated[str, "The name of the workflow"],
    output: Annotated[str, "The execution output/result of the workflow to store"],
    workflow_result_service: WorkflowResultService = Depends(
        get_workflow_result_service
    ),
) -> WorkflowResult:
    return await workflow_result_service.save_result(
        workflow_id=workflow_id,
        workflow_name=workflow_name,
        output=output,
    )


@mcp_app.tool(
    name="getSkillDefinitions",
    description="Returns the available skill names and their description. A skill is a set of instructions for performing a specific task, such as analyzing a company's balance sheet.",
)
async def get_skill_definitions() -> list[SkillDefinition]:
    return [
        SkillDefinition(
            skill_name=skill_name.value,
            skill_description=skill_descriptions[skill_name],
        )
        for skill_name in skills.keys()
    ]


@mcp_app.tool(
    name="getSkill",
    description="Returns the instructions for a specific skill. Use getSkillDefinitions to retrieve the list of available skill names.",
)
async def get_skill(
    skill_name: Annotated[str, "The name of the skill to retrieve"],
) -> str:
    try:
        skill_enum = SkillName(skill_name)
    except ValueError:
        return f"Skill '{skill_name}' not found. Use getSkillDefinitions to see available skills."
    return skills[skill_enum]


@mcp_app.tool(name="add", description="Add two numbers together.")
async def add(
    a: Annotated[float, "The first operand"],
    b: Annotated[float, "The second operand"],
) -> float:
    return a + b


@mcp_app.tool(name="subtract", description="Subtract b from a.")
async def subtract(
    a: Annotated[float, "The first operand"],
    b: Annotated[float, "The second operand"],
) -> float:
    return a - b


@mcp_app.tool(name="multiply", description="Multiply two numbers together.")
async def multiply(
    a: Annotated[float, "The first operand"],
    b: Annotated[float, "The second operand"],
) -> float:
    return a * b


@mcp_app.tool(
    name="divide", description="Divide a by b. Returns an error if b is zero."
)
async def divide(
    a: Annotated[float, "The first operand"],
    b: Annotated[float, "The second operand"],
) -> float | str:
    if b == 0:
        return "Error: division by zero"
    return a / b


@mcp_app.prompt
def get_invstment_advisor_prompt() -> str:
    return INVESTMENT_ADVISOR_PROMPT


if __name__ == "__main__":
    mcp_app.run(transport="http", port=settings.MCP_APP_SERVER_PORT)
