# AI DevKit - API端点详细说明

## 🎯 API概览

**基础URL**: `http://localhost:8000/api/v1`  
**API版本**: v1  
**文档**: `http://localhost:8000/docs` (Swagger UI)

---

## 📋 完整API端点列表

### 1. 根路径
- `GET /` - 应用基本信息
- `GET /health` - 健康检查

---

### 2. 项目管理 (Projects)
- `GET /projects` - 获取项目列表
  - 查询参数:
    - `skip` (int) - 跳过数量 (默认: 0)
    - `limit` (int) - 限制数量 (默认: 100, 最大: 1000)
  - 响应示例:
    ```json
    [
      {
        "id": 1,
        "name": "Test Project",
        "description": "A test project",
        "created_at": "2026-02-26T09:34:42.617980"
      }
    ]
    ```

- `POST /projects` - 创建新项目
  - 请求体:
    ```json
    {
      "name": "项目名称",
      "description": "项目描述"
    }
    ```
  - 响应示例:
    ```json
    {
      "id": 6,
      "name": "项目名称",
      "description": "项目描述",
      "created_at": "2026-02-26T22:35:00.000000"
    }
    ```

- `GET /projects/{id}` - 获取项目详情
  - 响应示例:
    ```json
    {
      "id": 1,
      "name": "项目名称",
      "description": "项目描述",
      "card_count": 5,
      "created_at": "2026-02-26T09:34:42.617980"
    }
    ```

- `DELETE /projects/{id}` - 删除项目

---

### 3. 卡片管理 (Cards)
- `GET /cards` - 获取卡片列表
  - 查询参数:
    - `project_id` (int, 可选) - 项目ID
    - `skip` (int) - 跳过数量
    - `limit` (int) - 限制数量
  - 响应示例:
    ```json
    [
      {
        "id": 1,
        "title": "Test Card",
        "card_type_id": 1,
        "description": "测试卡片",
        "project_id": 1,
        "content": {
          "type": "功能卡"
        },
        "created_at": "2026-02-26T10:00:00.000000"
      }
    ]
    ```

- `POST /cards` - 创建卡片
  - 请求体:
    ```json
    {
      "title": "卡片标题",
      "card_type_id": 1,
      "description": "卡片描述",
      "project_id": 1,
      "content": {},
      "parent_id": null,
      "display_order": 0
    }
    ```
  - 响应示例:
    ```json
    {
      "id": 10,
      "title": "卡片标题",
      "card_type_id": 1,
      "description": "卡片描述",
      "project_id": 1,
      "content": {},
      "created_at": "2026-02-26T22:35:00.000000"
    }
    ```

- `GET /cards/{id}` - 获取卡片详情
  - 响应包含卡片类型信息

- `PUT /cards/{id}` - 更新卡片

- `DELETE /cards/{id}` - 删除卡片

---

### 4. 卡片类型管理 (Card Types) 🆕
- `GET /card-types` - 获取卡片类型列表
  - 响应示例:
    ```json
    [
      {
        "id": 1,
        "name": "需求卡",
        "description": "需求分析卡片",
        "json_schema": {
          "type": "object",
          "properties": {
            "user_story": {
              "type": "string",
              "description": "用户故事"
            }
          },
          "required": []
        },
        "created_at": "2026-02-26T10:00:00.000000"
      }
    ]
    ```

- `POST /card-types` - 创建卡片类型
  - 请求体:
    ```json
    {
      "name": "功能卡",
      "description": "功能实现卡片",
      "json_schema": {
        "type": "object",
        "properties": {
          "function_name": {
            "type": "string",
            "description": "函数名称"
          },
          "input_params": {
            "type": "array",
            "description": "输入参数"
          }
        },
        "required": ["function_name"]
      }
    }
    ```

- `GET /card-types/{id}` - 获取卡片类型详情

- `PUT /card-types/{id}` - 更新卡片类型

- `DELETE /card-types/{id}` - 删除卡片类型

---

### 5. AI服务 (AI)
- `POST /ai/generate` - AI内容生成
  - 请求体:
    ```json
    {
      "prompt": "生成详细描述",
      "context": {
        "card_id": 1,
        "card_title": "用户登录功能",
        "card_type": "功能卡"
      },
      "temperature": 0.7,
      "max_tokens": 2000,
      "llm_config_id": 1
    }
    ```
  - 响应示例:
    ```json
    {
      "success": true,
      "message": "生成成功",
      "data": {
        "content": "{...}"
      }
    }
    ```

- `GET /ai/llm/configs` - 获取LLM配置列表
- `POST /ai/llm/configs` - 创建LLM配置
- `PUT /ai/llm/configs/{id}` - 更新LLM配置
- `DELETE /ai/llm/configs/{id}` - 删除LLM配置
- `POST /ai/llm/configs/{id}/test` - 测试LLM连接

---

### 6. 工作流管理 (Workflows)
- `POST /ai/workflows/execute` - 执行工作流
  - 请求体:
    ```json
    {
      "project_id": 1,
      "workflow_definition": "{...}"
    }
    ```

- `GET /ai/workflows/runs` - 获取运行记录
  - 查询参数:
    - `skip` (int)
    - `limit` (int)
    - `project_id` (int, 可选)

- `GET /ai/workflows/project/{id}/initialize` - 项目初始化
- `GET /ai/workflows/nodes/{run_id}` - 获取节点执行状态

---

## 🔐 API认证

当前版本API不需要认证。

---

## 📊 数据模型

### Project (项目)
- `id` (int) - 项目ID
- `name` (str) - 项目名称
- `description` (str, 可选) - 项目描述
- `created_at` (datetime) - 创建时间
- `updated_at` (datetime) - 更新时间

### Card (卡片)
- `id` (int) - 卡片ID
- `title` (str) - 卡片标题
- `card_type_id` (int) - 卡片类型ID
- `description` (str, 可选) - 卡片描述
- `project_id` (int, 可选) - 项目ID
- `content` (dict, 可选) - 卡片内容
- `parent_id` (int, 可选) - 父卡片ID
- `display_order` (int) - 显示顺序
- `ai_generated` (bool) - AI已生成
- `needs_review` (bool) - 需要审核
- `created_at` (datetime) - 创建时间
- `updated_at` (datetime) - 更新时间
- `card_type` (object, 可选) - 卡片类型信息

### CardType (卡片类型) 🆕
- `id` (int) - 类型ID
- `name` (str) - 类型名称
- `description` (str, 可选) - 类型描述
- `json_schema` (dict) - JSON Schema模板
- `created_at` (datetime) - 创建时间
- `updated_at` (datetime) - 更新时间

### LLMConfig (AI配置)
- `id` (int) - 配置ID
- `provider` (str) - 提供商
- `display_name` (str, 可选) - 显示名称
- `model_name` (str) - 模型名称
- `api_base` (str, 可选) - API基础URL
- `api_key` (str) - API密钥
- `base_url` (str, 可选) - 基础URL
- `created_at` (datetime) - 创建时间
- `updated_at` (datetime) - 更新时间

### Workflow (工作流)
- `id` (int) - 工作流ID
- `name` (str) - 工作流名称
- `description` (str, 可选) - 工作流描述
- `definition` (dict) - 工作流定义
- `is_active` (bool) - 是否激活
- `created_at` (datetime) - 创建时间
- `updated_at` (datetime) - 更新时间

### WorkflowRun (工作流运行)
- `id` (int) - 运行ID
- `workflow_id` (int) - 工作流ID
- `project_id` (int) - 项目ID
- `status` (str) - 运行状态
- `started_at` (datetime) - 开始时间
- `completed_at` (datetime) - 完成时间
- `error_message` (str, 可选) - 错误信息
- `created_at` (datetime) - 创建时间

---

## 🧪 测试示例

### 创建项目
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "测试项目", "description": "测试项目描述"}'
```

### 获取项目列表
```bash
curl http://localhost:8000/api/v1/projects?skip=0&limit=10
```

### 创建卡片
```bash
curl -X POST http://localhost:8000/api/v1/cards \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试卡片",
    "card_type_id": 1,
    "description": "这是测试卡片",
    "project_id": 1
  }'
```

### AI内容生成
```bash
curl -X POST http://localhost:8000/api/v1/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "生成详细描述",
    "context": {"card_id": 1, "card_title": "用户登录功能"},
    "temperature": 0.7,
    "max_tokens": 2000,
    "llm_config_id": 1
  }'
```

---

## 🎯 响应格式

### 成功响应
```json
{
  "id": 1,
  "name": "测试",
  "description": "测试"
}
```

### 错误响应
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "name"],
      "msg": "Field required"
    }
  ]
}
```

### 列表响应
```json
[
  {"id": 1, "name": "项目1"},
  {"id": 2, "name": "项目2"}
]
```

---

## 📝 注意事项

1. **分页**: 所有列表接口都支持分页参数
2. **排序**: 默认按创建时间倒序
3. **认证**: 当前版本不需要认证
4. **错误处理**: 所有错误都返回200，错误信息在响应体中
5. **JSON Schema**: 卡片类型需要使用有效的JSON Schema格式

---

## 🚀 下一步

查看完整API文档: http://localhost:8000/docs
