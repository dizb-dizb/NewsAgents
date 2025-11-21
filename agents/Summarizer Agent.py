from openai import OpenAI

class SummarizerAgent:
    """
    Summarizer Agent：生成长新闻摘要、要点和分段结构化信息
    """
    def __init__(self, client: OpenAI, model="qwen-plus"):
        self.client = client
        self.model = model

    def summarize_news(self, article: dict) -> dict:
        """
        article: {
            "title_zh": str,
            "description_zh": str,
            "content_zh": str
        }
        返回结构化摘要
        """
        text_to_summarize = "\n".join([
            article.get("title_zh", ""),
            article.get("description_zh", ""),
            article.get("content_zh", "")
        ])

        prompt = (
            "请根据以下新闻内容生成中文长摘要，并列出关键要点，"
            "同时按逻辑分段生成分段结构化信息，"
            "输出 JSON 格式：\n"
            f"{text_to_summarize}\n"
            "JSON 格式示例：\n"
            "{\n"
            "  \"summary\": \"新闻摘要文本\",\n"
            "  \"key_points\": [\"要点1\", \"要点2\"],\n"
            "  \"sections\": [\n"
            "      {\"heading\": \"段落标题1\", \"content\": \"段落内容1\"},\n"
            "      {\"heading\": \"段落标题2\", \"content\": \"段落内容2\"}\n"
            "  ]\n"
            "}"
        )

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业新闻摘要生成助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        import json
        try:
            result_text = completion.choices[0].message.content
            structured_result = json.loads(result_text)
        except Exception as e:
            print("解析 JSON 失败，返回原始文本。", e)
            structured_result = {"summary": result_text, "key_points": [], "sections": []}

        return structured_result
if __name__ == "__main__":
    import os
    API_KEY_QWEN = "sk-28767c54e7bd45f8a9e60de7f154e588"
    client = OpenAI(
        api_key=API_KEY_QWEN,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    summarizer = SummarizerAgent(client, model="qwen-plus")

    article = {
        "title_zh": "新型AI芯片发布",
        "description_zh": "新芯片可将训练速度提升2倍。",
        "content_zh": "2025年11月20日，某科技公司发布了全新的AI芯片..."
    }

    summary_result = summarizer.summarize_news(article)
    print("摘要:", summary_result["summary"])
    print("关键要点:", summary_result["key_points"])
    print("分段结构化信息:", summary_result["sections"])

