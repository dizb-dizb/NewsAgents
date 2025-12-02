import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm_utils import get_qwen_llm
# 加载环境变量
load_dotenv()
class NewsFilterAgent:
    """
    一个由 LLM 驱动的新闻过滤 Agent。
    它接收一个新闻元数据列表，并返回一个经过 LLM 判断为“真实新闻”的列表。
    """
    
    def __init__(self):
        """
        初始化 Agent。
        :param model_name: 要使用的 OpenAI 模型名称。
        """
        self.llm = get_qwen_llm()
        
        # 1. 定义 Prompt
        # 清晰地告诉 LLM 任务、判断标准和期望的输出格式。
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
                你是一位专业的新闻内容审核员。你的任务是从提供的新闻元数据列表中，筛选出那些属于“真正的新闻报道”的条目。
                
                判断标准：
                - **是新闻**: 对最近发生的事件、趋势、研究成果或重要信息进行客观报道的内容。例如，科技公司发布新产品、政府出台新政策、学术机构发表研究论文等。
                - **不是新闻**: 
                    - 广告、赞助内容、产品促销或评测。
                    - 个人博客、论坛帖子、社交媒体分享。
                    - 公司发布的公关稿（Press Release）。
                    - 教程、指南、How-to 文章。
                    - 娱乐八卦、未经证实的谣言。
                
                你的输出格式必须是一个 JSON 数组，其中包含你判断为“是新闻”的条目的 **原始索引 (index)**。
                请只返回 JSON 数组，不要添加任何其他解释或文本。
                例如，如果第 0 条和第 2 条是新闻，你的输出应该是：[0, 2]
                """,
            ),
            ("human", "请审核以下新闻元数据列表：\n{news_metadata_json}"),
        ])
        
        # 2. 定义输出解析器
        self.output_parser = JsonOutputParser()
        
        # 3. 创建链 (Chain)
        self.chain = self.prompt | self.llm | self.output_parser

    def run(self, raw_news_metadata_list: List[Dict]) -> List[Dict]:
        """
        执行过滤任务。
        :param raw_news_metadata_list: 原始的新闻元数据列表。
        :return: 经过 LLM 过滤后的新闻元数据列表。
        """
        if not raw_news_metadata_list:
            print("警告：输入的新闻元数据列表为空。")
            return []

        print(f"LLM 过滤 Agent 开始处理 {len(raw_news_metadata_list)} 条新闻...")
        
        # 将原始数据转换为 JSON 字符串，作为 Prompt 的输入
        news_metadata_json = json.dumps(raw_news_metadata_list, indent=2, ensure_ascii=False)
        
        try:
            # 执行链
            # LLM 将返回一个包含符合条件的新闻条目的索引列表，例如 [0, 2, 3]
            relevant_indices = self.chain.invoke({"news_metadata_json": news_metadata_json})
            
            print(f"LLM 判断出 {len(relevant_indices)} 条有效新闻。")

            # 根据索引从原始列表中筛选出有效新闻
            cleaned_news_list = [raw_news_metadata_list[i] for i in relevant_indices]
            
            return cleaned_news_list

        except Exception as e:
            print(f"错误：在调用 LLM 进行过滤时发生异常: {e}")
            # 在发生错误时，可以选择返回原始列表或空列表，这里选择返回原始列表作为降级策略
            return raw_news_metadata_list