from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from sqlalchemy import update as sa_update
from datetime import datetime

from app.db.models import Card, CardType, Card as CardModel, Project
from app.schemas import CardCreate, CardUpdate

class CardService:
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_default_content(self, json_schema: dict) -> dict:
        """根据 JSON Schema 生成默认内容"""
        default_content = {}
        
        if not json_schema:
            return default_content
        
        properties = json_schema.get('properties', {})
        
        for field_name, field_schema in properties.items():
            if 'default' in field_schema:
                default_content[field_name] = field_schema['default']
            elif field_schema.get('type') == 'string':
                if 'enum' in field_schema:
                    # 枚举类型使用第一个选项作为默认值
                    default_content[field_name] = field_schema['enum'][0] if field_schema['enum'] else ''
                else:
                    default_content[field_name] = field_schema.get('example', '')
            elif field_schema.get('type') == 'number' or field_schema.get('type') == 'integer':
                default_content[field_name] = field_schema.get('default', 0)
            elif field_schema.get('type') == 'boolean':
                default_content[field_name] = field_schema.get('default', False)
            elif field_schema.get('type') == 'array':
                default_content[field_name] = field_schema.get('default', [])
            elif field_schema.get('type') == 'object':
                default_content[field_name] = field_schema.get('default', {})
            else:
                default_content[field_name] = ''
        
        return default_content
    
    def get_card(self, card_id: int) -> Optional[CardModel]:
        """获取卡片"""
        return self.db.get(Card, card_id)
    
    def create_card(self, card_create: CardCreate, project_id: Optional[int] = None) -> CardModel:
        """创建卡片"""
        # 如果参数中有project_id，使用参数的值
        # 否则使用CardCreate对象中定义的值
        if project_id is not None:
            card_create.project_id = project_id
        else:
            # 如果没有传递project_id参数，使用CardCreate对象中的project_id
            # CardCreate schema中project_id是必填的，所以这里肯定有值
            if not card_create.project_id:
                raise ValueError("CardCreate must have a project_id")
        
        # 验证卡片类型并获取默认内容
        default_content = {}
        if card_create.card_type_id:
            card_type = self.db.get(CardType, card_create.card_type_id)
            if not card_type:
                raise ValueError(f"CardType with id {card_create.card_type_id} not found")
            
            # 根据卡片类型的 JSON Schema 生成默认内容
            if card_type.json_schema:
                default_content = self._generate_default_content(card_type.json_schema)
            
            # 如果用户没有提供内容，使用默认内容
            if not card_create.content:
                card_create.content = default_content
            else:
                # 合并默认内容和用户内容
                card_create.content = {**default_content, **card_create.content}
            
            # 单例限制检查
            if card_type.is_singleton:
                existing = self.db.exec(
                    select(Card).where(
                        Card.project_id == card_create.project_id,
                        Card.card_type_id == card_create.card_type_id
                    )
                ).first()
                if existing:
                    raise ValueError(f"A singleton card of type '{card_type.name}' already exists")
        
        # 确定显示顺序
        if card_create.parent_id is not None:
            parent_card = self.db.get(Card, card_create.parent_id)
            if not parent_card:
                raise ValueError(f"Parent card with id {card_create.parent_id} not found")
            
            statement = select(Card).where(
                Card.project_id == card_create.project_id,
                Card.parent_id == card_create.parent_id
            )
            siblings = self.db.exec(statement).all()
            card_create.display_order = len(siblings)
        else:
            statement = select(Card).where(
                Card.project_id == card_create.project_id,
                Card.parent_id.is_(None)
            )
            siblings = self.db.exec(statement).all()
            card_create.display_order = len(siblings)
        
        # 创建卡片
        card_data = card_create.dict(exclude_unset=True)
        card = Card(**card_data)
        
        self.db.add(card)
        self.db.commit()
        self.db.refresh(card)
        return card
    
    def update_card(self, card_id: int, card_update: CardUpdate) -> Optional[CardModel]:
        """更新卡片"""
        card = self.db.get(Card, card_id)
        if not card:
            return None
        
        update_data = card_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(card, key, value)
        
        card.updated_at = datetime.now()
        self.db.add(card)
        self.db.commit()
        self.db.refresh(card)
        return card
    
    def delete_card(self, card_id: int) -> bool:
        """删除卡片"""
        card = self.db.get(Card, card_id)
        if not card:
            return False
        
        # 删除所有子卡片
        self._delete_subtree(card)
        
        self.db.delete(card)
        self.db.commit()
        return True
    
    def _delete_subtree(self, card: CardModel):
        """递归删除子树"""
        children = self.db.exec(
            select(Card).where(Card.parent_id == card.id)
        ).all()
        
        for child in children:
            self._delete_subtree(child)
            self.db.delete(child)
    
    def list_cards(self, project_id: Optional[int] = None, card_type: Optional[str] = None, 
                   parent_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[CardModel]:
        """获取卡片列表"""
        statement = select(Card)
        
        if project_id:
            statement = statement.where(Card.project_id == project_id)
        
        if card_type:
            statement = statement.join(CardType).where(CardType.name == card_type)
        
        if parent_id is not None:
            statement = statement.where(Card.parent_id == parent_id)
        else:
            statement = statement.where(Card.parent_id.is_(None))
        
        statement = statement.offset(skip).limit(limit).order_by(Card.display_order)
        return self.db.exec(statement).all()
    
    def get_card_children(self, card_id: int) -> List[CardModel]:
        """获取子卡片"""
        statement = select(Card).where(Card.parent_id == card_id).order_by(Card.display_order)
        return self.db.exec(statement).all()
    
    def move_card(self, card_id: int, new_parent_id: Optional[int], new_order: int) -> bool:
        """移动卡片"""
        card = self.db.get(Card, card_id)
        if not card:
            return False
        
        # 更新父级
        if new_parent_id != card.parent_id:
            card.parent_id = new_parent_id
            
            # 重新计算显示顺序
            if new_parent_id:
                statement = select(Card).where(
                    Card.project_id == card.project_id,
                    Card.parent_id == new_parent_id
                ).order_by(Card.display_order)
            else:
                statement = select(Card).where(
                    Card.project_id == card.project_id,
                    Card.parent_id.is_(None)
                ).order_by(Card.display_order)
            
            siblings = self.db.exec(statement).all()
            
            # 插入到新位置
            for i, sibling in enumerate(siblings):
                if i == new_order:
                    card.display_order = sibling.display_order
                    break
                elif i > new_order:
                    sibling.display_order += 1
                    self.db.add(sibling)
        
        card.display_order = new_order
        self.db.add(card)
        self.db.commit()
        return True
    
    def get_card_tree(self, project_id: int) -> List[CardModel]:
        """获取项目卡片树"""
        # 获取所有根卡片
        roots = self.db.exec(
            select(Card).where(
                Card.project_id == project_id,
                Card.parent_id.is_(None)
            ).order_by(Card.display_order)
        ).all()
        
        # 构建树结构
        def build_tree(node: CardModel) -> CardModel:
            node.children = self.get_card_children(node.id)
            for child in node.children:
                build_tree(child)
            return node
        
        for root in roots:
            build_tree(root)
        
        return roots
    
    def search_cards(self, project_id: int, query: str) -> List[CardModel]:
        """搜索卡片"""
        statement = select(Card).where(Card.project_id == project_id)
        
        # 在标题和内容中搜索
        from sqlalchemy import or_
        statement = statement.where(
            or_(
                Card.title.ilike(f"%{query}%"),
                Card.content.ilike(f"%{query}%")
            )
        )
        
        return self.db.exec(statement).all()
    
    def get_card_relations(self, card_id: int) -> Dict[str, List[CardModel]]:
        """获取卡片关系"""
        from app.db.models import CardRelation
        
        # 获取作为源头的关系
        outgoing = self.db.exec(
            select(CardRelation).where(CardRelation.source_card_id == card_id)
        ).all()
        
        # 获取作为目标的关系
        incoming = self.db.exec(
            select(CardRelation).where(CardRelation.target_card_id == card_id)
        ).all()
        
        relations = {
            "outgoing": [],
            "incoming": []
        }
        
        for rel in outgoing:
            target_card = self.db.get(Card, rel.target_card_id)
            if target_card:
                relations["outgoing"].append({
                    "relation": rel.relation_type,
                    "card": target_card
                })
        
        for rel in incoming:
            source_card = self.db.get(Card, rel.source_card_id)
            if source_card:
                relations["incoming"].append({
                    "relation": rel.relation_type,
                    "card": source_card
                })
        
        return relations