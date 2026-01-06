<template>
  <div class="file-upload">
    <div class="upload-box" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
      <input 
        ref="fileInput"
        type="file" 
        accept=".docx,.doc,.pdf"
        @change="handleFileChange"
        style="display: none"
      />
      <div v-if="!selectedFile" class="upload-prompt">
        <span class="icon">📁</span>
        <p>点击或拖拽上传文档</p>
        <small>支持 .docx, .doc, .pdf</small>
      </div>
      <div v-else class="file-info">
        <span class="icon">✅</span>
        <p><strong>{{ selectedFile.name }}</strong></p>
        <small>{{ formatFileSize(selectedFile.size) }}</small>
        <button @click.stop="clearFile" class="clear-btn">✖</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'FileUpload',
  emits: ['file-selected'],
  
  setup(props, { emit }) {
    const fileInput = ref(null)
    const selectedFile = ref(null)

    const triggerFileInput = () => {
      fileInput.value?.click()
    }

    const handleFileChange = (event) => {
      const file = event.target.files?.[0]
      if (file) {
        selectedFile.value = file
        emit('file-selected', file)
      }
    }

    const handleDrop = (event) => {
      const file = event.dataTransfer.files?.[0]
      if (file && file.name.match(/\.(docx?|pdf)$/i)) {
        selectedFile.value = file
        emit('file-selected', file)
      }
    }

    const clearFile = () => {
      selectedFile.value = null
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    const formatFileSize = (bytes) => {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    }

    return {
      fileInput,
      selectedFile,
      triggerFileInput,
      handleFileChange,
      handleDrop,
      clearFile,
      formatFileSize
    }
  }
}
</script>

<style scoped>
.file-upload {
  margin: 20px 0;
}

.upload-box {
  border: 2px dashed #667eea;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #f8f9ff;
}

.upload-box:hover {
  border-color: #5568d3;
  background: #f0f2ff;
}

.icon {
  font-size: 3em;
  display: block;
  margin-bottom: 10px;
}

.upload-prompt p {
  font-size: 1.1em;
  margin: 10px 0;
  color: #333;
}

.file-info {
  position: relative;
}

.clear-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 1em;
}

.clear-btn:hover {
  background: #ff3838;
}

small {
  color: #999;
}
</style>
