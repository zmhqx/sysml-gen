<template>
  <div class="page-container">
    <div class="page-header">
      <h2>模板管理</h2>
      <el-button type="primary" @click="openCreate">新建模板</el-button>
    </div>

    <div class="card-table">
    <el-table :data="templates" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="模板名称" min-width="160" />
      <el-table-column prop="template_type" label="模板类型" width="140">
        <template #default="{ row }">
          <el-tag :type="typeTag(row.template_type)" size="small">
            {{ typeLabel(row.template_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
            {{ row.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button
            size="small"
            :type="row.status === 'active' ? 'warning' : 'success'"
            @click="toggleStatus(row)"
          >
            {{ row.status === 'active' ? '停用' : '启用' }}
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑模板' : '新建模板'" width="750px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="输入模板名称" />
        </el-form-item>
        <el-form-item label="类型" prop="template_type">
          <el-select v-model="form.template_type" placeholder="选择模板类型" style="width: 100%">
            <el-option label="需求文档" value="requirements" />
            <el-option label="设计文档" value="design" />
            <el-option label="测试文档" value="test" />
            <el-option label="用户手册" value="manual" />
            <el-option label="接口文档" value="api" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            ref="contentRef"
            v-model="form.content"
            type="textarea"
            :rows="18"
            placeholder="支持 Jinja2 模板语法，如模型名称、遍历元素等"
          />
        </el-form-item>
        <div style="padding-left: 80px; margin-top: -14px">
          <span style="font-size: 12px; color: #909399; margin-right: 8px;">快速插入：</span>
          <el-button size="small" @click="insertSnippet(snippets.modelName)">模型名称</el-button>
          <el-button size="small" @click="insertSnippet(snippets.forLoop)">遍历元素</el-button>
          <el-button size="small" @click="insertSnippet(snippets.generateTime)">生成时间</el-button>
          <el-button size="small" @click="insertSnippet(snippets.getElementById)">引用元素</el-button>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getTemplates, createTemplate, updateTemplate, deleteTemplate } from '../../api/template'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import type { Template } from '../../types'

const templates = ref<Template[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()
const contentRef = ref()

const snippets = {
  modelName: '{{ model_name }}',
  forLoop: '{% for e in elements %}\n  {{ e.name }} - {{ e.type }}\n{% endfor %}',
  generateTime: '{{ generate_time }}',
  getElementById: '{{ get_element_by_id("element_id") }}',
}

const form = reactive({
  name: '',
  template_type: '',
  content: '',
})
const rules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  template_type: [{ required: true, message: '请选择模板类型', trigger: 'change' }],
}

function typeLabel(type: string) {
  const m: Record<string, string> = {
    requirements: '需求文档',
    design: '设计文档',
    test: '测试文档',
    manual: '用户手册',
    api: '接口文档',
  }
  return m[type] || type
}

function typeTag(type: string) {
  const m: Record<string, string> = {
    requirements: 'primary',
    design: 'success',
    test: 'warning',
    manual: 'info',
    api: '',
  }
  return m[type] || ''
}

function insertSnippet(snippet: string) {
  form.content += snippet
}

function openCreate() {
  isEdit.value = false
  editingId.value = null
  form.name = ''
  form.template_type = ''
  form.content = ''
  dialogVisible.value = true
}

function openEdit(row: Template) {
  isEdit.value = true
  editingId.value = row.id
  form.name = row.name
  form.template_type = row.template_type
  form.content = row.content
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value && editingId.value) {
      await updateTemplate(editingId.value, {
        name: form.name,
        template_type: form.template_type,
        content: form.content,
      })
      ElMessage.success('模板已更新')
    } else {
      await createTemplate({
        name: form.name,
        template_type: form.template_type,
        content: form.content,
      })
      ElMessage.success('模板已创建')
    }
    dialogVisible.value = false
    await fetchTemplates()
  } finally {
    saving.value = false
  }
}

async function toggleStatus(row: Template) {
  const newStatus = row.status === 'active' ? 'inactive' : 'active'
  await updateTemplate(row.id, { status: newStatus })
  ElMessage.success(newStatus === 'active' ? '模板已启用' : '模板已停用')
  await fetchTemplates()
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该模板？')
    await deleteTemplate(id)
    ElMessage.success('模板已删除')
    await fetchTemplates()
  } catch {
    // cancelled
  }
}

async function fetchTemplates() {
  loading.value = true
  try {
    const res = await getTemplates()
    templates.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(fetchTemplates)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.el-textarea :deep(textarea) {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
}
</style>
