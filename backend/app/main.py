from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import create_db_and_tables, engine
from app.api import routes, ai_routes, workflow_routes
import logging

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("启动AI DevKit...")

    # 检查是否需要创建表（开发环境每次重启都创建，生产环境避免重复创建）
    create_tables = getattr(settings, 'create_tables', False)

    if create_tables:
        logger.info("开发模式：初始化数据库表...")
        create_db_and_tables()
        logger.info("数据库表创建成功")
    else:
        logger.info("生产模式：跳过数据库表创建（使用现有表）")
        # 检查表是否存在
        from app.db.models import SQLModel
        if hasattr(SQLModel.metadata, 'tables'):
            logger.info(f"数据库表状态：{len(SQLModel.metadata.tables)} 个表已存在")
        else:
            logger.warning("警告：未找到任何数据表，请检查数据库配置")

    yield
    # 关闭时执行
    engine.dispose()
    logger.info("AI DevKit已停止")

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI驱动的卡片式编程开发工具",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(routes.router)
app.include_router(ai_routes.router)
app.include_router(workflow_routes.router)

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "message": "欢迎使用AI DevKit - 卡片式编程开发工具",
        "docs": "/docs",
        "api": "/api/v1"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.app_version
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )