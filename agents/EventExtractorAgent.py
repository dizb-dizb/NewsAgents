from openai import OpenAI

class EventExtractorAgent:
    """
    EventExtractor Agent：从新闻中抽取事件信息和实体关键词
    """
    def __init__(self, client: OpenAI, model="qwen-plus"):
        self.client = client
        self.model = model

    def extract_events(self, article: dict) -> list:
        """
        article: {
            "title_zh": str,
            "description_zh": str,
            "content_zh": str
        }
        返回事件列表，每条事件为 dict
        """
        text_to_extract = "\n".join([
            article.get("title_zh", ""),
            article.get("description_zh", ""),
            article.get("content_zh", "")
        ])

        prompt = (
            "请从以下新闻内容中抽取所有核心事件，每条事件包括："
            "主语(subject)、动作(action)、客体(object)、影响(impact)，"
            "并列出相关实体关键词(entities)，"
            "请以 JSON 数组格式输出，示例：\n"
            "[\n"
            "  {\"subject\": \"科技公司\", \"action\": \"发布\", \"object\": \"AI芯片\", "
            "\"impact\": \"训练速度提升2倍\", \"entities\": [\"科技公司\", \"AI芯片\"]},\n"
            "  {...}\n"
            "]\n\n"
            f"新闻内容：\n{text_to_extract}"
        )

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业新闻事件抽取助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        import json
        try:
            result_text = completion.choices[0].message.content
            events = json.loads(result_text)
        except Exception as e:
            print("解析 JSON 失败，返回空列表。", e)
            events = []

        return events
