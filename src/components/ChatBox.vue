<template>
  <div class="chat-box" v-if="messages.length > 0">
    <h3>💬 对话记录</h3>
    <div class="messages">
      <div 
        v-for="(msg, index) in messages" 
        :key="index"
        :class="['message', `message-${msg.role}`]"
      >
        <div class="message-header">
          <span class="role-icon">{{ getRoleIcon(msg.role) }}</span>
          <span class="role-name">{{ getRoleName(msg.role) }}</span>
        </div>
        <div class="message-content" v-html="formatContent(msg.content)"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChatBox',
  props: {
    messages: {
      type: Array,
      required: true
    }
  },
  
  setup() {
    const getRoleIcon = (role) => {
      const icons = {
        'user': '👤',
        'assistant': '🤖',
        'system': 'ℹ️',
        'error': '❌'
      }
      return icons[role] || '💬'
    }

    const getRoleName = (role) => {
      const names = {
        'user': '你',
        'assistant': 'Agent',
        'system': '系统',
        'error': '错误'
      }
      return names[role] || role
    }

    const formatContent = (content) => {
      // 简单的 Markdown 转换
      return content
        .replace(/\n/g, '<br>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    }

    return {
      getRoleIcon,
      getRoleName,
      formatContent
    }
  }
}
</script>

<style scoped>
.chat-box {
  margin-top: 30px;
  border-top: 2px solid #eee;
  padding-top: 20px;
}

.messages {
  max-height: 500px;
  overflow-y: auto;
  padding: 10px;
}

.message {
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 10px;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-user {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
}

.message-assistant {
  background: #f3e5f5;
  border-left: 4px solid #9c27b0;
}

.message-system {
  background: #e8f5e9;
  border-left: 4px solid #4caf50;
}

.message-error {
  background: #ffebee;
  border-left: 4px solid #f44336;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555;
}

.role-icon {
  font-size: 1.2em;
}

.message-content {
  line-height: 1.6;
  color: #333;
}

.message-content code {
  background: rgba(0,0,0,0.05);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}
</style>
