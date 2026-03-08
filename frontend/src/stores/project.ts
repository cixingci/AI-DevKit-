import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Project, Card } from '@/types'

export const useProjectStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)

  const activeProject = computed(() => currentProject.value)

  // 加载项目列表
  const loadProjects = async () => {
    loading.value = true
    try {
      const response = await fetch('/api/v1/projects?skip=0&limit=100')
      projects.value = await response.json()
    } catch (error) {
      console.error('加载项目失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 加载项目详情
  const loadProject = async (id: number) => {
    loading.value = true
    try {
      const response = await fetch(`/api/v1/projects/${id}`)
      currentProject.value = await response.json()
    } catch (error) {
      console.error('加载项目详情失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 创建新项目
  const createProject = async (name: string, description?: string) => {
    try {
      const response = await fetch('/api/v1/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, description })
      })

      if (response.ok) {
        const newProject = await response.json()
        projects.value.unshift(newProject)
        currentProject.value = newProject
        return newProject
      }
    } catch (error) {
      console.error('创建项目失败:', error)
    }
    return null
  }

  // 删除项目
  const deleteProject = async (id: number) => {
    try {
      const response = await fetch(`/api/v1/projects/${id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        projects.value = projects.value.filter(p => p.id !== id)
        if (currentProject.value?.id === id) {
          currentProject.value = null
        }
      }
    } catch (error) {
      console.error('删除项目失败:', error)
    }
  }

  // 切换当前项目
  const selectProject = (project: Project) => {
    currentProject.value = project
  }

  return {
    projects,
    currentProject,
    activeProject,
    loading,
    loadProjects,
    loadProject,
    createProject,
    deleteProject,
    selectProject
  }
})