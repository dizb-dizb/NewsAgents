import requests
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from config.load_key import load_api_key
# --- 1. 定义新闻搜索函数 ---
firecrawl_api_key=load_api_key("FIRECRAWL_API_KEY")
NEW_API_KEY = load_api_key("NEW_API_KEY")
JINA_API_KEY=load_api_key("JINA_API_KEY")
def search_news(
    query: str,
    search_in: str = "title,description,content",
    sources: str = "",
    domains: str = "",
    exclude_domains: str = "",
    from_date: str = "",
    to_date: str = "",
    language: str = "",
    sort_by: str = "popularity",
    page_size: int = 20,
    page: int = 1
) -> str:
    """
    调用新闻 API 搜索相关文章。
    参数:
        query (str): 搜索关键词或短语。支持高级搜索语法，如 "exact phrase", +must_include, -must_not_include。
        search_in (str): 限制搜索的字段，可选值: title, description, content。多个值用逗号分隔。默认搜索所有字段。
        sources (str): 逗号分隔的新闻源ID列表。
        domains (str): 逗号分隔的域名列表，用于限制搜索范围。
        exclude_domains (str): 逗号分隔的域名列表，用于排除搜索结果。
        from_date (str): 最早文章的日期，格式为 ISO 8601 (YYYY-MM-DD)。
        to_date (str): 最新文章的日期，格式为 ISO 8601 (YYYY-MM-DD)。
        language (str): 文章语言的 2 字母 ISO 代码 (例如: en, zh)。
        sort_by (str): 结果排序方式。可选值: relevancy, popularity, publishedAt。默认是 publishedAt。
        page_size (int): 每页返回的结果数量。最大值为 100。默认是 20。
        page (int): 用于分页的页码。默认是 1。

    返回:
        str: 格式化后的新闻搜索结果字符串。
    """
    # 从环境变量获取 API Key，这是更安全的方式

    if not NEW_API_KEY:
        return "错误：未设置 NEWS_API_KEY 环境变量。"

    base_url = "https://newsapi.org/v2/everything"
    
    # 构建请求参数字典
    params = {
        "q": query,
        "searchIn": search_in,
        "sortBy": sort_by,
        "pageSize": page_size,
        "page": page,
    }

    # 仅当参数有值时才添加到请求中，避免发送空字符串
    if sources:
        params["sources"] = sources
    if domains:
        params["domains"] = domains
    if exclude_domains:
        params["excludeDomains"] = exclude_domains
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if language:
        params["language"] = language

    # 构建请求头
    headers = {
        "X-Api-Key": NEW_API_KEY
    }
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # 如果请求失败则抛出异常
        data = response.json()

        if data.get("status") != "ok":
            return f"API 请求失败: {data.get('message', '未知错误')}"

        articles = data.get("articles", [])
        if not articles:
            return "未找到相关新闻。"
        # 格式化返回结果
        formatted_results = []
        for idx, article in enumerate(articles, 1):
            title = article.get("title", "无标题")
            source = article.get("source", {}).get("name", "未知来源")
            published_at = article.get("publishedAt", "未知时间")
            url = article.get("url", "")
            
            # 改为字典格式，方便后续处理或序列化
            formatted_results.append({
                "index": idx,
                "title": title,
                "source": source,
                "published_at": published_at,
                "url": url
            })
        return formatted_results

    except requests.exceptions.RequestException as e:
        return f"请求新闻 API 时发生错误: {str(e)}"

# --- 2. 创建 LangChain Tool 对象 ---
# 注意：这里的 description 非常关键，它需要清晰地告诉 LLM 这个工具的作用和各个参数的含义。
# LLM 会根据这个描述来决定是否调用工具，以及如何构造参数。
news_search_tool = Tool(
    name="SearchNews",
    func=search_news,
    description="""
    一个用于搜索最新新闻文章的工具。当你需要了解当前事件、特定主题的最新动态或相关资讯时，应该使用这个工具。
    
    参数说明:
    - query: (必填) 你想要搜索的关键词或短语。你可以使用高级搜索语法，例如用引号括起来表示精确匹配，
             用 '+' 前缀表示必须包含某个词，用 '-' 前缀表示必须排除某个词。
    - language: (可选) 希望搜索的新闻语言，用 2 个字母的代码表示，例如 'en' 表示英文，'zh' 表示中文。
    - from_date: (可选) 搜索的起始日期，格式为 YYYY-MM-DD。
    - to_date: (可选) 搜索的结束日期，格式为 YYYY-MM-DD。
    - sort_by: (可选) 结果的排序方式，可选值为 'relevancy' (相关性), 'popularity' (热门程度), 'publishedAt' (发布时间)。
    - page_size: (可选) 每次返回的新闻数量，最大值为 100。
    
    例如，如果你想搜索 "2024年奥运会 篮球" 的英文新闻，可以这样调用: 
    SearchNews(query="2024 Olympics basketball", language="en")
    """
)
# ======================== 3. 你的工具函数（封装为 LangChain Tool）========================
def extract_news_original_content(url: str) -> str:
    """提取新闻原文（已过滤广告/导航）"""
    if not url.startswith(("http://", "https://")):
        return "错误：请输入有效的新闻 URL（需以 http:// 或 https:// 开头）"
    
    jina_url = f"https://r.jina.ai/{url}"
    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "X-Respond-With": "readerlm-v2",
        "X-Retain-Images": "none",
        "Accept": "application/json"
    }

    try:
        response = requests.get(jina_url, headers=headers, timeout=90)
        response.raise_for_status()
        result = response.json()
        
        original_content = result.get("data", {}).get("content", "") or result.get("content", "")
        if not original_content:
            return "错误：未提取到新闻原文"
        
        max_chars = 25000
        if len(original_content) > max_chars:
            original_content = original_content[:max_chars] + "\n\n...（内容过长，已保留核心部分）..."
        
        return original_content.strip()

    except requests.exceptions.Timeout:
        return f"错误：请求超时，无法访问网页 {url}"
    except requests.exceptions.RequestException as e:
        return f"错误：提取原文失败，原因：{str(e)}"
    except ValueError:
        return "错误：Jina 返回格式异常，无法解析"

# 封装为 LangChain Tool（便于 Agent 管理，不影响核心逻辑）
news_extract_tool = Tool(
    name="extract_news_original_content",
    func=extract_news_original_content,
    description="提取新闻网页的纯净原文，自动过滤广告、导航栏等冗余内容，仅支持新闻类 URL"
)