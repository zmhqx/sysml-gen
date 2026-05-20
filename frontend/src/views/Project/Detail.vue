<template>
  <div v-loading="loading">
    <div v-if="project">
      <el-page-header @back="$router.push('/project')" content="项目详情" />

      <el-card style="margin-top: 20px">
        <template #header>基本信息</template>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="项目名称">{{ project.name }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ project.description || '—' }}</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ getUserName(project.owner_id) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ project.created_at }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card style="margin-top: 20px">
        <template #header>
          <span>项目成员（{{ members.length }}）</span>
          <el-button
            v-if="isAdminOrManager"
            size="small"
            type="primary"
            style="margin-left: 12px"
            @click="showAddDialog = true"
          >添加成员</el-button>
        </template>
        <el-table :data="members" border stripe style="width: 100%">
          <el-table-column prop="username" label="用户名" width="140" />
          <el-table-column prop="full_name" label="姓名" width="140" />
          <el-table-column label="角色" width="100">
            <template #default>
              <el-tag size="small" type="info">member</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="添加时间" min-width="160" />
          <el-table-column v-if="isAdminOrManager" label="操作" width="80">
            <template #default="{ row }">
              <el-button size="small" type="danger" link @click="handleRemove(row)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="members.length === 0" description="暂无成员" :image-size="80" />
      </el-card>

      <el-dialog v-model="showAddDialog" title="添加成员" width="400px">
        <el-select v-model="selectedUserId" placeholder="选择用户" style="width: 100%" filterable>
          <el-option
            v-for="u in availableUsers"
            :key="u.id"
            :label="`${u.username}（${u.full_name || '—'}）`"
            :value="u.id"
          />
        </el-select>
        <template #footer>
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="handleAdd" :loading="adding">确认</el-button>
        </template>
      </el-dialog>
    </div>
    <el-empty v-else description="项目不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { getProject, getProjectMembers, addProjectMember, removeProjectMember } from '../../api/project'
import { getAdminUsers } from '../../api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Project, ProjectMember, User } from '../../types'

const route = useRoute()
const authStore = useAuthStore()
const project = ref<Project | null>(null)
const members = ref<ProjectMember[]>([])
const users = ref<User[]>([])
const loading = ref(true)
const showAddDialog = ref(false)
const selectedUserId = ref<number | null>(null)
const adding = ref(false)

const isAdminOrManager = computed(() =>
  authStore.user?.role === 'admin' || authStore.user?.role === 'manager'
)

const availableUsers = computed(() => {
  const memberIds = new Set(members.value.map((m) => m.user_id))
  if (project.value) memberIds.add(project.value.owner_id)
  return users.value.filter((u) => u.role === 'member' && !memberIds.has(u.id))
})

function getUserName(ownerId: number) {
  const u = users.value.find((u) => u.id === ownerId)
  return u?.full_name || u?.username || `ID:${ownerId}`
}

async function handleAdd() {
  if (!selectedUserId.value) {
    ElMessage.warning('请选择用户')
    return
  }
  adding.value = true
  try {
    const res = await addProjectMember(Number(route.params.id), selectedUserId.value)
    members.value.push(res.data)
    selectedUserId.value = null
    showAddDialog.value = false
    ElMessage.success('添加成功')
  } finally {
    adding.value = false
  }
}

async function handleRemove(row: ProjectMember) {
  try {
    await ElMessageBox.confirm(`确定移除成员「${row.username}」？`)
    await removeProjectMember(Number(route.params.id), row.user_id)
    members.value = members.value.filter((m) => m.user_id !== row.user_id)
    ElMessage.success('已移除')
  } catch {
    // cancelled
  }
}

onMounted(async () => {
  try {
    const id = Number(route.params.id)
    const [projectRes, usersRes] = await Promise.all([
      getProject(id),
      getAdminUsers(),
    ])
    project.value = projectRes.data
    users.value = usersRes.data
    const membersRes = await getProjectMembers(id)
    members.value = membersRes.data
  } finally {
    loading.value = false
  }
})
</script>
