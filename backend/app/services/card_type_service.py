from typing import Optional
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlmodel import SQLModel
import logging

from app.db.models import CardType
from app.schemas import CardTypeCreate, CardTypeUpdate

logger = logging.getLogger(__name__)

class CardTypeService:
    """卡片类型服务"""

    @staticmethod
    def create_card_type(db: Session, card_type: CardTypeCreate) -> CardType:
        """创建卡片类型"""
        db_card_type = CardType(**card_type.model_dump())
        db.add(db_card_type)
        db.commit()
        db.refresh(db_card_type)
        logger.info(f"创建卡片类型成功: {db_card_type.name} (ID: {db_card_type.id})")
        return db_card_type

    @staticmethod
    def get_card_type(db: Session, card_type_id: int) -> Optional[CardType]:
        """获取卡片类型"""
        return db.get(CardType, card_type_id)

    @staticmethod
    def get_card_types(
        db: Session,
        skip: int = 0,
        limit: int = 1000
    ) -> list[CardType]:
        """获取卡片类型列表"""
        statement = select(CardType).offset(skip).limit(limit).order_by(CardType.created_at.desc())
        return db.exec(statement).all()

    @staticmethod
    def update_card_type(
        db: Session,
        card_type_id: int,
        card_type: CardTypeUpdate
    ) -> Optional[CardType]:
        """更新卡片类型"""
        db_card_type = db.get(CardType, card_type_id)
        if not db_card_type:
            return None

        update_data = card_type.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_card_type, key, value)

        db.add(db_card_type)
        db.commit()
        db.refresh(db_card_type)
        logger.info(f"更新卡片类型成功: {db_card_type.name} (ID: {db_card_type.id})")
        return db_card_type

    @staticmethod
    def delete_card_type(db: Session, card_type_id: int) -> bool:
        """删除卡片类型"""
        db_card_type = db.get(CardType, card_type_id)
        if not db_card_type:
            return False

        db.delete(db_card_type)
        db.commit()
        logger.info(f"删除卡片类型成功: {db_card_type.name} (ID: {db_card_type.id})")
        return True

    @staticmethod
    def exists(db: Session, name: str) -> bool:
        """检查卡片类型名称是否存在"""
        statement = select(CardType).where(CardType.name == name)
        return len(db.exec(statement).all()) > 0
