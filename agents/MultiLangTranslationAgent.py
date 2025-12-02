# MultiLangTranslationAgent_Qwen.py
from langchain_openai import ChatOpenAI
import os

class MultiLangTranslationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key="sk-28767c54e7bd45f8a9e60de7f154e588",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 北京地区
            model="qwen-plus",
            temperature=0  # 翻译任务建议确定性输出
        )
    def translate_text(self, text, target_language="zh"):
        prompt = [
            {"role": "system", "content": "You are a professional translator."},
            {"role": "user", "content": f"请将以下文本翻译成{target_language}：\n{text}"}
        ]
        response = self.llm.invoke(prompt)
        response_dict = response.model_dump()  # 转为 dict
        return response_dict["content"]


    def translate_news(self, article):
        """
        article: dict, 例如 {"title": "...", "content": "..."}
        返回翻译后的文章字典
        """
        translated_article = {}
        # 翻译标题
        translated_article["title_zh"] = self.translate_text(article["title"], target_language="zh")
        # 翻译内容
        translated_article["content_zh"] = self.translate_text(article["content"], target_language="zh")
        return translated_article

