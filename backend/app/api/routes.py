from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import joinedload
from typing import List, Optional
from sqlmodel import Session, select

from app.db.models import Project, Card, CardType
from app.schemas import CardCreate, CardUpdate, ProjectCreate, CardTypeCreate, CardTypeUpdate
from app.db.session import get_db
from app.services.card_service import CardService
from app.services.project_service import ProjectService
from app.services.card_type_service import CardTypeService

router = APIRouter(prefix="/api/v1", tags=["cards"])

# ========== 项目 ==========

@router.post("/projects", response_model=dict)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
):
    """创建新项目"""
    project_service = ProjectService(db)
    project = project_service.create_project(project_data.name, project_data.description)
    return {"id": project.id, "name": project.name, "description": project.description}

@router.get("/projects", response_model=List[dict])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取项目列表"""
    statement = select(Project).offset(skip).limit(limit).order_by(Project.created_at.desc())
    projects = db.exec(statement).all()
    return [{"id": p.id, "name": p.name, "description": p.description, "created_at": p.created_at} for p in projects]

@router.get("/projects/{project_id}", response_model=dict)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """获取项目详情"""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 获取项目下的卡片数量
    card_count = len(db.exec(select(Card).where(Card.project_id == project_id)).all())
    
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "card_count": card_count,
        "created_at": project.created_at,
        "updated_at": project.updated_at
    }

# ========== 卡片类型 ==========

# ========== 卡片 ==========

@router.post("/cards", response_model=dict)
async def create_card(
    card_data: CardCreate,
    db: Session = Depends(get_db)
):
    """创建卡片"""
    card_service = CardService(db)

    # 验证项目存在
    project = db.get(Project, card_data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    card = card_service.create_card(card_data)

    return {
        "id": card.id,
        "title": card.title,
        "card_type_id": card.card_type_id,
        "content": card.content,
        "parent_id": card.parent_id,
        "display_order": card.display_order,
        "project_id": card.project_id,
        "card_type": card.card_type.name if card.card_type else None,
        "created_at": card.created_at.isoformat() if card.created_at else None
    }

@router.get("/cards", response_model=List[dict])
async def list_cards(
    project_id: Optional[int] = None,
    card_type: Optional[str] = None,
    parent_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取卡片列表"""
    statement = select(Card)
    
    # 过滤条件
    if project_id:
        statement = statement.where(Card.project_id == project_id)
    if card_type:
        statement = statement.join(CardType).where(CardType.name == card_type)
    if parent_id is not None:
        statement = statement.where(Card.parent_id == parent_id)
    
    statement = statement.offset(skip).limit(limit).order_by(Card.display_order)
    cards = db.exec(statement).all()
    
    return [
        {
            "id": card.id,
            "title": card.title,
            "content": card.content,
            "card_type": card.card_type.name if card.card_type else None,
            "parent_id": card.parent_id,
            "display_order": card.display_order,
            "created_at": card.created_at,
            "updated_at": card.updated_at
        }
        for card in cards
    ]

@router.get("/cards/tree", response_model=List[dict])
async def get_card_tree(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """获取项目卡片树"""
    card_service = CardService(db)
    tree = card_service.get_card_tree(project_id)
    
    def card_to_dict(card: Card, include_children: bool = True) -> dict:
        card_type_info = None
        if card.card_type:
            card_type_info = {
                "id": card.card_type.id,
                "name": card.card_type.name
            }
        
        result = {
            "id": card.id,
            "title": card.title,
            "content": card.content,
            "card_type_id": card.card_type_id,
            "card_type": card_type_info,
            "parent_id": card.parent_id,
            "display_order": card.display_order,
            "ai_generated": card.ai_generated,
            "created_at": card.created_at.isoformat() if card.created_at else None,
            "updated_at": card.updated_at.isoformat() if card.updated_at else None
        }
        
        # 递归处理子卡片
        if include_children:
            children = card.children if hasattr(card, 'children') else []
            if children:
                result["children"] = [card_to_dict(child, True) for child in children]
        
        return result
    
    return [card_to_dict(root, True) for root in tree]

@router.get("/cards/{card_id}", response_model=dict)
async def get_card(card_id: int, db: Session = Depends(get_db)):
    """获取卡片详情"""
    card = db.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    
    return {
        "id": card.id,
        "title": card.title,
        "content": card.content,
        "card_type_id": card.card_type_id,
        "project_id": card.project_id,
        "card_type": {
            "id": card.card_type.id,
            "name": card.card_type.name,
            "description": card.card_type.description,
            "json_schema": card.card_type.json_schema
        } if card.card_type else None,
        "parent_id": card.parent_id,
        "display_order": card.display_order,
        "ai_params": card.ai_params,
        "ai_generated": card.ai_generated,
        "needs_review": card.needs_review,
        "created_at": card.created_at,
        "updated_at": card.updated_at
    }

@router.put("/cards/{card_id}", response_model=dict)
async def update_card(
    card_id: int,
    card_update: CardUpdate,
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """更新卡片"""
    card_service = CardService(db)

    # 获取卡片信息，验证卡片存在且属于当前项目
    card = db.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")

    # 验证卡片是否属于当前项目
    if card.project_id != project_id:
        raise HTTPException(status_code=403, detail="无权限修改不属于当前项目的卡片")

    card = card_service.update_card(card_id, card_update)
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")

    return {
        "id": card.id,
        "title": card.title,
        "content": card.content,
        "updated_at": card.updated_at
    }

@router.delete("/cards/{card_id}")
async def delete_card(card_id: int, project_id: int = Query(..., description="项目ID"), db: Session = Depends(get_db)):
    """删除卡片"""
    card_service = CardService(db)

    # 获取卡片信息，验证卡片存在且属于当前项目
    card = db.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")

    # 验证卡片是否属于当前项目
    if card.project_id != project_id:
        raise HTTPException(status_code=403, detail="无权限删除不属于当前项目的卡片")

    success = card_service.delete_card(card_id)
    if not success:
        raise HTTPException(status_code=404, detail="卡片不存在")

    return {"message": "删除成功"}

@router.patch("/cards/{card_id}/move")
async def move_card(
    card_id: int,
    new_parent_id: int | None = Query(None, description="新的父卡片ID，null表示移到根级"),
    new_order: int | None = Query(None, description="新的排序位置"),
    db: Session = Depends(get_db)
):
    """移动卡片到新的位置（调整层级或顺序）"""
    card = db.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    
    # 更新父卡片
    if new_parent_id is not None:
        if new_parent_id == 0:
            card.parent_id = None
        else:
            # 验证目标父卡片存在且属于同一项目
            parent_card = db.get(Card, new_parent_id)
            if not parent_card:
                raise HTTPException(status_code=404, detail="父卡片不存在")
            if parent_card.project_id != card.project_id:
                raise HTTPException(status_code=400, detail="不能移动到不同项目的卡片下")
            card.parent_id = new_parent_id
    
    # 更新排序
    if new_order is not None:
        card.display_order = new_order
    
    db.commit()
    
    return {
        "id": card.id,
        "title": card.title,
        "parent_id": card.parent_id,
        "display_order": card.display_order,
        "message": "移动成功"
    }

@router.post("/cards/{card_id}/ai-generate")
async def ai_generate_card(card_id: int, db: Session = Depends(get_db)):
    """AI生成卡片内容"""
    # TODO: 实现AI生成逻辑
    raise HTTPException(status_code=501, detail="AI生成功能尚未实现")

@router.get("/cards/{card_id}/children", response_model=List[dict])
async def get_card_children(
    card_id: int,
    db: Session = Depends(get_db)
):
    """获取子卡片"""
    statement = select(Card).where(Card.parent_id == card_id).order_by(Card.display_order)
    children = db.exec(statement).all()
    
    return [
        {
            "id": child.id,
            "title": child.title,
            "content": child.content,
            "card_type": child.card_type.name if child.card_type else None,
            "display_order": child.display_order
        }
        for child in children
    ]

# ========== 卡片关系 ==========

@router.post("/cards/{source_id}/relations")
async def create_card_relation(
    source_id: int,
    target_id: int,
    relation_type: str,
    db: Session = Depends(get_db)
):
    """创建卡片关系"""
    from app.db.models import CardRelation
    
    # 验证卡片存在
    source_card = db.get(Card, source_id)
    target_card = db.get(Card, target_id)
    if not source_card or not target_card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    
    # 检查是否已存在相同关系
    existing = db.exec(select(CardRelation).where(
        CardRelation.source_card_id == source_id,
        CardRelation.target_card_id == target_id,
        CardRelation.relation_type == relation_type
    )).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="关系已存在")
    
    relation = CardRelation(
        source_card_id=source_id,
        target_card_id=target_id,
        relation_type=relation_type
    )
    db.add(relation)
    db.commit()
    
    return {"message": "关系创建成功"}

@router.get("/cards/{card_id}/relations", response_model=List[dict])
async def get_card_relations(
    card_id: int,
    db: Session = Depends(get_db)
):
    """获取卡片关系"""
    from app.db.models import CardRelation
    
    # 获取卡片作为源头的关系
    outgoing = db.exec(select(CardRelation).where(CardRelation.source_card_id == card_id)).all()
    
    # 获取卡片作为目标的关系
    incoming = db.exec(select(CardRelation).where(CardRelation.target_card_id == card_id)).all()
    
    relations = []
    
    for rel in outgoing:
        target_card = db.get(Card, rel.target_card_id)
        relations.append({
            "id": rel.id,
            "type": rel.relation_type,
            "source": "self",
            "target": {
                "id": target_card.id,
                "title": target_card.title
            } if target_card else None,
            "created_at": rel.created_at
        })
    
    for rel in incoming:
        source_card = db.get(Card, rel.source_card_id)
        relations.append({
            "id": rel.id,
            "type": rel.relation_type,
            "source": {
                "id": source_card.id,
                "title": source_card.title
            } if source_card else None,
            "target": "self",
            "created_at": rel.created_at
        })
    
    return relations
# ========== 卡片类型管理 ==========

@router.get("/card-types", response_model=list[dict])
async def get_card_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取卡片类型列表"""
    statement = select(CardType).offset(skip).limit(limit).order_by(CardType.created_at.desc())
    card_types = db.exec(statement).all()
    return [
        {
            "id": ct.id,
            "name": ct.name,
            "description": ct.description,
            "json_schema": ct.json_schema,
            "created_at": ct.created_at
        }
        for ct in card_types
    ]

@router.get("/card-types/{card_type_id}", response_model=dict)
async def get_card_type(card_type_id: int, db: Session = Depends(get_db)):
    """获取卡片类型详情"""
    card_type = db.get(CardType, card_type_id)
    if not card_type:
        raise HTTPException(status_code=404, detail="卡片类型不存在")
    return {
        "id": card_type.id,
        "name": card_type.name,
        "description": card_type.description,
        "json_schema": card_type.json_schema,
        "created_at": card_type.created_at,
        "updated_at": card_type.updated_at
    }

@router.post("/card-types", response_model=dict)
async def create_card_type(
    card_type: CardTypeCreate,
    db: Session = Depends(get_db)
):
    """创建卡片类型"""
    card_type_obj = CardTypeService.create_card_type(db, card_type)
    return {
        "id": card_type_obj.id,
        "name": card_type_obj.name,
        "description": card_type_obj.description,
        "json_schema": card_type_obj.json_schema,
        "created_at": card_type_obj.created_at
    }

@router.put("/card-types/{card_type_id}", response_model=dict)
async def update_card_type(
    card_type_id: int,
    card_type: CardTypeUpdate,
    db: Session = Depends(get_db)
):
    """更新卡片类型"""
    card_type_obj = CardTypeService.update_card_type(db, card_type_id, card_type)
    return {
        "id": card_type_obj.id,
        "name": card_type_obj.name,
        "description": card_type_obj.description,
        "json_schema": card_type_obj.json_schema,
        "updated_at": card_type_obj.updated_at
    }

@router.delete("/card-types/{card_type_id}")
async def delete_card_type(card_type_id: int, db: Session = Depends(get_db)):
    """删除卡片类型"""
    CardTypeService.delete_card_type(db, card_type_id)
    return {"message": "删除成功"}
