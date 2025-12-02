import json
from typing import Dict
import requests
from config.load_key import load_api_key
from agents.KGAgent import LLMEndToEndJsonToPngAgent
from tools.NewsTool import get_serp_json
if __name__ == "__main__":
    # 辅助函数：调用 SerpAPI 获取 JSON 数据
    SERP_API_KEY=load_api_key("SERP_API_KEY")
    # 初始化 Agent
    agent = LLMEndToEndJsonToPngAgent()
    # 测试1：处理单个实体（苹果公司）
    print("=== 测试1：单个实体（苹果公司）===")
    apple_json = get_serp_json("苹果公司")
    agent.run(apple_json)
    # 测试2：处理特殊类型实体（爱因斯坦-人物，CPI-经济指标）
    print("\n=== 测试2：特殊类型实体 ===")
    einstein_json = get_serp_json("阿尔伯特·爱因斯坦")
    cpi_json = get_serp_json("CPI 消费者物价指数")
    agent.run([einstein_json, cpi_json], output_dir="serp_png_special")
    # 测试3：处理 JSON 字符串输入
    print("\n=== 测试3：JSON 字符串输入 ===")
    tesla_json_str = json.dumps(get_serp_json("特斯拉"), ensure_ascii=False)
    agent.run(tesla_json_str)