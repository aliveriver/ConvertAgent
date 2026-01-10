<template>
  <div class="content-editor">
    <div class="editor-header">
      <h3>📝 内容编辑器</h3>
      <p class="hint">为每个内容块选择对应的样式</p>
    </div>

    <!-- 样式选择器 -->
    <div class="style-selector" v-if="availableStyles.headings.length || availableStyles.body.length">
      <div class="style-group">
        <span class="style-label">可用样式：</span>
        <span 
          v-for="style in [...availableStyles.headings, ...availableStyles.body].slice(0, 6)" 
          :key="style.name"
          class="style-tag"
        >
          {{ style.name }}
          <span v-if="style.font_size_pt" class="style-size">{{ style.font_size_pt }}pt</span>
        </span>
      </div>
    </div>

    <!-- 内容块列表 -->
    <div class="content-blocks">
      <div 
        v-for="(block, index) in contentBlocks" 
        :key="index"
        class="content-block"
      >
        <div class="block-header">
          <span class="block-number">#{{ index + 1 }}</span>
          <select v-model="block.style_name" class="style-select">
            <optgroup label="标题样式">
              <option 
                v-for="style in availableStyles.headings" 
                :key="style.name"
                :value="style.name"
              >
                {{ style.name }} {{ style.font_size_pt ? `(${style.font_size_pt}pt)` : '' }}
              </option>
            </optgroup>
            <optgroup label="正文样式">
              <option 
                v-for="style in availableStyles.body" 
                :key="style.name"
                :value="style.name"
              >
                {{ style.name }} {{ style.font_size_pt ? `(${style.font_size_pt}pt)` : '' }}
              </option>
            </optgroup>
          </select>
          <button @click="removeBlock(index)" class="remove-btn" title="删除">✕</button>
        </div>
        <textarea 
          v-model="block.text"
          :placeholder="getPlaceholder(block.style_name)"
          class="block-textarea"
          rows="3"
        ></textarea>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="editor-actions">
      <button @click="addBlock('Heading 1')" class="add-btn add-heading">
        ➕ 添加标题
      </button>
      <button @click="addBlock('Normal')" class="add-btn add-body">
        ➕ 添加正文
      </button>
    </div>

    <!-- 预览 -->
    <div class="preview-section" v-if="contentBlocks.length > 0">
      <h4>📋 内容预览</h4>
      <div class="preview-content">
        <div 
          v-for="(block, index) in contentBlocks" 
          :key="index"
          :class="['preview-item', getPreviewClass(block.style_name)]"
        >
          {{ block.text || '(空内容)' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'ContentEditor',
  props: {
    availableStyles: {
      type: Object,
      default: () => ({
        headings: [],
        body: []
      })
    },
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue'],
  
  setup(props, { emit }) {
    const contentBlocks = ref(props.modelValue.length > 0 ? props.modelValue : [
      { style_name: 'Heading 1', text: '' }
    ])

    // 监听变化并通知父组件
    watch(contentBlocks, (newVal) => {
      emit('update:modelValue', newVal)
    }, { deep: true })

    // 监听props变化
    watch(() => props.modelValue, (newVal) => {
      if (JSON.stringify(newVal) !== JSON.stringify(contentBlocks.value)) {
        contentBlocks.value = newVal.length > 0 ? newVal : [{ style_name: 'Heading 1', text: '' }]
      }
    }, { deep: true })

    const addBlock = (styleName) => {
      // 根据可用样式选择默认样式
      let defaultStyle = styleName
      if (styleName === 'Heading 1' && props.availableStyles.headings.length > 0) {
        defaultStyle = props.availableStyles.headings[0].name
      } else if (styleName === 'Normal' && props.availableStyles.body.length > 0) {
        defaultStyle = props.availableStyles.body[0].name
      }
      
      contentBlocks.value.push({
        style_name: defaultStyle,
        text: ''
      })
    }

    const removeBlock = (index) => {
      if (contentBlocks.value.length > 1) {
        contentBlocks.value.splice(index, 1)
      }
    }

    const getPlaceholder = (styleName) => {
      if (styleName.includes('Heading') || styleName.includes('标题') || styleName.includes('Title')) {
        return '输入标题内容...'
      }
      return '输入正文内容...'
    }

    const getPreviewClass = (styleName) => {
      if (styleName.includes('Heading 1') || styleName.includes('标题 1') || styleName.includes('Title')) {
        return 'preview-h1'
      }
      if (styleName.includes('Heading 2') || styleName.includes('标题 2')) {
        return 'preview-h2'
      }
      if (styleName.includes('Heading') || styleName.includes('标题')) {
        return 'preview-h3'
      }
      return 'preview-body'
    }

    return {
      contentBlocks,
      addBlock,
      removeBlock,
      getPlaceholder,
      getPreviewClass
    }
  }
}
</script>

<style scoped>
.content-editor {
  background: #f8f9ff;
  border-radius: 12px;
  padding: 20px;
  border: 2px solid #e0e7ff;
}

.editor-header h3 {
  margin: 0 0 5px 0;
  color: #667eea;
}

.hint {
  color: #999;
  font-size: 0.9em;
  margin-bottom: 15px;
}

.style-selector {
  background: #fff;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.style-label {
  font-weight: 600;
  color: #666;
  margin-right: 10px;
}

.style-tag {
  display: inline-block;
  background: #e8eeff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  margin-right: 6px;
  color: #667eea;
}

.style-size {
  color: #999;
  font-size: 0.85em;
  margin-left: 4px;
}

.content-blocks {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 15px;
}

.content-block {
  background: white;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #ddd;
}

.block-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.block-number {
  font-weight: 600;
  color: #667eea;
  font-size: 0.9em;
}

.style-select {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9em;
  background: white;
}

.remove-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: #ff5757;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8em;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: #ff3333;
  transform: scale(1.1);
}

.block-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95em;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}

.block-textarea:focus {
  outline: none;
  border-color: #667eea;
}

.editor-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.add-btn {
  padding: 10px 16px;
  border: 2px dashed #ccc;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  transition: all 0.2s;
}

.add-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.preview-section h4 {
  margin: 0 0 10px 0;
  color: #666;
}

.preview-content {
  background: white;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.preview-item {
  margin-bottom: 8px;
}

.preview-h1 {
  font-size: 1.5em;
  font-weight: bold;
  color: #333;
}

.preview-h2 {
  font-size: 1.3em;
  font-weight: bold;
  color: #444;
}

.preview-h3 {
  font-size: 1.1em;
  font-weight: 600;
  color: #555;
}

.preview-body {
  font-size: 1em;
  color: #666;
  text-indent: 2em;
}
</style>
