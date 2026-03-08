from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime

from app.db.session import get_db
from app.db.models import Workflow, WorkflowRun, NodeExecutionState
from app.schemas import WorkflowCreate, WorkflowUpdate, ResponseModel
from app.services.workflow.engine import WorkflowEngine, NodeType
import logging

from app.services.card_service import CardService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/ai/workflows", tags=["工作流管理"])

def get_workflow_engine(db: Session = Depends(get_db)) -> WorkflowEngine:
    """获取工作流引擎实例"""
    return WorkflowEngine(db)

@router.post("/execute", response_model=ResponseModel)
async def execute_workflow(
    workflow_id: int,
    params: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """执行工作流"""
    workflow = db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    try:
        engine = WorkflowEngine(db)
        context_data = {
            "project_id": params.get("project_id") if params else None,
            "card_id": params.get("card_id") if params else None,
            "variables": params.get("variables", {}) if params else {}
        }

        run = engine.execute_workflow(workflow, context_data)

        return ResponseModel(
            success=True,
            message="工作流执行成功",
            data={
                "run_id": run.id,
                "status": run.status,
                "progress": 100
            }
        )
    except Exception as e:
        logger.error(f"工作流执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs", response_model=List[WorkflowRun])
async def list_workflow_runs(
    workflow_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取工作流运行记录"""
    statement = select(WorkflowRun)

    if workflow_id:
        statement = statement.where(WorkflowRun.workflow_id == workflow_id)

    statement = statement.offset(skip).limit(limit).order_by(WorkflowRun.created_at.desc())
    runs = db.exec(statement).all()
    return runs

@router.get("/runs/{run_id}", response_model=WorkflowRun)
async def get_workflow_run(run_id: int, db: Session = Depends(get_db)):
    """获取工作流运行详情"""
    run = db.get(WorkflowRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="运行记录不存在")

    # 加载节点状态
    node_states = db.exec(
        select(NodeExecutionState).where(NodeExecutionState.run_id == run_id)
    ).all()

    run.node_states = node_states
    return run

@router.get("/nodes/{run_id}", response_model=List[NodeExecutionState])
async def get_workflow_node_states(
    run_id: int,
    db: Session = Depends(get_db)
):
    """获取工作流节点状态"""
    statement = select(NodeExecutionState).where(
        NodeExecutionState.run_id == run_id
    ).order_by(NodeExecutionState.created_at)
    states = db.exec(statement).all()
    return states

@router.get("/node-types", response_model=List[str])
async def get_available_node_types():
    """获取可用节点类型"""
    return [node_type.value for node_type in NodeType]

@router.get("/project/{project_id}/initialize", response_model=ResponseModel)
async def initialize_project(
    project_id: int,
    workflow_template: Optional[str] = "project-init",
    db: Session = Depends(get_db)
):
    """使用工作流初始化项目"""
    project_service = ProjectService(db)

    # 查找初始化工作流
    workflow = db.exec(
        select(Workflow).where(
            Workflow.name == workflow_template,
            Workflow.is_active == True
        )
    ).first()

    if not workflow:
        raise HTTPException(
            status_code=404,
            detail=f"工作流模板 '{workflow_template}' 不存在或未激活"
        )

    try:
        engine = WorkflowEngine(db)

        context_data = {
            "project_id": project_id,
            "variables": {
                "project_name": "新项目",  # TODO: 从项目信息获取
                "description": ""
            }
        }

        run = engine.execute_workflow(workflow, context_data)

        return ResponseModel(
            success=True,
            message=f"项目初始化成功，工作流ID: {run.id}",
            data={
                "workflow_id": workflow.id,
                "run_id": run.id,
                "status": run.status
            }
        )
    except Exception as e:
        logger.error(f"项目初始化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_model=dict)
async def get_workflow_statistics(db: Session = Depends(get_db)):
    """获取工作流统计数据"""
    total_workflows = len(db.exec(select(Workflow)).all())
    running_workflows = len(db.exec(
        select(WorkflowRun).where(WorkflowRun.status == "running")
    ).all())

    # 按状态统计运行次数
    status_counts = {}
    runs = db.exec(select(WorkflowRun)).all()
    for run in runs:
        status_counts[run.status] = status_counts.get(run.status, 0) + 1

    return {
        "total_workflows": total_workflows,
        "running_workflows": running_workflows,
        "status_distribution": status_counts
    }