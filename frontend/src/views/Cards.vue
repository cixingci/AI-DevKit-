<template>
  <div class="cards-page">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <el-select
        v-model="selectedProject"
        placeholder="选择项目"
        @change="handleProjectChange"
        style="width: 300px"
      >
        <el-option
          v-for="project in projects"
          :key="project.id"
          :label="project.name"
          :value="project.id"
        />
      </el-select>
      <el-button type="primary" :icon="Plus" @click="createCard" :disabled="!selectedProject">
        新建卡片
      </el-button>
      <el-input
        v-model="searchQuery"
        placeholder="搜索卡片..."
        :prefix-icon="Search"
        clearable
        style="width: 300px; margin-left: 20px"
      />
    </div>

    <!-- 主内容区：左侧树 + 右侧卡片 -->
    <div class="main-content">
      <!-- 左侧卡片树 -->
      <div class="card-tree-panel">
        <div class="panel-header">
          <span>卡片层级</span>
          <el-tooltip content="拖拽调整层级和顺序" placement="top">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
        <div class="tree-container" v-loading="treeLoading">
          <el-tree
            v-if="cardTree.length > 0"
            :data="cardTree"
            :props="treeProps"
            node-key="id"
            :expand-on-click-node="false"
            :default-expand-all="true"
            :filter-node-method="filterNode"
            ref="treeRef"
            draggable
            :allow-drop="allowDrop"
            @node-drop="handleNodeDrop"
            @node-click="handleNodeClick"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <el-icon class="node-icon" :class="{ 'ai-generated': data.ai_generated }">
                  <Document />
                </el-icon>
                <span class="node-label">{{ node.label }}</span>
                <el-tag v-if="data.ai_generated" type="success" size="small" class="node-tag">AI</el-tag>
              </div>
            </template>
          </el-tree>
          <el-empty v-else description="暂无卡片" :image-size="80" />
        </div>
      </div>

      <!-- 右侧卡片详情/编辑 -->
      <div class="card-detail-panel">
        <template v-if="selectedCard">
          <!-- 编辑模式 -->
          <div v-if="isEditing" class="edit-form">
            <div class="detail-header">
              <div class="detail-title">
                <h2>编辑卡片</h2>
              </div>
              <div class="detail-actions">
                <el-button @click="cancelEdit">取消</el-button>
                <el-button type="primary" :icon="DocumentChecked" @click="saveCard" :loading="saving">
                  保存
                </el-button>
              </div>
            </div>
            
            <el-divider />
            
            <el-form :model="editForm" label-width="100px" class="card-edit-form">
              <el-form-item label="标题">
                <el-input v-model="editForm.title" placeholder="请输入卡片标题" />
              </el-form-item>
              
              <el-form-item label="卡片类型">
                <el-select v-model="editForm.card_type_id" placeholder="选择卡片类型" style="width: 100%">
                  <el-option
                    v-for="type in cardTypes"
                    :key="type.id"
                    :label="type.name"
                    :value="type.id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="父卡片">
                <el-tree-select
                  v-model="editForm.parent_id"
                  :data="cardTree"
                  :props="treeProps"
                  placeholder="选择父卡片"
                  clearable
                  check-strictly
                  :render-after-expand="false"
                  style="width: 100%"
                />
              </el-form-item>
              
              <el-form-item label="描述">
                <el-input
                  v-model="editForm.content.description"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入描述"
                />
              </el-form-item>
              
              <el-form-item label="核心内容">
                <div class="content-editor">
                  <div v-for="(value, key) in editForm.content" :key="key" class="content-field">
                    <template v-if="key !== 'description'">
                      <el-input
                        v-if="typeof value === 'string'"
                        v-model="editForm.content[key]"
                        :placeholder="String(key)"
                      >
                        <template #prepend>{{ key }}</template>
                      </el-input>
                      <div v-else class="field-editor">
                        <span class="field-label">{{ key }}:</span>
                        <el-input
                          v-model="editForm.content[key]"
                          type="textarea"
                          :rows="2"
                        />
                      </div>
                    </template>
                  </div>
                  <el-button size="small" @click="addContentField">添加字段</el-button>
                </div>
              </el-form-item>
              
              <el-form-item label="排序">
                <el-input-number v-model="editForm.display_order" :min="1" />
              </el-form-item>
            </el-form>
          </div>
          
          <!-- 查看模式 -->
          <div v-else class="detail-view">
            <div class="detail-header">
              <div class="detail-title">
                <h2>{{ selectedCard.title }}</h2>
                <el-tag :type="getCardTypeColor(selectedCard.card_type)" size="small">
                  {{ selectedCard.card_type?.name }}
                </el-tag>
              </div>
              <div class="detail-actions">
                <el-button type="primary" :icon="Edit" @click="startEdit">
                  编辑
                </el-button>
                <el-button type="danger" :icon="Delete" @click="deleteCard(selectedCard.id)">
                  删除
                </el-button>
              </div>
            </div>
            
            <el-divider />

            <div class="detail-content">
              <div class="content-section">
                <h4>描述</h4>
                <p>{{ selectedCard.content?.description || '暂无描述' }}</p>
              </div>

              <div class="content-section" v-if="selectedCard.content && Object.keys(selectedCard.content).length > 1">
                <h4>详细内容</h4>
                <el-descriptions :column="2" border>
                  <el-descriptions-item
                    v-for="(value, key) in selectedCard.content"
                    :key="key"
                    :label="String(key)"
                    v-show="key !== 'description'"
                  >
                    {{ typeof value === 'object' ? JSON.stringify(value) : value }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>

              <div class="content-section meta-info">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="meta-item">
                      <span class="label">父卡片：</span>
                      <span>{{ selectedCard.parent_id ? getParentTitle(selectedCard.parent_id) : '无' }}</span>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="meta-item">
                      <span class="label">排序：</span>
                      <span>{{ selectedCard.display_order }}</span>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="meta-item">
                      <span class="label">创建时间：</span>
                      <span>{{ formatDate(selectedCard.created_at) }}</span>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="meta-item">
                      <span class="label">更新时间：</span>
                      <span>{{ formatDate(selectedCard.updated_at) }}</span>
                    </div>
                  </el-col>
                </el-row>
              </div>

              <div class="content-section" v-if="selectedCard.ai_generated">
                <el-tag type="success" effect="dark">AI生成</el-tag>
              </div>
            </div>
          </div>
        </template>
        <el-empty v-else description="点击左侧卡片查看详情" :image-size="120" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Edit,
  Delete,
  Document,
  InfoFilled,
  DocumentChecked
} from '@element-plus/icons-vue'
import { cardAPI, projectAPI, cardTypeAPI } from '@/services/api'

const router = useRouter()

const loading = ref(false)
const treeLoading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const selectedProject = ref<number | null>(null)
const projects = ref<any[]>([])
const cardTree = ref<any[]>([])
const selectedCard = ref<any | null>(null)
const treeRef = ref()

// 编辑相关
const isEditing = ref(false)
const editForm = ref({
  title: '',
  card_type_id: null as number | null,
  parent_id: null as number | null,
  display_order: 1,
  content: {} as Record<string, any>
})
const cardTypes = ref<any[]>([])

const treeProps = {
  children: 'children',
  label: 'title',
  value: 'id'
}

const filteredCardTree = computed(() => {
  if (!searchQuery.value) return cardTree.value
  const query = searchQuery.value.toLowerCase()
  return filterTree(cardTree.value, query)
})

const filterTree = (nodes: any[], query: string): any[] => {
  const result: any[] = []
  for (const node of nodes) {
    const titleMatch = node.title?.toLowerCase().includes(query)
    const children = node.children ? filterTree(node.children, query) : []
    if (titleMatch || children.length > 0) {
      result.push({
        ...node,
        children: titleMatch ? node.children : children
      })
    }
  }
  return result
}

const filterNode = (value: string, data: any) => {
  if (!value) return true
  return data.title?.toLowerCase().includes(value.toLowerCase())
}

const loadProjects = async () => {
  try {
    const response = await projectAPI.getProjects({ skip: 0, limit: 100 })
    projects.value = response || []
  } catch (error) {
    console.error('加载项目失败:', error)
    ElMessage.error('加载项目失败')
  }
}

const loadCardTree = async () => {
  if (!selectedProject.value) {
    cardTree.value = []
    return
  }

  treeLoading.value = true
  try {
    const response = await cardAPI.getCardTree(selectedProject.value)
    cardTree.value = response || []
    console.log('卡片树加载完成:', cardTree.value)
  } catch (error) {
    console.error('加载卡片树失败:', error)
    ElMessage.error('加载卡片树失败')
  } finally {
    treeLoading.value = false
  }
}

const handleProjectChange = async () => {
  selectedCard.value = null
  await loadCardTree()
}

const handleNodeClick = (data: any) => {
  selectedCard.value = data
}

const allowDrop = (draggingNode: any, dropNode: any, type: string) => {
  // 不能将父节点拖到自己的子节点下
  if (isDescendant(draggingNode, dropNode)) {
    return false
  }
  return true
}

const isDescendant = (parent: any, node: any): boolean => {
  if (!node.children) return false
  for (const child of node.children) {
    if (child.id === parent.id) return true
    if (isDescendant(parent, child)) return true
  }
  return false
}

const handleNodeDrop = async (draggingNode: any, dropNode: any, dropType: string) => {
  console.log('拖拽完成:', draggingNode.data.id, dropType, dropNode.data.id)
  
  const cardId = draggingNode.data.id
  let newParentId: number | null = null
  let newOrder = dropNode.data.display_order || 1

  if (dropType === 'inner') {
    // 拖入目标节点内部，成为其子节点
    newParentId = dropNode.data.id
  } else if (dropType === 'before' || dropType === 'after') {
    // 拖到目标节点前后，与目标节点同级
    newParentId = dropNode.data.parent_id
    if (dropType === 'before') {
      newOrder = dropNode.data.display_order
    } else {
      newOrder = dropNode.data.display_order + 1
    }
  }

  try {
    await cardAPI.moveCard(cardId, newParentId, newOrder)
    ElMessage.success('卡片移动成功')
    await loadCardTree()
  } catch (error: any) {
    console.error('移动卡片失败:', error)
    ElMessage.error('移动失败: ' + (error.response?.data?.detail || error.message))
    await loadCardTree()
  }
}

const getParentTitle = (parentId: number): string => {
  const findInTree = (nodes: any[]): string | null => {
    for (const node of nodes) {
      if (node.id === parentId) return node.title
      if (node.children) {
        const found = findInTree(node.children)
        if (found) return found
      }
    }
    return null
  }
  return findInTree(cardTree.value) || '未知'
}

const createCard = () => {
  if (!selectedProject.value) {
    ElMessage.warning('请先选择一个项目')
    return
  }
  router.push(`/cards/create?project_id=${selectedProject.value}`)
}

const editCard = (card: any) => {
  router.push(`/cards/${card.id}/edit?project_id=${selectedProject.value}`)
}

const deleteCard = async (id: number) => {
  if (!selectedProject.value) {
    ElMessage.warning('请先选择一个项目')
    return
  }

  try {
    await ElMessageBox.confirm('确定要删除这个卡片吗？此操作不可恢复。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await cardAPI.deleteCard(id, selectedProject.value || undefined)
    ElMessage.success('卡片删除成功')
    selectedCard.value = null
    await loadCardTree()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除卡片失败:', error)
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

const loadCardTypes = async () => {
  try {
    const response = await cardTypeAPI.getCardTypes()
    cardTypes.value = response || []
  } catch (error) {
    console.error('加载卡片类型失败:', error)
  }
}

const startEdit = () => {
  if (!selectedCard.value) return
  editForm.value = {
    title: selectedCard.value.title,
    card_type_id: selectedCard.value.card_type_id,
    parent_id: selectedCard.value.parent_id,
    display_order: selectedCard.value.display_order,
    content: { ...selectedCard.value.content } || {}
  }
  isEditing.value = true
}

const cancelEdit = () => {
  isEditing.value = false
}

const saveCard = async () => {
  if (!selectedCard.value || !selectedProject.value) return
  
  if (!editForm.value.title) {
    ElMessage.warning('请输入卡片标题')
    return
  }

  saving.value = true
  try {
    await cardAPI.updateCard(selectedCard.value.id, {
      title: editForm.value.title,
      card_type_id: editForm.value.card_type_id,
      parent_id: editForm.value.parent_id,
      display_order: editForm.value.display_order,
      content: editForm.value.content,
      project_id: selectedProject.value
    })
    ElMessage.success('保存成功')
    isEditing.value = false
    await loadCardTree()
    
    // 更新选中卡片
    const updatedCard = await cardAPI.getCard(selectedCard.value.id)
    selectedCard.value = updatedCard
  } catch (error: any) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const addContentField = () => {
  const fieldName = prompt('请输入字段名称:')
  if (fieldName) {
    editForm.value.content[fieldName] = ''
  }
}

const getCardTypeColor = (cardType: any) => {
  const typeColors: Record<string, string> = {
    '需求卡': 'primary',
    '设计卡': 'success',
    '功能卡': 'warning',
    '测试卡': 'danger',
    '文档卡': 'info'
  }
  return typeColors[cardType?.name] || 'info'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

watch(searchQuery, (val) => {
  treeRef.value?.filter(val)
})

onMounted(async () => {
  await loadProjects()
  await loadCardTypes()

  const params = new URLSearchParams(window.location.search)
  const projectIdFromUrl = params.get('project_id')

  if (projectIdFromUrl) {
    selectedProject.value = parseInt(projectIdFromUrl)
    await loadCardTree()
    localStorage.setItem('lastEditedProjectId', projectIdFromUrl)
  } else {
    const lastProjectId = localStorage.getItem('lastEditedProjectId')
    if (lastProjectId && projects.value.some(p => p.id === parseInt(lastProjectId))) {
      selectedProject.value = parseInt(lastProjectId)
      await loadCardTree()
    } else if (projects.value.length > 0) {
      selectedProject.value = projects.value[0].id
      await loadCardTree()
    }
  }
})
</script>

<style scoped>
.cards-page {
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.toolbar {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  gap: 16px;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.card-tree-panel {
  width: 350px;
  min-width: 280px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  font-weight: 600;
  border-bottom: 1px solid #e4e7ed;
}

.tree-container {
  flex: 1;
  overflow: auto;
  padding: 12px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
}

.node-icon {
  flex-shrink: 0;
}

.node-icon.ai-generated {
  color: #67c23a;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-tag {
  flex-shrink: 0;
  margin-left: 4px;
}

.card-detail-panel {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background: #f5f7fa;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.detail-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-title h2 {
  margin: 0;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.detail-content {
  margin-top: 16px;
}

.content-section {
  margin-bottom: 24px;
}

.content-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
}

.content-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.meta-info .meta-item {
  display: flex;
  margin-bottom: 8px;
}

.meta-info .label {
  color: #909399;
  min-width: 70px;
}

:deep(.el-tree) {
  background: transparent;
}

:deep(.el-tree-node__content) {
  height: 32px;
}

:deep(.el-tree-node.is-drop-inner > .el-tree-node__content) {
  background-color: #ecf5ff;
}

.edit-form {
  padding: 0;
}

.card-edit-form {
  padding: 0 20px;
}

.content-editor {
  width: 100%;
}

.content-field {
  margin-bottom: 12px;
}

.field-editor {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-label {
  font-size: 12px;
  color: #606266;
}
</style>
