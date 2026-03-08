from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from sqlalchemy import update as sa_update
from datetime import datetime

from app.db.models import Project, CardType
from app.schemas import ProjectCreate, ProjectUpdate

class ProjectService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_project(self, name: str, description: Optional[str] = None) -> Project:
        """创建新项目"""
        project = Project(name=name, description=description)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """获取项目"""
        return self.db.get(Project, project_id)
    
    def update_project(self, project_id: int, update_data: ProjectUpdate) -> Optional[Project]:
        """更新项目"""
        project = self.db.get(Project, project_id)
        if not project:
            return None
        
        update_data_dict = update_data.dict(exclude_unset=True)
        for key, value in update_data_dict.items():
            setattr(project, key, value)
        
        project.updated_at = datetime.now()
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def delete_project(self, project_id: int) -> bool:
        """删除项目"""
        project = self.db.get(Project, project_id)
        if not project:
            return False
        
        self.db.delete(project)
        self.db.commit()
        return True
    
    def list_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """获取项目列表"""
        statement = select(Project).offset(skip).limit(limit).order_by(Project.created_at.desc())
        return self.db.exec(statement).all()
    
    def get_project_count(self) -> int:
        """获取项目总数"""
        statement = select(Project)
        return len(self.db.exec(statement).all())