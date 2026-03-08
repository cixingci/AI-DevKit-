<template>
  <div class="card-types-test">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>卡片类型管理测试页面</span>
        </div>
      </template>

      <div class="test-info">
        <h3>测试说明</h3>
        <p>此页面用于测试卡片类型管理界面的显示效果</p>

        <el-divider />

        <h4>1. 网格布局测试</h4>
        <p>卡片类型卡片应使用网格布局，每个卡片至少350px宽</p>

        <h4>2. 功能测试</h4>
        <ul>
          <li>新建卡片类型</li>
          <li>编辑卡片类型</li>
          <li>删除卡片类型</li>
          <li>预览卡片类型</li>
          <li>搜索卡片类型</li>
        </ul>

        <h4>3. 样式测试</h4>
        <ul>
          <li>卡片标题和ID显示</li>
          <li>模板JSON显示</li>
          <li>展开/收起JSON结构</li>
          <li>描述和时间显示</li>
          <li>按钮布局</li>
        </ul>

        <el-divider />

        <h4>当前卡片类型数量: {{ cardTypes.length }}</h4>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const cardTypes = ref<any[]>([])

const loadCardTypes = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/card-types')
    cardTypes.value = await response.json()
    console.log('卡片类型数据:', cardTypes.value)
  } catch (error) {
    console.error('加载卡片类型失败:', error)
    alert('加载卡片类型失败，请确保后端服务运行正常')
  }
}

onMounted(() => {
  loadCardTypes()
})
</script>

<style scoped>
.card-types-test {
  padding: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
}

.test-info {
  line-height: 1.8;
}

.test-info h3 {
  margin-top: 0;
  color: #303133;
}

.test-info h4 {
  color: #606266;
  margin-bottom: 12px;
}

.test-info p {
  color: #909399;
  margin-bottom: 20px;
}

ul {
  padding-left: 20px;
  margin-bottom: 20px;
}

li {
  color: #909399;
  margin-bottom: 8px;
}
</style>
