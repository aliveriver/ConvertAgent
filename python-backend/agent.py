"""
LangChain Agent 核心逻辑
负责理解用户指令，调用工具，生成结果
"""
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import get_document_tools

class DocumentAgent:
    """文档处理 Agent"""
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        """
        初始化 Agent
        
        Args:
            model_name: OpenAI 模型名称
        """
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            streaming=True
        )
        
        # 获取工具集（操作 Word 的函数）
        self.tools = get_document_tools()
        
        # 定义 Agent 的 Prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的文档处理助手，精通多种文档格式。

你的职责：
1. 理解用户对文档的操作需求
2. 使用提供的工具来完成任务
3. 返回清晰的处理结果

可用工具分类：

【Word 文档】
- read_document: 读取 Word 文档内容
- write_document: 写入新的 Word 文档
- modify_document: 修改现有文档的内容、格式等

【Markdown 文档】
- read_markdown: 读取 Markdown 文件和结构
- write_markdown: 创建 Markdown 文件

【LaTeX 文档】
- read_latex: 读取 LaTeX 文件和结构
- write_latex: 创建 LaTeX 文件

【图片处理】
- extract_images_from_document: 从 Word 中提取图片

【文档分析】
- extract_document_structure: 提取文档结构（标题、样式等）

【模板应用】
- apply_template_structure: 将内容应用到模板结构
- convert_format: 转换文档格式

工作流程建议：
1. 分析模板文件的结构（使用 extract_document_structure）
2. 读取内容文件的文本和图片
3. 将内容映射到模板结构
4. 生成目标格式的文档
5. 确保图片和格式正确应用

注意事项：
- 确保文件路径正确
- 操作前先读取文档了解结构
- 修改时保持原有格式（除非用户要求修改）
- 处理图片时注意路径和尺寸
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
            max_iterations=10
        )
    
    def process(self, file_path: str, instruction: str) -> dict:
        """
        处理文档
        
        Args:
            file_path: 文档路径
            instruction: 用户指令
            
        Returns:
            处理结果
        """
        try:
            # 构建完整的输入
            full_input = f"""
文件路径：{file_path}

用户需求：{instruction}

请按照用户需求处理文档，并返回处理结果。
"""
            
            # 执行 Agent
            result = self.executor.invoke({"input": full_input})
            
            return {
                "success": True,
                "output": result["output"],
                "steps": len(result.get("intermediate_steps", []))
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_with_template(
        self, 
        template_path: str, 
        content_path: str, 
        output_format: str,
        instruction: str
    ) -> dict:
        """
        使用模板处理文档
        
        Args:
            template_path: 模板文件路径
            content_path: 内容文件路径
            output_format: 输出格式
            instruction: 完整指令
            
        Returns:
            处理结果
        """
        try:
            # 执行 Agent
            result = self.executor.invoke({"input": instruction})
            
            return {
                "success": True,
                "output": result["output"],
                "steps": len(result.get("intermediate_steps", [])),
                "template": template_path,
                "content": content_path,
                "format": output_format
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
