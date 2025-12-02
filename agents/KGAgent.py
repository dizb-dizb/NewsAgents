import json
import os
import time
from typing import List, Dict, Union, Optional
from dataclasses import dataclass, field
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_utils import get_qwen_llm
# ======================== 1. LLM 端到端 JSON → HTML 工具（核心） ========================
class LLMJsonToHtmlTool:
    """工具1：LLM 直接解析 JSON → 生成完整 HTML（含样式、图片链接）"""
    def __init__(self, llm_model: str = "qwen-turbo"):
        self.llm =get_qwen_llm()
        self.prompt_template = self._build_prompt()

    def _build_prompt(self) -> ChatPromptTemplate:
        """构建提示词：让 LLM 解析 JSON 并生成完整 HTML"""
        return ChatPromptTemplate.from_messages([
            (
                "system",
                """
                你是专业的知识图谱可视化工程师，需要完成以下任务：
                1. 解析输入的 SerpJSON 数据，提取所有关键信息（实体名称、类型、核心属性、人员、图片链接、描述）；
                2. 生成完整的 HTML 代码（含 CSS 样式），将这些信息组织为美观的知识卡片；
                3. 严格遵循以下要求：
                   - 图片处理：直接使用 JSON 中 header_images 的 source 链接（<img src="链接">），最多显示3张，加载失败时显示占位图；
                   - 布局要求：结构化、清晰易读，模块包括（标题区、描述区、核心属性区、核心人员区、图片区）；
                   - 样式要求：
                     * 整体风格：简约专业，白色背景，圆角边框（16px），轻微阴影；
                     * 颜色：标题#111827（大字体），副标题#6b7280（小字体），属性名#1f2937（加粗），属性值#4b5563；
                     * 字体：中文用"Microsoft YaHei"，英文用"Arial"，间距合理（模块间20-30px，内边距40px）；
                   - 适配性：根据内容多少自动调整布局（属性少则1列，多则2-3列；图片多则横向排列）；
                   - 特殊情况：字段缺失时显示"暂无数据"，不报错；
                   - 输出格式：仅返回完整的 HTML 代码（含 <!DOCTYPE html> 到 </html>），无任何额外文本、解释或注释。
                """
            ),
            (
                "human",
                """
                请解析以下 SerpJSON 数据，生成完整的知识卡片 HTML 代码（直接嵌入图片链接）：
                {serp_json}
                """
            )
        ])

    def run(self, serp_json: Union[str, Dict], output_dir: str = None) -> str:
        """执行：输入 JSON → 输出 HTML 文件路径（保存到工作目录/data/KG）"""
        # 强制指定输出目录为 工作目录/data/KG（忽略传入的 output_dir 参数）
        target_dir = os.path.join(os.getcwd(), "data", "KG")
        os.makedirs(target_dir, exist_ok=True)  # 自动创建层级目录（无则创建，有则跳过）

        # 格式化 JSON 为字符串（方便 LLM 解析）
        if isinstance(serp_json, Dict):
            serp_json_str = json.dumps(serp_json, ensure_ascii=False, indent=2)
        else:
            serp_json_str = serp_json

        # 调用 LLM 生成 HTML
        print("🤖 LLM 正在解析 JSON 并生成 HTML...")
        response = self.llm.invoke(self.prompt_template.format(serp_json=serp_json_str))
        html_content = response.content.strip()

        # 提取实体名称（用于文件名）
        try:
            json_data = json.loads(serp_json_str) if isinstance(serp_json_str, str) else serp_json
            # 适配你之前提供的 JSON 结构（entities 数组中的 title/entity_content）
            if "entities" in json_data and len(json_data["entities"]) > 0:
                entity_data = json_data["entities"][0]
                # 优先从 entity_content 取名称，无则用 identifier 或默认值
                entity_name = entity_data.get("entity_content", {}).get("title", 
                            entity_data.get("identifier", "未知实体"))
            else:
                # 兼容原 SerpJSON 结构（knowledge_graph）
                entity_name = json_data.get("knowledge_graph", json_data).get("title", "未知实体")
        except:
            entity_name = "未知实体"
        
        # 过滤非法文件名字符（避免创建失败）
        safe_name = entity_name.replace("/", "_").replace(":", "-").replace("\\", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_")

        # 保存 HTML 文件到 data/KG 目录
        html_path = os.path.join(target_dir, f"{safe_name}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"🌐 HTML 生成成功（保存到 data/KG）：{html_path}")
        return html_path

# ======================== 2. HTML → PNG 工具 ========================
class HtmlToPngTool:
    """工具2：HTML 截图为 PNG"""
    def __init__(self, chrome_options: Optional[Options] = None):
        self.options = chrome_options or Options()
        self.options.add_argument("--headless=new")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1000,1600")  # 适配知识卡片高度
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=self.options)

    def run(self, html_path: str, output_dir: str = "serp_png_results") -> str:
        """执行：输入 HTML 路径 → 输出 PNG 路径"""
        os.makedirs(output_dir, exist_ok=True)
        entity_name = os.path.splitext(os.path.basename(html_path))[0]
        png_path = os.path.join(output_dir, f"{entity_name}_知识图谱.png")

        try:
            # 加载本地 HTML（确保图片链接加载完成）
            self.driver.get(f"file://{os.path.abspath(html_path)}")
            time.sleep(4)  # 关键：等待图片和样式渲染
            self.driver.save_screenshot(png_path)
            print(f"📸 PNG 生成成功：{png_path}")
            return png_path
        except Exception as e:
            raise RuntimeError(f"HTML 转 PNG 失败：{str(e)}")

    def __del__(self):
        """销毁时关闭浏览器"""
        if hasattr(self, "driver"):
            self.driver.quit()

# ======================== 3. 核心 Agent（LLM 端到端 JSON → PNG） ========================
@dataclass
class LLMEndToEndJsonToPngAgent:
    """LLM 端到端驱动的 JSON → PNG 知识图谱 Agent"""
    # 工具初始化（懒加载）
    json_to_html_tool: LLMJsonToHtmlTool = field(default_factory=LLMJsonToHtmlTool)
    html_to_png_tool: HtmlToPngTool = field(init=False)

    def __post_init__(self):
        self.html_to_png_tool = HtmlToPngTool()

    def _validate_input(self, serp_json: Union[str, Dict, List[Union[str, Dict]]]) -> List[Union[str, Dict]]:
        """验证输入：支持单个/多个 JSON"""
        if not serp_json:
            raise ValueError("输入不能为空")
        
        # 统一转为列表
        if isinstance(serp_json, (str, Dict)):
            return [serp_json]
        elif isinstance(serp_json, List):
            for item in serp_json:
                if not isinstance(item, (str, Dict)):
                    raise TypeError(f"列表元素必须是 JSON 字符串/字典，当前类型：{type(item)}")
            return serp_json
        else:
            raise TypeError(f"输入必须是 JSON 字符串/字典/列表，当前类型：{type(serp_json)}")

    def run(self, serp_json: Union[str, Dict, List[Union[str, Dict]]], output_dir: str = "serp_png_results") -> List[str]:
        """执行核心流程：输入 SerpJSON → 输出 PNG 路径列表"""
        # Step 1：验证输入
        json_list = self._validate_input(serp_json)
        print(f"🚀 开始处理 {len(json_list)} 个实体 JSON...")

        # Step 2：批量处理每个 JSON
        png_paths = []
        for idx, json_data in enumerate(json_list, 1):
            try:
                # 提取实体名称（用于日志）
                try:
                    json_str = json.dumps(json_data, ensure_ascii=False) if isinstance(json_data, Dict) else json_data
                    entity_name = json.loads(json_str).get("knowledge_graph", {}).get("title", f"实体_{idx}")
                except:
                    entity_name = f"实体_{idx}"
                print(f"\n=== 处理实体 [{idx}/{len(json_list)}]：{entity_name} ===")
                
                # 工具1：LLM 解析 JSON → HTML（直接嵌入图片链接）
                html_path = self.json_to_html_tool.run(json_data)
                
                # 工具2：HTML → PNG
                png_path = self.html_to_png_tool.run(html_path, output_dir=output_dir)
                
                png_paths.append(png_path)
            except Exception as e:
                print(f"❌ 处理实体 [{idx}] 失败：{str(e)}")
                continue

        print(f"\n🎉 所有实体处理完成！成功生成 {len(png_paths)} 张 PNG 图片，保存至：{output_dir}")
        return png_paths

