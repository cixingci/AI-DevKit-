<template>
  <div class="project-detail">
    <el-page-header @back="goBack" :content="project?.name" />
    <el-card class="content-card" v-loading="loading">
      <template v-if="project">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">{{ project.name }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ project.description }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(project.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="卡片数量">{{ project.card_count }}</el-descriptions-item>
        </el-descriptions>
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
const project = ref<any>(null)

const loadProject = async () => {
  const projectId = parseInt(route.params.id as string)
  if (!projectId) return

  loading.value = true
  try {
    const response = await fetch(`/api/v1/projects/${projectId}`)
    if (response.ok) {
      project.value = await response.json()
    } else {
      ElMessage.error('加载项目失败')
    }
  } catch (error) {
    console.error('加载项目失败:', error)
    ElMessage.error('加载项目失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
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
  loadProject()
})
</script>

<style scoped>
.project-detail {
  padding: 20px;
}

.content-card {
  margin-top: 20px;
}
</style>
