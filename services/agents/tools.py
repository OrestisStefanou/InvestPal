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
from models.holdings import Holding
from models.ticker_records import TickerRecord
from models.user_context import (
    UserConversationNote,
    UserConversationNoteSearchResult,
    UserProfileNote,
)
from services.agent_reminder import AgentReminderService
from services.holdings import HoldingsService
from services.ticker_records import TickerRecordsService
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


@dataclass
class HoldingsToolsRuntimeContext:
    holdings_service: HoldingsService


@dataclass
class TickerRecordsToolsRuntimeContext:
    ticker_records_service: TickerRecordsService


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
            "A single self-contained durable fact about the user, such as risk "
            "tolerance, investment horizon, goals, expenses, liquidity constraints or "
            "sector interests."
        )
    )


@tool(
    "createUserProfileNote",
    args_schema=CreateUserProfileNoteToolInput,
    description=(
        "Store one durable fact about the client as a new note. The test: would this "
        "still be true, and still matter, in six months regardless of market prices? "
        "Yes for age, risk tolerance, investment goal, horizon, knowledge level, "
        "profession, income, expenses, liquidity constraints, sector interests, ethical "
        "preferences, and standing policies the client has set for their own book. "
        "NO for anything priced, dated or positional: never store holdings, share "
        "counts, prices, P&L, portfolio values, watchlist entries, entry triggers, "
        "research theses, or what happened in a session. Positions belong in holdings "
        "(upsertHolding), convictions and price triggers belong in ticker records "
        "(upsertTickerRecord), session events belong in conversation notes "
        "(createUserConversationNote), and general valuation methodology belongs in the "
        "skills, not here. Notes are append-only: when a fact stops being true, mark the "
        "old note as outdated instead of editing it and add a replacement."
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
        "Store what happened in a session, by default against today's date. This is the "
        "home for anything dated: decisions taken and the reasoning behind them, analysis "
        "run and what it concluded, trades executed, advice given, questions asked, and "
        "follow-ups left open. If it begins with 'on <date> we...' it belongs here and "
        "not in a profile note. A date can hold any number of notes, so this adds a note "
        "rather than replacing existing ones. Keep each note short and factual; the "
        "durable conclusions it produced belong in the profile, holdings or ticker "
        "records, and this note is the narrative record of how they were reached."
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


class GetHoldingsToolInput(BaseModel):
    include_closed: bool = Field(
        default=False, description="Include positions that have been closed"
    )


@tool(
    "getHoldings",
    args_schema=GetHoldingsToolInput,
    description=(
        "What the client owns: broker positions, cash, fixed income and anything "
        "held off-platform. Read this before any portfolio review, allocation "
        "question or position-sizing decision. Rows whose source is a broker are a "
        "CACHE of that broker's own record: when the broker's tools are available, "
        "call them and refresh with upsertHolding rather than trusting what is "
        "stored here. When they are not available, this is the best record there "
        "is, but every figure must be quoted with its as_of date rather than "
        "presented as current. Market prices, market values and P&L are never "
        "stored here; fetch those live."
    ),
)
async def get_holdings(
    runtime: ToolRuntime[HoldingsToolsRuntimeContext],
    include_closed: bool = False,
) -> list[Holding]:
    holdings_service = runtime.context.holdings_service
    return await holdings_service.get_holdings(include_closed=include_closed)


class UpsertHoldingToolInput(BaseModel):
    name: str = Field(
        description=(
            "What the position is: a ticker like 'NVDA', or a description like "
            "'Bank cash'. Part of the holding's identity, so reuse it exactly when "
            "refreshing."
        )
    )
    kind: str | None = Field(
        default=None,
        description=(
            "cash | fixed_income | equity | etf | crypto | private_equity | other. "
            "Required when creating."
        ),
    )
    ticker: str | None = Field(
        default=None, description="Exchange ticker, when the holding has one"
    )
    quantity: float | None = Field(default=None, description="Shares or units held")
    cost_basis: float | None = Field(
        default=None, description="Average cost per unit, in `currency`"
    )
    amount: float | None = Field(
        default=None,
        description=(
            "Total value, for holdings with no unit price such as a cash balance or "
            "a bill's face value. Not a market value."
        ),
    )
    currency: str | None = Field(
        default=None, description="ISO currency code, e.g. 'EUR', 'USD'"
    )
    custodian: str | None = Field(
        default=None,
        description=(
            "Who holds it: 'Interactive Brokers', 'Coinbase', 'Sophic', 'Bank', "
            "'Carta'. Part of the holding's identity."
        ),
    )
    source: str | None = Field(
        default=None,
        description=(
            "manual | interactive_brokers | coinbase | alpaca. Required when "
            "creating. Use the broker you actually read the figures from."
        ),
    )
    as_of: str | None = Field(
        default=None,
        description=(
            "YYYY-MM-DD, the date these figures were true. Required when creating, "
            "and should be updated on every refresh."
        ),
    )
    detail: str | None = Field(
        default=None,
        description=(
            "Facts the columns do not carry: interest rate, maturity, vesting, "
            "strike. Not theses or price targets."
        ),
    )


@tool(
    "upsertHolding",
    args_schema=UpsertHoldingToolInput,
    description=(
        "Record or refresh one position. Identified by name plus custodian, so "
        "writing the same pair again updates that row rather than adding a second "
        "one. Only the fields you pass are written, so refreshing a share count "
        "from a broker leaves the cost basis alone. Always set as_of to the date "
        "the figures were true, and set source to the broker you read them from, "
        "or 'manual' when the client told you. Use this after reading broker "
        "positions so the record survives the next outage, and whenever the client "
        "reports something no integration can see. Do not record prices, market "
        "values or P&L; those are fetched live, and a stored copy goes stale and "
        "then gets believed."
    ),
)
async def upsert_holding(
    runtime: ToolRuntime[HoldingsToolsRuntimeContext],
    name: str,
    kind: str | None = None,
    ticker: str | None = None,
    quantity: float | None = None,
    cost_basis: float | None = None,
    amount: float | None = None,
    currency: str | None = None,
    custodian: str | None = None,
    source: str | None = None,
    as_of: str | None = None,
    detail: str | None = None,
) -> Holding:
    holdings_service = runtime.context.holdings_service
    return await holdings_service.upsert_holding(
        name=name,
        kind=kind,
        ticker=ticker,
        quantity=quantity,
        cost_basis=cost_basis,
        amount=amount,
        currency=currency,
        custodian=custodian,
        source=source,
        as_of=as_of,
        detail=detail,
    )


class CloseHoldingToolInput(BaseModel):
    holding_id: str = Field(description="The id of the holding to close")


@tool(
    "closeHolding",
    args_schema=CloseHoldingToolInput,
    description=(
        "Mark a position as closed once it is fully sold, matured or otherwise "
        "gone. It keeps its cost basis and history and stops appearing in "
        "getHoldings. Do not use this to correct a mistake; upsertHolding with the "
        "right figures."
    ),
)
async def close_holding(
    runtime: ToolRuntime[HoldingsToolsRuntimeContext],
    holding_id: str,
) -> str:
    holdings_service = runtime.context.holdings_service
    closed = await holdings_service.close_holding(holding_id=holding_id)
    if not closed:
        return f"No open holding with id {holding_id}"
    return f"Holding {holding_id} closed successfully"


class GetTickerRecordsToolInput(BaseModel):
    status: str | None = Field(
        default=None,
        description=(
            "Filter by watching | held | exited | rejected. Omit to return everything."
        ),
    )


@tool(
    "getTickerRecords",
    args_schema=GetTickerRecordsToolInput,
    description=(
        "The names being tracked and why: thesis, entry trigger, falsifier and "
        "status. This is the watchlist and the conviction record in one. Read it "
        "before screening a new idea (to check overlap with what is already "
        "tracked) and during a portfolio review (to check whether any entry trigger "
        "has fired). Holdings answer what is owned and how much; these answer why, "
        "and at what price to act."
    ),
)
async def get_ticker_records(
    runtime: ToolRuntime[TickerRecordsToolsRuntimeContext],
    status: str | None = None,
) -> list[TickerRecord]:
    ticker_records_service = runtime.context.ticker_records_service
    return await ticker_records_service.get_ticker_records(status=status)


class UpsertTickerRecordToolInput(BaseModel):
    ticker: str = Field(
        description="Exchange ticker, e.g. 'LHX', 'ENR.DE', '7011.T'"
    )
    status: str | None = Field(
        default=None,
        description=(
            "watching | held | exited | rejected. Required when creating a new record."
        ),
    )
    thesis: str | None = Field(
        default=None,
        description="Why this name is interesting: the business and the structural case",
    )
    entry_trigger: str | None = Field(
        default=None,
        description=(
            "The condition that would make this a buy, checkable against live data, "
            "e.g. 'limit $238,22 or below'"
        ),
    )
    falsifier: str | None = Field(
        default=None,
        description="What would prove the thesis wrong and take this off the list",
    )
    notes: str | None = Field(
        default=None,
        description="Anything else durable about the name the other fields do not hold",
    )


@tool(
    "upsertTickerRecord",
    args_schema=UpsertTickerRecordToolInput,
    description=(
        "Record or update why a name is interesting. Keyed by ticker and updated in "
        "place, so resetting an entry trigger edits the existing record rather than "
        "adding a second one. Only the fields you pass are written, so moving a name "
        "to 'held' leaves its thesis intact. Use this whenever a name is added to "
        "the watchlist, a thesis or trigger changes, a position is opened or closed, "
        "or a candidate is screened and rejected. Record the reasoning for a change "
        "in a conversation note; this record holds only the current state."
    ),
)
async def upsert_ticker_record(
    runtime: ToolRuntime[TickerRecordsToolsRuntimeContext],
    ticker: str,
    status: str | None = None,
    thesis: str | None = None,
    entry_trigger: str | None = None,
    falsifier: str | None = None,
    notes: str | None = None,
) -> TickerRecord:
    ticker_records_service = runtime.context.ticker_records_service
    return await ticker_records_service.upsert_ticker_record(
        ticker=ticker,
        status=status,
        thesis=thesis,
        entry_trigger=entry_trigger,
        falsifier=falsifier,
        notes=notes,
    )


class DeleteTickerRecordToolInput(BaseModel):
    ticker: str = Field(description="The ticker whose record should be deleted")


@tool(
    "deleteTickerRecord",
    args_schema=DeleteTickerRecordToolInput,
    description=(
        "Permanently remove a ticker record. Prefer setting status to 'rejected' or "
        "'exited' instead: why a name was turned down is worth keeping, and stops it "
        "being re-screened from scratch. Use this only for a record created by mistake."
    ),
)
async def delete_ticker_record(
    runtime: ToolRuntime[TickerRecordsToolsRuntimeContext],
    ticker: str,
) -> str:
    ticker_records_service = runtime.context.ticker_records_service
    deleted = await ticker_records_service.delete_ticker_record(ticker=ticker)
    if not deleted:
        return f"No ticker record found for {ticker}"
    return f"Ticker record {ticker} deleted successfully"


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
