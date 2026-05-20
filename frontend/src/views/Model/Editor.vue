<template>
  <div v-loading="loading">
    <el-page-header @back="$router.push(`/model/${modelId}`)" content="视图编辑器" />

    <!-- 概览区 -->
    <el-row :gutter="16" style="margin-top: 20px">
      <el-col :span="6" v-for="s in stats" :key="s.label">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-num">{{ s.count }}</div>
            <div class="stat-label">
              <el-tag :type="s.type" size="small" effect="plain">{{ s.label }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索 -->
    <el-card style="margin-top: 16px">
      <el-input
        v-model="searchQuery"
        placeholder="搜索元素名称或 ID..."
        clearable
        style="width: 100%"
        @input="onSearch"
      />
    </el-card>

    <!-- 分组元素列表 -->
    <el-card v-if="filteredGroups.length" style="margin-top: 16px">
      <el-collapse v-model="activeNames">
        <el-collapse-item
          v-for="group in filteredGroups"
          :key="group.type"
          :name="group.type"
          :title="`${group.label}（${group.items.length}）`"
        >
          <div v-for="item in group.items" :key="item.element_id" class="element-card">
            <div class="card-header">
              <el-tag :type="elementTypeTag(item.element_type)" size="small">
                {{ item.element_type }}
              </el-tag>
              <span class="card-id">{{ item.element_id }}</span>
              <span
                v-if="editingId !== item.element_id"
                class="card-name"
                @click="startEdit(item)"
              >
                {{ item.element_name || '（未命名）' }}
              </span>
              <el-input
                v-else
                v-model="editForm.element_name"
                size="small"
                style="width: 300px"
                @blur="saveEdit(item)"
                @keyup.enter="saveEdit(item)"
                ref="nameInputRef"
              />
            </div>
            <div class="card-body">
              <span
                v-if="editingDescId !== item.element_id"
                class="card-desc"
                @click="startEditDesc(item)"
              >
                {{ item.description || '（无描述）' }}
              </span>
              <el-input
                v-else
                v-model="editForm.description"
                type="textarea"
                :rows="2"
                size="small"
                style="width: 100%"
                @blur="saveEditDesc(item)"
                @keyup.enter.ctrl="saveEditDesc(item)"
              />
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <el-empty v-else-if="!loading" description="无匹配元素" style="margin-top: 40px" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getModel, getModelElements, updateElement } from '../../api/model'
import { ElMessage } from 'element-plus'
import type { SysModel, ModelElement } from '../../types'

const route = useRoute()
const modelId = computed(() => Number(route.params.id))
const model = ref<SysModel | null>(null)
const elements = ref<ModelElement[]>([])
const loading = ref(true)
const searchQuery = ref('')
const activeNames = ref<string[]>([])
const nameInputRef = ref<HTMLInputElement>()

const editingId = ref<string | null>(null)
const editingDescId = ref<string | null>(null)
const editForm = reactive({ element_name: '', description: '' })

const typeConfig: Record<string, { label: string; type: string }> = {
  Package: { label: '包', type: '' },
  Requirement: { label: '需求', type: 'warning' },
  Block: { label: '模块', type: 'primary' },
  Interface: { label: '接口', type: 'success' },
}

const stats = computed(() => {
  const counts: Record<string, number> = {}
  const typeMap: Record<string, string> = {}
  for (const e of elements.value) {
    counts[e.element_type] = (counts[e.element_type] || 0) + 1
    typeMap[e.element_type] = typeConfig[e.element_type]?.type || ''
  }
  return Object.entries(counts).map(([label, count]) => ({
    label,
    count,
    type: typeMap[label] || 'info',
  }))
})

const filteredGroups = computed(() => {
  const q = searchQuery.value.toLowerCase()
  let filtered = elements.value
  if (q) {
    filtered = elements.value.filter(
      (e) =>
        (e.element_name && e.element_name.toLowerCase().includes(q)) ||
        (e.element_id && e.element_id.toLowerCase().includes(q)) ||
        (e.description && e.description.toLowerCase().includes(q)),
    )
  }

  const groups: { type: string; label: string; items: ModelElement[] }[] = []
  const configOrder = ['Package', 'Requirement', 'Block', 'Interface']
  const others: ModelElement[] = []

  const grouped: Record<string, ModelElement[]> = {}
  for (const e of filtered) {
    const t = e.element_type
    if (configOrder.includes(t)) {
      if (!grouped[t]) grouped[t] = []
      grouped[t].push(e)
    } else {
      others.push(e)
    }
  }

  for (const t of configOrder) {
    if (grouped[t]) {
      groups.push({ type: t, label: typeConfig[t]?.label || t, items: grouped[t] })
    }
  }
  if (others.length) {
    groups.push({ type: '_other', label: '其他', items: others })
  }

  return groups
})

function elementTypeTag(type: string) {
  const colors: Record<string, string> = {
    Block: 'primary', Requirement: 'warning', Package: '',
    Interface: 'success',
  }
  return colors[type] || ''
}

function startEdit(item: ModelElement) {
  editingId.value = item.element_id
  editForm.element_name = item.element_name || ''
  editForm.description = item.description || ''
  nextTick(() => {
    const el = document.querySelector('.card-header .el-input__inner') as HTMLInputElement
    el?.focus()
  })
}

async function saveEdit(item: ModelElement) {
  if (editingId.value !== item.element_id) return
  editingId.value = null
  const data: { element_name?: string; description?: string } = {}
  if (editForm.element_name !== item.element_name) {
    data.element_name = editForm.element_name
  }
  if (Object.keys(data).length === 0) return
  try {
    const res = await updateElement(modelId.value, item.element_id, data)
    Object.assign(item, res.data)
    ElMessage.success('已保存')
  } catch {
    ElMessage.error('保存失败')
  }
}

function startEditDesc(item: ModelElement) {
  editingDescId.value = item.element_id
  editForm.element_name = item.element_name || ''
  editForm.description = item.description || ''
}

async function saveEditDesc(item: ModelElement) {
  if (editingDescId.value !== item.element_id) return
  editingDescId.value = null
  if (editForm.description === item.description) return
  try {
    const res = await updateElement(modelId.value, item.element_id, {
      description: editForm.description,
    })
    Object.assign(item, res.data)
    ElMessage.success('已保存')
  } catch {
    ElMessage.error('保存失败')
  }
}

function onSearch() {
  // 搜索时展开所有匹配组
  if (searchQuery.value) {
    activeNames.value = filteredGroups.value.map((g) => g.type)
  }
}

onMounted(async () => {
  try {
    const id = modelId.value
    const [modelRes, elemRes] = await Promise.all([
      getModel(id),
      getModelElements(id),
    ])
    model.value = modelRes.data
    elements.value = elemRes.data
    // 默认全部展开
    activeNames.value = Object.keys(typeConfig)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stat-card {
  text-align: center;
  padding: 8px 0;
}
.stat-num {
  font-size: 32px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 4px;
}
.stat-label {
  font-size: 14px;
}
.element-card {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 8px;
  transition: box-shadow 0.2s;
}
.element-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.card-id {
  font-size: 12px;
  color: #c0c4cc;
  font-family: monospace;
}
.card-name {
  cursor: pointer;
  font-weight: 600;
  color: #303133;
  padding: 2px 4px;
  border-radius: 3px;
}
.card-name:hover {
  background: #ecf5ff;
  color: #409eff;
}
.card-desc {
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  padding: 2px 4px;
  border-radius: 3px;
  display: block;
  line-height: 1.6;
}
.card-desc:hover {
  background: #f5f7fa;
  color: #303133;
}
</style>
