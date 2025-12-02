from typing import List, Dict
# 复用你已有的 LLM 获取函数（无需重新定义）
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from tools.NewsTool import news_extract_tool
from utils.llm_utils import get_qwen_llm
# ======================== 3. 核心：新闻总结 Chain（纯串联，无多余代码）========================
class NewsSummaryagent:
    """
    输入：新闻 URL → 输出：结构化总结（核心要点+概括）
    流程：URL → 工具提取原文 → LLM 总结 → 直接输出结果
    """
    
    def __init__(self):
        # 复用你的 LLM 实例（不重复定义）
        self.llm = get_qwen_llm()
        
        # 总结 Prompt（保持你想要的输出格式）
        self.summary_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
                你是专业新闻总结助手，基于原文按以下要求生成总结：
                1. 核心要点：提炼 3-5 点关键信息，必须包含事件主体、时间、核心动作、结果/影响；
                2. 核心概括：100-150 字简洁总结全文核心，不添加额外评论或扩展解读；
                3. 输出格式严格遵循（不要添加任何多余文本）：
                【核心要点】
                1. XXXX
                2. XXXX
                ...
                【核心概括】
                XXXX
                4. 仅基于提供的原文内容，不编造任何未提及的信息。
                """,
            ),
            ("human", "新闻原文：\n{news_content}"),
        ])
        
        # 构建 Chain：URL → 提取原文 → 总结（纯串联，无 Agent）
        self.chain = self._build_chain()

    def _build_chain(self):
        """构建线性 Chain：URL → 原文 → 总结"""
        # 第一步：接收 URL，调用工具提取原文
        extract_step = RunnablePassthrough.assign(
            news_content=lambda x: news_extract_tool.run(x["url"])
        )
        
        # 第二步：用 LLM 处理原文，生成总结
        summary_step = self.summary_prompt | self.llm | StrOutputParser()
        
        # 串联两步：输入 URL → 输出总结
        return extract_step | (lambda x: x["news_content"]) | summary_step

    def run(self, url: str) -> str:
        """核心方法：输入单个新闻 URL，返回结构化总结"""
        if not url:
            return "错误：新闻 URL 不能为空"
        
        print(f"\n===== 开始处理新闻 =====")
        print(f"URL：{url}")
        
        try:
            result = self.chain.invoke({"url": url})
            
            # 处理工具返回的错误信息
            if "错误" in result[:10]:
                return f"新闻处理失败：{result}"
            
            print(f"===== 总结完成 =====")
            return result
        
        except Exception as e:
            error_msg = f"新闻总结异常：{str(e)}"
            print(error_msg)
            return error_msg

    def batch_run(self, url_list: List[str]) -> List[Dict[str, str]]:
        """批量处理：输入 URL 列表，返回包含 URL 和总结的字典列表"""
        if not url_list:
            print("警告：输入的 URL 列表为空")
            return []
        
        results = []
        print(f"\n===== 开始批量处理 {len(url_list)} 条新闻 =====")
        for idx, url in enumerate(url_list, 1):
            print(f"\n【{idx}/{len(url_list)}】处理 URL：{url}")
            summary = self.run(url)
            results.append({
                "url": url,
                "summary": summary
            })
        
        print(f"\n===== 批量处理完成 =====")
        return results