import http

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel

from dependencies import (
    get_agent_workflow_service,
    get_workflow_result_service,
    get_workflow_runner,
)
from services.agent_workflows.workflow import (
    AgentWorkflowService,
    AgentWorkflowNotFoundError,
)
from models.agent_workflow import WorkflowStatus
from services.agent_workflows.results import WorkflowResultService
from services.agent_workflows.runner import WorkflowRunner

router = APIRouter(tags=["Agent Workflows"])


class AgentWorkflowSchema(BaseModel):
    workflow_id: str
    name: str
    description: str
    schedule: str
    status: WorkflowStatus
    created_at: str
    last_run_at: str | None = None
    next_run_at: str | None = None


class CreateAgentWorkflowRequest(BaseModel):
    name: str
    description: str
    schedule: str


class UpdateAgentWorkflowRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    schedule: str | None = None
    status: WorkflowStatus | None = None


class WorkflowResultSchema(BaseModel):
    result_id: str
    workflow_id: str
    workflow_name: str
    output: str
    ran_at: str


@router.post("/workflows", response_model=AgentWorkflowSchema, status_code=http.HTTPStatus.CREATED)
async def create_workflow(
    body: CreateAgentWorkflowRequest,
    service: AgentWorkflowService = Depends(get_agent_workflow_service),
):
    workflow = await service.create_workflow(
        name=body.name,
        description=body.description,
        schedule=body.schedule,
    )
    return AgentWorkflowSchema(**workflow.model_dump())


@router.get("/workflows", response_model=list[AgentWorkflowSchema])
async def get_workflows(
    service: AgentWorkflowService = Depends(get_agent_workflow_service),
):
    workflows = await service.get_workflows()
    return [AgentWorkflowSchema(**w.model_dump()) for w in workflows]


@router.patch("/workflows/{workflow_id}", response_model=AgentWorkflowSchema)
async def update_workflow(
    workflow_id: str,
    body: UpdateAgentWorkflowRequest,
    service: AgentWorkflowService = Depends(get_agent_workflow_service),
):
    try:
        workflow = await service.update_workflow(
            workflow_id=workflow_id,
            name=body.name,
            description=body.description,
            schedule=body.schedule,
            status=body.status,
        )
    except AgentWorkflowNotFoundError as e:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=str(e))
    return AgentWorkflowSchema(**workflow.model_dump())


@router.delete("/workflows/{workflow_id}", status_code=http.HTTPStatus.NO_CONTENT)
async def delete_workflow(
    workflow_id: str,
    service: AgentWorkflowService = Depends(get_agent_workflow_service),
):
    try:
        await service.delete_workflow(workflow_id=workflow_id)
    except AgentWorkflowNotFoundError as e:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=str(e))


@router.post("/workflows/check-and-run", status_code=http.HTTPStatus.ACCEPTED)
async def check_and_run_workflows(
    background_tasks: BackgroundTasks,
    runner: WorkflowRunner = Depends(get_workflow_runner),
):
    """Heartbeat endpoint called by an external cron job. Runs all due workflows asynchronously."""
    background_tasks.add_task(runner.run_due_workflows)


@router.get("/workflow_results", response_model=list[WorkflowResultSchema])
async def get_workflow_results(
    limit: int = 10,
    service: WorkflowResultService = Depends(get_workflow_result_service),
):
    results = await service.get_results(limit=limit)
    return [WorkflowResultSchema(**r.model_dump()) for r in results]
