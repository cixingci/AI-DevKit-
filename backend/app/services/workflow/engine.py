import re
import logging
import ast
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
from dataclasses import dataclass, field
from sqlmodel import Session, select
from datetime import datetime

from app.db.models import Workflow, WorkflowRun, NodeExecutionState, Card
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class NodeType(Enum):
    """节点类型"""
    # 逻辑节点
    LOGIC = "Logic"
    WAIT = "Wait"
    CONDITION = "Condition"

    # 卡片节点
    CARD_CREATE = "Card.Create"
    CARD_UPDATE = "Card.Update"
    CARD_READ = "Card.Read"
    CARD_DELETE = "Card.Delete"
    CARD_BATCH = "Card.BatchUpsert"

    # 项目节点
    PROJECT_CREATE = "Project.Create"
    PROJECT_UPDATE = "Project.Update"
    PROJECT_DELETE = "Project.Delete"

    # 触发器节点
    TRIGGER = "Trigger"

    # 工作流节点
    WORKFLOW_RUN = "Workflow.Run"

    # 代码节点
    EXPRESSION = "Expression"

@dataclass
class WorkflowContext:
    """工作流上下文"""
    variables: Dict[str, Any] = field(default_factory=dict)
    project_id: Optional[int] = None
    card_id: Optional[int] = None
    previous_results: Dict[str, Any] = field(default_factory=dict)

class WorkflowEngine:
    """工作流引擎"""

    def __init__(self, db: Session):
        self.db = db
        self.context = None

    def execute_workflow(self, workflow: Workflow, context_data: Dict[str, Any]) -> WorkflowRun:
        """执行工作流"""
        logger.info(f"开始执行工作流: {workflow.name}")

        # 创建运行记录
        run = WorkflowRun(
            workflow_id=workflow.id,
            status="running",
            scope_json=context_data,
            params_json={}
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        # 初始化上下文
        self.context = WorkflowContext(
            variables=context_data.get("variables", {}),
            project_id=context_data.get("project_id"),
            card_id=context_data.get("card_id")
        )

        try:
            # 解析和执行工作流定义
            self._parse_and_execute(workflow.definition_code, run.id)

            run.status = "succeeded"
            run.finished_at = datetime.now()

        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            run.status = "failed"
            run.error_json = {"error": str(e)}
            run.finished_at = datetime.now()

        finally:
            self.db.add(run)
            self.db.commit()

            # 清理上下文
            self.context = None

        return run

    def _parse_and_execute(self, code: str, run_id: int):
        """解析并执行工作流代码"""
        # 提取所有节点
        nodes = self._extract_nodes(code)

        for node in nodes:
            try:
                # 创建节点状态
                node_state = self._create_node_state(run_id, node)
                node_state.status = "running"
                node_state.start_time = datetime.now()
                self.db.add(node_state)
                self.db.commit()

                # 执行节点
                result = self._execute_node(node, node_state)
                node_state.outputs_json = {"result": result}
                node_state.status = "success"
                node_state.progress = 100
                node_state.end_time = datetime.now()

                self.db.add(node_state)
                self.db.commit()

            except Exception as e:
                logger.error(f"执行节点失败: {node.get('description', 'Unknown')}: {e}")
                self._update_node_state_error(run_id, node["name"], str(e))
                raise

    def _extract_nodes(self, code: str) -> List[Dict[str, Any]]:
        """从工作流代码中提取节点"""
        nodes = []
        pattern = r'#@node\s*\(\s*description\s*=\s*["\'](.*?)["\']\s*\)\s*\n\s*([^#]+)\n\s*#</node>'

        matches = re.findall(pattern, code, re.MULTILINE | re.DOTALL)

        for description, content in matches:
            node = {
                "name": self._extract_node_name(content),
                "description": description.strip(),
                "content": content.strip(),
                "parameters": self._extract_parameters(content)
            }
            nodes.append(node)

        return nodes

    def _extract_node_name(self, content: str) -> str:
        """提取节点名称"""
        # 尝试从行首提取
        first_line = content.split('\n')[0].strip()
        # 移除赋值操作符
        if '=' in first_line:
            name_part = first_line.split('=')[0].strip()
            return name_part
        return "unnamed"

    def _extract_parameters(self, content: str) -> Dict[str, Any]:
        """提取节点参数"""
        params = {}
        param_pattern = r'(\w+)\s*=\s*([^\n,]+)'

        matches = re.findall(param_pattern, content)
        for key, value in matches:
            key = key.strip()
            value = value.strip()

            # 尝试解析为数字
            try:
                if '.' in value:
                    params[key] = float(value)
                else:
                    params[key] = int(value)
            except ValueError:
                # 字符串值
                if value.startswith('"') and value.endswith('"'):
                    params[key] = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    params[key] = value[1:-1]
                elif value.lower() == "true":
                    params[key] = True
                elif value.lower() == "false":
                    params[key] = False
                elif value.lower() == "none":
                    params[key] = None
                else:
                    params[key] = value

        return params

    def _execute_node(self, node: Dict[str, Any], node_state: NodeExecutionState) -> Any:
        """执行节点"""
        node_type = node["name"].split('(')[0].split('.')[-1].split('_')[0].upper()

        logger.info(f"执行节点: {node_type} - {node['description']}")

        if node_type == "TRIGGER":
            return self._execute_trigger_node(node)
        elif node_type == "CARD_CREATE":
            return self._execute_card_create_node(node)
        elif node_type == "CARD_UPDATE":
            return self._execute_card_update_node(node)
        elif node_type == "LOGIC":
            return self._execute_logic_node(node)
        elif node_type == "WAIT":
            return self._execute_wait_node(node)
        elif node_type == "EXPRESSION":
            return self._execute_expression_node(node)
        else:
            raise ValueError(f"不支持的节点类型: {node_type}")

    def _execute_trigger_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """执行触发器节点"""
        # TODO: 实现触发器逻辑
        return {"triggered": True}

    def _execute_card_create_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """执行卡片创建节点"""
        from app.services.card_service import CardService
        from app.schemas import CardCreate

        card_service = CardService(self.db)

        # 获取参数
        project_id = node["parameters"].get("project_id")
        card_type = node["parameters"].get("card_type", "通用卡片")
        title = node["parameters"].get("title", "新卡片")
        content = node["parameters"].get("content", {})
        parent_id = node["parameters"].get("parent_id")

        card_create = CardCreate(
            title=title,
            content=content,
            card_type_id=None,  # TODO: 根据card_type名称查找ID
            parent_id=parent_id
        )

        card = card_service.create_card(card_create, project_id)
        return {"card_id": card.id}

    def _execute_card_update_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """执行卡片更新节点"""
        from app.services.card_service import CardService
        from app.schemas import CardUpdate

        card_service = CardService(self.db)

        card_id = node["parameters"].get("card_id")
        if not card_id:
            raise ValueError("更新卡片需要card_id参数")

        card_update = CardUpdate(
            content=node["parameters"].get("content", {}),
            display_order=node["parameters"].get("display_order")
        )

        card = card_service.update_card(card_id, card_update)
        return {"card_id": card.id}

    def _execute_logic_node(self, node: Dict[str, Any]) -> Any:
        """执行逻辑节点"""
        # TODO: 实现逻辑节点
        return {"result": True}

    def _execute_wait_node(self, node: Dict[str, Any]) -> Any:
        """执行等待节点"""
        # TODO: 实现等待逻辑
        return {"result": True}

    def _execute_expression_node(self, node: Dict[str, Any]) -> Any:
        """执行表达式节点"""
        expression = node["parameters"].get("expression", "")
        try:
            result = eval(expression, {"__builtins__": None}, self.context.variables)
            return result
        except Exception as e:
            logger.error(f"表达式执行失败: {expression}, 错误: {e}")
            raise

    def _create_node_state(self, run_id: int, node: Dict[str, Any]) -> NodeExecutionState:
        """创建节点执行状态"""
        return NodeExecutionState(
            run_id=run_id,
            node_id=node["name"],
            node_type=node["name"].split('(')[0].split('.')[-1],
            status="pending"
        )

    def _update_node_state_error(self, run_id: int, node_name: str, error_message: str):
        """更新节点状态为错误"""
        node_state = self.db.exec(
            select(NodeExecutionState).where(
                NodeExecutionState.run_id == run_id,
                NodeExecutionState.node_id == node_name
            )
        ).first()

        if node_state:
            node_state.status = "error"
            node_state.error_message = error_message
            node_state.end_time = datetime.now()

            self.db.add(node_state)
            self.db.commit()

    def _evaluate_expression(self, expression: str) -> Any:
        """评估表达式"""
        try:
            # 简单的变量替换
            for var_name, var_value in self.context.variables.items():
                expression = expression.replace(f"${var_name}", str(var_value))

            # 尝试作为Python表达式执行
            return eval(expression, {"__builtins__": None}, self.context.variables)
        except Exception as e:
            logger.error(f"表达式评估失败: {expression}, 错误: {e}")
            return None