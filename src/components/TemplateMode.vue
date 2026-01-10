<template>
  <div class="template-mode">
    <h2>🎨 模板模式</h2>
    <p class="description">上传模板，AI 分析后您可以为每段内容选择对应样式</p>

    <!-- 步骤指示器 -->
    <div class="steps-indicator">
      <div :class="['step', { active: currentStep >= 1, completed: currentStep > 1 }]">
        <span class="step-num">1</span>
        <span class="step-text">上传模板</span>
      </div>
      <div class="step-line" :class="{ active: currentStep > 1 }"></div>
      <div :class="['step', { active: currentStep >= 2, completed: currentStep > 2 }]">
        <span class="step-num">2</span>
        <span class="step-text">编辑内容</span>
      </div>
      <div class="step-line" :class="{ active: currentStep > 2 }"></div>
      <div :class="['step', { active: currentStep >= 3 }]">
        <span class="step-num">3</span>
        <span class="step-text">生成文档</span>
      </div>
    </div>

    <!-- 步骤 1: 上传模板 -->
    <div class="step-content" v-if="currentStep === 1">
      <div class="upload-section">
        <div class="upload-item">
          <h3>📋 模板文件</h3>
          <p class="hint">上传包含样式定义的 Word 模板</p>
          <FileUploadSimple 
            @file-selected="handleTemplateSelected" 
            :accept="'.docx,.doc'"
            :placeholder="'上传模板文件 (.docx)'"
          />
          <div v-if="templateFile" class="file-info">
            <span>✅ {{ templateFile.name }}</span>
          </div>
        </div>
      </div>

      <button 
        @click="analyzeTemplate" 
        class="btn btn-primary"
        :disabled="!templateFile || analyzing"
      >
        <span v-if="analyzing">⏳ 分析中...</span>
        <span v-else>📊 分析模板样式</span>
      </button>

      <div v-if="analyzeError" class="error-message">
        ❌ {{ analyzeError }}
      </div>
    </div>

    <!-- 步骤 2: 编辑内容 -->
    <div class="step-content" v-if="currentStep === 2">
      <div class="template-info">
        <h3>📋 模板: {{ templateFile?.name }}</h3>
        <button @click="currentStep = 1" class="btn-link">重新选择模板</button>
      </div>

      <ContentEditor 
        :available-styles="templateStyles"
        v-model="contentBlocks"
      />

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

      <button 
        @click="generateDocument" 
        class="btn btn-primary btn-large"
        :disabled="!hasContent || loading"
      >
        <span v-if="loading">⏳ 生成中...</span>
        <span v-else>✨ 生成文档</span>
      </button>
    </div>

    <!-- 步骤 3: 生成完成 -->
    <div class="step-content" v-if="currentStep === 3">
      <div class="success-message">
        <h3>✅ 文档生成成功！</h3>
        <p>文件已保存，您可以在进度面板中下载。</p>
        <button @click="resetAll" class="btn btn-secondary">🔄 创建新文档</button>
      </div>
    </div>

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
import axios from 'axios'
import FileUploadSimple from './FileUploadSimple.vue'
import FilePreview from './FilePreview.vue'
import ContentEditor from './ContentEditor.vue'

const API_BASE = 'http://127.0.0.1:8765'

export default {
  name: 'TemplateMode',
  components: {
    FileUploadSimple,
    FilePreview,
    ContentEditor
  },
  props: {
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['process'],
  
  setup(props, { emit }) {
    const currentStep = ref(1)
    const templateFile = ref(null)
    const templatePath = ref('')
    const templateStyles = ref({ headings: [], body: [] })
    const contentBlocks = ref([])
    const selectedFormat = ref('word')
    const previewVisible = ref(false)
    const previewFile = ref(null)
    const analyzing = ref(false)
    const analyzeError = ref('')

    const outputFormats = [
      { value: 'word', label: 'Word', icon: '📝' }
    ]

    const hasContent = computed(() => {
      return contentBlocks.value.some(b => b.text && b.text.trim())
    })

    const handleTemplateSelected = (file) => {
      templateFile.value = file
      analyzeError.value = ''
    }

    const analyzeTemplate = async () => {
      if (!templateFile.value) return
      
      analyzing.value = true
      analyzeError.value = ''
      
      try {
        const formData = new FormData()
        formData.append('template_file', templateFile.value)
        
        const response = await axios.post(
          `${API_BASE}/api/analyze-template`,
          formData,
          { headers: { 'Content-Type': 'multipart/form-data' } }
        )
        
        if (response.data.success) {
          templatePath.value = response.data.template_path
          templateStyles.value = response.data.styles
          
          // 初始化内容块
          const defaultHeading = templateStyles.value.headings[0]?.name || 'Heading 1'
          contentBlocks.value = [
            { style_name: defaultHeading, text: '' }
          ]
          
          currentStep.value = 2
        } else {
          analyzeError.value = response.data.error || '分析失败'
        }
      } catch (error) {
        analyzeError.value = error.response?.data?.error || error.message
      } finally {
        analyzing.value = false
      }
    }

    const generateDocument = async () => {
      if (!hasContent.value) return
      
      try {
        const structuredContent = {
          elements: contentBlocks.value.filter(b => b.text && b.text.trim())
        }
        
        const formData = new FormData()
        formData.append('template_path', templatePath.value)
        formData.append('structured_content', JSON.stringify(structuredContent))
        formData.append('output_format', selectedFormat.value)
        
        const response = await axios.post(
          `${API_BASE}/api/process-structured`,
          formData,
          { headers: { 'Content-Type': 'multipart/form-data' } }
        )
        
        if (response.data.success) {
          currentStep.value = 3
        }
      } catch (error) {
        console.error('生成失败:', error)
      }
    }

    const resetAll = () => {
      currentStep.value = 1
      templateFile.value = null
      templatePath.value = ''
      templateStyles.value = { headings: [], body: [] }
      contentBlocks.value = []
    }

    const closePreview = () => {
      previewVisible.value = false
      previewFile.value = null
    }

    return {
      currentStep,
      templateFile,
      templatePath,
      templateStyles,
      contentBlocks,
      selectedFormat,
      outputFormats,
      hasContent,
      previewVisible,
      previewFile,
      analyzing,
      analyzeError,
      handleTemplateSelected,
      analyzeTemplate,
      generateDocument,
      resetAll,
      closePreview
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

/* 步骤指示器 */
.steps-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
}

.step {
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0.5;
}

.step.active {
  opacity: 1;
}

.step.completed .step-num {
  background: #4caf50;
}

.step-num {
  width: 28px;
  height: 28px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9em;
}

.step-text {
  font-weight: 500;
  color: #333;
}

.step-line {
  width: 60px;
  height: 3px;
  background: #ddd;
  margin: 0 10px;
}

.step-line.active {
  background: #667eea;
}

/* 上传区域 */
.upload-section {
  margin-bottom: 20px;
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

.error-message {
  margin-top: 15px;
  padding: 12px;
  background: #ffebee;
  border-radius: 8px;
  color: #c62828;
}

/* 模板信息 */
.template-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  background: #e8f5e9;
  border-radius: 8px;
  margin-bottom: 20px;
}

.template-info h3 {
  margin: 0;
  font-size: 1em;
  color: #2e7d32;
}

.btn-link {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  font-size: 0.9em;
  text-decoration: underline;
}

/* 格式选择 */
.format-selection {
  margin: 25px 0;
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

/* 按钮 */
.btn {
  padding: 12px 30px;
  border: none;
  border-radius: 8px;
  font-size: 1em;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-large {
  width: 100%;
  padding: 18px;
  font-size: 1.2em;
  font-weight: 600;
  margin-top: 20px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 成功消息 */
.success-message {
  text-align: center;
  padding: 40px;
  background: #e8f5e9;
  border-radius: 12px;
}

.success-message h3 {
  color: #2e7d32;
  margin-bottom: 10px;
}

.success-message p {
  color: #666;
  margin-bottom: 20px;
}
</style>
