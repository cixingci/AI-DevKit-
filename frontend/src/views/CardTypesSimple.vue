<template>
  <div class="test-page">
    <h1>卡片类型管理测试页面</h1>

    <el-button type="primary" @click="loadCardTypes">加载卡片类型</el-button>

    <div v-if="loading" style="margin-top: 20px;">
      <el-progress :percentage="50" />
    </div>

    <div v-if="cardTypes.length === 0 && !loading" class="empty-state">
      <el-empty description="暂无数据" :image-size="150" />
    </div>

    <div v-else class="card-types-grid">
      <el-card v-for="type in cardTypes" :key="type.id" class="type-card">
        <template #header>
          <div class="card-header">
            <h3>{{ type.name }}</h3>
            <el-tag :type="getTypeColor(type.name)" size="small">ID: {{ type.id }}</el-tag>
          </div>
        </template>

        <div class="card-content">
          <p><strong>描述:</strong> {{ type.description }}</p>
          <p><strong>创建时间:</strong> {{ formatDate(type.created_at) }}</p>
          <p><strong>JSON Schema:</strong></p>
          <pre class="json-schema">{{ formatJson(type.json_schema) }}</pre>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const loading = ref(false)
const cardTypes = ref<any[]>([])

const loadCardTypes = async () => {
  loading.value = true
  try {
    console.log('开始加载卡片类型...')
    const response = await axios.get('http://localhost:8888/api/v1/card-types')
    cardTypes.value = response.data
    console.log('成功加载卡片类型:', cardTypes.value)
    console.log('卡片类型数量:', cardTypes.value.length)
  } catch (error) {
    console.error('加载失败:', error)
    alert('加载失败: ' + (error as any).message)
  } finally {
    loading.value = false
  }
}

const formatJson = (obj: any) => {
  try {
    return JSON.stringify(obj, null, 2)
  } catch (e) {
    return String(obj)
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const getTypeColor = (name: string) => {
  const colors: Record<string, string> = {
    '需求卡': 'primary',
    '设计卡': 'success',
    '功能卡': 'warning',
    '测试卡': 'danger',
    '文档卡': 'info'
  }
  return colors[name] || 'info'
}

onMounted(() => {
  console.log('CardTypes组件已挂载')
  loadCardTypes()
})
</script>

<style scoped>
.test-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #303133;
  margin-bottom: 20px;
}

.card-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.type-card {
  transition: all 0.3s ease;
}

.type-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.card-content {
  line-height: 1.8;
}

.card-content p {
  margin: 8px 0;
  color: #606266;
}

.card-content strong {
  color: #303133;
}

.json-schema {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
}

.empty-state {
  margin-top: 50px;
}
</style>
