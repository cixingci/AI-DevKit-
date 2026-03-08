<template>
  <div class="dynamic-fields">
    <template v-if="fieldKeys.length">
      <Draggable
        v-if="sortable"
        v-model="fieldKeys"
        :item-key="(k: string) => k"
        :animation="150"
        handle=".field-handle"
        class="draggable-list"
        @end="persistAndEmitOrder"
      >
        <template #item="{ element: fieldName }">
          <div class="field-row">
            <el-icon class="field-handle" title="拖拽调整顺序">
              <Rank />
            </el-icon>
            <div class="field-main">
              <template v-if="getFieldSchema(fieldName)">
                <component
                  :is="FieldRenderer"
                  :field-name="fieldName"
                  :field-schema="getFieldSchema(fieldName)"
                  v-model="localContent[fieldName]"
                />
              </template>
            </div>
          </div>
        </template>
      </Draggable>

      <template v-else>
        <div v-for="fieldName in fieldKeys" :key="fieldName" class="field-row">
          <div class="field-main">
            <template v-if="getFieldSchema(fieldName)">
              <component
                :is="FieldRenderer"
                :field-name="fieldName"
                :field-schema="getFieldSchema(fieldName)"
                v-model="localContent[fieldName]"
              />
            </template>
          </div>
        </div>
      </template>
    </template>

    <el-empty v-else description="该类型暂无字段定义" :image-size="80" />
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, ref, watch } from 'vue'
import Draggable from 'vuedraggable'
import { Rank } from '@element-plus/icons-vue'

type JSONSchema = Record<string, any>

interface Props {
  schema: JSONSchema | null
  content: Record<string, any>
  sortable?: boolean
  persistKey?: string
}

const props = withDefaults(defineProps<Props>(), {
  sortable: false,
  persistKey: ''
})
const emit = defineEmits<{
  update: [content: Record<string, any>]
  'field-order-change': [order: string[]]
}>()

// 创建本地内容副本，支持实时更新
const localContent = ref<Record<string, any>>({})

// 初始化本地内容
watch(() => props.content, (newContent) => {
  localContent.value = { ...newContent }
}, { immediate: true })

watch(localContent, (newContent) => {
  emit('update', newContent)
}, { deep: true })

const properties = computed<Record<string, any>>(() => {
  const s = props.schema
  if (!s) return {}
  if (s.properties && typeof s.properties === 'object') return s.properties
  // 兼容旧形态：直接把 schema 当字段字典（尽量不破坏已有数据）
  if (!s.type && !s.required && !s.$schema) return s
  return {}
})

const sortable = computed(() => !!props.sortable)

const fieldKeys = ref<string[]>([])

const getPersistedOrder = (): string[] | null => {
  if (!props.persistKey) return null
  try {
    const raw = localStorage.getItem(props.persistKey)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed.filter((x) => typeof x === 'string') : null
  } catch {
    return null
  }
}

const setPersistedOrder = (order: string[]) => {
  if (!props.persistKey) return
  try {
    localStorage.setItem(props.persistKey, JSON.stringify(order))
  } catch {
    // ignore
  }
}

const rebuildFieldKeys = () => {
  const keys = Object.keys(properties.value || {})
  const persisted = getPersistedOrder()
  if (!persisted?.length) {
    fieldKeys.value = keys
    return
  }

  const kept = persisted.filter((k) => keys.includes(k))
  const rest = keys.filter((k) => !kept.includes(k))
  fieldKeys.value = [...kept, ...rest]
}

watch([properties, () => props.persistKey], rebuildFieldKeys, { immediate: true })

const getFieldSchema = (fieldName: string) => {
  return properties.value?.[fieldName] || null
}

const persistAndEmitOrder = () => {
  setPersistedOrder(fieldKeys.value)
  emit('field-order-change', [...fieldKeys.value])
}

// 获取数组项的标签
const getArrayOptions = (fieldSchema: any): string[] => {
  const items = fieldSchema?.items
  if (items?.enum && Array.isArray(items.enum)) return items.enum
  if (fieldSchema?.enum && Array.isArray(fieldSchema.enum)) return fieldSchema.enum
  if (Array.isArray(items)) return items
  return []
}

const FieldRenderer = defineComponent({
  name: 'FieldRenderer',
  props: {
    fieldName: { type: String, required: true },
    fieldSchema: { type: Object as () => Record<string, any>, required: true },
    modelValue: { type: null as any, required: false }
  },
  emits: ['update:modelValue'],
  setup(p, { emit: em }) {
    const update = (v: any) => em('update:modelValue', v)

    return () => {
      const s = p.fieldSchema || {}
      const label = s.title || p.fieldName
      const desc = s.description

      const type = s.type
      const isEnumString = type === 'string' && Array.isArray(s.enum)

      let control = null as any

      if (isEnumString) {
        control = h(
          'el-select',
          {
            modelValue: p.modelValue,
            'onUpdate:modelValue': update,
            placeholder: desc || '请选择',
            style: { width: '100%' },
            filterable: true,
            clearable: true
          },
          () => (s.enum || []).map((opt: any) =>
            h('el-option', { key: String(opt), label: String(opt), value: opt })
          )
        )
      } else if (type === 'number' || type === 'integer') {
        control = h('el-input-number', {
          modelValue: p.modelValue,
          'onUpdate:modelValue': update,
          min: s.minimum,
          max: s.maximum,
          step: s.step || 1,
          style: { width: '100%' }
        })
      } else if (type === 'boolean') {
        control = h('el-switch', {
          modelValue: !!p.modelValue,
          'onUpdate:modelValue': update
        })
      } else if (type === 'array') {
        const options = getArrayOptions(s)
        const value = Array.isArray(p.modelValue) ? p.modelValue : []
        if (options.length) {
          control = h(
            'el-checkbox-group',
            { modelValue: value, 'onUpdate:modelValue': update },
            () => options.map((opt: any) => h('el-checkbox', { key: String(opt), label: opt }, () => String(opt)))
          )
        } else {
          control = h('el-input', {
            modelValue: JSON.stringify(value, null, 2),
            'onUpdate:modelValue': (raw: string) => {
              try {
                const parsed = JSON.parse(raw)
                update(Array.isArray(parsed) ? parsed : value)
              } catch {
                update(value)
              }
            },
            type: 'textarea',
            rows: 3,
            placeholder: '请输入 JSON 数组'
          })
        }
      } else if (type === 'object') {
        const raw = typeof p.modelValue === 'string' ? p.modelValue : JSON.stringify(p.modelValue ?? {}, null, 2)
        control = h('el-input', {
          modelValue: raw,
          'onUpdate:modelValue': (next: string) => {
            try {
              update(JSON.parse(next))
            } catch {
              update(next)
            }
          },
          type: 'textarea',
          rows: s.rows || 4,
          placeholder: '请输入 JSON 对象'
        })
      } else {
        control = h('el-input', {
          modelValue: p.modelValue,
          'onUpdate:modelValue': update,
          placeholder: desc || '',
          type: s.rows ? 'textarea' : 'text',
          rows: s.rows || 3
        })
      }

      return h(
        'el-form-item',
        { label },
        {
          default: () => [
            control,
            desc ? h('div', { class: 'field-description' }, desc) : null
          ]
        }
      )
    }
  }
})
</script>

<style scoped>
.dynamic-fields {
  width: 100%;
}

.draggable-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.field-handle {
  margin-top: 10px;
  cursor: grab;
  color: #c0c4cc;
  user-select: none;
}

.field-handle:hover {
  color: #409eff;
}

.field-main {
  flex: 1;
  min-width: 0;
}

.field-description {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.5;
}
</style>