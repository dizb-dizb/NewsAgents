import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
import requests
# 复用你的 LLM 配置
from config.load_key import load_api_key
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import SequentialChain
from utils.llm_utils import get_qwen_llm
# 加载环境变量
load_dotenv()
# 搜索引擎 API 配置（这里用 SerpAPI 示例，也可替换为百度/必应等）
SERP_API_KEY = os.getenv("SERP_API_KEY") or load_api_key("SERP_API_KEY")
SEARCH_ENGINE_URL = "https://serpapi.com/search"  # SerpAPI 接口（免费版足够测试）

# ======================== 1. 复用你的 LLM 函数 ========================
def get_qwen_llm(model_name: str = "qwen-turbo") -> ChatOpenAI:
    api_key = load_api_key("DASHSCOPE_API_KEY")
    api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    print(f"正在初始化 Qwen LLM (实体处理模式)...")
    print(f"  - API Base: {api_base}")
    print(f"  - Model Name: {model_name}")
    
    return ChatOpenAI(
        model_name=model_name,
        openai_api_key=api_key,
        openai_api_base=api_base,
        temperature=0.1,  # 低温度保证实体提取准确性
    )



# ======================== 3. 核心 Chain：新闻内容 → 实体提取 → 知识卡片 ========================
class EntityQueryAgent:
    """
    实体查询 Agent：
    输入：新闻原文 / 新闻总结 → 输出：核心实体知识卡片集合
    流程：新闻内容 → LLM 提取核心实体 → 批量搜索实体信息 → 整理结构化知识卡片
    """
    
    def __init__(self):
        self.llm = get_qwen_llm()
        self._build_chains()  # 初始化所有子 Chain
    
    def _build_chains(self):
        """构建两个核心子 Chain：实体提取 Chain + 知识卡片生成 Chain"""
        # 子 Chain 1：新闻内容 → 提取核心实体（JSON 格式输出）
        entity_extract_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
                你是专业的实体提取专家，从新闻内容中提取 3-5 个核心实体。
                实体定义：
                - 必须是新闻的核心要素（公司、人物、政策、事件、机构、技术等）；
                - 排除通用词汇（如“经济”“市场”“消费者”等无特定指向的词）；
                - 实体名称需准确完整（如“国家统计局”而非“统计局”）。
                
                输出格式：严格返回 JSON 数组，仅包含实体名称，无其他文本。
                示例：["国家统计局", "CPI", "新能源汽车", "社会消费品零售总额"]
                """,
            ),
            ("human", "新闻内容：\n{news_content}"),
        ])
        
        self.entity_extract_chain = entity_extract_prompt | self.llm | JsonOutputParser()
        
        # 子 Chain 2：单个实体 → 生成知识卡片（结构化文本）
        self.entity_search_chain = RunnablePassthrough.assign(
            knowledge_card=lambda x: search_entity_info(x["entity"])
        )
    
    def run(self, news_content: str) -> str:
        """
        核心方法：输入新闻内容（原文/总结），返回核心实体知识卡片集合
        :param news_content: 新闻原文或结构化总结
        :return: 整理后的实体知识卡片（字符串）
        """
        if not news_content or len(news_content) < 50:
            return "错误：输入的新闻内容为空或过短"
        
        print(f"\n===== EntityQuery Agent 开始处理 =====")
        print(f"新闻内容长度：{len(news_content)} 字符")
        
        try:
            # 步骤1：提取核心实体
            print("\nStep 1: 提取核心实体...")
            core_entities = self.entity_extract_chain.invoke({"news_content": news_content})
            if not core_entities or not isinstance(core_entities, list):
                return "未从新闻中提取到有效核心实体"
            
            print(f"提取到 {len(core_entities)} 个核心实体：{core_entities}")
            
            # 步骤2：批量搜索实体信息，生成知识卡片
            print("\nStep 2: 搜索实体信息，生成知识卡片...")
            knowledge_cards = []
            for idx, entity in enumerate(core_entities, 1):
                print(f"[{idx}/{len(core_entities)}] 处理实体：{entity}")
                result = self.entity_search_chain.invoke({"entity": entity})
                knowledge_cards.append(f"===== 实体 {idx} =====\n{result['knowledge_card']}")
            
            # 步骤3：整理最终输出
            final_output = "【新闻核心实体知识卡片集合】\n\n" + "\n\n".join(knowledge_cards)
            print(f"\n===== EntityQuery Agent 处理完成 =====")
            return final_output
        
        except Exception as e:
            error_msg = f"EntityQuery Agent 处理异常：{str(e)}"
            print(error_msg)
            return error_msg
    
    def batch_run(self, news_content_list: List[str]) -> List[Dict[str, str]]:
        """
        批量处理：输入新闻内容列表，返回每个新闻的实体知识卡片
        :param news_content_list: 新闻内容列表
        :return: 包含新闻索引、内容、知识卡片的字典列表
        """
        if not news_content_list:
            print("警告：输入的新闻列表为空")
            return []
        
        results = []
        print(f"\n===== 开始批量处理 {len(news_content_list)} 条新闻 =====")
        for idx, content in enumerate(news_content_list, 1):
            print(f"\n【批量处理 {idx}/{len(news_content_list)}】")
            cards = self.run(content)
            results.append({
                "news_index": idx,
                "news_content": content[:100] + "..." if len(content) > 100 else content,
                "entity_knowledge_cards": cards
            })
        
        print(f"\n===== 批量处理完成 =====")
        return results