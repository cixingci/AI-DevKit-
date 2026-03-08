import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: {
      title: '工作台',
      icon: 'Odometer'
    }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('@/views/Projects.vue'),
    meta: {
      title: '项目管理',
      icon: 'FolderOpened'
    }
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetail',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: {
      title: '项目详情',
      icon: 'Document'
    }
  },
  {
    path: '/cards',
    name: 'Cards',
    component: () => import('@/views/Cards.vue'),
    meta: {
      title: '卡片视图',
      icon: 'CreditCard'
    }
  },
  {
    path: '/cards/:id',
    name: 'CardDetail',
    component: () => import('@/views/Cards.vue'),
    meta: {
      title: '卡片详情',
      icon: 'Document'
    }
  },
  {
    path: '/cards/:id/edit',
    name: 'CardEditor',
    component: () => import('@/views/CardEditor.vue'),
    meta: {
      title: '编辑卡片',
      icon: 'Edit'
    }
  },
  {
    path: '/cards/create',
    name: 'CardCreate',
    component: () => import('@/views/CardEditor.vue'),
    meta: {
      title: '创建卡片',
      icon: 'Plus'
    }
  },
  {
    path: '/workflows',
    name: 'Workflows',
    component: () => import('@/views/Workflows.vue'),
    meta: {
      title: '工作流',
      icon: 'Connection'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: {
      title: '设置',
      icon: 'Setting'
    }
  },
  {
    path: '/card-types',
    name: 'CardTypes',
    component: () => import('@/views/CardTypes.vue'),
    meta: {
      title: '卡片类型管理',
      icon: 'Collection'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  console.log('导航到:', to.path, to.name)
  // 设置页面标题
  document.title = `${to.meta.title} - AI DevKit`
  next()
})

export default router