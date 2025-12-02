import os
from config import load_key
from langchain_community.chat_models import ChatOpenAI
from config.load_key import load_api_key 
def get_qwen_llm(model_name: str = "qwen-turbo") -> ChatOpenAI:
    """
    获取一个配置好的、用于调用阿里云百炼 Qwen 模型的 ChatOpenAI 实例。
    """
    # 确保你的环境变量中已经设置了 DASHSCOPE_API_KEY
    # 例如: export DASHSCOPE_API_KEY="sk_..."
    api_key = load_api_key("DASHSCOPE_API_KEY")
    
    # 阿里云百炼的 OpenAI 兼容 API 地址
    api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    print(f"正在初始化 Qwen LLM (兼容 OpenAI 模式)...")
    print(f"  - API Base: {api_base}")
    print(f"  - Model Name: {model_name}")
    
    return ChatOpenAI(
        model_name=model_name,
        openai_api_key=api_key,
        openai_api_base=api_base,
        temperature=0.0, # 根据你的需求调整
    )