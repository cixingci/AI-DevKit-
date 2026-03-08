<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon project-icon"><Folder /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ projectCount }}</div>
              <div class="stat-label">项目总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon card-icon"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ cardCount }}</div>
              <div class="stat-label">卡片总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon workflow-icon"><Connection /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ workflowCount }}</div>
              <div class="stat-label">工作流数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon task-icon"><Operation /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ runningWorkflows }}</div>
              <div class="stat-label">运行中的工作流</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最近项目</span>
              <el-button type="primary" size="small" @click="navigateTo('/projects')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentProjects" style="width: 100%">
            <el-table-column prop="name" label="项目名称" />
            <el-table-column prop="card_count" label="卡片数" width="100" />
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <el-space direction="vertical" fill>
            <el-button type="primary" :icon="Plus" @click="createNewProject">新建项目</el-button>
            <el-button type="success" :icon="Plus" @click="createNewCard">新建卡片</el-button>
            <el-button type="warning" :icon="Setting" @click="openWorkflowStudio">工作流工作室</el-button>
            <el-button type="info" :icon="Lightbulb" @click="openAIAssistant">AI助手</el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>AI生成建议</span>
            </div>
          </template>
          <div class="ai-suggestions">
            <el-empty v-if="!aiSuggestions.length" description="暂无建议" />
            <div v-else class="suggestion-list">
              <el-alert
                v-for="(suggestion, index) in aiSuggestions"
                :key="index"
                :title="suggestion.title"
                :description="suggestion.description"
                :type="suggestion.type"
                :closable="false"
                show-icon
                class="mb-10"
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Folder,
  Document,
  Connection,
  Operation,
  Plus,
  Setting
} from '@element-plus/icons-vue'

const router = useRouter()
const projectCount = ref(0)
const cardCount = ref(0)
const workflowCount = ref(0)
const runningWorkflows = ref(0)
const recentProjects = ref<any[]>([])
const aiSuggestions = ref<any[]>([])

onMounted(async () => {
  await loadDashboardData()
})

const loadDashboardData = async () => {
  try {
    // 加载统计数据
    const response = await fetch('/api/v1/projects?skip=0&limit=5')
    const data = await response.json()
    projectCount.value = data.length
    
    // 加载卡片统计
    const cardsResponse = await fetch('/api/v1/cards?limit=1000')
    const cardsData = await cardsResponse.json()
    cardCount.value = cardsData.length
    
    // 加载工作流统计
    const workflowsResponse = await fetch('/api/v1/workflows?skip=0&limit=1000')
    const workflowsData = await workflowsResponse.json()
    workflowCount.value = workflowsData.length
    
    // 模拟运行中的工作流
    runningWorkflows.value = Math.floor(Math.random() * 5)
    
    // 加载最近项目
    recentProjects.value = data.slice(0, 5)
    
    // 加载AI建议
    aiSuggestions.value = [
      {
        title: '项目初始化建议',
        description: '建议使用"项目初始化"工作流快速搭建基础结构',
        type: 'success'
      },
      {
        title: '代码质量优化',
        description: '当前项目有3个卡片未完成，建议完成后再进行AI生成',
        type: 'warning'
      },
      {
        title: '新增工作流',
        description: '您可以创建自定义工作流自动化日常开发任务',
        type: 'info'
      }
    ]
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

const navigateTo = (path: string) => {
  router.push(path)
}

const createNewProject = () => {
  ElMessage.success('新建项目功能开发中...')
}

const createNewCard = () => {
  ElMessage.success('新建卡片功能开发中...')
}

const openWorkflowStudio = () => {
  router.push('/workflows')
}

const openAIAssistant = () => {
  ElMessage.success('AI助手功能开发中...')
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    'active': 'success',
    'planning': 'warning',
    'completed': 'info',
    'archived': 'default'
  }
  return typeMap[status] || 'default'
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-icon {
  font-size: 48px;
  opacity: 0.8;
}

.project-icon {
  color: #409eff;
}

.card-icon {
  color: #67c23a;
}

.workflow-icon {
  color: #e6a23c;
}

.task-icon {
  color: #f56c6c;
}

.stat-info {
  flex: 1;
  margin-left: 20px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.mt-20 {
  margin-top: 20px;
}

.mt-10 {
  margin-top: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-suggestions {
  min-height: 200px;
}

.suggestion-list {
  width: 100%;
}

.mb-10 {
  margin-bottom: 10px;
}
</style>