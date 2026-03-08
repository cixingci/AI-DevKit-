<template>
  <div class="projects">
    <div class="toolbar">
      <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
        新建项目
      </el-button>
      <el-input
        v-model="searchQuery"
        placeholder="搜索项目..."
        :prefix-icon="Search"
        clearable
        style="width: 300px; margin-left: 20px"
      />
    </div>

    <el-table
      :data="filteredProjects"
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="name" label="项目名称" width="200">
        <template #default="{ row }">
          <div class="project-name">
            <el-icon><Folder /></el-icon>
            {{ row.name }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="card_count" label="卡片数" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            :icon="View"
            @click="viewProject(row.id)"
          >
            查看项目
          </el-button>
          <el-button
            type="danger"
            size="small"
            :icon="Delete"
            @click="deleteProject(row.id)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建项目"
      width="500px"
    >
      <el-form :model="projectForm" :rules="rules" ref="projectFormRef" label-width="100px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createProject" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Folder,
  Delete,
  View
} from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const creating = ref(false)
const searchQuery = ref('')
const showCreateDialog = ref(false)

const projects = ref<any[]>([])
const projectFormRef = ref()

const projectForm = ref({
  name: '',
  description: ''
})

const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 1, max: 100, message: '项目名称长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '项目描述不能超过 500 个字符', trigger: 'blur' }
  ]
}

const filteredProjects = computed(() => {
  if (!searchQuery.value) return projects.value
  const query = searchQuery.value.toLowerCase()
  return projects.value.filter(p =>
    p.name.toLowerCase().includes(query) ||
    (p.description && p.description.toLowerCase().includes(query))
  )
})

const loadProjects = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/v1/projects?skip=0&limit=100')
    projects.value = await response.json()
  } catch (error) {
    console.error('加载项目失败:', error)
    ElMessage.error('加载项目失败')
  } finally {
    loading.value = false
  }
}

const createProject = async () => {
  if (!projectFormRef.value) return
  
  await projectFormRef.value.validate(async (valid) => {
    if (valid) {
      creating.value = true
      try {
        const response = await fetch('/api/v1/projects', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: projectForm.value.name,
            description: projectForm.value.description
          })
        })
        
        if (response.ok) {
          ElMessage.success('项目创建成功')
          showCreateDialog.value = false
          projectForm.value = { name: '', description: '' }
          await loadProjects()
        } else {
          ElMessage.error('项目创建失败')
        }
      } catch (error) {
        console.error('创建项目失败:', error)
        ElMessage.error('创建项目失败')
      } finally {
        creating.value = false
      }
    }
  })
}

const deleteProject = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个项目吗？此操作不可恢复。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await fetch(`/api/v1/projects/${id}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('项目删除成功')
      await loadProjects()
    } else {
      ElMessage.error('项目删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除项目失败:', error)
      ElMessage.error('删除项目失败')
    }
  }
}

const viewProject = (id: number) => {
  router.push(`/projects/${id}`)
}

const formatDate = (dateStr: string) => {
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
  loadProjects()
})
</script>

<style scoped>
.projects {
  padding: 0;
}

.toolbar {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  position: sticky;
  top: 0;
  z-index: 100;
}

.project-name {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  font-weight: 500;
}
</style>