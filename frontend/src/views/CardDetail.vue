<template>
  <div class="card-detail">
    <el-page-header @back="goBack" content="卡片详情" />
    <el-card class="content-card" v-loading="loading">
      <template v-if="card">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="标题">{{ card.title }}</el-descriptions-item>
          <el-descriptions-item label="卡片类型">
            <el-tag :type="getCardTypeColor(card.card_type)" size="small">
              {{ card.card_type?.name }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ card.description }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(card.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(card.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="AI生成" :span="2">
            <el-tag :type="card.ai_generated ? 'success' : 'info'" size="small">
              {{ card.ai_generated ? '已生成' : '未生成' }}
            </el-tag>
            <el-tag v-if="card.needs_review" type="warning" size="small" style="margin-left: 10px;">
              需要审核
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div v-if="card.content && Object.keys(card.content).length > 0" class="content-section">
          <h3>详细内容</h3>
          <pre>{{ JSON.stringify(card.content, null, 2) }}</pre>
        </div>
      </template>
      <el-empty v-else description="加载中..." />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const card = ref<any>(null)

const loadCard = async () => {
  const cardId = parseInt(route.params.id as string)
  if (!cardId) return

  loading.value = true
  try {
    const response = await fetch(`/api/v1/cards/${cardId}`)
    if (response.ok) {
      card.value = await response.json()
    } else {
      ElMessage.error('加载卡片失败')
    }
  } catch (error) {
    console.error('加载卡片失败:', error)
    ElMessage.error('加载卡片失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
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
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadCard()
})
</script>

<style scoped>
.card-detail {
  padding: 20px;
}

.content-card {
  margin-top: 20px;
}

.content-section {
  margin-top: 20px;
}

.content-section h3 {
  margin-top: 0;
  color: #303133;
}

pre {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
