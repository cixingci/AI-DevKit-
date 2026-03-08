from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings
import logging

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # 在调试模式下打印SQL
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

logger = logging.getLogger(__name__)

def create_db_and_tables(drop=False):
    """
    创建数据库和表
    :param drop: 是否删除所有表后重新创建
    """
    try:
        if drop:
            logger.warning("即将删除所有数据表...")
            SQLModel.metadata.drop_all(engine)
            logger.info("所有数据表已删除")

        SQLModel.metadata.create_all(engine)
        logger.info("数据库表创建/检查成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        raise

def get_db():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session