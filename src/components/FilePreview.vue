<template>
  <div class="file-preview-modal" v-if="visible" @click.self="close">
    <div class="preview-container">
      <div class="preview-header">
        <h3>📄 {{ fileName }}</h3>
        <button @click="close" class="close-btn">✖</button>
      </div>
      
      <div class="preview-content" v-if="!loading">
        <!-- Word/PDF 预览（使用 iframe） -->
        <div v-if="fileType === 'office'" class="office-preview">
          <iframe 
            v-if="previewUrl" 
            :src="previewUrl" 
            frameborder="0"
            class="preview-iframe"
          ></iframe>
          <div v-else class="preview-placeholder">
            <p>📝 {{ fileName }}</p>
            <p class="hint">Word/PDF 文件无法直接预览</p>
            <p class="hint">文件大小: {{ formatFileSize(fileSize) }}</p>
            <p class="hint">文件类型: {{ fileExtension }}</p>
          </div>
        </div>

        <!-- Markdown 预览 -->
        <div v-else-if="fileType === 'markdown'" class="markdown-preview">
          <div v-html="renderedMarkdown" class="markdown-content"></div>
        </div>

        <!-- 纯文本预览 -->
        <div v-else-if="fileType === 'text'" class="text-preview">
          <pre>{{ textContent }}</pre>
        </div>

        <!-- LaTeX 预览 -->
        <div v-else-if="fileType === 'latex'" class="latex-preview">
          <pre>{{ textContent }}</pre>
        </div>

        <!-- 图片预览 -->
        <div v-else-if="fileType === 'image'" class="image-preview">
          <img :src="previewUrl" :alt="fileName" />
        </div>

        <!-- 不支持的格式 -->
        <div v-else class="unsupported-preview">
          <p>❌ 不支持预览此文件格式</p>
          <p class="hint">{{ fileName }}</p>
        </div>
      </div>

      <div v-else class="preview-loading">
        <div class="spinner"></div>
        <p>加载预览中...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'FilePreview',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    file: {
      type: File,
      default: null
    }
  },
  emits: ['close'],
  
  setup(props, { emit }) {
    const loading = ref(false)
    const fileName = ref('')
    const fileSize = ref(0)
    const fileExtension = ref('')
    const fileType = ref('')
    const previewUrl = ref('')
    const textContent = ref('')
    const renderedMarkdown = ref('')

    // 监听文件变化
    watch(() => props.file, async (newFile) => {
      if (newFile) {
        await loadPreview(newFile)
      }
    })

    // 加载预览
    const loadPreview = async (file) => {
      loading.value = true
      fileName.value = file.name
      fileSize.value = file.size
      fileExtension.value = file.name.split('.').pop().toLowerCase()
      
      try {
        // 判断文件类型
        if (['docx', 'doc', 'pdf'].includes(fileExtension.value)) {
          fileType.value = 'office'
          // Office 文件创建对象 URL（某些浏览器支持）
          previewUrl.value = URL.createObjectURL(file)
        } else if (['md', 'markdown'].includes(fileExtension.value)) {
          fileType.value = 'markdown'
          textContent.value = await file.text()
          renderedMarkdown.value = renderMarkdown(textContent.value)
        } else if (['tex', 'latex'].includes(fileExtension.value)) {
          fileType.value = 'latex'
          textContent.value = await file.text()
        } else if (['txt', 'text'].includes(fileExtension.value)) {
          fileType.value = 'text'
          textContent.value = await file.text()
        } else if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'].includes(fileExtension.value)) {
          fileType.value = 'image'
          previewUrl.value = URL.createObjectURL(file)
        } else {
          fileType.value = 'unsupported'
        }
      } catch (error) {
        console.error('预览加载失败:', error)
        fileType.value = 'unsupported'
      } finally {
        loading.value = false
      }
    }

    // 简单的 Markdown 渲染
    const renderMarkdown = (markdown) => {
      let html = markdown
        // 标题
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        // 粗体和斜体
        .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        // 代码块
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/`(.+?)`/g, '<code>$1</code>')
        // 链接
        .replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
        // 图片
        .replace(/!\[([^\]]*)\]\(([^\)]+)\)/g, '<img src="$2" alt="$1" />')
        // 列表
        .replace(/^\* (.+)$/gim, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
        // 段落
        .replace(/\n\n/g, '</p><p>')
        .replace(/^(.+)$/gim, '<p>$1</p>')
      
      return html
    }

    const formatFileSize = (bytes) => {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    }

    const close = () => {
      // 释放对象 URL
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value)
      }
      emit('close')
    }

    return {
      loading,
      fileName,
      fileSize,
      fileExtension,
      fileType,
      previewUrl,
      textContent,
      renderedMarkdown,
      formatFileSize,
      close
    }
  }
}
</script>

<style scoped>
.file-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.preview-container {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 1200px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.3s;
}

@keyframes slideUp {
  from { transform: translateY(50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 2px solid #f0f0f0;
}

.preview-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.3em;
}

.close-btn {
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 1.2em;
  cursor: pointer;
  transition: all 0.3s;
}

.close-btn:hover {
  background: #ff3838;
  transform: rotate(90deg);
}

.preview-content {
  flex: 1;
  overflow: auto;
  padding: 30px;
}

.preview-loading {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.office-preview,
.markdown-preview,
.text-preview,
.latex-preview,
.image-preview,
.unsupported-preview {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.preview-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
  border-radius: 8px;
}

.preview-placeholder p {
  font-size: 1.2em;
  margin: 10px 0;
}

.hint {
  color: #999;
  font-size: 0.9em;
}

.markdown-content {
  background: #f9f9f9;
  padding: 30px;
  border-radius: 8px;
  line-height: 1.8;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3 {
  color: #333;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

.markdown-content code {
  background: #e8e8e8;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.markdown-content pre {
  background: #2d2d2d;
  color: #f8f8f8;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
}

.markdown-content img {
  max-width: 100%;
  border-radius: 8px;
  margin: 20px 0;
}

.text-preview pre,
.latex-preview pre {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  line-height: 1.6;
}

.image-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
  border-radius: 8px;
}

.image-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.unsupported-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
}

.unsupported-preview p {
  font-size: 1.2em;
  margin: 10px 0;
}
</style>
