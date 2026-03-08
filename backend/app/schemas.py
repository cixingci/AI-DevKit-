from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
from datetime import datetime

# ========== 项目相关Schema ==========

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

# ========== 卡片类型相关Schema ==========

class CardTypeCreate(BaseModel):
    """创建卡片类型"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    json_schema: dict = Field(..., description="JSON Schema格式")

class CardTypeUpdate(BaseModel):
    """更新卡片类型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    json_schema: Optional[dict] = Field(None, description="JSON Schema格式")

# ========== 卡片相关Schema ==========

class CardCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: Dict[str, Any] = Field(default_factory=dict)
    project_id: int = Field(..., description="项目ID")
    card_type_id: Optional[int] = None
    parent_id: Optional[int] = None
    display_order: int = Field(default=1)
    ai_params: Optional[Dict[str, Any]] = None
    ai_context_template: Optional[str] = None

class CardUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[Dict[str, Any]] = None
    json_schema: Optional[Dict[str, Any]] = None
    ai_params: Optional[Dict[str, Any]] = None
    ai_context_template: Optional[str] = None
    display_order: Optional[int] = None
    card_type_id: Optional[int] = None
    parent_id: Optional[int] = None

class CardResponse(BaseModel):
    id: int
    title: str
    content: Dict[str, Any]
    card_type_id: Optional[int]
    parent_id: Optional[int]
    display_order: int
    ai_params: Optional[Dict[str, Any]]
    ai_generated: bool
    needs_review: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ========== AI相关Schema ==========

class LLMConfigCreate(BaseModel):
    provider: str = Field(..., pattern="^(openai|anthropic|google|local)$")
    display_name: Optional[str] = None
    model_name: str
    api_base: Optional[str] = None
    api_key: str
    base_url: Optional[str] = None

class LLMConfigUpdate(BaseModel):
    display_name: Optional[str] = None
    model_name: Optional[str] = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None

class AIGenerateRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1, le=4000)
    llm_config_id: Optional[int] = None

class AIGenerateResponse(BaseModel):
    content: str
    model: str
    usage: Dict[str, int]
    token_count: int

# ========== 提示词管理相关Schema ==========

class PromptCreate(BaseModel):
    name: str = Field(..., unique=True)
    description: Optional[str] = None
    template: str

class PromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template: Optional[str] = None

# ========== 工作流相关Schema ==========

class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    definition_code: str = Field(...)
    project_id: int

class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    definition_code: Optional[str] = None
    is_active: Optional[bool] = None

class WorkflowExecuteRequest(BaseModel):
    params: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: Optional[str] = None

class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    progress: int
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ========== 知识图谱相关Schema ==========

class KnowledgeItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    content: str
    category: str
    tags: Optional[List[str]] = None

class KnowledgeItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

# ========== 响应模型 ==========

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
