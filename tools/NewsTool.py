import requests
from datetime import datetime, timedelta

class NewsTool:
    """
    NewsTool: 基于 NewsAPI 抓取新闻的工具
    输出统一的结构化新闻数据，便于智能体使用。
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/top-headlines"

    def fetch_news(
        self,
        category: str = "technology",
        language: str = "en",
        country: str = None,
        query: str = None,
        page_size: int = 50,
    ):
        """
        抓取新闻
        """
        params = {
            "apiKey": self.api_key,
            "category": category,
            "language": language,
            "pageSize": page_size,
        }
        if country:
            params["country"] = country
        if query:
            params["q"] = query

        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            raise Exception(f"NewsAPI请求失败: {response.status_code} {response.text}")

        data = response.json()
        if data.get("status") != "ok":
            raise Exception(f"NewsAPI返回错误: {data}")

        # 将新闻转换为统一结构
        articles = []
        for item in data.get("articles", []):
            articles.append({
                "title": item.get("title"),
                "description": item.get("description"),
                "content": item.get("content"),
                "url": item.get("url"),
                "source": item.get("source", {}).get("name"),
                "published_at": item.get("publishedAt"),
            })

        return articles

if __name__ == "__main__":
    API_KEY = "a77926ae7b92421d8af3fecd7bbb745b"  # 替换为你的 NewsAPI Key
    news_tool = NewsTool(api_key=API_KEY)

    # 示例：抓取科技新闻
    articles = news_tool.fetch_news(category="technology", language="en", page_size=10,query="AI")
    for idx, article in enumerate(articles, 1):
        print(f"===== 新闻 {idx} =====")
        print("标题:", article["title"])
        print("描述:", article["description"])
        print("来源:", article["source"])
        print("内容:",article["content"])
        print("发布时间:", article["published_at"])
        print("链接:", article["url"])
        print()
