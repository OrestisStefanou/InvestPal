import datetime as dt
from dataclasses import dataclass

from langchain.tools import (
    ToolRuntime,
    tool,
)
from pydantic import (
    BaseModel,
    Field,
)

from models.agent_reminder import AgentReminder
from models.agent_workflow import AgentWorkflow, WorkflowResult, WorkflowStatus
from models.user_context import (
    UserConversationNote,
    UserConversationNoteSearchResult,
    UserProfileNote,
)
from services.agent_reminder import AgentReminderService
from services.agent_workflows.results import WorkflowResultService
from services.agent_workflows.workflow import AgentWorkflowService
from services.agents.skills import (
    SkillName,
    skill_descriptions,
    skills,
)
from services.user_context import (
    UserConversationNotesService,
    UserProfileService,
)


@dataclass
class UserProfileToolsRuntimeContext:
    user_profile_service: UserProfileService


@dataclass
class UserConversationNotesToolsRuntimeContext:
    user_conversation_notes_service: UserConversationNotesService


@dataclass
class AgentReminderToolsRuntimeContext:
    agent_reminder_service: AgentReminderService


@dataclass
class AgentWorkflowToolsRuntimeContext:
    agent_workflow_service: AgentWorkflowService


@dataclass
class WorkflowResultsToolRuntimeContext:
    workflow_result_service: WorkflowResultService


@tool("getUserProfileNotes")
async def get_user_profile_notes(
    runtime: ToolRuntime[UserProfileToolsRuntimeContext],
) -> list[UserProfileNote]:
    """Get the notes that make up the user's profile, excluding outdated ones."""
    user_profile_service = runtime.context.user_profile_service
    return await user_profile_service.get_user_profile_notes()


class CreateUserProfileNoteToolInput(BaseModel):
    note: str = Field(
        description=(
            "A permanent fact about the user's profile or preferences, such as risk "
            "tolerance, investment horizon, goals or sector interests. Keep it to a "
            "single self-contained fact."
        )
    )


@tool(
    "createUserProfileNote",
    args_schema=CreateUserProfileNoteToolInput,
    description=(
        "Store a permanent fact about the user's profile. The profile is a set of notes, "
        "so this adds a note rather than replacing the existing ones. When a fact stops "
        "being true, mark the old note as outdated instead of editing it."
    ),
)
async def create_user_profile_note(
    runtime: ToolRuntime[UserProfileToolsRuntimeContext],
    note: str,
) -> UserProfileNote:
    user_profile_service = runtime.context.user_profile_service
    return await user_profile_service.create_user_profile_note(note=note)


class MarkUserProfileNoteAsOutdatedToolInput(BaseModel):
    note_id: str = Field(description="The unique id of the profile note to mark as outdated")


@tool(
    "markUserProfileNoteAsOutdated",
    args_schema=MarkUserProfileNoteAsOutdatedToolInput,
    description=(
        "Mark a profile note as outdated so it stops being part of the user's profile. "
        "Use this when a fact you previously recorded is no longer true."
    ),
)
async def mark_user_profile_note_as_outdated(
    runtime: ToolRuntime[UserProfileToolsRuntimeContext],
    note_id: str,
) -> None:
    user_profile_service = runtime.context.user_profile_service
    await user_profile_service.mark_note_as_outdated(note_id)


@tool("getCurrentDatetime")
async def get_current_datetime() -> str:
    """
    Get the current datetime.
    """
    return dt.datetime.now().isoformat()


class GetUserConversationNotesToolInput(BaseModel):
    limit: int | None = Field(
        default=5,
        description="Maximum number of notes to return, ordered by most recent first. Defaults to 5. Pass None to return all notes.",
    )


@tool(
    "getUserConversationNotes",
    args_schema=GetUserConversationNotesToolInput,
    description=(
        "Retrieve conversation notes, ordered by most recent first. "
        "Allows recalling specific details from past conversations."
    ),
)
async def get_user_conversation_notes(
    runtime: ToolRuntime[UserConversationNotesToolsRuntimeContext],
    limit: int | None = 5,
) -> list[UserConversationNote]:
    user_conversation_notes_service = runtime.context.user_conversation_notes_service
    return await user_conversation_notes_service.get_user_conversation_notes(
        limit=limit
    )


class SearchUserConversationNotesToolInput(BaseModel):
    query: str = Field(
        description=(
            "A natural-language description of what to recall, for example "
            "\"the client's view on pension allocation\". Full sentences work "
            "better than keywords."
        )
    )
    limit: int = Field(
        default=5,
        description="Maximum number of notes to return, most similar first. Defaults to 5.",
    )
    min_similarity: float | None = Field(
        default=None,
        description=(
            "Optional 0.0-1.0 similarity floor. Leave unset unless you specifically "
            "want to drop weak matches; scores are relative, so it is usually better "
            "to read them and judge."
        ),
    )


@tool(
    "searchUserConversationNotes",
    args_schema=SearchUserConversationNotesToolInput,
    description=(
        "Search past conversation notes by meaning rather than by date. "
        "Returns the most semantically similar notes, each with a similarity score. "
        "Prefer this over getUserConversationNotes whenever you are looking for a "
        "specific topic rather than simply reviewing the latest notes."
    ),
)
async def search_user_conversation_notes(
    runtime: ToolRuntime[UserConversationNotesToolsRuntimeContext],
    query: str,
    limit: int = 5,
    min_similarity: float | None = None,
) -> list[UserConversationNoteSearchResult]:
    user_conversation_notes_service = runtime.context.user_conversation_notes_service
    return await user_conversation_notes_service.search_user_conversation_notes(
        query=query,
        limit=limit,
        min_similarity=min_similarity,
    )


class CreateUserConversationNoteToolInput(BaseModel):
    note: str = Field(
        description=(
            "A short, concise note about the conversation. "
            "Keep it brief and focused on information useful for future investment advice."
        )
    )
    date: str | None = Field(
        default=None,
        description="The date of the conversation in YYYY-MM-DD format. Defaults to today, so only pass it when recording a note for a different date.",
    )


@tool(
    "createUserConversationNote",
    args_schema=CreateUserConversationNoteToolInput,
    description=(
        "Store a conversation note. Defaults to today's date. "
        "Use this to capture conversation-specific context such as topics discussed, "
        "questions asked, or recommendations given — information that is relevant to a particular "
        "conversation but not a permanent part of the user's profile. "
        "A date can hold any number of notes, so this adds a note rather than replacing existing ones."
    ),
)
async def create_user_conversation_note(
    runtime: ToolRuntime[UserConversationNotesToolsRuntimeContext],
    note: str,
    date: str | None = None,
) -> UserConversationNote:
    user_conversation_notes_service = runtime.context.user_conversation_notes_service
    return await user_conversation_notes_service.create_user_conversation_note(
        note=note,
        date=date,
    )


class CreateAgentReminderToolInput(BaseModel):
    reminder_description: str = Field(description="The description of the reminder")
    due_date: str | None = Field(
        default=None,
        description="Optional due date for the reminder in YYYY-MM-DD format",
    )


@tool(
    "createAgentReminder",
    args_schema=CreateAgentReminderToolInput,
    description="Create a new reminder for the user.",
)
async def create_agent_reminder(
    runtime: ToolRuntime[AgentReminderToolsRuntimeContext],
    reminder_description: str,
    due_date: str | None = None,
) -> AgentReminder:
    agent_reminder_service = runtime.context.agent_reminder_service
    return await agent_reminder_service.create_agent_reminder(
        reminder_description=reminder_description,
        due_date=due_date,
    )


@tool("getAgentReminders")
async def get_agent_reminders(
    runtime: ToolRuntime[AgentReminderToolsRuntimeContext],
) -> list[AgentReminder]:
    """Get all reminders for the user."""
    agent_reminder_service = runtime.context.agent_reminder_service
    return await agent_reminder_service.get_agent_reminders()


class UpdateAgentReminderToolInput(BaseModel):
    reminder_id: str = Field(description="The unique id of the reminder to update")
    reminder_description: str | None = Field(
        default=None,
        description="New description for the reminder. If omitted, the existing description is kept.",
    )
    due_date: str | None = Field(
        default=None,
        description="New due date for the reminder in YYYY-MM-DD format. If omitted, the existing due date is kept.",
    )


@tool(
    "updateAgentReminder",
    args_schema=UpdateAgentReminderToolInput,
    description="Update an existing reminder for the user.",
)
async def update_agent_reminder(
    runtime: ToolRuntime[AgentReminderToolsRuntimeContext],
    reminder_id: str,
    reminder_description: str | None = None,
    due_date: str | None = None,
) -> AgentReminder:
    agent_reminder_service = runtime.context.agent_reminder_service
    return await agent_reminder_service.update_agent_reminder(
        reminder_id=reminder_id,
        reminder_description=reminder_description,
        due_date=due_date,
    )


class DeleteAgentReminderToolInput(BaseModel):
    reminder_id: str = Field(description="The unique id of the reminder to delete")


@tool(
    "deleteAgentReminder",
    args_schema=DeleteAgentReminderToolInput,
    description="Delete a reminder for the user.",
)
async def delete_agent_reminder(
    runtime: ToolRuntime[AgentReminderToolsRuntimeContext],
    reminder_id: str,
) -> None:
    agent_reminder_service = runtime.context.agent_reminder_service
    await agent_reminder_service.delete_agent_reminder(
        reminder_id=reminder_id,
    )


class SkillDefinition(BaseModel):
    skill_name: str
    skill_description: str


@tool("getSkillDefinitions")
async def get_skill_definitions() -> list[SkillDefinition]:
    """Returns the available skill names and their description.
    A skill is a set of instructions for performing a specific task,
    such as analyzing a company's balance sheet.
    """
    return [
        SkillDefinition(
            skill_name=skill_name.value,
            skill_description=skill_descriptions[skill_name],
        )
        for skill_name in skills.keys()
    ]


@tool("getSkill")
async def get_skill(skill_name: str) -> str:
    """
    Returns the instructions for a specific skill. Use getSkillDefinitions to retrieve the list of available skill names.
    """
    try:
        skill_enum = SkillName(skill_name)
    except ValueError:
        return f"Skill '{skill_name}' not found. Use getSkillDefinitions to see available skills."

    return skills[skill_enum]


class MathOperationToolInput(BaseModel):
    a: float = Field(description="The first operand")
    b: float = Field(description="The second operand")


@tool(
    "add", args_schema=MathOperationToolInput, description="Add two numbers together."
)
async def add(a: float, b: float) -> float:
    return a + b


@tool("subtract", args_schema=MathOperationToolInput, description="Subtract b from a.")
async def subtract(a: float, b: float) -> float:
    return a - b


@tool(
    "multiply",
    args_schema=MathOperationToolInput,
    description="Multiply two numbers together.",
)
async def multiply(a: float, b: float) -> float:
    return a * b


@tool(
    "divide",
    args_schema=MathOperationToolInput,
    description="Divide a by b. Returns an error if b is zero.",
)
async def divide(a: float, b: float) -> float | str:
    if b == 0:
        return "Error: division by zero"
    return a / b


class CalculateInvestmentFutureValueToolInput(BaseModel):
    initial_investment: float = Field(description="Initial investment amount")
    annual_return: float = Field(
        description="Annual return percentage (10 means 10%)"
    )
    years: int = Field(description="Number of years")


@tool(
    "calculateInvestmentFutureValue",
    args_schema=CalculateInvestmentFutureValueToolInput,
    description="Calculate the future value of an investment compounded annually.",
)
async def calculate_investment_future_value(
    initial_investment: float,
    annual_return: float,
    years: int,
) -> float:
    return initial_investment * (1 + annual_return / 100) ** years


class CreateAgentWorkflowToolInput(BaseModel):
    name: str = Field(description="A short human-readable name for the workflow")
    description: str = Field(
        description="Goal-only description of what the agent should achieve on each run. No tool names, no user data, no implementation steps — just the intent."
    )
    schedule: str = Field(
        description="Cron expression for the schedule, e.g. '0 0 1 * *' for monthly on the 1st"
    )


@tool(
    "createAgentWorkflow",
    args_schema=CreateAgentWorkflowToolInput,
    description="""Create a new scheduled workflow for the user. An agent will execute the description autonomously on the given schedule.
    The description must state only WHAT goal to achieve — not HOW. Do not include tool names, user data, or implementation steps.
    The execution agent has its own tools and will independently access the user's profile.
    """,
)
async def create_agent_workflow(
    runtime: ToolRuntime[AgentWorkflowToolsRuntimeContext],
    name: str,
    description: str,
    schedule: str,
) -> AgentWorkflow:
    return await runtime.context.agent_workflow_service.create_workflow(
        name=name,
        description=description,
        schedule=schedule,
    )


@tool("getAgentWorkflows")
async def get_agent_workflows(
    runtime: ToolRuntime[AgentWorkflowToolsRuntimeContext],
) -> list[AgentWorkflow]:
    """Get all scheduled workflows."""
    return await runtime.context.agent_workflow_service.get_workflows()


class UpdateAgentWorkflowToolInput(BaseModel):
    workflow_id: str = Field(description="The unique id of the workflow to update")
    name: str | None = Field(
        default=None, description="New name. If omitted, existing name is kept."
    )
    description: str | None = Field(
        default=None,
        description="Updated goal-only description. No tool names, no user data, no implementation steps. If omitted, existing description is kept.",
    )
    schedule: str | None = Field(
        default=None,
        description="New cron schedule. If omitted, existing schedule is kept.",
    )
    status: WorkflowStatus | None = Field(
        default=None,
        description="New status: 'active' or 'paused'. If omitted, existing status is kept.",
    )


@tool(
    "updateAgentWorkflow",
    args_schema=UpdateAgentWorkflowToolInput,
    description="Update an existing scheduled workflow. Only fields provided will be changed.",
)
async def update_agent_workflow(
    runtime: ToolRuntime[AgentWorkflowToolsRuntimeContext],
    workflow_id: str,
    name: str | None = None,
    description: str | None = None,
    schedule: str | None = None,
    status: WorkflowStatus | None = None,
) -> AgentWorkflow:
    return await runtime.context.agent_workflow_service.update_workflow(
        workflow_id=workflow_id,
        name=name,
        description=description,
        schedule=schedule,
        status=status,
    )


class DeleteAgentWorkflowToolInput(BaseModel):
    workflow_id: str = Field(description="The unique id of the workflow to delete")


@tool(
    "deleteAgentWorkflow",
    args_schema=DeleteAgentWorkflowToolInput,
    description="Delete a scheduled workflow for the user.",
)
async def delete_agent_workflow(
    runtime: ToolRuntime[AgentWorkflowToolsRuntimeContext],
    workflow_id: str,
) -> None:
    await runtime.context.agent_workflow_service.delete_workflow(
        workflow_id=workflow_id,
    )


class GetWorkflowResultsToolInput(BaseModel):
    limit: int | None = Field(
        default=10,
        description="Maximum number of results to return. Defaults to 10. Pass None to return all results.",
    )


@tool(
    "getWorkflowResults",
    args_schema=GetWorkflowResultsToolInput,
    description="Get the results of all past workflow runs for the user, ordered by most recent first. Use this when the user asks what the agent has done on their behalf since the last conversation.",
)
async def get_workflow_results(
    runtime: ToolRuntime[WorkflowResultsToolRuntimeContext],
    limit: int | None = 10,
) -> list[WorkflowResult]:
    return await runtime.context.workflow_result_service.get_results(limit=limit)
