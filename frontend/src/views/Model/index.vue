<template>
  <div>
    <div class="page-header">
      <h2>模型管理</h2>
      <el-button type="primary" @click="showUpload = true">上传模型</el-button>
    </div>

    <el-table :data="models" border stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="模型名称" min-width="200">
        <template #default="{ row }">
          <router-link :to="`/model/${row.id}`">{{ row.name }}</router-link>
        </template>
      </el-table-column>
      <el-table-column label="所属项目" width="160">
        <template #default="{ row }">
          {{ projectMap[row.project_id] || '—' }}
        </template>
      </el-table-column>
      <el-table-column prop="file_type" label="文件类型" width="100" />
      <el-table-column prop="file_size" label="大小" width="100">
        <template #default="{ row }">
          {{ formatSize(row.file_size) }}
        </template>
      </el-table-column>
      <el-table-column prop="parse_status" label="解析状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType(row.parse_status)" size="small">
            {{ statusLabel(row.parse_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="upload_time" label="上传时间" width="180" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/model/${row.id}`)">详情</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showUpload" title="上传模型" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="所属项目" prop="project_id">
          <el-select v-model="form.project_id" placeholder="选择项目" style="width: 100%">
            <el-option
              v-for="p in projectStore.projects"
              :key="p.id"
              :label="p.name"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模型文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :show-file-list="true"
            :limit="1"
            :on-change="onFileChange"
          >
            <el-button type="primary" size="small">选择文件</el-button>
            <template #tip>
              <span style="font-size: 12px; color: #909399">支持 .xmi .xml .json 格式</span>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input v-model="form.name" placeholder="留空则使用文件名" />
        </el-form-item>
        <el-form-item label="版本号">
          <el-input v-model="form.version_tag" placeholder="v1.0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUpload = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useProjectStore } from '../../stores/project'
import { getModels, uploadModel, deleteModel } from '../../api/model'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, UploadInstance } from 'element-plus'
import type { SysModel } from '../../types'

const projectStore = useProjectStore()
const models = ref<SysModel[]>([])
const showUpload = ref(false)
const uploading = ref(false)
const formRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()
const selectedFile = ref<File | null>(null)

const form = reactive({
  project_id: null as number | null,
  name: '',
  version_tag: 'v1.0',
})

const rules = {
  project_id: [{ required: true, message: '请选择所属项目', trigger: 'change' }],
}

const projectMap = computed(() => {
  const map: Record<number, string> = {}
  projectStore.projects.forEach((p) => { map[p.id] = p.name })
  return map
})

function formatSize(bytes: number) {
  if (!bytes) return '—'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function statusType(status: string) {
  return { pending: 'info', parsing: 'warning', success: 'success', failed: 'danger' }[status] || 'info'
}

function statusLabel(status: string) {
  return { pending: '待解析', parsing: '解析中', success: '已解析', failed: '解析失败' }[status] || status
}

function onFileChange(file: any) {
  selectedFile.value = file.raw
}

async function handleUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择模型文件')
    return
  }
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    fd.append('project_id', String(form.project_id))
    fd.append('name', form.name)
    fd.append('version_tag', form.version_tag)
    await uploadModel(fd)
    ElMessage.success('上传成功')
    showUpload.value = false
    fetchModels()
  } finally {
    uploading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该模型？')
    await deleteModel(id)
    ElMessage.success('已删除')
    models.value = models.value.filter((m) => m.id !== id)
  } catch { /* cancelled */ }
}

async function fetchModels() {
  const res = await getModels()
  models.value = res.data
}

onMounted(async () => {
  await projectStore.fetchAll()
  await fetchModels()
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
