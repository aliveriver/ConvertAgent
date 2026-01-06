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
        <h2>🔑 配置 AI 服务</h2>
        
        <!-- 提供商选择 -->
        <div class="provider-selection">
          <label class="form-label">选择 AI 提供商</label>
          <div class="provider-grid">
            <label 
              v-for="provider in providers" 
              :key="provider.id"
              :class="['provider-card', { active: selectedProvider === provider.id }]"
            >
              <input 
                type="radio" 
                :value="provider.id" 
                v-model="selectedProvider"
                name="provider"
              />
              <span class="provider-name">{{ provider.name }}</span>
              <span class="provider-hint">{{ getProviderHint(provider.id) }}</span>
            </label>
          </div>
        </div>

        <!-- 模型选择（输入框） -->
        <div class="model-selection">
          <label class="form-label">
            模型名称（可选）
            <span class="hint-inline">留空使用默认模型</span>
          </label>
          <input 
            v-model="selectedModel" 
            type="text"
            :placeholder="getModelPlaceholder()"
            class="input"
          />
          <p class="model-examples" v-if="selectedProvider">
            <strong>常用模型：</strong>
            <span 
              v-for="model in availableModels" 
              :key="model"
              class="model-tag"
              @click="selectedModel = model"
            >
              {{ model }}
            </span>
          </p>
        </div>

        <!-- API Key 输入 -->
        <div class="api-key-input">
          <label class="form-label">API Key</label>
          <input 
            v-model="apiKey" 
            type="password" 
            :placeholder="getApiKeyPlaceholder()"
            class="input"
            @keyup.enter="initAgent"
          />
        </div>

        <button @click="initAgent" class="btn btn-primary" :disabled="loading || !apiKey">
          {{ loading ? '初始化中...' : '初始化 Agent' }}
        </button>
        <p class="hint">API Key 和设置将安全保存在本地浏览器中</p>
      </div>

      <!-- 模板模式 -->
      <div class="template-section" v-if="agentReady">
        <TemplateMode @process="processWithTemplate" :loading="loading" />
        
        <!-- 进度面板 -->
        <ProgressPanel ref="progressPanel" />
        
        <!-- 结果显示 -->
        <ChatBox :messages="messages" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import ChatBox from './components/ChatBox.vue'
import TemplateMode from './components/TemplateMode.vue'
import ProgressPanel from './components/ProgressPanel.vue'

const API_BASE = 'http://127.0.0.1:8765'
const API_KEY_STORAGE = 'convertagent_api_key'
const PROVIDER_STORAGE = 'convertagent_provider'
const MODEL_STORAGE = 'convertagent_model'

export default {
  name: 'App',
  components: {
    ChatBox,
    TemplateMode,
    ProgressPanel
  },
  
  setup() {
    const apiKey = ref('')
    const agentReady = ref(false)
    const loading = ref(false)
    const messages = ref([])
    const providers = ref([])
    const selectedProvider = ref('openai')
    const selectedModel = ref('')

    // 可用模型列表（根据选择的提供商）
    const availableModels = computed(() => {
      const provider = providers.value.find(p => p.id === selectedProvider.value)
      return provider ? provider.models : []
    })

    // 监听提供商变化，重置模型选择
    watch(selectedProvider, () => {
      selectedModel.value = ''
    })

    // 获取提供商提示信息
    const getProviderHint = (providerId) => {
      const hints = {
        'openai': '官方 GPT-4',
        'siliconflow': '国内高性价比',
        'zhipu': '智谱 GLM-4',
        'moonshot': 'Kimi 长上下文',
        'deepseek': 'DeepSeek 编程'
      }
      return hints[providerId] || ''
    }

    // 获取 API Key 占位符
    const getApiKeyPlaceholder = () => {
      const placeholders = {
        'openai': '输入 OpenAI API Key (sk-...)',
        'siliconflow': '输入硅基流动 API Key',
        'zhipu': '输入智谱 API Key',
        'moonshot': '输入月之暗面 API Key',
        'deepseek': '输入 DeepSeek API Key'
      }
      return placeholders[selectedProvider.value] || '输入 API Key'
    }

    // 获取模型输入占位符
    const getModelPlaceholder = () => {
      const provider = providers.value.find(p => p.id === selectedProvider.value)
      if (provider) {
        return `如：${provider.default_model}`
      }
      return '输入模型名称'
    }

    // 加载提供商列表
    const loadProviders = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/providers`)
        providers.value = response.data.providers
      } catch (error) {
        console.error('加载提供商失败:', error)
      }
    }

    // 页面加载时，尝试从 localStorage 读取配置
    onMounted(async () => {
      await loadProviders()
      
      const savedKey = localStorage.getItem(API_KEY_STORAGE)
      const savedProvider = localStorage.getItem(PROVIDER_STORAGE)
      const savedModel = localStorage.getItem(MODEL_STORAGE)
      
      if (savedKey) {
        apiKey.value = savedKey
        selectedProvider.value = savedProvider || 'openai'
        selectedModel.value = savedModel || ''
        // 自动初始化 Agent
        await autoInitAgent(savedKey, selectedProvider.value, selectedModel.value)
      }
    })

    // 自动初始化（静默模式）
    const autoInitAgent = async (key, provider, model) => {
      try {
        const formData = new FormData()
        formData.append('api_key', key)
        formData.append('provider', provider)
        if (model) formData.append('model', model)
        
        const response = await axios.post(`${API_BASE}/api/init`, formData)
        
        if (response.data.success) {
          agentReady.value = true
          messages.value.push({
            role: 'system',
            content: `✅ ${response.data.message}`
          })
        }
      } catch (error) {
        // 静默失败，清除无效的配置
        localStorage.removeItem(API_KEY_STORAGE)
        localStorage.removeItem(PROVIDER_STORAGE)
        localStorage.removeItem(MODEL_STORAGE)
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
        formData.append('provider', selectedProvider.value)
        if (selectedModel.value) {
          formData.append('model', selectedModel.value)
        }
        
        const response = await axios.post(`${API_BASE}/api/init`, formData)
        
        if (response.data.success) {
          agentReady.value = true
          // 保存配置到 localStorage
          localStorage.setItem(API_KEY_STORAGE, apiKey.value)
          localStorage.setItem(PROVIDER_STORAGE, selectedProvider.value)
          localStorage.setItem(MODEL_STORAGE, selectedModel.value || '')
          
          messages.value.push({
            role: 'system',
            content: `✅ ${response.data.message}`
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
      if (confirm('确定要清除配置并退出吗？')) {
        localStorage.removeItem(API_KEY_STORAGE)
        localStorage.removeItem(PROVIDER_STORAGE)
        localStorage.removeItem(MODEL_STORAGE)
        apiKey.value = ''
        selectedProvider.value = 'openai'
        selectedModel.value = ''
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
            role: 'system',
            content: `✅ ${response.data.message}`
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
      providers,
      selectedProvider,
      selectedModel,
      availableModels,
      getProviderHint,
      getApiKeyPlaceholder,
      getModelPlaceholder,
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

.provider-selection,
.model-selection,
.api-key-input {
  margin-bottom: 25px;
}

.form-label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  font-size: 1em;
}

.provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.provider-card {
  padding: 20px 15px;
  border: 2px solid #ddd;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.provider-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.provider-card.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
}

.provider-card input[type="radio"] {
  display: none;
}

.provider-name {
  font-weight: 600;
  color: #333;
  font-size: 0.95em;
}

.provider-hint {
  font-size: 0.8em;
  color: #999;
}

.select {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1em;
  box-sizing: border-box;
  background: white;
  cursor: pointer;
}

.select:focus {
  outline: none;
  border-color: #667eea;
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
