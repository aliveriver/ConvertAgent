<template>
  <div class="file-upload-simple">
    <div class="upload-box" @click="triggerFileInput">
      <input 
        ref="fileInput"
        type="file" 
        :accept="accept"
        @change="handleFileChange"
        style="display: none"
      />
      <span class="placeholder">{{ placeholder }}</span>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'FileUploadSimple',
  props: {
    accept: {
      type: String,
      default: '.docx,.doc,.pdf'
    },
    placeholder: {
      type: String,
      default: '点击选择文件'
    }
  },
  emits: ['file-selected'],
  
  setup(props, { emit }) {
    const fileInput = ref(null)

    const triggerFileInput = () => {
      fileInput.value?.click()
    }

    const handleFileChange = (event) => {
      const file = event.target.files?.[0]
      if (file) {
        emit('file-selected', file)
      }
    }

    return {
      fileInput,
      triggerFileInput,
      handleFileChange
    }
  }
}
</script>

<style scoped>
.upload-box {
  border: 2px dashed #667eea;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.upload-box:hover {
  border-color: #5568d3;
  background: #f9fafb;
}

.placeholder {
  color: #667eea;
  font-weight: 500;
}
</style>
