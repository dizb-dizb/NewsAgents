from typing import List, Dict, Optional
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import SequentialChain
from utils.llm_utils import get_qwen_llm
from tools.NewsTool import entity_search_tool
# ======================== 4. 核心 Chain：新闻内容 → 实体提取 → 知识卡片 ========================
class EntityQueryAgent:
    """
    实体查询 Agent：
    输入：新闻原文 / 新闻总结 → 输出：核心实体知识卡片集合
    流程：新闻内容 → LLM 提取核心实体 → 调用 LangChain Tool 搜索 → 整理知识卡片
    """
    
    def __init__(self):
        self.llm = get_qwen_llm()
        self.tool = entity_search_tool  # 注入 LangChain Tool
        self._build_chains()
    
    def _build_chains(self):
        """构建子 Chain：实体提取 + Tool 调用"""
        # 子 Chain 1：新闻内容 → 提取核心实体（JSON 输出）
        entity_extract_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
                你是专业的实体提取专家，从新闻内容中提取 3-5 个核心实体。
                实体定义：
                - 必须是新闻核心要素（公司、人物、政策、事件、机构、技术等）；
                - 排除通用词汇（如“经济”“市场”）；
                - 名称准确完整（如“国家统计局”而非“统计局”）。
                
                输出格式：严格返回 JSON 数组，仅含实体名称，无其他文本。
                示例：["国家统计局", "CPI", "新能源汽车"]
                """,
            ),
            ("human", "新闻内容：\n{news_content}"),
        ])
        self.entity_extract_chain = entity_extract_prompt | self.llm | JsonOutputParser()
        
        # 子 Chain 2：实体名称 → 调用 LangChain Tool 获取知识卡片
        # 用 RunnablePassthrough 传递参数，调用 Tool 的 run 方法
        self.entity_tool_chain = RunnablePassthrough.assign(
            knowledge_card=lambda x: self.tool.run(x["entity"])  # 调用 Tool
        )
    
    def run(self, news_content: str) -> str:
        if not news_content or len(news_content) < 50:
            return "错误：新闻内容为空或过短"
        
        print(f"\n===== EntityQuery Agent 开始处理 =====")
        print(f"新闻内容长度：{len(news_content)} 字符")
        
        try:
            # 步骤1：提取核心实体
            print("\nStep 1: 提取核心实体...")
            core_entities = self.entity_extract_chain.invoke({"news_content": news_content})
            if not core_entities or not isinstance(core_entities, list):
                return "未提取到有效核心实体"
            print(f"提取到 {len(core_entities)} 个核心实体：{core_entities}")
            
            # 步骤2：调用 LangChain Tool 批量生成知识卡片
            print("\nStep 2: 调用实体查询 Tool，生成知识卡片...")
            knowledge_cards = []
            for idx, entity in enumerate(core_entities, 1):
                print(f"[{idx}/{len(core_entities)}] 调用 Tool 查询实体：{entity}")
                result = self.entity_tool_chain.invoke({"entity": entity})
                knowledge_cards.append(f"===== 实体 {idx} =====\n{result['knowledge_card']}")
            
            # 步骤3：整理输出
            final_output = "【新闻核心实体知识卡片集合】\n\n" + "\n\n".join(knowledge_cards)
            print(f"\n===== EntityQuery Agent 处理完成 =====")
            return final_output
        
        except Exception as e:
            error_msg = f"EntityQuery Agent 处理异常：{str(e)}"
            print(error_msg)
            return error_msg
    
    def batch_run(self, news_content_list: List[str]) -> List[Dict[str, str]]:
        if not news_content_list:
            print("警告：新闻列表为空")
            return []
        
        results = []
        print(f"\n===== 批量处理 {len(news_content_list)} 条新闻 =====")
        for idx, content in enumerate(news_content_list, 1):
            print(f"\n【批量处理 {idx}/{len(news_content_list)}】")
            cards = self.run(content)
            results.append({
                "news_index": idx,
                "news_content": content[:100] + "..." if len(content) > 100 else content,
                "entity_knowledge_cards": cards
            })
        return results