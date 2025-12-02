from pydantic import BaseModel
from typing import Optional, Dict
class NewsArticle(BaseModel):
    """标准化新闻文章模型，供多 Agent 交互使用"""
    url: str                      # 原始 URL
    title: Optional[str] = None   # 文章标题
    core_content: str = ""        # 提取的核心正文
    published_at: Optional[str] = None  # 发布时间
    source: Optional[str] = None  # 来源（如 Wired）
    raw_metadata: Optional[Dict] = None  # 原始爬取元数据（用于调试）

    class Config:
        arbitrary_types_allowed = True