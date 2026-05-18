<template>
  <div v-loading="loading">
    <el-page-header @back="$router.push(`/model/${modelId}`)" content="模型元素树" />

    <div v-if="errorMsg" style="margin-top: 20px">
      <el-alert :title="errorMsg" type="error" show-icon />
    </div>

    <el-card v-else style="margin-top: 20px">
      <template #header>
        <span>{{ modelName }}</span>
        <span style="font-size: 13px; color: #909399; margin-left: 12px">
          （共 {{ totalElements }} 个元素）
        </span>
      </template>

      <el-input
        v-model="searchQuery"
        placeholder="搜索元素名称..."
        clearable
        style="width: 300px; margin-bottom: 16px"
        @input="onSearch"
      />

      <el-tree
        v-if="!searchQuery"
        :data="treeData"
        :props="treeProps"
        node-key="element_id"
        default-expand-all
        :highlight-current="true"
        :expand-on-click-node="true"
      >
        <template #default="{ data }">
          <span class="tree-node">
            <el-tag
              :type="elementTypeTag(data.element_type)"
              size="small"
              style="margin-right: 8px"
            >
              {{ data.element_type }}
            </el-tag>
            <span>{{ data.element_name }}</span>
            <span style="margin-left: 12px; font-size: 12px; color: #c0c4cc">
              {{ data.element_id }}
            </span>
          </span>
        </template>
      </el-tree>

      <el-table v-else :data="searchResults" border stripe>
        <el-table-column prop="element_id" label="ID" width="120" />
        <el-table-column prop="element_name" label="名称" min-width="200" />
        <el-table-column prop="element_type" label="类型" width="140">
          <template #default="{ row }">
            <el-tag :type="elementTypeTag(row.element_type)" size="small">
              {{ row.element_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getModel, getModelTree, getModelElements } from '../../api/model'
import type { ElementTreeItem, ModelElement } from '../../types'

const route = useRoute()
const modelId = computed(() => Number(route.params.id))
const modelName = ref('')
const treeData = ref<ElementTreeItem[]>([])
const loading = ref(true)
const errorMsg = ref('')

const searchQuery = ref('')
const searchResults = ref<ModelElement[]>([])

const treeProps = {
  children: 'children',
  label: 'element_name',
}

const totalElements = computed(() => countNodes(treeData.value))

function countNodes(items: ElementTreeItem[]): number {
  let count = 0
  for (const item of items) {
    count++
    if (item.children?.length) count += countNodes(item.children)
  }
  return count
}

function elementTypeTag(type: string) {
  const m: Record<string, string> = {
    Block: 'primary',
    Requirement: 'warning',
    Package: '',
    Interface: 'success',
    Association: 'info',
  }
  return m[type] || ''
}

let searchTimer: ReturnType<typeof setTimeout>

async function onSearch() {
  clearTimeout(searchTimer)
  if (!searchQuery.value) {
    searchResults.value = []
    return
  }
  searchTimer = setTimeout(async () => {
    try {
      const res = await getModelElements(modelId.value)
      const q = searchQuery.value.toLowerCase()
      searchResults.value = res.data.filter(
        (e) => e.element_name && e.element_name.toLowerCase().includes(q),
      )
    } catch {
      // ignore
    }
  }, 300)
}

onMounted(async () => {
  try {
    const [modelRes, treeRes] = await Promise.all([
      getModel(modelId.value),
      getModelTree(modelId.value),
    ])
    modelName.value = modelRes.data.name
    treeData.value = treeRes.data
  } catch {
    errorMsg.value = '加载模型元素失败'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.tree-node {
  font-size: 14px;
}
</style>
