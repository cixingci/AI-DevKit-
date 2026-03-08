<template>
  <div class="workflows">
    <el-page-header @back="goBack" content="工作流" />
    <el-card class="content-card">
      <el-empty description="工作流功能开发中..." />
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
.workflows {
  padding: 20px;
}

.content-card {
  margin-top: 20px;
}
</style>
