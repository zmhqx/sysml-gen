<template>
  <div>
    <div class="page-header">
      <h2>生成文档</h2>
    </div>

    <el-card style="max-width: 600px; margin: 20px auto">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="选择项目" prop="project_id">
          <el-select
            v-model="form.project_id"
            placeholder="请先选择项目"
            style="width: 100%"
            @change="onProjectChange"
          >
            <el-option
              v-for="p in projectStore.projects"
              :key="p.id"
              :label="p.name"
              :value="p.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="选择模型" prop="model_id">
          <el-select
            v-model="form.model_id"
            placeholder="请选择模型"
            style="width: 100%"
            :disabled="!form.project_id"
            :loading="modelsLoading"
          >
            <el-option
              v-for="m in filteredModels"
              :key="m.id"
              :label="`${m.name} (${m.version_tag})`"
              :value="m.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="选择模板" prop="template_id">
          <el-select
            v-model="form.template_id"
            placeholder="请选择模板"
            style="width: 100%"
            :disabled="!form.model_id"
            :loading="templatesLoading"
          >
            <el-option
              v-for="t in templates"
              :key="t.id"
              :label="t.name"
              :value="t.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="generating"
            :disabled="!form.project_id || !form.model_id || !form.template_id"
            style="width: 100%"
            @click="handleGenerate"
          >
            开始生成
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../../stores/project'
import { getModels } from '../../api/model'
import { getTemplates } from '../../api/template'
import { generateDocument } from '../../api/document'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import type { SysModel, Template } from '../../types'

const router = useRouter()
const projectStore = useProjectStore()
const formRef = ref<FormInstance>()

const form = reactive({
  project_id: null as number | null,
  model_id: null as number | null,
  template_id: null as number | null,
})
const rules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  model_id: [{ required: true, message: '请选择模型', trigger: 'change' }],
  template_id: [{ required: true, message: '请选择模板', trigger: 'change' }],
}

const filteredModels = ref<SysModel[]>([])
const modelsLoading = ref(false)
const templates = ref<Template[]>([])
const templatesLoading = ref(false)
const generating = ref(false)

async function onProjectChange() {
  form.model_id = null
  form.template_id = null
  filteredModels.value = []
  templates.value = []
  if (!form.project_id) return
  modelsLoading.value = true
  try {
    const res = await getModels(form.project_id)
    filteredModels.value = res.data
    // 自动加载模板
    templatesLoading.value = true
    try {
      const tplRes = await getTemplates()
      templates.value = tplRes.data
    } finally {
      templatesLoading.value = false
    }
  } finally {
    modelsLoading.value = false
  }
}

async function handleGenerate() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  generating.value = true
  try {
    await generateDocument({
      project_id: form.project_id!,
      model_id: form.model_id!,
      template_id: form.template_id!,
    })
    ElMessage.success('文档生成成功')
    router.push('/document')
  } catch {
    // error handled by interceptor
  } finally {
    generating.value = false
  }
}

onMounted(async () => {
  await projectStore.fetchAll()
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
