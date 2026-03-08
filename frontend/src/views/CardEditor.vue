<template>
  <div class="card-editor">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-editor-header">
          <div class="header-left">
            <el-button :icon="ArrowLeft" @click="goBack" circle />
            <span class="card-title">{{ isEdit ? '编辑卡片' : '创建卡片' }}</span>
          </div>
          <div class="header-right">
            <el-button :icon="Refresh" @click="loadCard" :loading="loading">刷新</el-button>
            <el-button :icon="DocumentChecked" type="primary" @click="saveCard" :loading="saving">
              保存
            </el-button>
            <el-button :icon="MagicStick" type="success" @click="openAIGenerate" :loading="generating">
              AI生成
            </el-button>
          </div>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <!-- 基础信息 -->
        <el-form-item label="标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="请输入卡片标题"
            @input="handleTitleChange"
          />
        </el-form-item>

         <!-- 卡片类型 -->
         <el-form-item label="卡片类型" prop="card_type_id">
           <el-select
             v-model="form.card_type_id"
             placeholder="选择卡片类型"
             @change="handleCardTypeChange"
             :loading="cardTypesLoading"
             :clearable="true"
             :disabled="cardTypesLoading"
             filterable
           >
             <el-option
               v-for="type in cardTypeOptions"
               :key="`card-type-${type.id}`"
               :label="type.name"
               :value="type.id"
             >
               <span>{{ type.name }}</span>
               <span v-if="type.description" style="color: #8492a6; font-size: 12px; margin-left: 10px;">{{ type.description }}</span>
             </el-option>
           </el-select>
         </el-form-item>

        <!-- 描述 -->
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="cardContent.description"
            type="textarea"
            :rows="3"
            placeholder="请输入卡片描述"
            @input="handleContentChange"
          />
        </el-form-item>

        <!-- 项目选择（仅创建卡片时显示） -->
        <el-form-item label="项目" prop="project_id" v-if="!isEdit">
          <el-select
            v-model="form.project_id"
            placeholder="请选择项目"
            :loading="projectsLoading"
            filterable
            clearable
            style="width: 100%"
            @change="handleProjectChange"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            >
              <div style="display: flex; align-items: center; gap: 8px">
                <el-icon><Folder /></el-icon>
                <span>{{ project.name }}</span>
                <span v-if="project.description" style="color: #909399; font-size: 12px; margin-left: auto">
                  {{ project.description }}
                </span>
              </div>
            </el-option>
          </el-select>
          <div v-if="!form.project_id && !isEdit && formRef" style="color: #f56c6c; font-size: 12px; margin-top: 5px">
            * 创建卡片必须选择项目
          </div>
        </el-form-item>

        <!-- 核心内容 -->
        <el-divider content-position="left">
          <span>核心内容</span>
          <el-tag v-if="form.card_type_id && sortableFields" type="info" size="small" style="margin-left: 10px">
            拖拽排序
          </el-tag>
        </el-divider>

        <el-alert
          v-if="schemaValidationSummary"
          :title="schemaValidationSummary"
          :type="schemaValidationOk ? 'success' : 'error'"
          show-icon
          :closable="false"
          style="margin-bottom: 12px"
        />

        <!-- 动态内容 -->
        <div class="dynamic-content">
          <template v-if="form.card_type_id">
            <el-tabs v-model="contentMode" class="content-tabs">
              <el-tab-pane label="表单模式" name="form">
                <div v-if="sortableFields" class="field-order-controls">
                  <el-button :icon="Sort" @click="toggleFieldOrder" size="small">
                    {{ fieldOrder ? '取消排序' : '启用排序' }}
                  </el-button>
                  <span class="hint">仅影响显示顺序（本地保存）</span>
                </div>

                <DynamicFields
                  v-if="currentCardType"
                  :schema="currentCardType.json_schema"
                  :content="cardContent"
                  :sortable="fieldOrder"
                  :persist-key="fieldOrderPersistKey"
                  @update="handleContentUpdate"
                />
                <el-empty v-else description="请选择卡片类型" :image-size="100" />
              </el-tab-pane>

              <el-tab-pane label="JSON模式" name="json">
                <div class="json-toolbar">
                  <el-button size="small" @click="syncJsonFromForm">从表单同步</el-button>
                  <el-button size="small" type="primary" @click="applyJsonToForm" :disabled="!!jsonParseError">
                    应用到表单
                  </el-button>
                  <el-button size="small" @click="formatJsonContent" :disabled="!!jsonParseError">格式化</el-button>
                  <el-tag v-if="jsonParseError" type="danger" size="small">{{ jsonParseError }}</el-tag>
                </div>

                <MonacoJsonEditor
                  v-model="contentJsonText"
                  :schema="normalizedJsonSchema"
                  height="520px"
                />
              </el-tab-pane>
            </el-tabs>
          </template>
          <el-empty v-else description="请先选择卡片类型" :image-size="100" />
        </div>

        <!-- 关联卡片 -->
        <el-divider content-position="left">关联卡片</el-divider>
        <el-form-item label="父卡片">
          <el-tree-select
            v-model="form.parent_id"
            :data="cardTree"
            :props="treeProps"
            placeholder="选择父卡片"
            clearable
            :render-after-expand="false"
            check-strictly
            style="width: 100%"
          />
        </el-form-item>

        <!-- 元数据 -->
        <el-divider content-position="left">元数据</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="创建时间">
              <el-input :value="formatDate(created_at)" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="更新时间">
              <el-input :value="formatDate(updated_at)" disabled />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="生成状态">
          <el-tag :type="aiGenerated ? 'success' : 'info'" size="small">
            {{ aiGenerated ? 'AI已生成' : '待生成' }}
          </el-tag>
          <el-tag v-if="needs_review" type="warning" size="small" style="margin-left: 10px;">
            需要审核
          </el-tag>
        </el-form-item>
      </el-form>

      <!-- AI生成对话框 -->
      <el-dialog
        v-model="aiDialogVisible"
        title="AI生成"
        width="600px"
      >
        <el-form label-width="100px">
          <el-form-item label="生成要求">
            <el-input
              v-model="aiPrompt"
              type="textarea"
              :rows="4"
              placeholder="请输入生成要求，例如：基于以下需求创建详细的描述：{{ form.title }}"
            />
          </el-form-item>
          <el-form-item label="温度设置">
            <el-slider
              v-model="aiTemperature"
              :min="0"
              :max="2"
              :step="0.1"
              :marks="{ 0: '保守', 1: '平衡', 2: '创造性' }"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="aiDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="generateContent" :loading="generating">
            开始生成
          </el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Refresh,
  DocumentChecked,
  MagicStick,
  Sort,
  Folder
} from '@element-plus/icons-vue'
import axios from 'axios'
import { cardTypeAPI, cardAPI } from '@/services/api'
import MonacoJsonEditor from '@/components/MonacoJsonEditor.vue'
import Ajv from 'ajv'
import addFormats from 'ajv-formats'
import type { FormInstance, FormRules } from 'element-plus'
import type { Card, CardType } from '@/types'

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const generating = ref(false)

const form = ref({
  title: '',
  card_type_id: null as number | null,
  parent_id: null as number | null,
  display_order: 1,
  project_id: null as number | null
})

const cardContent = ref<Record<string, any>>({})
const created_at = ref('')
const updated_at = ref('')

const cardTypes = ref<CardType[]>([])
const cardTypesLoading = ref(false)
const cardTree = ref<any[]>([])
const currentCardType = ref<CardType | null>(null)
const projects = ref<any[]>([])
const projectsLoading = ref(false)

const queryProjectId = computed(() => {
  const raw = route.query.project_id
  if (raw === undefined || raw === null) return null
  const str = Array.isArray(raw) ? raw[0] : String(raw)
  const parsed = parseInt(str)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
})

// 计算属性：卡片类型选项
const cardTypeOptions = computed(() => {
  console.log('cardTypeOptions computed, cardTypes数量:', cardTypes.value.length)
  return cardTypes.value
})

// 字段排序
const fieldOrder = ref(false)
const sortableFields = computed(() => {
  if (!currentCardType.value) return false
  const s: any = currentCardType.value.json_schema
  if (!s) return false
  if (s.properties && typeof s.properties === 'object') return Object.keys(s.properties).length > 0
  return Object.keys(s).length > 0
})

const fieldOrderPersistKey = computed(() => {
  const id = currentCardType.value?.id
  return id ? `ai-devkit:fieldOrder:${id}` : ''
})

// 内容模式：表单 / JSON
const contentMode = ref<'form' | 'json'>('form')
const contentJsonText = ref('{}')
const jsonParseError = ref('')

// JSON Schema校验：卡片内容 -> 卡片类型 Schema
const ajv = new Ajv({ allErrors: true, strict: false, allowUnionTypes: true })
addFormats(ajv)
const validateFn = ref<((data: any) => boolean) | null>(null)
const schemaValidationOk = ref(true)
const schemaValidationSummary = ref('')

const normalizedJsonSchema = computed(() => {
  const s: any = currentCardType.value?.json_schema
  if (!s) return null
  
  // 如果是完整的 JSON Schema（包含 type 或 properties）
  if (s.type || s.properties || s.$schema) {
    // 确保 required 字段存在
    return {
      type: 'object',
      properties: s.properties || {},
      required: s.required || [],
      additionalProperties: true,
      ...s
    }
  }
  
  // 兼容旧形态：直接把 schema 当字段字典
  return {
    type: 'object',
    properties: s,
    additionalProperties: true
  }
})

let validateTimer: number | null = null
const scheduleValidateContent = () => {
  if (validateTimer) window.clearTimeout(validateTimer)
  validateTimer = window.setTimeout(() => {
    validateTimer = null
    runValidateContent()
  }, 250)
}

const runValidateContent = () => {
  if (!validateFn.value) {
    schemaValidationOk.value = true
    schemaValidationSummary.value = ''
    return
  }
  const ok = validateFn.value(cardContent.value)
  schemaValidationOk.value = !!ok
  if (ok) {
    schemaValidationSummary.value = '内容校验通过'
    return
  }
  const errors = (validateFn.value as any).errors as any[] | null | undefined
  const first = errors?.[0]
  const msg = first
    ? `${first.instancePath || '/'} ${first.message || '不符合 Schema'}`
    : '内容不符合 Schema'
  schemaValidationSummary.value = `内容校验失败：${msg}`
}

const aiDialogVisible = ref(false)
const aiPrompt = ref('')
const aiTemperature = ref(0.7)
const aiGenerated = ref(false)
const needs_review = ref(false)

const rules = {
  title: [
    { required: true, message: '请输入卡片标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度在1到200个字符', trigger: 'blur' }
  ],
  card_type_id: [
    { required: true, message: '请选择卡片类型', trigger: 'change' }
  ],
  project_id: [
    { required: true, message: '请选择项目', trigger: 'change' }
  ]
}

const treeProps = {
  children: 'children',
  label: 'title',
  value: 'id'
}

// 判断是新建还是编辑
const isEdit = computed(() => {
  const routeName = route.name as string
  return routeName === 'CardEditor' && !!cardId.value
})

// 加载项目列表
const loadProjects = async () => {
  projectsLoading.value = true
  try {
    const response = await axios.get('/api/v1/projects?skip=0&limit=100')
    projects.value = response.data || []
    console.log('加载项目列表完成:', projects.value.length, '个项目')
    projects.value.forEach(p => console.log(`  项目ID ${p.id}: ${p.name}`))
  } catch (error) {
    console.error('加载项目失败:', error)
    projects.value = []
  } finally {
    projectsLoading.value = false
  }
}

// 从路由获取卡片ID
const cardId = computed(() => {
  const routeName = route.name as string
  if (routeName === 'CardEditor') {
    return parseInt(route.params.id as string) || undefined
  }
  return undefined
})

// 从路由获取项目ID
const projectId = computed(() => {
  const routeName = route.name as string
  console.log('=== projectId computed ===')
  console.log('路由名称:', routeName)
  console.log('路由参数:', route.query)

  // 从query参数获取project_id
  const queryProjectId = route.query.project_id
  if (queryProjectId && typeof queryProjectId === 'string' && queryProjectId !== '0') {
    const parsedId = parseInt(queryProjectId)
    const result = isNaN(parsedId) ? null : parsedId
    console.log('从query解析后的项目ID:', result)
    return result
  }
  
  // 如果是编辑模式，从表单获取project_id（loadCard后已设置）
  if (form.value.project_id) {
    console.log('从表单获取项目ID:', form.value.project_id)
    return form.value.project_id
  }
  
  console.log('无有效的project_id，返回null')
  return null
})

// 加载卡片类型
const loadCardTypes = async () => {
  cardTypesLoading.value = true
  console.log('开始加载卡片类型...')

  try {
    console.log('调用 cardTypeAPI.getCardTypes()')
    const response = await cardTypeAPI.getCardTypes()
    console.log('API响应:', response)
    console.log('响应类型:', typeof response)
    console.log('响应是否为数组:', Array.isArray(response))

    cardTypes.value = Array.isArray(response) ? response : []

    console.log('设置cardTypes.value:', cardTypes.value)
    console.log('卡片类型数量:', cardTypes.value.length)

    if (!cardTypes.value || cardTypes.value.length === 0) {
      ElMessage.warning('没有可用的卡片类型，请先创建卡片类型')
    } else {
      ElMessage.success(`成功加载 ${cardTypes.value.length} 个卡片类型`)
    }
  } catch (error) {
    console.error('加载卡片类型失败:', error)
    console.error('错误详情:', error.response || error.message)
    cardTypes.value = []
    ElMessage.error('加载卡片类型失败: ' + (error.response?.data?.detail || error.message || '请稍后重试'))
  } finally {
    cardTypesLoading.value = false
    console.log('卡片类型加载完成, loading:', cardTypesLoading.value)
  }
}

// 加载卡片数据
const loadCard = async () => {
  if (!cardId.value) return

  loading.value = true
  try {
    // 使用 cardAPI 获取卡片详情
    const card = await cardAPI.getCard(cardId.value)

    form.value = {
      title: card.title,
      card_type_id: card.card_type_id,
      parent_id: card.parent_id,
      display_order: card.display_order,
      project_id: card.project_id ?? queryProjectId.value
    }

    console.log('loadCard - 卡片数据:', card)
    console.log('loadCard - parent_id:', card.parent_id)
    console.log('loadCard - project_id:', card.project_id)
    
    cardContent.value = card.content
    created_at.value = card.created_at
    updated_at.value = card.updated_at
    aiGenerated.value = card.ai_generated
    needs_review.value = card.needs_review

    // 设置当前卡片类型
    if (card.card_type) {
      currentCardType.value = card.card_type
      console.log('成功加载卡片类型:', card.card_type)
    } else {
      // 兼容：若详情接口不带 card_type，则从已加载列表反查
      const typeId = Number(card.card_type_id ?? form.value.card_type_id)
      const found = cardTypes.value.find(t => t.id === typeId) || null
      currentCardType.value = found
      console.log('卡片类型未找到，已从列表反查:', found)
    }

    // 若接口未返回 project_id，编辑模式也需要用 queryProjectId 补齐（用于父卡片树）
    if (!form.value.project_id && queryProjectId.value) {
      form.value.project_id = queryProjectId.value
    }
  } catch (error) {
    console.error('加载卡片失败:', error)
    ElMessage.error('加载卡片失败')
  } finally {
    loading.value = false
  }
}

// 加载卡片树
const loadCardTree = async () => {
  // 优先使用卡片详情返回的 project_id
  let currentProjectId = form.value.project_id
  if (!currentProjectId) {
    // 尝试从 query 参数获取
    currentProjectId = queryProjectId.value
  }
  if (!currentProjectId) {
    // 尝试从 projectId 计算属性获取
    currentProjectId = projectId.value
  }
  
  console.log('loadCardTree - 当前项目ID:', currentProjectId)
  console.log('loadCardTree - form.value:', form.value)
  
  if (!currentProjectId) {
    console.log('没有项目ID，跳过加载卡片树')
    return
  }

  try {
    const cards = await cardAPI.getCards({
      project_id: currentProjectId,
      parent_id: null,
      skip: 0,
      limit: 1000
    })
    // 排除当前正在编辑的卡片
    const currentCardId = cardId.value
    cardTree.value = cards
      .filter((card: any) => card.id !== currentCardId)
      .map((card: any) => ({
        ...card,
        children: undefined
      }))
    console.log('成功加载卡片树:', cardTree.value.length, '个根卡片')
    console.log('卡片树数据:', cardTree.value)
  } catch (error) {
    console.error('加载卡片树失败:', error)
  }
}

// 保存卡片
const saveCard = async () => {
  if (!formRef.value) return

  // 使用正确的 validate 用法
  const valid = await formRef.value.validate()
  if (valid) {
    saving.value = true

    // 获取项目ID - 确保优先使用projectId.value
    const currentProjectId = projectId.value !== null && projectId.value !== undefined
      ? projectId.value
      : form.value.project_id

    // 记录详细信息
    console.log('=== 保存卡片 ===')
    console.log('路由名称:', route.name)
    console.log('路由参数 project_id:', route.query.project_id)
    console.log('computed projectId:', projectId.value)
    console.log('表单项目ID:', form.value.project_id)
    console.log('最终项目ID:', currentProjectId)
    console.log('当前选择的项目:', projects.value.find(p => p.id === currentProjectId))

    // 验证项目ID
    if (!isEdit.value && !currentProjectId) {
      console.error('错误：创建卡片时没有项目ID')
      ElMessage.error('请先选择一个项目！', {
        duration: 5000,
        offset: 60
      })
      saving.value = false
      return
    }

    try {
      if (isEdit.value) {
        // 编辑模式
        const currentProjectId = projectId.value || form.value.project_id
        const updateData: any = {
          title: form.value.title,
          card_type_id: form.value.card_type_id,
          parent_id: form.value.parent_id,
          content: cardContent.value,
          display_order: form.value.display_order,
          project_id: currentProjectId
        }

        // 使用 cardAPI 更新卡片
        const updatedCard = await cardAPI.updateCard(cardId.value, updateData)
        console.log('卡片更新成功:', updatedCard)
        ElMessage.success('更新成功')
        goBack()
      } else {
        // 新建模式
        const createData: any = {
          title: form.value.title,
          card_type_id: form.value.card_type_id,
          parent_id: form.value.parent_id,
          content: cardContent.value,
          display_order: form.value.display_order,
          project_id: currentProjectId
        }

        // 使用 cardAPI 创建卡片
        const newCard = await cardAPI.createCard(createData)
        console.log('卡片创建成功:', newCard)
        ElMessage.success('创建成功')
        goBack()
      }
    } catch (error: any) {
      console.error('保存失败:', error)
      if (error.response) {
        console.error('错误详情:', error.response.data)
        ElMessage.error('保存失败: ' + (error.response.data?.detail || error.message), {
          duration: 5000,
          offset: 60
        })
      } else {
        ElMessage.error('保存失败: ' + error.message, {
          duration: 5000,
          offset: 60
        })
      }
    } finally {
      saving.value = false
    }
  }
}

// AI生成内容
const openAIGenerate = () => {
  aiPrompt.value = `基于以下需求生成详细内容：${form.value.title}\n描述：${cardContent.value.description || ''}`
  aiDialogVisible.value = true
}

const generateContent = async () => {
  if (!aiPrompt.value) {
    ElMessage.warning('请输入生成要求')
    return
  }

  generating.value = true
  try {
    const response = await axios.post('http://localhost:8888/api/v1/ai/generate', {
      prompt: aiPrompt.value,
      context: {
        card_id: cardId.value,
        card_title: form.value.title,
        card_type: currentCardType.value?.name
      },
      temperature: aiTemperature.value,
      max_tokens: 2000,
      llm_config_id: 1 // TODO: 从设置中获取
    })

    const result = response.data

    // 更新内容
    if (result.data && result.data.content) {
      cardContent.value = JSON.parse(result.data.content)
      aiGenerated.value = true
      ElMessage.success('AI生成成功')
    }
  } catch (error) {
    console.error('AI生成失败:', error)
    ElMessage.error('AI生成失败')
  } finally {
    generating.value = false
    aiDialogVisible.value = false
  }
}

// 处理标题变化
const handleTitleChange = () => {
  // 可以在这里添加标题验证或自动修正
}

// 处理卡片类型变化
const handleCardTypeChange = async () => {
  const typeId = form.value.card_type_id

  if (!typeId) {
    currentCardType.value = null
    return
  }

  // 获取类型详细信息
  const type = cardTypes.value.find(t => t.id === typeId)
  if (type) {
    currentCardType.value = type
    
    // 根据 JSON Schema 生成默认内容
    if (type.json_schema && type.json_schema.properties) {
      const defaultContent: Record<string, any> = {}
      const properties = type.json_schema.properties || {}
      const required = type.json_schema.required || []
      
      for (const [key, fieldSchema] of Object.entries(properties)) {
        const schema = fieldSchema as Record<string, any>
        
        // 如果是必填字段或已有默认值，生成内容
        if (required.includes(key) || schema.default !== undefined) {
          if (schema.default !== undefined) {
            defaultContent[key] = schema.default
          } else if (schema.type === 'string') {
            defaultContent[key] = schema.example || ''
          } else if (schema.type === 'number' || schema.type === 'integer') {
            defaultContent[key] = schema.default || 0
          } else if (schema.type === 'boolean') {
            defaultContent[key] = schema.default || false
          } else if (schema.type === 'array') {
            defaultContent[key] = schema.default || []
          } else if (schema.type === 'object') {
            defaultContent[key] = schema.default || {}
          }
        }
      }
      
      // 如果当前内容为空，或者是在新建模式下，应用默认内容
      if (!isEdit.value && (!cardContent.value || Object.keys(cardContent.value).length === 0)) {
        cardContent.value = defaultContent
      }
    }
  }
}

// 处理项目选择变化
const handleProjectChange = (projectId: number | null) => {
  console.log('项目选择变化:', projectId, '类型:', typeof projectId)
  if (projectId) {
    form.value.project_id = projectId
    console.log('项目ID已更新:', form.value.project_id, '项目名称:', projects.value.find(p => p.id === projectId)?.name)
    // 项目改变时重新加载卡片树
    loadCardTree()
  } else {
    form.value.project_id = null
    console.log('项目ID已清空')
    cardTree.value = []
  }
}

// 处理内容更新
const handleContentUpdate = (content: Record<string, any>) => {
  cardContent.value = { ...cardContent.value, ...content }
  needs_review.value = false
  scheduleValidateContent()
}

const handleContentChange = () => {
  needs_review.value = false
  scheduleValidateContent()
}

// 处理父卡片变化
const handleParentChange = () => {
  // 父卡片选择后更新显示顺序
  if (form.value.parent_id) {
    // 查找子卡片数量
    const currentProjectId = projectId.value || form.value.project_id
    cardAPI.getCards({
      project_id: currentProjectId,
      parent_id: form.value.parent_id,
      skip: 0,
      limit: 1000
    }).then(response => {
      form.value.display_order = response.length
    }).catch(error => {
      console.error('获取子卡片数量失败:', error)
    })
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 切换字段排序
const toggleFieldOrder = () => {
  fieldOrder.value = !fieldOrder.value
  if (fieldOrder.value) {
    ElMessage.success('已启用字段排序，拖拽字段即可调整顺序')
  } else {
    ElMessage.info('已取消字段排序')
  }
}

const syncJsonFromForm = () => {
  try {
    contentJsonText.value = JSON.stringify(cardContent.value ?? {}, null, 2)
    jsonParseError.value = ''
  } catch (e: any) {
    jsonParseError.value = e?.message || '无法序列化'
  }
}

const applyJsonToForm = () => {
  try {
    const parsed = JSON.parse(contentJsonText.value || '{}')
    cardContent.value = parsed && typeof parsed === 'object' ? parsed : {}
    jsonParseError.value = ''
    needs_review.value = false
    scheduleValidateContent()
    ElMessage.success('已应用到表单')
  } catch (e: any) {
    jsonParseError.value = 'JSON解析错误：' + (e?.message || '')
  }
}

const formatJsonContent = () => {
  try {
    const parsed = JSON.parse(contentJsonText.value || '{}')
    contentJsonText.value = JSON.stringify(parsed, null, 2)
    jsonParseError.value = ''
    ElMessage.success('已格式化')
  } catch (e: any) {
    jsonParseError.value = 'JSON解析错误：' + (e?.message || '')
  }
}

// 监听路由变化
watch(() => route.params.id, () => {
  if (cardId.value) {
    loadCard()
  }
})

// 监听项目ID变化，更新项目选择器
watch(() => projectId.value, (newProjectId) => {
  if (newProjectId) {
    const project = projects.value.find(p => p.id === newProjectId)
    if (project) {
      console.log('项目ID已设置:', newProjectId, '项目名称:', project.name)
    }
    if (!isEdit.value) {
      form.value.project_id = newProjectId
    } else if (isEdit.value) {
      console.log('编辑卡片 - 项目ID已更新:', newProjectId)
      form.value.project_id = newProjectId
    }
  } else {
    console.log('项目ID已清空')
  }
})

// 监听卡片类型变化，重置表单
watch(() => form.value.card_type_id, (newTypeId) => {
  if (newTypeId && !isEdit.value) {
    // 当选择新的卡片类型时，重置内容
    cardContent.value = {}
    console.log('卡片类型已切换，内容已重置')
  }

  if (newTypeId) {
    // 编辑/新建都要确保 currentCardType 被设置
    handleCardTypeChange()
  }
})

watch(cardTypes, () => {
  if (!currentCardType.value && form.value.card_type_id) {
    handleCardTypeChange()
  }
}, { deep: true })

watch(() => currentCardType.value?.json_schema, () => {
  const schema = normalizedJsonSchema.value
  try {
    validateFn.value = schema ? ajv.compile(schema as any) : null
  } catch {
    validateFn.value = null
  }
  scheduleValidateContent()
  syncJsonFromForm()
}, { deep: true })

watch(() => cardContent.value, () => {
  if (contentMode.value !== 'json') {
    syncJsonFromForm()
  }
  scheduleValidateContent()
}, { deep: true })

let jsonDebounceTimer: number | null = null
watch(() => contentJsonText.value, (txt) => {
  if (contentMode.value !== 'json') return
  if (jsonDebounceTimer) window.clearTimeout(jsonDebounceTimer)
  jsonDebounceTimer = window.setTimeout(() => {
    jsonDebounceTimer = null
    try {
      JSON.parse(txt || '{}')
      jsonParseError.value = ''
    } catch (e: any) {
      jsonParseError.value = 'JSON解析错误：' + (e?.message || '')
    }
  }, 250)
})

onMounted(async () => {
  console.log('=== CardEditor 组件挂载 ===')
  console.log('路由名称:', route.name)
  console.log('路由参数:', route.query)
  console.log('编辑模式:', isEdit.value)

  // 加载项目列表
  await loadProjects()

  // 加载卡片类型
  await loadCardTypes()

  // 如果是编辑模式，加载卡片数据
  if (cardId.value) {
    await loadCard()
    console.log('编辑模式 - 加载完成，form.value.parent_id:', form.value.parent_id)
    // 加载卡片树用于父卡片选择（loadCard后form.value.project_id已设置）
    await loadCardTree()
    console.log('卡片树加载完成，当前选中父ID:', form.value.parent_id)
  } else {
    // 创建模式：从路由参数获取项目ID
    if (projectId.value) {
      form.value.project_id = projectId.value
      console.log('创建模式 - 初始化项目ID:', projectId.value)
    }
  }

  console.log('=== 组件挂载完成 ===')
})
</script>

<style scoped>
.card-editor {
  padding: 0;
}

.card-editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.field-order-controls {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.content-tabs {
  margin-top: 6px;
}

.json-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.hint {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.header-left {
  align-items: center;
  gap: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 8px;
}

.dynamic-content {
  margin-bottom: 20px;
}

:deep(.el-divider__text) {
  font-weight: 600;
  font-size: 14px;
}
</style>