<template>
  <div class="template-mode">
    <h2>🎨 模板模式</h2>
    <p class="description">上传模板和内容文档，AI 会根据模板格式生成新文档</p>

    <div class="upload-section">
      <div class="upload-item">
        <h3>📋 模板文件</h3>
        <p class="hint">定义文档的结构和样式</p>
        <FileUploadSimple 
          @file-selected="handleTemplateSelected" 
          :accept="'.docx,.doc,.md,.tex'"
          :placeholder="'上传模板文件 (.docx/.md/.tex)'"
        />
        <div v-if="templateFile" class="file-info">
          <span>✅ {{ templateFile.name }}</span>
          <button @click="previewTemplate" class="preview-btn">👁 预览</button>
        </div>
      </div>

      <div class="upload-item">
        <h3>📄 内容文件</h3>
        <p class="hint">包含实际内容和图片</p>
        <FileUploadSimple 
          @file-selected="handleContentSelected"
          :accept="'.docx,.doc,.pdf,.md'"
          :placeholder="'上传内容文件'"
        />
        <div v-if="contentFile" class="file-info">
          <span>✅ {{ contentFile.name }}</span>
          <button @click="previewContent" class="preview-btn">👁 预览</button>
        </div>
      </div>
    </div>

    <div class="format-selection">
      <h3>📦 输出格式</h3>
      <div class="format-options">
        <label 
          v-for="format in outputFormats" 
          :key="format.value"
          :class="['format-option', { active: selectedFormat === format.value }]"
        >
          <input 
            type="radio" 
            :value="format.value" 
            v-model="selectedFormat"
            name="output-format"
          />
          <span class="format-icon">{{ format.icon }}</span>
          <span class="format-name">{{ format.label }}</span>
        </label>
      </div>
    </div>

    <div class="instruction-section">
      <h3>💬 额外要求（可选）</h3>
      <textarea 
        v-model="additionalInstruction"
        placeholder="例如：保持所有图片，调整标题为蓝色，添加页眉页脚..."
        rows="3"
        class="textarea"
      ></textarea>
    </div>

    <button 
      @click="processTemplate" 
      class="btn btn-primary btn-large"
      :disabled="!canProcess || loading"
    >
      <span v-if="loading">⏳ 处理中...</span>
      <span v-else>✨ 开始生成</span>
    </button>

    <!-- 文件预览弹窗 -->
    <FilePreview 
      :visible="previewVisible"
      :file="previewFile"
      @close="closePreview"
    />
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import FileUploadSimple from './FileUploadSimple.vue'
import FilePreview from './FilePreview.vue'

export default {
  name: 'TemplateMode',
  components: {
    FileUploadSimple,
    FilePreview
  },
  props: {
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['process'],
  
  setup(props, { emit }) {
    const templateFile = ref(null)
    const contentFile = ref(null)
    const selectedFormat = ref('word')
    const additionalInstruction = ref('')
    const previewVisible = ref(false)
    const previewFile = ref(null)

    const outputFormats = [
      { value: 'word', label: 'Word', icon: '📝' },
      { value: 'markdown', label: 'Markdown', icon: '📋' },
      { value: 'latex', label: 'LaTeX', icon: '📐' }
    ]

    const canProcess = computed(() => {
      return templateFile.value && contentFile.value && selectedFormat.value
    })

    const handleTemplateSelected = (file) => {
      templateFile.value = file
    }

    const handleContentSelected = (file) => {
      contentFile.value = file
    }

    const previewTemplate = () => {
      previewFile.value = templateFile.value
      previewVisible.value = true
    }

    const previewContent = () => {
      previewFile.value = contentFile.value
      previewVisible.value = true
    }

    const closePreview = () => {
      previewVisible.value = false
      previewFile.value = null
    }

    const processTemplate = () => {
      if (!canProcess.value) return

      emit('process', {
        templateFile: templateFile.value,
        contentFile: contentFile.value,
        outputFormat: selectedFormat.value,
        additionalInstruction: additionalInstruction.value
      })
    }

    return {
      templateFile,
      contentFile,
      selectedFormat,
      additionalInstruction,
      outputFormats,
      canProcess,
      previewVisible,
      previewFile,
      handleTemplateSelected,
      handleContentSelected,
      previewTemplate,
      previewContent,
      closePreview,
      processTemplate
    }
  }
}
</script>

<style scoped>
.template-mode {
  padding: 20px 0;
}

.description {
  color: #666;
  margin-bottom: 30px;
}

.upload-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-btn {
  padding: 6px 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
  transition: all 0.3s;
}

.preview-btn:hover {
  background: #5568d3;
  transform: translateY(-1px);
}

.upload-item {
  background: #f8f9ff;
  padding: 20px;
  border-radius: 12px;
  border: 2px solid #e0e7ff;
}

.upload-item h3 {
  margin: 0 0 5px 0;
  color: #667eea;
  font-size: 1.1em;
}

.hint {
  color: #999;
  font-size: 0.9em;
  margin-bottom: 15px;
}

.file-info {
  margin-top: 10px;
  padding: 10px;
  background: #e8f5e9;
  border-radius: 8px;
  color: #2e7d32;
  font-weight: 500;
}

.format-selection {
  margin-bottom: 30px;
}

.format-options {
  display: flex;
  gap: 15px;
  margin-top: 15px;
}

.format-option {
  flex: 1;
  padding: 20px;
  border: 2px solid #ddd;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.format-option:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.format-option.active {
  border-color: #667eea;
  background: #f0f2ff;
}

.format-option input[type="radio"] {
  display: none;
}

.format-icon {
  display: block;
  font-size: 2em;
  margin-bottom: 8px;
}

.format-name {
  display: block;
  font-weight: 600;
  color: #333;
}

.instruction-section {
  margin-bottom: 30px;
}

.textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1em;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}

.btn-large {
  width: 100%;
  padding: 18px;
  font-size: 1.2em;
  font-weight: 600;
}

@media (max-width: 768px) {
  .upload-section {
    grid-template-columns: 1fr;
  }
  
  .format-options {
    flex-direction: column;
  }
}
</style>
