from tools.NewsTool import search_news
from agents.NewsCrawlAgent import NewsSummaryagent
if __name__ == "__main__":
    # 单条新闻测试
    test_url = "https://finance.sina.com.cn/jjxw/2025-11-27/doc-infyuwaq9601021.shtml"
    summary_tool = NewsSummaryagent()
    single_result = summary_tool.run(test_url)
    print("\n单条新闻总结结果：")
    print(single_result)

    # 批量新闻测试（取消注释即可使用）
    # test_urls = [
    #     "https://finance.sina.com.cn/jjxw/2025-11-27/doc-infyuwaq9601021.shtml",
    #     "https://tech.sina.com.cn/it/2025-11-26/doc-iahfyxkr32456789.shtml"
    # ]
    # batch_results = summary_tool.batch_run(test_urls)
    # print("\n批量总结结果：")
    # print(json.dumps(batch_results, ensure_ascii=False, indent=2))