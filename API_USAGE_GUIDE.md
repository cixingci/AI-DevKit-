# AI DevKit - API使用指南

## 🚀 快速开始

### 1. 配置LLM模型

首先需要在系统中配置LLM模型：

```bash
# 启动后端服务
cd backend
python main.py
```

然后在`/api/v1/ai/llm/configs`端点配置你的AI模型。

### 2. 创建配置

```bash
curl -X POST http://localhost:8000/api/v1/ai/llm/configs \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "display_name": "GPT-4",
    "model_name": "gpt-4",
    "api_base": "https://api.openai.com/v1",
    "api_key": "your-api-key-here",
    "base_url": "https://api.openai.com/v1"
  }'
```

## 📡 API接口

### 1. AI配置管理

#### 创建LLM配置
```bash
POST /api/v1/ai/llm/configs
Content-Type: application/json

{
  "provider": "openai",
  "display_name": "GPT-4",
  "model_name": "gpt-4",
  "api_base": "https://api.openai.com/v1",
  "api_key": "sk-xxx",
  "base_url": "https://api.openai.com/v1"
}
```

#### 获取配置列表
```bash
GET /api/v1/ai/llm/configs?skip=0&limit=10
```

#### 测试连接
```bash
POST /api/v1/ai/llm/configs/{config_id}/test
```

### 2. AI内容生成

#### 基础生成
```bash
POST /api/v1/ai/generate
Content-Type: application/json

{
  "prompt": "创建一个用户注册功能的描述",
  "context": {
    "project_type": "web_application",
    "requirements": "需要用户名、邮箱、密码"
  },
  "temperature": 0.7,
  "max_tokens": 1000,
  "llm_config_id": 1
}
```

#### 自定义参数
```bash
POST /api/v1/ai/generate
{
  "prompt": "分析以下技术栈：Python, Django, React",
  "context": {
    "tech_stack": ["python", "django", "react"],
    "use_case": "web_application"
  },
  "temperature": 0.5,
  "max_tokens": 1500,
  "llm_config_id": 1
}
```

### 3. 工作流管理

#### 执行工作流
```bash
POST /api/v1/ai/workflows/execute?workflow_id=1
Content-Type: application/json

{
  "project_id": 1,
  "card_id": 1,
  "variables": {
    "project_name": "示例项目",
    "user_count": 1000
  }
}
```

#### 获取工作流运行记录
```bash
GET /api/v1/ai/workflows/runs?skip=0&limit=20
```

#### 获取运行详情
```bash
GET /api/v1/ai/workflows/runs/{run_id}
```

#### 获取节点状态
```bash
GET /api/v1/ai/workflows/nodes/{run_id}
```

#### 统计数据
```bash
GET /api/v1/ai/workflows/statistics
```

### 4. 工作流初始化

#### 初始化项目
```bash
POST /api/v1/ai/workflows/project/{project_id}/initialize?workflow_template=project-init
```

## 🎯 使用示例

### 示例1: 创建项目并初始化

```bash
# 1. 创建项目
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "电商系统", "description": "在线商城系统"}'

# 响应: {"id": 1, "name": "电商系统", "description": "在线商城系统"}

# 2. 初始化项目
curl -X POST http://localhost:8000/api/v1/ai/workflows/project/1/initialize?workflow_template=project-init

# 3. 查看卡片
curl http://localhost:8000/api/v1/cards?project_id=1
```

### 示例2: AI生成卡片内容

```bash
# 1. 创建卡片
curl -X POST http://localhost:8000/api/v1/cards \
  -H "Content-Type: application/json" \
  -d '{
    "title": "用户登录功能",
    "content": {
      "functionality": "实现用户登录系统",
      "requirements": ["用户名认证", "密码加密"]
    },
    "card_type_id": 1,
    "project_id": 1
  }'

# 响应: {"id": 2, "title": "用户登录功能", "content": {...}}

# 2. AI生成描述
curl -X POST http://localhost:8000/api/v1/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "基于以下需求创建详细的功能规格说明：{{content}}",
    "context": {"card_id": 2},
    "temperature": 0.6,
    "max_tokens": 2000
  }'
```

### 示例3: 使用工作流批量创建卡片

```bash
# 创建工作流
curl -X POST http://localhost:8000/api/v1/ai/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "创建完整用户模块",
    "description": "批量创建用户模块的所有卡片",
    "definition_code": "# 工作流：创建用户模块\n#@node(description=\"创建用户卡\")\nuser_card = Card.Create(\n  project_id=1,\n  card_type=\"功能卡\",\n  title=\"用户管理\",\n  content={\"type\": \"user_management\"}\n)\n#</node>\n\n#@node(description=\"创建登录卡\")\nlogin_card = Card.Create(\n  project_id=1,\n  card_type=\"功能卡\",\n  title=\"用户登录\",\n  parent_id=user_card.id,\n  content={\"type\": \"user_login\"}\n)\n#</node>\n\n#@node(description=\"等待完成\")\nwait_result = Logic.Wait(tasks=[user_card, login_card])\n#</node>",
    "project_id": 1
  }'

# 执行工作流
curl -X POST http://localhost:8000/api/v1/ai/workflows/execute?workflow_id=1

# 查看结果
curl http://localhost:8000/api/v1/ai/workflows/runs
```

## 🔧 技术细节

### AI服务支持

#### OpenAI配置
```json
{
  "provider": "openai",
  "model_name": "gpt-4",
  "api_key": "sk-xxx",
  "api_base": "https://api.openai.com/v1",
  "base_url": "https://api.openai.com/v1"
}
```

#### Anthropic Claude配置
```json
{
  "provider": "anthropic",
  "model_name": "claude-3-opus-20240229",
  "api_key": "sk-ant-xxx",
  "api_base": null,
  "base_url": null
}
```

### 工作流DSL语法

```wf
# 节点格式
#@node(description="节点描述")
节点名称 = Card.Create(
    project_id=1,
    card_type="卡片类型",
    title="卡片标题",
    content={},
    parent_id=0
)
#</node>

# 表达式节点
#@node(description="表达式节点")
result = Logic.Expression(
    expression="[{'index': i} for i in range(10)]"
)
#</node>

# 等待节点
#@node(description="等待节点")
wait_result = Logic.Wait(tasks=[node1, node2])
#</node>
```

### 支持的节点类型

- **Card.Create** - 创建卡片
- **Card.Update** - 更新卡片
- **Card.Delete** - 删除卡片
- **Project.Create** - 创建项目
- **Logic.Wait** - 等待节点
- **Logic.Expression** - 表达式节点
- **Logic.Condition** - 条件节点

## 📝 错误处理

### 常见错误

1. **认证错误**
   ```
   HTTP 401: API密钥无效
   ```

2. **模型错误**
   ```
   HTTP 400: 模型不存在
   ```

3. **参数错误**
   ```
   HTTP 400: 缺少必需参数
   ```

4. **服务错误**
   ```
   HTTP 500: AI服务不可用
   ```

### 调试建议

1. 检查环境变量配置
2. 验证API密钥有效性
3. 确认模型名称正确
4. 查看工作流执行日志

## 🚦 最佳实践

### AI生成

1. **明确需求** - 提供清晰的prompt
2. **合理参数** - temperature: 0.5-0.8, max_tokens: 1000-3000
3. **上下文丰富** - 提供充分的上下文信息
4. **结果验证** - 生成的结果需要人工验证

### 工作流使用

1. **简单开始** - 从简单工作流开始
2. **逐步复杂** - 逐步增加工作流复杂度
3. **充分测试** - 在测试环境充分测试
4. **合理编排** - 避免过长的嵌套

### 卡片管理

1. **结构化** - 保持卡片结构清晰
2. **层次化** - 合理设置父/子关系
3. **命名规范** - 使用有意义的标题
4. **及时更新** - 保持内容最新

## 📊 监控和统计

### 查看执行统计
```bash
curl http://localhost:8000/api/v1/ai/workflows/statistics
```

### 查看最近的运行记录
```bash
curl http://localhost:8000/api/v1/ai/workflows/runs?skip=0&limit=10
```

## 🔐 安全建议

1. **保护API密钥** - 不要在代码中硬编码
2. **环境变量** - 使用环境变量管理敏感信息
3. **IP限制** - 配置合理的CORS策略
4. **定期轮换** - 定期更新API密钥

---

**文档版本**: 1.0
**最后更新**: 2026年2月25日
**维护者**: AI DevKit开发团队