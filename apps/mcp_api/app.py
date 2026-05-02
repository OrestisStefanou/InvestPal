import datetime as dt
import logging
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan
from fastmcp.dependencies import (
    Depends,
    CurrentContext,
)
from fastmcp.server.context import Context
from fastmcp.server.middleware import (
    Middleware,
    MiddlewareContext,
)
from pymongo import AsyncMongoClient

from config import settings
from services.user_context import (
    MongoDBUserContextService,
    UserContextService,
)
from services.agent_reminder import (
    MongoDBAgentReminderService,
    AgentReminderService,
)
from services.agent_workflows.workflow import (
    MongoDBAgentWorkflowService,
    AgentWorkflowService,
)
from services.agent_workflows.results import (
    MongoDBWorkflowResultService,
    WorkflowResultService,
)
from services.agents.prompts import INVESTMENT_ADVISOR_PROMPT
from services.agents.skills import SkillName, skills
from models.user_context import (
    UserContext,
    UserConversationNotes,
)
from models.agent_reminder import AgentReminder
from models.agent_workflow import (
    AgentWorkflow,
    WorkflowResult,
    WorkflowStatus,
)


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
        logger.info("Tool call %s with arguments %s returned result %s", tool_name, args, result)
        return result


@lifespan
async def db_lifespan(server):
    db_client = AsyncMongoClient(settings.MONGO_URI)
    yield {"db_client": db_client}
    await db_client.close()


def get_user_context_service(ctx: Context = CurrentContext()) -> UserContextService:
    db_client = ctx.lifespan_context["db_client"]
    return MongoDBUserContextService(mongo_client=db_client)


def get_agent_reminder_service(ctx: Context = CurrentContext()) -> AgentReminderService:
    db_client = ctx.lifespan_context["db_client"]
    return MongoDBAgentReminderService(mongo_client=db_client)


def get_agent_workflow_service(ctx: Context = CurrentContext()) -> AgentWorkflowService:
    db_client = ctx.lifespan_context["db_client"]
    return MongoDBAgentWorkflowService(mongo_client=db_client)


def get_workflow_result_service(ctx: Context = CurrentContext()) -> WorkflowResultService:
    db_client = ctx.lifespan_context["db_client"]
    return MongoDBWorkflowResultService(mongo_client=db_client)


mcp_app = FastMCP("InvestPal MCP Server", lifespan=db_lifespan)
mcp_app.add_middleware(LoggingMiddleware())


@mcp_app.tool(
    name="updateUserContext",
    description="Update the user context(for the given user_id) including user profile. Note: The provided context will completely replace the existing one, so the entire updated object must be provided.",
)
async def update_user_context(
    user_id: Annotated[str, "The id of the user to update the context for"],
    user_profile: Annotated[dict, "General information about the user. Must provide the complete user profile as it will replace the existing one."],
    user_context_service: UserContextService = Depends(get_user_context_service),
) -> UserContext:
    updated_user_context = await user_context_service.update_user_context(
        user_id=user_id,
        user_profile=user_profile,
    )

    return updated_user_context


@mcp_app.tool(
    name="getUserContext",
    description="Get the user context(for the given user_id) including user profile and portfolio holdings.",
)
async def update_user_context(
    user_id: Annotated[str, "The id of the user to get the context for"],
    user_context_service: UserContextService = Depends(get_user_context_service),
) -> UserContext:
    user_context = await user_context_service.get_user_context(user_id=user_id)
    return user_context


@mcp_app.tool(
    name="getCurrentDatetime",
    description="Get the current datetime.",
)
async def get_current_datetime() -> str:
    return dt.datetime.now().isoformat()


@mcp_app.tool(
    name="getUserConversationNotes",
    description=(
        "Retrieve conversation notes for a user, ordered by most recent date first. "
        "Allows the agent to recall specific details from past conversations."
    ),
)
async def get_user_conversation_notes(
    user_id: Annotated[str, "The id of the user to get conversation notes for"],
    limit: Annotated[int | None, "Maximum number of dates to return, ordered by most recent first. Defaults to 5. Pass None to return all notes."] = 5,
    user_context_service: UserContextService = Depends(get_user_context_service),
) -> list[UserConversationNotes]:
    return await user_context_service.get_user_conversation_notes(user_id=user_id, limit=limit)


@mcp_app.tool(
    name="updateUserConversationNotes",
    description=(
        "Store or update conversation notes for a specific user and date. "
        "The provided notes will be MERGED with existing ones for that date (only keys "
        "provided will be overwritten or added). Keep notes short and concise."
    ),
)
async def update_user_conversation_notes(
    user_id: Annotated[str, "The id of the user to update conversation notes for"],
    date: Annotated[str, "The date of the conversation in YYYY-MM-DD format"],
    notes: Annotated[dict, "A key-value store of notes about the conversation. These will be merged with any existing notes for this date"],
    user_context_service: UserContextService = Depends(get_user_context_service),
) -> None:
    await user_context_service.update_user_conversation_notes(
        user_id=user_id,
        date=date,
        notes=notes,
    )


@mcp_app.tool(
    name="createAgentReminder",
    description="Create a new reminder for the user.",
)
async def create_agent_reminder(
    user_id: Annotated[str, "The id of the user to create the reminder for"],
    reminder_description: Annotated[str, "The description of the reminder"],
    due_date: Annotated[str | None, "Optional due date for the reminder in YYYY-MM-DD format"] = None,
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
) -> AgentReminder:
    return await agent_reminder_service.create_agent_reminder(
        user_id=user_id,
        reminder_description=reminder_description,
        due_date=due_date,
    )


@mcp_app.tool(
    name="getAgentReminders",
    description="Get all reminders for the given user.",
)
async def get_agent_reminders(
    user_id: Annotated[str, "The id of the user to get reminders for"],
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
) -> list[AgentReminder]:
    return await agent_reminder_service.get_agent_reminders(user_id=user_id)


@mcp_app.tool(
    name="updateAgentReminder",
    description="Update an existing reminder for the user.",
)
async def update_agent_reminder(
    user_id: Annotated[str, "The id of the user the reminder belongs to"],
    reminder_id: Annotated[str, "The unique id of the reminder to update"],
    reminder_description: Annotated[str | None, "New description for the reminder. If omitted, the existing description is kept."] = None,
    due_date: Annotated[str | None, "New due date for the reminder in YYYY-MM-DD format. If omitted, the existing due date is kept."] = None,
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
) -> AgentReminder:
    return await agent_reminder_service.update_agent_reminder(
        user_id=user_id,
        reminder_id=reminder_id,
        reminder_description=reminder_description,
        due_date=due_date,
    )


@mcp_app.tool(
    name="deleteAgentReminder",
    description="Delete a reminder for the user.",
)
async def delete_agent_reminder(
    user_id: Annotated[str, "The id of the user the reminder belongs to"],
    reminder_id: Annotated[str, "The unique id of the reminder to delete"],
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
) -> None:
    await agent_reminder_service.delete_agent_reminder(
        user_id=user_id,
        reminder_id=reminder_id,
    )


@mcp_app.tool(
    name="createAgentWorkflow",
    description="""Create a new scheduled workflow for the user. An agent will execute the description autonomously on the given schedule.
    The description must state only WHAT goal to achieve — not HOW. Do not include tool names, user data, or implementation steps.
    The execution agent has its own tools and will independently access the user's profile.
    """
)
async def create_agent_workflow(
    user_id: Annotated[str, "The id of the user to create the workflow for"],
    name: Annotated[str, "A short human-readable name for the workflow"],
    description: Annotated[str, "Goal-only description of what the agent should achieve on each run. No tool names, no user data, no implementation steps — just the intent."],
    schedule: Annotated[str, "Cron expression for the schedule, e.g. '0 0 1 * *' for monthly on the 1st"],
    agent_workflow_service: AgentWorkflowService = Depends(get_agent_workflow_service),
) -> AgentWorkflow:
    return await agent_workflow_service.create_workflow(
        user_id=user_id,
        name=name,
        description=description,
        schedule=schedule,
    )


@mcp_app.tool(
    name="getAgentWorkflows",
    description="Get all scheduled workflows for the given user.",
)
async def get_agent_workflows(
    user_id: Annotated[str, "The id of the user to get workflows for"],
    agent_workflow_service: AgentWorkflowService = Depends(get_agent_workflow_service),
) -> list[AgentWorkflow]:
    return await agent_workflow_service.get_workflows(user_id=user_id)


@mcp_app.tool(
    name="updateAgentWorkflow",
    description="Update an existing scheduled workflow. Only fields provided will be changed.",
)
async def update_agent_workflow(
    user_id: Annotated[str, "The id of the user the workflow belongs to"],
    workflow_id: Annotated[str, "The unique id of the workflow to update"],
    name: Annotated[str | None, "New name. If omitted, existing name is kept."] = None,
    description: Annotated[str | None, "Updated goal-only description. No tool names, no user data, no implementation steps. If omitted, existing description is kept."] = None,
    schedule: Annotated[str | None, "New cron schedule. If omitted, existing schedule is kept."] = None,
    status: Annotated[WorkflowStatus | None, "New status: 'active' or 'paused'. If omitted, existing status is kept."] = None,
    agent_workflow_service: AgentWorkflowService = Depends(get_agent_workflow_service),
) -> AgentWorkflow:
    return await agent_workflow_service.update_workflow(
        user_id=user_id,
        workflow_id=workflow_id,
        name=name,
        description=description,
        schedule=schedule,
        status=status,
    )


@mcp_app.tool(
    name="deleteAgentWorkflow",
    description="Delete a scheduled workflow for the user.",
)
async def delete_agent_workflow(
    user_id: Annotated[str, "The id of the user the workflow belongs to"],
    workflow_id: Annotated[str, "The unique id of the workflow to delete"],
    agent_workflow_service: AgentWorkflowService = Depends(get_agent_workflow_service),
) -> None:
    await agent_workflow_service.delete_workflow(
        user_id=user_id,
        workflow_id=workflow_id,
    )


@mcp_app.tool(
    name="getWorkflowResults",
    description="Get the results of all past workflow runs for the user, ordered by most recent first. Use this when the user asks what the agent has done on their behalf since the last conversation.",
)
async def get_workflow_results(
    user_id: Annotated[str, "The id of the user to get workflow results for"],
    limit: Annotated[int | None, "Maximum number of results to return. Defaults to 10. Pass None to return all."] = 10,
    workflow_result_service: WorkflowResultService = Depends(get_workflow_result_service),
) -> list[WorkflowResult]:
    return await workflow_result_service.get_results(user_id=user_id, limit=limit)


@mcp_app.tool(
    name="getSkillNames",
    description="Returns the available skill names. A skill is a set of instructions for performing a specific task, such as analyzing a company's balance sheet.",
)
async def get_skill_names() -> list[str]:
    return [skill_name.value for skill_name in skills.keys()]


@mcp_app.tool(
    name="getSkill",
    description="Returns the instructions for a specific skill. Use getSkillNames to retrieve the list of available skill names.",
)
async def get_skill(
    skill_name: Annotated[str, "The name of the skill to retrieve"],
) -> str:
    try:
        skill_enum = SkillName(skill_name)
    except ValueError:
        return f"Skill '{skill_name}' not found. Use getSkillNames to see available skills."
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


@mcp_app.tool(name="divide", description="Divide a by b. Returns an error if b is zero.")
async def divide(
    a: Annotated[float, "The first operand"],
    b: Annotated[float, "The second operand"],
) -> float | str:
    if b == 0:
        return "Error: division by zero"
    return a / b


@mcp_app.prompt
def get_invstment_advisor_prompt(user_id: str) -> str:
    return INVESTMENT_ADVISOR_PROMPT.format(user_id=user_id)

if __name__ == "__main__":
    mcp_app.run(transport="http", port=settings.MCP_APP_SERVER_PORT)