import asyncio
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
from models.holdings import Holding
from models.ticker_records import TickerRecord
from models.user_context import (
    UserConversationNote,
    UserConversationNoteSearchResult,
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
from repos.workflow_results import WorkflowResultsTable
from services.agents.prompts import INVESTMENT_ADVISOR_PROMPT
from services.agents.skills import (
    SkillName,
    skill_descriptions,
    skills,
)
from services.agents.tools import SkillDefinition
from repos.embeddings import get_embedder
from repos.user_conversation_note_embeddings import (
    UserConversationNoteEmbeddingsTable,
)
from services.holdings import HoldingsService
from services.ticker_records import TickerRecordsService
from services.user_context import (
    UserConversationNotesService,
    UserProfileService,
)
from repos.holdings import HoldingsTable
from repos.ticker_records import TickerRecordsTable
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


async def _warm_up_embedder():
    """Load the embedding model off the startup path.

    Kicked off as a background task rather than awaited: searchUserConversationNotes
    is user-facing and synchronous, so it should not be the call that pays the
    model load (and, on a cold cache, the download).
    """
    embedder = get_embedder()
    if embedder is None:
        return
    try:
        await asyncio.to_thread(embedder.warm_up)
    except Exception:
        logger.warning("Failed to warm up the embedding model", exc_info=True)


@lifespan
async def db_lifespan(server):
    # Initialize Turso/SQLite database schema
    init_db(settings.TURSO_DB_PATH)
    warm_up_task = asyncio.create_task(_warm_up_embedder())
    try:
        yield {}
    finally:
        warm_up_task.cancel()


def get_user_profile_notes_table(ctx: Context = CurrentContext()) -> UserProfileNotesTable:
    return UserProfileNotesTable(db_path=settings.TURSO_DB_PATH)


def get_user_profile_service(
    table: UserProfileNotesTable = Depends(get_user_profile_notes_table),
) -> UserProfileService:
    return UserProfileService(table=table)


def get_user_conversation_notes_table() -> UserConversationNotesTable:
    return UserConversationNotesTable(db_path=settings.TURSO_DB_PATH)


def get_user_conversation_note_embeddings_table() -> UserConversationNoteEmbeddingsTable:
    # get_embedder returns the process-wide singleton: this factory runs on
    # every tool call and must never construct a model of its own.
    return UserConversationNoteEmbeddingsTable(
        db_path=settings.TURSO_DB_PATH, embedder=get_embedder()
    )


def get_user_conversation_notes_service(
    table: UserConversationNotesTable = Depends(get_user_conversation_notes_table),
    embeddings_table: UserConversationNoteEmbeddingsTable = Depends(
        get_user_conversation_note_embeddings_table
    ),
) -> UserConversationNotesService:
    return UserConversationNotesService(table=table, embeddings_table=embeddings_table)



def get_agent_reminder_service() -> AgentReminderService:
    table = AgentRemindersTable(db_path=settings.TURSO_DB_PATH)
    return TursoAgentReminderService(table=table)


def get_agent_workflows_table() -> AgentWorkflowsTable:
    return AgentWorkflowsTable(db_path=settings.TURSO_DB_PATH)


def get_agent_workflow_service(
    table: AgentWorkflowsTable = Depends(get_agent_workflows_table),
) -> AgentWorkflowService:
    return TursoAgentWorkflowService(table=table)


def get_workflow_results_table() -> WorkflowResultsTable:
    return WorkflowResultsTable(db_path=settings.TURSO_DB_PATH)


def get_workflow_result_service(
    table: WorkflowResultsTable = Depends(get_workflow_results_table),
    workflows_table: AgentWorkflowsTable = Depends(get_agent_workflows_table),
) -> WorkflowResultService:
    return TursoWorkflowResultService(table=table, workflows_table=workflows_table)


def get_holdings_table() -> HoldingsTable:
    return HoldingsTable(db_path=settings.TURSO_DB_PATH)


def get_holdings_service(
    table: HoldingsTable = Depends(get_holdings_table),
) -> HoldingsService:
    return HoldingsService(table=table)


def get_ticker_records_table() -> TickerRecordsTable:
    return TickerRecordsTable(db_path=settings.TURSO_DB_PATH)


def get_ticker_records_service(
    table: TickerRecordsTable = Depends(get_ticker_records_table),
) -> TickerRecordsService:
    return TickerRecordsService(table=table)


mcp_app = FastMCP("InvestPal MCP Server", lifespan=db_lifespan)
mcp_app.add_middleware(LoggingMiddleware())


@mcp_app.tool(
    name="createUserProfileNote",
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
        "skills, not here. Notes are append-only: when a fact stops being true call "
        "markUserProfileNoteAsOutdated and add a replacement."
    ),
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
    name="searchUserConversationNotes",
    description=(
        "Search past conversation notes by meaning rather than by date. Pass a "
        "natural-language description of what you are trying to recall and this "
        "returns the most semantically similar notes, each with a similarity score. "
        "Prefer this over getUserConversationNotes whenever you are looking for a "
        "specific topic rather than simply reviewing the latest notes."
    ),
)
async def search_user_conversation_notes(
    query: Annotated[
        str,
        "A natural-language description of what to recall, for example 'the client's view on pension allocation'. Full sentences work better than keywords.",
    ],
    limit: Annotated[
        int, "Maximum number of notes to return, most similar first. Defaults to 5."
    ] = 5,
    min_similarity: Annotated[
        float | None,
        "Optional 0.0-1.0 similarity floor. Leave unset unless you specifically want to drop weak matches; scores are relative, so it is usually better to read them and judge.",
    ] = None,
    user_conversation_notes_service: UserConversationNotesService = Depends(
        get_user_conversation_notes_service
    ),
) -> list[UserConversationNoteSearchResult]:
    return await user_conversation_notes_service.search_user_conversation_notes(
        query=query,
        limit=limit,
        min_similarity=min_similarity,
    )


@mcp_app.tool(
    name="createUserConversationNote",
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
    name="getHoldings",
    description=(
        "What the client owns: broker positions, cash, fixed income and anything "
        "held off-platform. Read this before any portfolio review, allocation "
        "question or position-sizing decision. Rows whose source is a broker are a "
        "CACHE of that broker's own record: when the broker's tools are available, "
        "call them and refresh with upsertHolding rather than trusting what is "
        "stored here. When they are not available, this is the best record there is, "
        "but every figure must be quoted with its as_of date rather than presented "
        "as current. Market prices, market values and P&L are never stored here; "
        "fetch those live."
    ),
)
async def get_holdings(
    include_closed: Annotated[
        bool, "Include positions that have been closed. Defaults to False."
    ] = False,
    holdings_service: HoldingsService = Depends(get_holdings_service),
) -> list[Holding]:
    return await holdings_service.get_holdings(include_closed=include_closed)


@mcp_app.tool(
    name="upsertHolding",
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
    name: Annotated[
        str,
        "What the position is: a ticker like 'NVDA', or a description like 'Bank cash'. Part of the holding's identity, so reuse it exactly when refreshing.",
    ],
    kind: Annotated[
        str | None,
        "cash | fixed_income | equity | etf | crypto | private_equity | other. Required when creating.",
    ] = None,
    ticker: Annotated[str | None, "Exchange ticker, when the holding has one"] = None,
    quantity: Annotated[float | None, "Shares or units held"] = None,
    cost_basis: Annotated[float | None, "Average cost per unit, in `currency`"] = None,
    amount: Annotated[
        float | None,
        "Total value, for holdings with no unit price such as a cash balance or a bill's face value. Not a market value.",
    ] = None,
    currency: Annotated[str | None, "ISO currency code, e.g. 'EUR', 'USD'"] = None,
    custodian: Annotated[
        str | None,
        "Who holds it: 'Interactive Brokers', 'Coinbase', 'Sophic', 'Bank', 'Carta'. Part of the holding's identity.",
    ] = None,
    source: Annotated[
        str | None,
        "manual | interactive_brokers | coinbase | alpaca. Required when creating. Use the broker you actually read the figures from.",
    ] = None,
    as_of: Annotated[
        str | None,
        "YYYY-MM-DD, the date these figures were true. Required when creating, and should be updated on every refresh.",
    ] = None,
    detail: Annotated[
        str | None,
        "Facts the columns do not carry: interest rate, maturity, vesting, strike. Not theses or price targets.",
    ] = None,
    holdings_service: HoldingsService = Depends(get_holdings_service),
) -> Holding:
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


@mcp_app.tool(
    name="closeHolding",
    description=(
        "Mark a position as closed once it is fully sold, matured or otherwise gone. "
        "It keeps its cost basis and history and stops appearing in getHoldings. "
        "Do not use this to correct a mistake; upsertHolding with the right figures."
    ),
)
async def close_holding(
    holding_id: Annotated[str, "The id of the holding to close"],
    holdings_service: HoldingsService = Depends(get_holdings_service),
) -> str:
    closed = await holdings_service.close_holding(holding_id=holding_id)
    if not closed:
        return f"No open holding with id {holding_id}"
    return f"Holding {holding_id} closed successfully"


@mcp_app.tool(
    name="getTickerRecords",
    description=(
        "The names being tracked and why: thesis, entry trigger, falsifier and "
        "status. This is the watchlist and the conviction record in one. Read it "
        "before screening a new idea (to check overlap with what is already tracked) "
        "and during a portfolio review (to check whether any entry trigger has "
        "fired). Holdings answer what is owned and how much; these answer why, and "
        "at what price to act."
    ),
)
async def get_ticker_records(
    status: Annotated[
        str | None,
        "Filter by watching | held | exited | rejected. Omit to return everything.",
    ] = None,
    ticker_records_service: TickerRecordsService = Depends(get_ticker_records_service),
) -> list[TickerRecord]:
    return await ticker_records_service.get_ticker_records(status=status)


@mcp_app.tool(
    name="upsertTickerRecord",
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
    ticker: Annotated[str, "Exchange ticker, e.g. 'LHX', 'ENR.DE', '7011.T'"],
    status: Annotated[
        str | None,
        "watching | held | exited | rejected. Required when creating a new record.",
    ] = None,
    thesis: Annotated[
        str | None, "Why this name is interesting: the business and the structural case"
    ] = None,
    entry_trigger: Annotated[
        str | None,
        "The condition that would make this a buy, checkable against live data, e.g. 'limit $238,22 or below'",
    ] = None,
    falsifier: Annotated[
        str | None, "What would prove the thesis wrong and take this off the list"
    ] = None,
    notes: Annotated[
        str | None, "Anything else durable about the name the other fields do not hold"
    ] = None,
    ticker_records_service: TickerRecordsService = Depends(get_ticker_records_service),
) -> TickerRecord:
    return await ticker_records_service.upsert_ticker_record(
        ticker=ticker,
        status=status,
        thesis=thesis,
        entry_trigger=entry_trigger,
        falsifier=falsifier,
        notes=notes,
    )


@mcp_app.tool(
    name="deleteTickerRecord",
    description=(
        "Permanently remove a ticker record. Prefer setting status to 'rejected' or "
        "'exited' instead: why a name was turned down is worth keeping, and stops it "
        "being re-screened from scratch. Use this only for a record created by mistake."
    ),
)
async def delete_ticker_record(
    ticker: Annotated[str, "The ticker whose record should be deleted"],
    ticker_records_service: TickerRecordsService = Depends(get_ticker_records_service),
) -> str:
    deleted = await ticker_records_service.delete_ticker_record(ticker=ticker)
    if not deleted:
        return f"No ticker record found for {ticker}"
    return f"Ticker record {ticker} deleted successfully"


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
