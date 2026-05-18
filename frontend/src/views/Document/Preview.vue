<template>
  <div>
    <div v-loading="loading">
      <div v-if="document">
        <el-page-header @back="$router.push('/document')" :content="document.document_name" />

        <div class="action-bar">
          <span class="doc-meta">
            状态：
            <el-tag :type="statusType(document.status)" size="small">
              {{ statusLabel(document.status) }}
            </el-tag>
            <span v-if="document.generate_time" style="margin-left: 16px; color: #909399">
              生成时间：{{ document.generate_time }}
            </span>
          </span>
          <div v-if="document.status === 'success'">
            <el-button-group>
              <el-button type="primary" :loading="downloading" @click="handleDownload('docx')">
                <el-icon><Download /></el-icon> 下载 DOCX
              </el-button>
              <el-button :loading="downloading" @click="handleDownload('pdf')">
                <el-icon><Download /></el-icon> 下载 PDF
              </el-button>
              <el-button :loading="downloading" @click="handleDownload('html')">
                <el-icon><Download /></el-icon> 下载 HTML
              </el-button>
            </el-button-group>
          </div>
        </div>

        <el-alert
          v-if="document.status === 'failed'"
          :title="document.generate_message || '文档生成失败'"
          type="error"
          show-icon
          style="margin-bottom: 16px"
        />

        <el-card v-if="document.status === 'success' && sanitizedContent">
          <div class="preview-content" v-html="sanitizedContent"></div>
        </el-card>
        <el-empty v-else-if="document.status === 'success'" description="文档内容为空" />
      </div>
      <el-empty v-else description="文档不存在或加载失败" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getDocument, previewDocument, downloadDocument } from '../../api/document'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import type { Document } from '../../types'

const route = useRoute()
const document = ref<Document | null>(null)
const loading = ref(true)
const downloading = ref(false)
const rawContent = ref('')

const sanitizedContent = computed(() => {
  if (!rawContent.value) return ''
  return rawContent.value
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/\son\w+\s*=\s*["'][^"']*["']/gi, '')
})

function statusType(status: string) {
  return { generating: 'warning', success: 'success', failed: 'danger' }[status] || 'info'
}

function statusLabel(status: string) {
  return { generating: '生成中', success: '已生成', failed: '失败' }[status] || status
}

function triggerDownload(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

async function handleDownload(fmt: string) {
  downloading.value = true
  try {
    const id = Number(route.params.id)
    const docName = document.value?.document_name || 'document'
    if (fmt === 'html') {
      const res = await downloadDocument(id, 'html')
      const blob = new Blob([res.data.content], { type: 'text/html;charset=utf-8' })
      triggerDownload(blob, `${docName}.html`)
    } else {
      const res = await downloadDocument(id, fmt)
      const ext = fmt === 'pdf' ? 'pdf' : 'docx'
      triggerDownload(res.data as Blob, `${docName}.${ext}`)
    }
    ElMessage.success('下载已开始')
  } catch {
    ElMessage.error('下载失败')
  } finally {
    downloading.value = false
  }
}

onMounted(async () => {
  try {
    const id = Number(route.params.id)
    const [docRes, previewRes] = await Promise.all([
      getDocument(id),
      previewDocument(id),
    ])
    document.value = docRes.data
    rawContent.value = previewRes.data.content || ''
  } catch {
    ElMessage.error('加载文档失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0;
}
.preview-content {
  padding: 20px;
  line-height: 1.8;
  font-size: 14px;
}
.preview-content :deep(h1),
.preview-content :deep(h2),
.preview-content :deep(h3) {
  margin-top: 1.2em;
  margin-bottom: 0.6em;
}
.preview-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}
.preview-content :deep(table th),
.preview-content :deep(table td) {
  border: 1px solid #dcdfe6;
  padding: 8px 12px;
}
.preview-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 13px;
}
.preview-content :deep(pre) {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
