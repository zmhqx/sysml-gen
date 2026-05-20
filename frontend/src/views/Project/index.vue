<template>
  <div>
    <div class="page-header">
      <h2>项目管理</h2>
      <el-button v-if="isAdminOrManager" type="primary" @click="showForm = true; editData = null">新建项目</el-button>
    </div>

    <el-table :data="projectStore.projects" border stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="项目名称" min-width="200">
        <template #default="{ row }">
          <router-link :to="`/project/${row.id}`">{{ row.name }}</router-link>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
      <el-table-column label="负责人" width="120">
        <template #default="{ row }">
          {{ getUserName(row.owner_id) }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column v-if="isAdminOrManager" label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="showForm = true; editData = row">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showForm" :title="editData ? '编辑项目' : '新建项目'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForm = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useProjectStore } from '../../stores/project'
import { useAuthStore } from '../../stores/auth'
import { getAdminUsers } from '../../api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import type { User } from '../../types'

const projectStore = useProjectStore()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const showForm = ref(false)
const saving = ref(false)
const editData = ref<any>(null)
const users = ref<User[]>([])

const isAdminOrManager = computed(() =>
  authStore.user?.role === 'admin' || authStore.user?.role === 'manager'
)

const form = reactive({ name: '', description: '' })
const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
}

function getUserName(ownerId: number) {
  const u = users.value.find((u) => u.id === ownerId)
  return u?.full_name || u?.username || `ID:${ownerId}`
}

watch(showForm, (val) => {
  if (!val) {
    form.name = ''
    form.description = ''
    editData.value = null
  } else if (editData.value) {
    form.name = editData.value.name
    form.description = editData.value.description
  }
})

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (editData.value) {
      await projectStore.update(editData.value.id, form)
      ElMessage.success('更新成功')
    } else {
      await projectStore.create(form)
      ElMessage.success('创建成功')
    }
    showForm.value = false
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该项目？')
    await projectStore.remove(id)
    ElMessage.success('已删除')
  } catch {
    // cancelled
  }
}

onMounted(async () => {
  await Promise.all([
    projectStore.fetchAll(),
    getAdminUsers().then((res) => { users.value = res.data }),
  ])
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
