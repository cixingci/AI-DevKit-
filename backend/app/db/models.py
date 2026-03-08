from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from sqlalchemy import UniqueConstraint
import sqlalchemy as sa
from typing import Optional, List, Any, Dict
from datetime import datetime

# ========== 项目管理 ==========

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # 关联
    cards: List["Card"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    workflows: List["Workflow"] = Relationship(back_populates="project")

# ========== 卡片系统 ==========

class CardType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    model_name: Optional[str] = Field(default=None, index=True)  # 兼容旧的模型名称
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Schema定义
    json_schema: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # AI配置
    ai_params: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    default_ai_context_template: Optional[str] = None
    
    # UI配置
    editor_component: Optional[str] = None  # 自定义编辑器组件
    ui_layout: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # 系统配置
    is_ai_enabled: bool = Field(default=True)
    is_singleton: bool = Field(default=False)  # 单例限制（如每个项目只能有一个概览卡片）
    built_in: bool = Field(default=False)  # 是否内置类型
    
    # 关联
    cards: List["Card"] = Relationship(back_populates="card_type")

class Card(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    model_name: Optional[str] = Field(default=None, index=True)
    
    # 卡片内容（JSON格式）
    content: Any = Field(default={}, sa_column=Column(JSON))
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # 树形结构
    parent_id: Optional[int] = Field(default=None, foreign_key="card.id")
    parent: Optional["Card"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "[Card.id]"}
    )
    children: List["Card"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "cascade": "all, delete, delete-orphan",
            "single_parent": True,
        },
    )
    display_order: int = Field(default=1)  # 用于排序
    
    # 项目外键
    project_id: int = Field(foreign_key="project.id")
    project: "Project" = Relationship(back_populates="cards")
    
    # 卡片类型外键
    card_type_id: int = Field(foreign_key="cardtype.id")
    card_type: "CardType" = Relationship(back_populates="cards")
    
    # 自定义Schema和AI参数
    json_schema: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    ai_params: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    ai_context_template: Optional[str] = Field(default=None)
    
    # AI处理状态
    ai_generated: bool = Field(default=False)  # 是否AI生成
    needs_review: bool = Field(default=False)  # 需要人工审核
    last_modified_by: Optional[str] = Field(default=None)  # 'user' | 'ai' | 'system'
    
    # 版本控制
    version: int = Field(default=1)

# ========== AI 模型配置 ==========

class LLMConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    provider: str = Field(index=True)  # openai, anthropic, etc.
    display_name: Optional[str] = None
    model_name: str
    api_base: Optional[str] = None
    api_key: str
    base_url: Optional[str] = None
    
    # 统计信息
    token_limit: int = Field(default=-1, sa_column=Column(sa.Integer, nullable=False, server_default='-1'))
    call_limit: int = Field(default=-1, sa_column=Column(sa.Integer, nullable=False, server_default='-1'))
    used_tokens_input: int = Field(default=0, sa_column=Column(sa.Integer, nullable=False, server_default='0'))
    used_tokens_output: int = Field(default=0, sa_column=Column(sa.Integer, nullable=False, server_default='0'))
    used_calls: int = Field(default=0, sa_column=Column(sa.Integer, nullable=False, server_default='0'))
    
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

# ========== 提示词管理 ==========

class Prompt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    template: str
    version: int = 1
    built_in: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

# ========== 工作流系统 ==========

class Workflow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    dsl_version: int = Field(default=2)  # 2=代码式工作流
    is_built_in: bool = Field(default=False)
    is_active: bool = Field(default=True)
    
    # 工作流定义
    definition_code: str = Field(default="")
    
    # 模板信息
    is_template: bool = Field(default=False)
    template_category: Optional[str] = None
    
    # 运行策略
    keep_run_history: bool = Field(default=False)
    max_execution_time: Optional[int] = None
    
    # 触发器缓存
    triggers_cache: Optional[List[dict]] = Field(default=None, sa_column=Column(JSON))
    
    # 关联
    project_id: int = Field(foreign_key="project.id")
    project: "Project" = Relationship(back_populates="workflows")
    runs: List["WorkflowRun"] = Relationship(back_populates="workflow", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

class WorkflowRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: int = Field(foreign_key="workflow.id")
    workflow: Workflow = Relationship(back_populates="runs")
    
    definition_version: int = Field(default=1)
    status: str = Field(default="queued", index=True)  # queued, running, succeeded, failed, cancelled, paused, timeout
    
    # 执行数据
    scope_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    params_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    state_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    error_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    summary_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # 时间控制
    idempotency_key: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # 关联
    node_states: List["NodeExecutionState"] = Relationship(back_populates="run", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class NodeExecutionState(SQLModel, table=True):
    __tablename__ = "nodeexecutionstate"
    __table_args__ = (
        UniqueConstraint('run_id', 'node_id', name='uq_run_node'),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="workflowrun.id", index=True)
    run: WorkflowRun = Relationship(back_populates="node_states")
    
    node_id: str = Field(index=True)
    node_type: str
    
    # 执行状态
    status: str = Field(default="idle", index=True)  # idle, pending, running, success, error, skipped
    progress: int = Field(default=0)  # 0-100
    
    # 时间
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # 输出和错误
    outputs_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    error_message: Optional[str] = None
    
    # 检查点数据
    checkpoint_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

# ========== 知识图谱 ==========

class KnowledgeItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    content: str
    category: str = Field(index=True)
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    built_in: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

# ========== 关系表 ==========

class CardRelation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_card_id: int = Field(foreign_key="card.id")
    target_card_id: int = Field(foreign_key="card.id")
    relation_type: str = Field(index=True)  # depends_on, related_to, etc.
    card_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
# ========== Pydantic Schemas ==========

class CardCreate(SQLModel):
    title: str
    card_type_id: int
    description: Optional[str] = None
    content: Optional[dict] = None
    parent_id: Optional[int] = None
    display_order: int = 0
    project_id: Optional[int] = None

class CardUpdate(SQLModel):
    title: Optional[str] = None
    card_type_id: Optional[int] = None
    description: Optional[str] = None
    content: Optional[dict] = None
    parent_id: Optional[int] = None
    display_order: Optional[int] = None

class ProjectCreate(SQLModel):
    name: str
    description: Optional[str] = None

class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
