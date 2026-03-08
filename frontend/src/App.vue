<template>
  <div id="app">
    <el-container class="layout-container">
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-content">
          <div class="logo">
            <el-icon><Document /></el-icon>
            <span>AI DevKit</span>
          </div>
          <div class="nav-menu">
            <el-menu
              mode="horizontal"
              :default-active="activeMenu"
              class="nav-menu-items"
              router
            >
              <el-menu-item index="/">
                <el-icon><HomeFilled /></el-icon>
                <span>工作台</span>
              </el-menu-item>

              <el-menu-item index="/projects">
                <el-icon><Folder /></el-icon>
                <span>项目管理</span>
              </el-menu-item>

              <el-menu-item index="/cards">
                <el-icon><Document /></el-icon>
                <span>卡片视图</span>
              </el-menu-item>

              <el-menu-item index="/workflows">
                <el-icon><Connection /></el-icon>
                <span>工作流</span>
              </el-menu-item>

              <el-menu-item index="/settings">
                <el-icon><Setting /></el-icon>
                <span>设置</span>
              </el-menu-item>

              <el-menu-item index="/card-types">
                <el-icon><Files /></el-icon>
                <span>卡片类型管理</span>
              </el-menu-item>
            </el-menu>
          </div>
          <div class="user-menu">
            <el-dropdown trigger="click">
              <el-avatar :size="32" src="https://via.placeholder.com/32" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>个人信息</el-dropdown-item>
                  <el-dropdown-item>设置</el-dropdown-item>
                  <el-dropdown-item divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Document,
  HomeFilled,
  Folder,
  Connection,
  Setting,
  Files
} from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => route.path)
</script>

<style scoped>
.layout-container {
  height: 100vh;
  width: 100vw;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
}

.nav-menu {
  flex: 1;
  padding-right: 20px;
}

.nav-menu-items {
  border-bottom: none;
  background: transparent;
  border-radius: 0 !important;
  height: 60px;
}

.nav-menu-items .el-menu-item {
  margin: 0;
  height: 60px;
  line-height: 60px;
  padding-left: 16px !important;
  padding-right: 16px !important;
  flex: 0 0 auto;
  min-width: 120px;
  justify-content: flex-start;
}

.nav-menu-items .el-menu-item span {
  display: inline-block;
  padding-left: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

.nav-menu-items .el-menu-item .el-icon {
  margin-right: 8px;
}

.user-menu {
  margin-left: 20px;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<style>
/* 全局样式 */
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  background: #f5f7fa;
}

#app {
  height: 100vh;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
