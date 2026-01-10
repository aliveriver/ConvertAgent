"""
LangChain Agent 核心逻辑
负责理解用户指令，生成代码处理文档
"""
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import get_document_tools
import json
from code_executor import get_code_execution_tools

class DocumentAgent:
    """文档处理 Agent - 基于代码生成"""
    
    # API 提供商配置
    PROVIDERS = {
        "openai": {
            "name": "OpenAI",
            "base_url": "https://api.openai.com/v1",
            "models": ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
            "default_model": "gpt-4-turbo-preview"
        },
        "siliconflow": {
            "name": "硅基流动 SiliconFlow",
            "base_url": "https://api.siliconflow.cn/v1",
            "models": ["Pro/zai-org/GLM-4.7", "Qwen/Qwen2.5-72B-Instruct", "deepseek-ai/DeepSeek-V2.5"],
            "default_model": "Qwen/Qwen2.5-72B-Instruct"
        },
        "zhipu": {
            "name": "智谱AI GLM",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "models": ["glm-4", "glm-4-plus", "glm-3-turbo"],
            "default_model": "glm-4"
        },
        "moonshot": {
            "name": "月之暗面 Kimi",
            "base_url": "https://api.moonshot.cn/v1",
            "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
            "default_model": "moonshot-v1-32k"
        },
        "deepseek": {
            "name": "DeepSeek",
            "base_url": "https://api.deepseek.com/v1",
            "models": ["deepseek-chat", "deepseek-coder"],
            "default_model": "deepseek-chat"
        }
    }
    
    def __init__(
        self, 
        api_key: str,
        provider: str = "openai",
        model_name: str = None
    ):
        """
        初始化 Agent
        
        Args:
            api_key: API 密钥
            provider: 提供商 ID (openai/siliconflow/zhipu/moonshot/deepseek)
            model_name: 模型名称（可选，使用默认模型）
        """
        # 获取提供商配置
        if provider not in self.PROVIDERS:
            raise ValueError(f"不支持的提供商: {provider}")
        
        provider_config = self.PROVIDERS[provider]
        
        # 确定使用的模型
        if model_name is None:
            model_name = provider_config["default_model"]
        
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            streaming=True,
            openai_api_key=api_key,
            openai_api_base=provider_config["base_url"]
        )
        
        self.provider = provider
        self.provider_name = provider_config["name"]
        self.model_name = model_name
        
        # 🔧 将API配置设置为环境变量，让代码执行工具也能使用
        import os
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_API_BASE"] = provider_config["base_url"]
        os.environ["MODEL_NAME"] = model_name
        print(f"[OK] API配置已设置: {self.provider_name} - {self.model_name}")
        
        # 获取工具集（文档分析 + 代码执行）
        self.tools = get_document_tools() + get_code_execution_tools()
        
        # 定义 Agent 的 Prompt（简化版，明确三步流程）
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的文档处理助手。

你的任务：根据模板格式生成新文档

📋 标准工作流程（严格按顺序执行三步）：

**第1步：分析模板** 📐
- 调用工具：analyze_template_structure(模板文件路径)
- 目的：了解模板中有哪些样式（标题样式、正文样式、字体大小等）
- 记住分析结果的关键信息

**第2步：分析内容** 📄
- 调用工具：analyze_content_structure(内容文件路径)
- 目的：识别内容中哪些是标题、哪些是正文、有无图片和表格
- 记住分析结果的关键信息

**第3步：生成并执行代码** 🚀
- 调用工具：generate_and_execute_document_code
- 必需参数（从用户指令的【文件信息】部分获取）：
  * template_path: 模板文件的完整路径
  * content_path: 内容文件的完整路径
  * output_path: 输出文件的完整路径
  * template_summary: 第1步得到的模板分析摘要（简短文字，不要传JSON！）
  * content_summary: 第2步得到的内容分析摘要（简短文字，不要传JSON！）
- 这个工具会自动生成Python代码并执行，你不需要做其他事情

⚠️ 重要提醒：
1. 严格按照1→2→3的顺序执行，不要跳步
2. template_summary 和 content_summary 必须是简短的文字描述，不要传递完整的JSON
3. 所有路径都从用户指令中的【文件信息】部分获取
4. 第3步调用后，代码会自动执行，不需要你再做任何处理

就这么简单！三步走，完成任务。
"""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建 Agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # 创建 Executor（真正执行 Agent 的组件）
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,  # 打印详细日志，方便调试
            handle_parsing_errors=True,
            max_iterations=15,  # 增加迭代次数
            return_intermediate_steps=True  # 返回中间步骤
        )
    
    def process(self, file_path: str, instruction: str, progress_callback=None) -> dict:
        """
        处理文档
        
        Args:
            file_path: 文档路径
            instruction: 用户指令
            progress_callback: 进度回调函数
            
        Returns:
            处理结果
        """
        try:
            if progress_callback:
                progress_callback("🔍 分析用户需求...")
            
            # 构建完整的输入
            full_input = f"""
文件路径：{file_path}

用户需求：{instruction}

请按照用户需求处理文档，并返回处理结果。
"""
            
            if progress_callback:
                progress_callback("🤖 启动 Agent 执行...")
            
            # 创建自定义回调来捕获中间步骤
                if progress_callback:
                    # 执行 Agent 并捕获步骤
                    result = self.executor.invoke({"input": full_input})

                    # 分析中间步骤（防御性解析：处理 tool input 为 JSON 字符串的情况）
                    intermediate_steps = result.get("intermediate_steps", [])
                    for i, (action, observation) in enumerate(intermediate_steps):
                        tool_name = action.tool if hasattr(action, 'tool') else 'unknown'
                        # 尝试解析 action 的输入（若为字符串且为 JSON，则解析为对象）
                        display_input = None
                        try:
                            if hasattr(action, 'tool_input') and isinstance(action.tool_input, str):
                                try:
                                    display_input = json.loads(action.tool_input)
                                except Exception:
                                    display_input = action.tool_input
                            elif hasattr(action, 'tool_input'):
                                display_input = action.tool_input
                        except Exception:
                            display_input = None

                        if display_input is None:
                            progress_callback(f"[STEP] 步骤 {i+1}: 调用工具 {tool_name}")
                        else:
                            progress_callback(f"[STEP] 步骤 {i+1}: 调用工具 {tool_name} 参数: {display_input}")
            else:
                result = self.executor.invoke({"input": full_input})
            
            if progress_callback:
                progress_callback("[OK] 处理完成")
            
            return {
                "success": True,
                "output": result["output"],
                "steps": len(result.get("intermediate_steps", []))
            }
        
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ 错误: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_with_template(
        self, 
        template_path: str, 
        content_path: str, 
        output_format: str,
        instruction: str,
        output_path: str = None,
        progress_callback=None
    ) -> dict:
        """
        使用模板处理文档
        
        Args:
            template_path: 模板文件路径
            content_path: 内容文件路径
            output_format: 输出格式
            instruction: 完整指令
            output_path: 输出文件路径（可选）
            progress_callback: 进度回调函数
            
        Returns:
            处理结果
        """
        try:
            if progress_callback:
                progress_callback("🔍 分析模板和内容...")
            
            # 如果指定了输出路径，添加到指令中
            if output_path:
                instruction = instruction.replace(
                    "output.docx",
                    output_path
                )
                instruction = instruction.replace(
                    "uploads/output.docx",
                    output_path
                )
            
            # 执行 Agent
            result = self.executor.invoke({"input": instruction})

            if progress_callback:
                # 分析中间步骤（尝试解析字符串形式的工具参数）
                intermediate_steps = result.get("intermediate_steps", [])
                for i, (action, observation) in enumerate(intermediate_steps):
                    tool_name = action.tool if hasattr(action, 'tool') else 'unknown'
                    display_input = None
                    try:
                        if hasattr(action, 'tool_input') and isinstance(action.tool_input, str):
                            try:
                                display_input = json.loads(action.tool_input)
                            except Exception:
                                display_input = action.tool_input
                        elif hasattr(action, 'tool_input'):
                            display_input = action.tool_input
                    except Exception:
                        display_input = None

                    if display_input is None:
                        progress_callback(f"[STEP] 步骤 {i+1}: 调用工具 {tool_name}")
                    else:
                        progress_callback(f"[STEP] 步骤 {i+1}: 调用工具 {tool_name} 参数: {display_input}")
            
            if progress_callback:
                progress_callback("[OK] 模板处理完成")
            
            return {
                "success": True,
                "output": result["output"],
                "steps": len(result.get("intermediate_steps", [])),
                "template": template_path,
                "content": content_path,
                "format": output_format
            }
        
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ 错误: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
