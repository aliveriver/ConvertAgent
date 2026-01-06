<template>
  <div id="app">
    <div class="container">
      <header class="app-header">
        <h1>📄 ConvertAgent</h1>
        <p class="subtitle">AI 驱动的文档模板处理助手</p>
        <button v-if="agentReady" @click="logout" class="logout-btn">🔑 重新配置</button>
      </header>

      <!-- API Key 配置区 -->
      <div class="config-section" v-if="!agentReady">
        <h2>🔑 配置 API Key</h2>
        <input 
          v-model="apiKey" 
          type="password" 
          placeholder="输入你的 OpenAI API Key"
          class="input"
          @keyup.enter="initAgent"
        />
        <button @click="initAgent" class="btn btn-primary" :disabled="loading">
          {{ loading ? '初始化中...' : '初始化 Agent' }}
        </button>
        <p class="hint">API Key 将安全保存在本地浏览器中</p>
      </div>

      <!-- 模板模式 -->
      <div class="template-section" v-if="agentReady">
        <TemplateMode @process="processWithTemplate" :loading="loading" />
        
        <!-- 结果显示 -->
        <ChatBox :messages="messages" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import ChatBox from './components/ChatBox.vue'
import TemplateMode from './components/TemplateMode.vue'

const API_BASE = 'http://127.0.0.1:8765'
const API_KEY_STORAGE = 'convertagent_api_key'

export default {
  name: 'App',
  components: {
    ChatBox,
    TemplateMode
  },
  
  setup() {
    const apiKey = ref('')
    const agentReady = ref(false)
    const loading = ref(false)
    const messages = ref([])

    // 页面加载时，尝试从 localStorage 读取 API Key
    onMounted(async () => {
      const savedKey = localStorage.getItem(API_KEY_STORAGE)
      if (savedKey) {
        apiKey.value = savedKey
        // 自动初始化 Agent
        await autoInitAgent(savedKey)
      }
    })

    // 自动初始化（静默模式）
    const autoInitAgent = async (key) => {
      try {
        const formData = new FormData()
        formData.append('api_key', key)
        
        const response = await axios.post(`${API_BASE}/api/init`, formData)
        
        if (response.data.success) {
          agentReady.value = true
          messages.value.push({
            role: 'system',
            content: '✅ Agent 已自动初始化，可以开始使用！'
          })
        }
      } catch (error) {
        // 静默失败，清除无效的 key
        localStorage.removeItem(API_KEY_STORAGE)
        console.error('自动初始化失败:', error)
      }
    }

    // 手动初始化 Agent
    const initAgent = async () => {
      if (!apiKey.value) {
        alert('请输入 API Key')
        return
      }

      loading.value = true
      try {
        const formData = new FormData()
        formData.append('api_key', apiKey.value)
        
        const response = await axios.post(`${API_BASE}/api/init`, formData)
        
        if (response.data.success) {
          agentReady.value = true
          // 保存 API Key 到 localStorage
          localStorage.setItem(API_KEY_STORAGE, apiKey.value)
          messages.value.push({
            role: 'system',
            content: '✅ Agent 已就绪，API Key 已安全保存！'
          })
        }
      } catch (error) {
        alert('初始化失败：' + (error.response?.data?.error || error.message))
      } finally {
        loading.value = false
      }
    }

    // 退出登录
    const logout = () => {
      if (confirm('确定要清除 API Key 并退出吗？')) {
        localStorage.removeItem(API_KEY_STORAGE)
        apiKey.value = ''
        agentReady.value = false
        messages.value = []
      }
    }

    // 模板模式：使用模板处理
    const processWithTemplate = async (data) => {
      loading.value = true
      
      messages.value.push({
        role: 'user',
        content: `🎨 使用模板模式生成文档\n📋 模板：${data.templateFile.name}\n📄 内容：${data.contentFile.name}\n📦 输出：${data.outputFormat}`
      })

      try {
        const formData = new FormData()
        formData.append('template_file', data.templateFile)
        formData.append('content_file', data.contentFile)
        formData.append('output_format', data.outputFormat)
        formData.append('additional_instruction', data.additionalInstruction || '')

        const response = await axios.post(
          `${API_BASE}/api/process-with-template`, 
          formData,
          { headers: { 'Content-Type': 'multipart/form-data' } }
        )

        if (response.data.success) {
          messages.value.push({
            role: 'assistant',
            content: `✅ ${response.data.message}\n\n${response.data.result.output}`
          })
        }
      } catch (error) {
        messages.value.push({
          role: 'error',
          content: '❌ 处理失败：' + (error.response?.data?.error || error.message)
        })
      } finally {
        loading.value = false
      }
    }

    return {
      apiKey,
      agentReady,
      loading,
      messages,
      initAgent,
      logout,
      processWithTemplate
    }
  }
}
</script>

<style scoped>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.app-header > div:first-child {
  flex: 1;
}

h1 {
  font-size: 2.5em;
  margin: 0;
  color: #667eea;
}

.subtitle {
  color: #666;
  margin-top: 5px;
}

.logout-btn {
  padding: 10px 20px;
  background: #fff;
  border: 2px solid #667eea;
  border-radius: 8px;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
}

.config-section, .template-section {
  margin-top: 30px;
}

.hint {
  color: #999;
  font-size: 0.9em;
  margin-top: 10px;
  text-align: center;
}

.input, .textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1em;
  box-sizing: border-box;
  margin-bottom: 15px;
}

.textarea {
  resize: vertical;
  font-family: inherit;
}

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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
