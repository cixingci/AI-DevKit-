import axios from 'axios'
import type { Project, Card } from '@/types'

const api = axios.create({
  baseURL: 'http://localhost:8888/api/v1',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加认证token等
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API错误:', error)
    return Promise.reject(error)
  }
)

// 项目API
export const projectAPI = {
  // 获取项目列表
  getProjects: (params?: { skip?: number, limit?: number }) => {
    return api.get('/projects', { params })
  },

  // 获取项目详情
  getProject: (id: number) => {
    return api.get(`/projects/${id}`)
  },

  // 创建项目
  createProject: (data: { name: string, description?: string }) => {
    return api.post('/projects', data)
  },

  // 更新项目
  updateProject: (id: number, data: Partial<Project>) => {
    return api.put(`/projects/${id}`, data)
  },

  // 删除项目
  deleteProject: (id: number) => {
    return api.delete(`/projects/${id}`)
  }
}

// 卡片API
export const cardAPI = {
  // 获取卡片列表
  getCards: (params?: {
    project_id?: number,
    card_type?: string,
    parent_id?: number,
    skip?: number,
    limit?: number
  }) => {
    return api.get('/cards', { params })
  },

  // 获取卡片详情
  getCard: (id: number) => {
    return api.get(`/cards/${id}`)
  },

  // 创建卡片
  createCard: (data: {
    title: string,
    content: any,
    card_type_id?: number,
    parent_id?: number,
    display_order?: number
  }) => {
    return api.post('/cards', data)
  },

  // 更新卡片
  updateCard: (id: number, data: {
    title?: string,
    content?: any,
    card_type_id?: number,
    parent_id?: number,
    display_order?: number,
    project_id?: number
  }) => {
    const params = data.project_id ? { project_id: data.project_id } : {}
    const { project_id, ...body } = data
    return api.put(`/cards/${id}`, body, { params })
  },

  // 删除卡片
  deleteCard: (id: number, projectId?: number) => {
    const params = projectId ? { project_id: projectId } : {}
    return api.delete(`/cards/${id}`, { params })
  },

  // AI生成卡片
  aiGenerate: (id: number, prompt: string) => {
    return api.post(`/cards/${id}/ai-generate`, { prompt })
  },

  // 获取卡片子项
  getCardChildren: (id: number) => {
    return api.get(`/cards/${id}/children`)
  },

  // 获取卡片树
  getCardTree: (projectId: number) => {
    return api.get('/cards/tree', { params: { project_id: projectId } })
  },

  // 移动卡片（调整层级或顺序）
  moveCard: (cardId: number, newParentId?: number | null, newOrder?: number) => {
    const params: any = {}
    if (newParentId !== undefined) {
      params.new_parent_id = newParentId === null ? 0 : newParentId
    }
    if (newOrder !== undefined) {
      params.new_order = newOrder
    }
    return api.patch(`/cards/${cardId}/move`, {}, { params })
  }
}

// 卡片类型API
export const cardTypeAPI = {
  // 获取卡片类型列表
  getCardTypes: () => {
    return api.get('/card-types')
  },

  // 创建卡片类型
  createCardType: (data: {
    name: string,
    description?: string,
    json_schema?: any,
    ai_params?: any
  }) => {
    return api.post('/card-types', data)
  }
}

// 工作流API
export const workflowAPI = {
  // 获取工作流列表
  getWorkflows: (params?: { skip?: number, limit?: number }) => {
    return api.get('/workflows', { params })
  },

  // 创建工作流
  createWorkflow: (data: {
    name: string,
    description?: string,
    definition_code: string,
    project_id: number
  }) => {
    return api.post('/workflows', data)
  },

  // 执行工作流
  executeWorkflow: (id: number, params?: any) => {
    return api.post(`/workflows/${id}/execute`, { params })
  }
}

export default api