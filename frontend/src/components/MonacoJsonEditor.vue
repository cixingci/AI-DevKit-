<template>
  <div class="monaco-json-editor">
    <div ref="containerRef" class="editor-container" />
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api'

import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'
import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker'

declare global {
  interface Window {
    MonacoEnvironment?: {
      getWorker: (moduleId: string, label: string) => Worker
    }
  }
}

const props = withDefaults(defineProps<{
  modelValue: string
  schema?: Record<string, any> | null
  readOnly?: boolean
  height?: string
}>(), {
  schema: null,
  readOnly: false,
  height: '420px'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  change: [value: string]
}>()

const containerRef = ref<HTMLDivElement | null>(null)
let editor: monaco.editor.IStandaloneCodeEditor | null = null
let model: monaco.editor.ITextModel | null = null

const instanceId = Math.random().toString(36).slice(2)
const modelUri = monaco.Uri.parse(`inmemory://ai-devkit/${instanceId}.json`)

let suppressEmit = false

const ensureWorkersConfigured = () => {
  if (window.MonacoEnvironment?.getWorker) return
  window.MonacoEnvironment = {
    getWorker: (_moduleId, label) => {
      if (label === 'json') return new jsonWorker()
      return new editorWorker()
    }
  }
}

const applyJsonDiagnosticsSchema = (jsonSchema: Record<string, any> | null | undefined) => {
  // 检查 JSON 语言服务是否已加载
  if (!monaco.languages.json) {
    console.warn('Monaco JSON 语言服务未加载，跳过 Schema 配置')
    return
  }
  
  const schemas = jsonSchema
    ? [{
        uri: `inmemory://ai-devkit/schema/${instanceId}`,
        fileMatch: [modelUri.toString()],
        schema: jsonSchema
      }]
    : []

  monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
    validate: true,
    allowComments: true,
    schemas
  })
}

onMounted(() => {
  ensureWorkersConfigured()
  if (!containerRef.value) return

  model = monaco.editor.createModel(props.modelValue ?? '', 'json', modelUri)
  
  // 延迟应用 Schema，确保语言服务已加载
  setTimeout(() => {
    applyJsonDiagnosticsSchema(props.schema)
  }, 100)

  editor = monaco.editor.create(containerRef.value, {
    model,
    readOnly: props.readOnly,
    automaticLayout: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    formatOnPaste: true,
    formatOnType: true,
    tabSize: 2,
    fontSize: 13
  })

  editor.onDidChangeModelContent(() => {
    if (!model || suppressEmit) return
    const value = model.getValue()
    emit('update:modelValue', value)
    emit('change', value)
  })
})

watch(() => props.modelValue, (next) => {
  if (!model) return
  const current = model.getValue()
  if ((next ?? '') === current) return
  suppressEmit = true
  model.setValue(next ?? '')
  suppressEmit = false
})

watch(() => props.readOnly, (ro) => {
  if (!editor) return
  editor.updateOptions({ readOnly: ro })
})

watch(() => props.schema, (s) => {
  applyJsonDiagnosticsSchema(s || null)
}, { deep: true })

onBeforeUnmount(() => {
  editor?.dispose()
  editor = null
  model?.dispose()
  model = null
})
</script>

<style scoped>
.editor-container {
  width: 100%;
  height: v-bind(height);
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
}
</style>

