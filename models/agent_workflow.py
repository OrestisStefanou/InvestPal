from pydantic import BaseModel, Field


class AgentWorkflow(BaseModel):
    workflow_id: str = Field(description="Unique id of the workflow")
    user_id: str = Field(description="The user this workflow belongs to")
    name: str = Field(description="Human-readable name for the workflow")
    instructions: str = Field(description="The instructions the agent will execute on each run")
    schedule: str = Field(description="Cron expression, e.g. '0 0 1 * *' for monthly")
    status: str = Field(description="'active' or 'paused'")
    created_at: str = Field(description="ISO 8601 creation timestamp")
    last_run_at: str | None = Field(default=None, description="ISO 8601 timestamp of last run")
    next_run_at: str | None = Field(default=None, description="ISO 8601 timestamp of next scheduled run")


class WorkflowResult(BaseModel):
    result_id: str = Field(description="Unique id of this result")
    workflow_id: str = Field(description="The workflow that produced this result")
    user_id: str = Field(description="The user this result belongs to")
    workflow_name: str = Field(description="Name of the workflow at time of execution")
    output: str = Field(description="The agent's report for this run")
    ran_at: str = Field(description="ISO 8601 timestamp of when the workflow ran")
