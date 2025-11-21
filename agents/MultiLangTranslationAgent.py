import os
from openai import OpenAI

class MultiLangTranslationAgent:
    """
    多语言翻译 Agent，将任意语言新闻翻译成中文
    使用 OpenAI SDK 调用 Qwen 系列模型（qwen-plus / qwen-3）
    """
    def __init__(self, client: OpenAI, model="qwen-plus"):
        self.client = client
        self.model = model

    def translate_news(self, article: dict) -> dict:
        translated_article = article.copy()
        original_language = article.get("language", "未知语言")
        translated_article["original_language"] = original_language

        # 翻译标题
        if article.get("title"):
            translated_article["title_zh"] = self._translate_text(
                f"请将下面的新闻标题翻译成中文，并保持新闻专业风格：\n{article['title']}"
            )
        else:
            translated_article["title_zh"] = ""

        # 翻译描述
        if article.get("description"):
            translated_article["description_zh"] = self._translate_text(
                f"请将下面的新闻摘要翻译成中文，并保持新闻专业风格：\n{article['description']}"
            )
        else:
            translated_article["description_zh"] = ""

        # 翻译内容
        if article.get("content"):
            translated_article["content_zh"] = self._translate_text(
                f"请将下面的新闻内容翻译成中文，并保持新闻专业风格：\n{article['content']}"
            )
        else:
            translated_article["content_zh"] = ""

        return translated_article

    def _translate_text(self, text: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的新闻翻译助手。"},
                {"role": "user", "content": text}
            ],
            temperature=0
        )
        return completion.choices[0].message.content
if __name__ == "__main__":
    # 使用环境变量或直接填入 API Key
    API_KEY_QWEN = "sk-28767c54e7bd45f8a9e60de7f154e588"
    client = OpenAI(
        api_key=API_KEY_QWEN,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    translator = MultiLangTranslationAgent(client, model="qwen-plus")

    # 示例多语言新闻
    article_jp = {
        "title": "新しいAIチップがリリースされました",
        "description": "新しいAIチップはトレーニング速度を2倍に向上させます。",
        "content": "2025年11月20日、あるテック企業は新しいAIチップを発表し、機械学習モデルのトレーニング速度を2倍に向上させました。",
        "url": "https://example.com/news_jp",
        "source": "TechCrunch Japan",
        "published_at": "2025-11-20T10:00:00Z",
    }

    translated = translator.translate_news(article_jp)
    print("标题:", translated["title_zh"])
    print("摘要:", translated["description_zh"])
    print("内容:", translated["content_zh"])
