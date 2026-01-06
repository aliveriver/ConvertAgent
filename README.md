# ConvertAgent

🚀 一个基于 AI 的文档处理桌面应用，使用 **Tauri + Vue 3 + FastAPI + LangChain** 构建

## 📦 技术栈

- **前端**: Vue 3 + Vite
- **后端**: Python FastAPI + LangChain/LangGraph
- **桌面**: Tauri (Rust)
- **AI**: OpenAI GPT-4

## 🏗️ 项目结构

```
ConvertAgent/
├── src/                      # Vue 3 前端代码
│   ├── components/           # 组件
│   │   ├── ChatBox.vue       # 对话框
│   │   └── FileUpload.vue    # 文件上传
│   ├── App.vue               # 主应用
│   └── main.js               # 入口
├── python-backend/           # Python 后端
│   ├── app.py                # FastAPI 应用
│   ├── agent.py              # LangChain Agent
│   ├── tools.py              # 文档操作工具
│   └── requirements.txt      # Python 依赖
├── src-tauri/                # Tauri 配置
│   ├── tauri.conf.json       # 主配置
│   └── src/main.rs           # Rust 入口
├── package.json              # Node 依赖
└── vite.config.ts            # Vite 配置
```

## 🚀 快速开始

### 1️⃣ 安装依赖

#### 前端依赖
```bash
npm install
```

#### Python 依赖
```bash
cd python-backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2️⃣ 开发模式

#### 启动 Python 后端
```bash
cd python-backend
.\venv\Scripts\activate
python app.py
```

后端将在 http://127.0.0.1:8765 运行

#### 启动前端开发服务器
```bash
npm run dev
```

前端将在 http://localhost:5173 运行

#### 启动 Tauri 开发模式 (可选)
```bash
npm run tauri dev
```

### 3️⃣ 使用应用

1. 打开应用后，首先输入你的 **OpenAI API Key**
2. 点击"初始化 Agent"
3. 上传 Word 文档 (.docx)
4. 输入处理指令，例如：
   - "将这份简历翻译成英文"
   - "提取所有联系方式并制作表格"
   - "把标题改成红色并加粗"
5. 点击"开始处理"

## 📦 打包发布

```bash
npm run tauri build
```

生成的安装包在 `src-tauri/target/release/bundle/` 目录下

## 🔧 配置说明

### Python 后端配置

复制 `.env.example` 为 `.env` 并填写配置：

```env
OPENAI_API_KEY=your-api-key-here
BACKEND_PORT=8765
MODEL_NAME=gpt-4-turbo-preview
```

### Tauri 配置

编辑 `src-tauri/tauri.conf.json` 可以修改：
- 窗口大小和标题
- 应用图标
- 打包选项

## 🛠️ 开发指南

### 添加新的文档处理工具

在 `python-backend/tools.py` 中添加新的 `@tool` 函数：

```python
@tool
def your_new_tool(param: str) -> str:
    """
    工具描述（LLM 会读取这个）
    """
    # 你的实现
    return "结果"
```

### 修改前端 UI

编辑 `src/App.vue` 和 `src/components/` 下的组件

## 📝 注意事项

1. **首次运行**: 需要先激活 Python 虚拟环境并安装依赖
2. **API Key**: 请妥善保管你的 OpenAI API Key
3. **文件路径**: Windows 路径使用反斜杠 `\`
4. **调试**: 查看终端输出了解 Agent 的思考过程

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

---

**Made with ❤️ by ConvertAgent Team**
