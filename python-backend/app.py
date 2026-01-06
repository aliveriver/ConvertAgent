"""
FastAPI 主应用入口
运行在本地，为前端提供 API 服务
"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pathlib import Path
from typing import Optional
import os

from agent import DocumentAgent

app = FastAPI(title="ConvertAgent API", version="1.0.0")

# 配置 CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tauri 会从 tauri://localhost 访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 Agent（延迟初始化，等待 API Key）
agent: Optional[DocumentAgent] = None

@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "ConvertAgent Backend is running"}

@app.post("/api/init")
async def init_agent(api_key: str = Form(...)):
    """
    初始化 Agent
    前端传入 OpenAI API Key
    """
    global agent
    try:
        os.environ["OPENAI_API_KEY"] = api_key
        agent = DocumentAgent()
        return {"success": True, "message": "Agent 初始化成功"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/process")
async def process_document(
    file: UploadFile = File(...),
    instruction: str = Form(...)
):
    """
    处理文档
    接收文件 + 用户指令，返回处理结果
    """
    if agent is None:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "请先初始化 Agent"}
        )
    
    try:
        # 保存上传的文件
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 调用 Agent 处理
        result = agent.process(str(file_path), instruction)
        
        return {
            "success": True,
            "message": "处理完成",
            "result": result
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/process-with-template")
async def process_with_template(
    template_file: UploadFile = File(...),
    content_file: UploadFile = File(...),
    output_format: str = Form(...),
    additional_instruction: str = Form(default="")
):
    """
    使用模板处理文档
    接收模板文件 + 内容文件，生成指定格式的输出
    
    Args:
        template_file: 模板文件（word/markdown/latex）
        content_file: 内容文件（包含文本和图片）
        output_format: 输出格式（word/markdown/latex）
        additional_instruction: 额外的处理指令
    """
    if agent is None:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "请先初始化 Agent"}
        )
    
    try:
        # 保存上传的文件
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        template_path = upload_dir / f"template_{template_file.filename}"
        content_path = upload_dir / f"content_{content_file.filename}"
        
        with open(template_path, "wb") as f:
            f.write(await template_file.read())
        
        with open(content_path, "wb") as f:
            f.write(await content_file.read())
        
        # 构建指令
        instruction = f"""
任务：根据模板生成文档

模板文件：{template_path}
内容文件：{content_path}
输出格式：{output_format}

步骤：
1. 分析模板文件的结构（标题层级、格式、样式等）
2. 提取内容文件中的文本和图片
3. 将内容按照模板的结构和样式进行排版
4. 生成 {output_format} 格式的文档
5. 保持图片在文档中的位置和大小

{f"额外要求：{additional_instruction}" if additional_instruction else ""}
"""
        
        # 调用 Agent 处理
        result = agent.process_with_template(
            str(template_path), 
            str(content_path), 
            output_format,
            instruction
        )
        
        return {
            "success": True,
            "message": "模板处理完成",
            "result": result
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/api/status")
async def get_status():
    """检查 Agent 状态"""
    return {
        "initialized": agent is not None,
        "ready": agent is not None
    }

@app.get("/api/preview/{file_type}/{filename}")
async def preview_file(file_type: str, filename: str):
    """
    预览文件
    返回文件内容用于前端预览
    """
    try:
        upload_dir = Path("uploads")
        file_path = upload_dir / filename
        
        if not file_path.exists():
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "文件不存在"}
            )
        
        # 根据文件类型返回不同内容
        if file_type == "text" or file_type == "markdown":
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"success": True, "content": content, "type": file_type}
        
        elif file_type == "docx":
            # 简单提取 Word 文档文本
            from docx import Document
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return {
                "success": True,
                "content": "\n\n".join(paragraphs),
                "type": "docx"
            }
        
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "不支持的预览类型"}
            )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

if __name__ == "__main__":
    # 在 8765 端口启动（避免与常见端口冲突）
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8765,
        log_level="info"
    )
