<template>
  <div class="progress-panel" v-if="steps.length > 0 || isProcessing">
    <div class="progress-header">
      <h3>⚙️ 执行进度</h3>
      <div class="status-badge" :class="statusClass">
        {{ statusText }}
      </div>
    </div>
    
    <div class="progress-timeline">
      <div 
        v-for="(step, index) in steps" 
        :key="index"
        :class="['progress-step', `step-${step.type}`]"
      >
        <div class="step-indicator">
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-line" v-if="index < steps.length - 1"></div>
        </div>
        
        <div class="step-content">
          <div class="step-message" v-html="formatMessage(step.message)"></div>
          <div class="step-time">{{ formatTime(step.timestamp) }}</div>
        </div>
      </div>
    </div>
    
    <!-- 加载动画 -->
    <div class="loading-indicator" v-if="isProcessing && !isComplete">
      <div class="spinner"></div>
      <span>正在处理中...</span>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'ProgressPanel',
  
  setup() {
    const steps = ref([])
    const isProcessing = ref(false)
    const isComplete = ref(false)
    const hasError = ref(false)
    let eventSource = null
    
    const statusClass = computed(() => {
      if (hasError.value) return 'status-error'
      if (isComplete.value) return 'status-complete'
      if (isProcessing.value) return 'status-processing'
      return 'status-idle'
    })
    
    const statusText = computed(() => {
      if (hasError.value) return '❌ 失败'
      if (isComplete.value) return '✅ 完成'
      if (isProcessing.value) return '🔄 处理中'
      return '⏸️ 等待'
    })
    
    const formatTime = (timestamp) => {
      const date = new Date(timestamp * 1000)
      return date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
      })
    }
    
    const formatMessage = (message) => {
      // 转换文件链接为可点击的下载链接
      return message.replace(
        /📄 \[([^\]]+)\]\(([^)]+)\)/g,
        '<a href="http://localhost:8765$2" target="_blank" class="file-link">📄 $1</a>'
      ).replace(/\n/g, '<br>')
    }
    
    const connectProgressStream = () => {
      // 连接到 SSE 端点
      eventSource = new EventSource('http://localhost:8765/api/progress')
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // 根据消息类型处理
          switch (data.type) {
            case 'start':
              steps.value = []
              isProcessing.value = true
              isComplete.value = false
              hasError.value = false
              steps.value.push(data)
              break
              
            case 'step':
              steps.value.push(data)
              break
              
            case 'complete':
              steps.value.push(data)
              isProcessing.value = false
              isComplete.value = true
              // 3秒后自动关闭连接
              setTimeout(() => {
                if (eventSource) {
                  eventSource.close()
                }
              }, 3000)
              break
              
            case 'error':
              steps.value.push(data)
              isProcessing.value = false
              hasError.value = true
              if (eventSource) {
                eventSource.close()
              }
              break
          }
        } catch (e) {
          console.error('解析进度消息失败:', e)
        }
      }
      
      eventSource.onerror = (error) => {
        console.error('SSE 连接错误:', error)
        if (eventSource) {
          eventSource.close()
          eventSource = null
        }
      }
    }
    
    const reset = () => {
      steps.value = []
      isProcessing.value = false
      isComplete.value = false
      hasError.value = false
    }
    
    onMounted(() => {
      connectProgressStream()
    })
    
    onUnmounted(() => {
      if (eventSource) {
        eventSource.close()
      }
    })
    
    return {
      steps,
      isProcessing,
      isComplete,
      statusClass,
      statusText,
      formatTime,
      formatMessage,
      reset
    }
  }
}
</script>

<style scoped>
.progress-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
  color: white;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.progress-header h3 {
  margin: 0;
  font-size: 1.3em;
  font-weight: bold;
}

.status-badge {
  padding: 6px 15px;
  border-radius: 20px;
  font-size: 0.9em;
  font-weight: bold;
  transition: all 0.3s;
}

.status-idle {
  background: rgba(255,255,255,0.2);
}

.status-processing {
  background: #ffc107;
  color: #000;
  animation: pulse 2s infinite;
}

.status-complete {
  background: #4caf50;
  color: white;
}

.status-error {
  background: #f44336;
  color: white;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.progress-timeline {
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 15px;
  max-height: 400px;
  overflow-y: auto;
}

.progress-step {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  animation: fadeInStep 0.4s ease-out;
}

@keyframes fadeInStep {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255,255,255,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.9em;
  flex-shrink: 0;
}

.step-start .step-number {
  background: #2196f3;
}

.step-step .step-number {
  background: #ff9800;
}

.step-complete .step-number {
  background: #4caf50;
}

.step-error .step-number {
  background: #f44336;
}

.step-line {
  width: 2px;
  flex: 1;
  background: rgba(255,255,255,0.3);
  margin-top: 5px;
}

.step-content {
  flex: 1;
  padding: 8px 0;
}

.step-message {
  font-size: 1em;
  margin-bottom: 4px;
  line-height: 1.4;
}

.step-message .file-link {
  display: inline-block;
  padding: 6px 12px;
  margin: 5px 5px 5px 0;
  background: rgba(255,255,255,0.9);
  color: #667eea;
  text-decoration: none;
  border-radius: 6px;
  font-weight: bold;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.step-message .file-link:hover {
  background: white;
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.step-time {
  font-size: 0.85em;
  opacity: 0.7;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
  padding: 15px;
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 滚动条样式 */
.progress-timeline::-webkit-scrollbar {
  width: 6px;
}

.progress-timeline::-webkit-scrollbar-track {
  background: rgba(255,255,255,0.1);
  border-radius: 3px;
}

.progress-timeline::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.3);
  border-radius: 3px;
}

.progress-timeline::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.5);
}
</style>
