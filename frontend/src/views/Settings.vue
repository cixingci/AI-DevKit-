<template>
  <div class="settings">
    <el-page-header @back="goBack" content="设置" />
    <el-card class="content-card">
      <el-empty description="设置功能开发中..." />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.settings {
  padding: 20px;
}

.content-card {
  margin-top: 20px;
}
</style>
