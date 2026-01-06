"""
文档操作工具集
这些函数会被 LangChain Agent 调用
"""
from langchain.tools import tool
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pathlib import Path
from typing import Optional, List, Dict
import re
import json
from PIL import Image
import base64
from io import BytesIO

@tool
def read_document(file_path: str) -> str:
    """
    读取 Word 文档内容
    
    Args:
        file_path: Word 文档的完整路径
        
    Returns:
        文档的文本内容
    """
    try:
        doc = Document(file_path)
        
        # 提取所有段落
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        
        # 提取表格
        tables_content = []
        for table in doc.tables:
            table_text = "\n".join([
                "\t".join([cell.text for cell in row.cells])
                for row in table.rows
            ])
            tables_content.append(f"[表格]\n{table_text}")
        
        content = "\n\n".join(paragraphs + tables_content)
        
        return f"成功读取文档，内容如下：\n\n{content[:2000]}..."  # 限制长度避免 token 溢出
    
    except Exception as e:
        return f"读取文档失败：{str(e)}"

@tool
def write_document(file_path: str, content: str, title: Optional[str] = None) -> str:
    """
    创建新的 Word 文档
    
    Args:
        file_path: 保存路径
        content: 文档内容（支持段落分隔符 \\n\\n）
        title: 可选的文档标题
        
    Returns:
        操作结果
    """
    try:
        doc = Document()
        
        # 添加标题
        if title:
            doc.add_heading(title, level=0)
        
        # 添加内容（按段落分割）
        paragraphs = content.split("\n\n")
        for para in paragraphs:
            if para.strip():
                doc.add_paragraph(para.strip())
        
        # 保存
        output_path = Path(file_path).with_suffix('.docx')
        doc.save(str(output_path))
        
        return f"成功创建文档：{output_path}"
    
    except Exception as e:
        return f"创建文档失败：{str(e)}"

@tool
def modify_document(
    file_path: str,
    operation: str,
    target: Optional[str] = None,
    replacement: Optional[str] = None
) -> str:
    """
    修改现有 Word 文档
    
    Args:
        file_path: 文档路径
        operation: 操作类型（replace_text, add_paragraph, change_style）
        target: 目标内容（如要替换的文本）
        replacement: 替换内容
        
    Returns:
        操作结果
    """
    try:
        doc = Document(file_path)
        
        if operation == "replace_text" and target and replacement:
            # 替换文本
            count = 0
            for para in doc.paragraphs:
                if target in para.text:
                    para.text = para.text.replace(target, replacement)
                    count += 1
            
            # 保存修改
            output_path = Path(file_path).with_stem(
                Path(file_path).stem + "_modified"
            )
            doc.save(str(output_path))
            
            return f"成功替换 {count} 处文本，保存至：{output_path}"
        
        elif operation == "add_paragraph":
            # 添加新段落
            doc.add_paragraph(replacement or "")
            output_path = Path(file_path).with_stem(
                Path(file_path).stem + "_modified"
            )
            doc.save(str(output_path))
            return f"成功添加段落，保存至：{output_path}"
        
        else:
            return f"不支持的操作：{operation}"
    
    except Exception as e:
        return f"修改文档失败：{str(e)}"

# ============ Markdown 处理工具 ============

@tool
def read_markdown(file_path: str) -> str:
    """
    读取 Markdown 文件内容和结构
    
    Args:
        file_path: Markdown 文件路径
        
    Returns:
        文档内容和结构信息
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题结构
        headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        structure = [{"level": len(h[0]), "text": h[1]} for h in headers]
        
        # 提取图片引用
        images = re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', content)
        
        result = {
            "content": content[:2000],  # 限制长度
            "structure": structure,
            "images": [{"alt": img[0], "path": img[1]} for img in images],
            "lines": len(content.split('\n'))
        }
        
        return f"成功读取 Markdown 文件：\n{json.dumps(result, ensure_ascii=False, indent=2)}"
    
    except Exception as e:
        return f"读取 Markdown 失败：{str(e)}"

@tool
def write_markdown(
    file_path: str,
    content: str,
    title: Optional[str] = None,
    metadata: Optional[str] = None
) -> str:
    """
    创建 Markdown 文件
    
    Args:
        file_path: 保存路径
        content: Markdown 内容
        title: 文档标题（会作为一级标题）
        metadata: YAML 格式的元数据（可选）
        
    Returns:
        操作结果
    """
    try:
        md_content = ""
        
        # 添加元数据
        if metadata:
            md_content += f"---\n{metadata}\n---\n\n"
        
        # 添加标题
        if title:
            md_content += f"# {title}\n\n"
        
        # 添加内容
        md_content += content
        
        # 保存文件
        output_path = Path(file_path).with_suffix('.md')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return f"成功创建 Markdown 文件：{output_path}"
    
    except Exception as e:
        return f"创建 Markdown 失败：{str(e)}"

# ============ LaTeX 处理工具 ============

@tool
def read_latex(file_path: str) -> str:
    """
    读取 LaTeX 文件内容和结构
    
    Args:
        file_path: LaTeX 文件路径
        
    Returns:
        文档内容和结构信息
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取文档类
        doc_class = re.search(r'\\documentclass\[?([^\]]*)\]?\{([^\}]+)\}', content)
        
        # 提取章节结构
        sections = re.findall(
            r'\\(chapter|section|subsection|subsubsection)\{([^\}]+)\}',
            content
        )
        
        # 提取图片
        figures = re.findall(r'\\includegraphics\[?([^\]]*)\]?\{([^\}]+)\}', content)
        
        result = {
            "document_class": doc_class.group(2) if doc_class else "unknown",
            "sections": [{"type": s[0], "title": s[1]} for s in sections],
            "figures": [{"options": f[0], "path": f[1]} for f in figures],
            "content_preview": content[:1000]
        }
        
        return f"成功读取 LaTeX 文件：\n{json.dumps(result, ensure_ascii=False, indent=2)}"
    
    except Exception as e:
        return f"读取 LaTeX 失败：{str(e)}"

@tool
def write_latex(
    file_path: str,
    content: str,
    document_class: str = "article",
    packages: Optional[List[str]] = None,
    title: Optional[str] = None,
    author: Optional[str] = None
) -> str:
    """
    创建 LaTeX 文件
    
    Args:
        file_path: 保存路径
        content: LaTeX 内容（document 环境内的内容）
        document_class: 文档类（article, report, book 等）
        packages: 需要引入的包列表
        title: 文档标题
        author: 作者
        
    Returns:
        操作结果
    """
    try:
        # 构建 LaTeX 文档
        latex_content = f"\\documentclass{{{document_class}}}\n\n"
        
        # 添加常用包
        default_packages = ['graphicx', 'amsmath', 'geometry', 'xeCJK']
        all_packages = default_packages + (packages or [])
        
        for pkg in all_packages:
            latex_content += f"\\usepackage{{{pkg}}}\n"
        
        latex_content += "\n"
        
        # 添加标题和作者
        if title:
            latex_content += f"\\title{{{title}}}\n"
        if author:
            latex_content += f"\\author{{{author}}}\n"
        
        latex_content += f"\\date{{\\today}}\n\n"
        latex_content += "\\begin{document}\n\n"
        
        if title:
            latex_content += "\\maketitle\n\n"
        
        # 添加正文内容
        latex_content += content
        
        latex_content += "\n\\end{document}"
        
        # 保存文件
        output_path = Path(file_path).with_suffix('.tex')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        return f"成功创建 LaTeX 文件：{output_path}"
    
    except Exception as e:
        return f"创建 LaTeX 失败：{str(e)}"

# ============ 图片处理工具 ============

@tool
def extract_images_from_document(file_path: str, output_dir: str = "extracted_images") -> str:
    """
    从 Word 文档中提取所有图片
    
    Args:
        file_path: Word 文档路径
        output_dir: 图片保存目录
        
    Returns:
        提取的图片信息
    """
    try:
        doc = Document(file_path)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        images_info = []
        
        # 遍历文档中的所有关系（包含图片）
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                # 提取图片
                image_data = rel.target_part.blob
                
                # 确定文件扩展名
                ext = rel.target_ref.split('.')[-1]
                image_name = f"image_{len(images_info) + 1}.{ext}"
                image_path = output_path / image_name
                
                # 保存图片
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                # 获取图片尺寸
                img = Image.open(BytesIO(image_data))
                
                images_info.append({
                    "name": image_name,
                    "path": str(image_path),
                    "size": img.size,
                    "format": img.format
                })
        
        return f"成功提取 {len(images_info)} 张图片：\n{json.dumps(images_info, ensure_ascii=False, indent=2)}"
    
    except Exception as e:
        return f"提取图片失败：{str(e)}"

# ============ 文档结构分析工具 ============

@tool
def extract_document_structure(file_path: str) -> str:
    """
    提取文档的结构信息（标题、段落、样式等）
    
    Args:
        file_path: 文档路径（支持 .docx, .md, .tex）
        
    Returns:
        文档结构的 JSON 表示
    """
    try:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.docx':
            doc = Document(file_path)
            structure = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    # 分析样式
                    style_info = {
                        "text": para.text[:100],
                        "style": para.style.name,
                        "is_heading": para.style.name.startswith('Heading'),
                        "alignment": str(para.alignment),
                        "font_size": para.runs[0].font.size.pt if para.runs and para.runs[0].font.size else None,
                        "bold": para.runs[0].bold if para.runs else False,
                        "italic": para.runs[0].italic if para.runs else False
                    }
                    structure.append(style_info)
            
            return f"Word 文档结构（共 {len(structure)} 个元素）：\n{json.dumps(structure[:10], ensure_ascii=False, indent=2)}"
        
        elif file_ext == '.md':
            return read_markdown(file_path)
        
        elif file_ext == '.tex':
            return read_latex(file_path)
        
        else:
            return f"不支持的文件格式：{file_ext}"
    
    except Exception as e:
        return f"提取结构失败：{str(e)}"

# ============ 模板应用工具 ============

@tool
def apply_template_structure(
    template_structure: str,
    content_text: str,
    output_path: str,
    output_format: str = "docx"
) -> str:
    """
    将内容应用到模板结构中
    
    Args:
        template_structure: 模板的结构信息（JSON 字符串）
        content_text: 要填充的内容
        output_path: 输出文件路径
        output_format: 输出格式（docx/md/tex）
        
    Returns:
        操作结果
    """
    try:
        structure = json.loads(template_structure)
        
        if output_format == "docx":
            doc = Document()
            
            # 按照模板结构创建文档
            content_paragraphs = content_text.split('\n\n')
            
            for i, item in enumerate(structure):
                if i < len(content_paragraphs):
                    para = doc.add_paragraph(content_paragraphs[i])
                    
                    # 应用样式
                    if item.get('is_heading'):
                        para.style = item.get('style', 'Normal')
                    
                    if item.get('bold') and para.runs:
                        para.runs[0].bold = True
                    
                    if item.get('italic') and para.runs:
                        para.runs[0].italic = True
            
            doc.save(output_path)
            return f"成功应用模板并保存到：{output_path}"
        
        elif output_format == "md":
            # 构建 Markdown
            md_lines = []
            content_paragraphs = content_text.split('\n\n')
            
            for i, item in enumerate(structure):
                if i < len(content_paragraphs):
                    text = content_paragraphs[i]
                    
                    # 根据原结构添加格式
                    if item.get('level'):
                        prefix = '#' * item['level']
                        md_lines.append(f"{prefix} {text}")
                    else:
                        md_lines.append(text)
                    
                    md_lines.append("")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_lines))
            
            return f"成功生成 Markdown：{output_path}"
        
        else:
            return f"暂不支持输出格式：{output_format}"
    
    except Exception as e:
        return f"应用模板失败：{str(e)}"

# ============ 格式转换工具 ============

@tool
def convert_format(
    input_path: str,
    output_format: str,
    preserve_images: bool = True
) -> str:
    """
    转换文档格式
    
    Args:
        input_path: 输入文件路径
        output_format: 目标格式（word/markdown/latex）
        preserve_images: 是否保留图片
        
    Returns:
        转换结果和输出文件路径
    """
    try:
        input_ext = Path(input_path).suffix.lower()
        output_path = Path(input_path).with_suffix(f'.{output_format}')
        
        # 读取原文档
        if input_ext == '.docx':
            doc = Document(input_path)
            text_content = '\n\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
        elif input_ext == '.md':
            with open(input_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        else:
            return f"暂不支持从 {input_ext} 格式转换"
        
        # 转换为目标格式
        if output_format == 'markdown' or output_format == 'md':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            return f"成功转换为 Markdown：{output_path}"
        
        elif output_format == 'word' or output_format == 'docx':
            new_doc = Document()
            for para in text_content.split('\n\n'):
                if para.strip():
                    new_doc.add_paragraph(para.strip())
            new_doc.save(str(output_path))
            return f"成功转换为 Word：{output_path}"
        
        else:
            return f"不支持的输出格式：{output_format}"
    
    except Exception as e:
        return f"格式转换失败：{str(e)}"

def get_document_tools():
    """返回所有工具的列表"""
    return [
        read_document,
        write_document,
        modify_document,
        read_markdown,
        write_markdown,
        read_latex,
        write_latex,
        extract_images_from_document,
        extract_document_structure,
        apply_template_structure,
        convert_format
    ]
