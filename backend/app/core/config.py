from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 应用设置
    app_name: str = "AI DevKit"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # 数据库设置
    database_url: str = "sqlite:///./devkit.db"
    
    # Neo4j 设置 (可选，用于知识图谱)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    
    # Redis 设置 (用于缓存和任务队列)
    redis_url: str = "redis://localhost:6379"
    
    # AI 模型配置
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    anthropic_api_key: str = ""
    
    # 默认AI模型
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4"
    
    # 工作流设置
    workflow_max_execution_time: int = 3600  # 1小时
    workflow_task_timeout: int = 300  # 5分钟
    
    # 文件上传设置
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"
    
    # 日志设置
    log_level: str = "INFO"
    log_file: str = "logs/devkit.log"

    # 数据库初始化设置
    create_tables: bool = False  # 生产环境设为False，避免每次重启都创建表

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()