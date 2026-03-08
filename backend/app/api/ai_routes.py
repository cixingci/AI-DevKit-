from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.db.models import LLMConfig
from app.schemas import LLMConfigCreate, LLMConfigUpdate, ResponseModel
from app.services.ai_service import AIManager

router = APIRouter(prefix="/ai/llm", tags=["LLM配置"])

def get_ai_manager(db: Session = Depends(get_db)) -> AIManager:
    """获取AI管理器实例"""
    return AIManager(db)

@router.post("/configs", response_model=ResponseModel)
async def create_llm_config(
    config_data: LLMConfigCreate,
    db: Session = Depends(get_db),
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """创建LLM配置"""
    try:
        # 创建配置
        config = LLMConfig(
            **config_data.dict(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(config)
        db.commit()
        db.refresh(config)

        return ResponseModel(
            success=True,
            message="LLM配置创建成功",
            data={"id": config.id}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configs", response_model=List[LLMConfig])
async def list_llm_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取LLM配置列表"""
    statement = select(LLMConfig).offset(skip).limit(limit).order_by(LLMConfig.created_at.desc())
    configs = db.exec(statement).all()
    return configs

@router.get("/configs/{config_id}", response_model=LLMConfig)
async def get_llm_config(config_id: int, db: Session = Depends(get_db)):
    """获取LLM配置详情"""
    config = db.get(LLMConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config

@router.put("/configs/{config_id}", response_model=ResponseModel)
async def update_llm_config(
    config_id: int,
    config_data: LLMConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新LLM配置"""
    config = db.get(LLMConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    update_data = config_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    config.updated_at = datetime.now()

    db.add(config)
    db.commit()
    db.refresh(config)

    return ResponseModel(
        success=True,
        message="LLM配置更新成功",
        data={"id": config.id}
    )

@router.delete("/configs/{config_id}", response_model=ResponseModel)
async def delete_llm_config(config_id: int, db: Session = Depends(get_db)):
    """删除LLM配置"""
    config = db.get(LLMConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    db.delete(config)
    db.commit()

    return ResponseModel(
        success=True,
        message="LLM配置删除成功",
        data={}
    )

@router.post("/configs/{config_id}/test", response_model=ResponseModel)
async def test_llm_config(config_id: int, db: Session = Depends(get_db)):
    """测试LLM配置连接"""
    config = db.get(LLMConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    try:
        ai_manager = AIManager(db)
        ai_manager.get_service(config_id)

        return ResponseModel(
            success=True,
            message="LLM配置测试成功",
            data={"config_id": config_id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"测试失败: {str(e)}")

@router.post("/generate", response_model=ResponseModel)
async def generate_content(
    prompt: str,
    context: Optional[dict] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    llm_config_id: Optional[int] = None,
    db: Session = Depends(get_db),
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """使用AI生成内容"""
    try:
        result = ai_manager.generate(prompt, context, temperature, max_tokens, llm_config_id)

        return ResponseModel(
            success=True,
            message="生成成功",
            data=result.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))