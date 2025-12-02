import json
import os
def load_api_key(key_name="DASHSCOPE_API_KEY"):
    """
    加载 API Key：
    - key.json 永远存储在本 py 文件同一目录下
    - 若不存在则要求用户输入并写入
    """

    # 当前 py 文件所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(base_dir, "key.json")

    api_key = None

    # 1. 如果 key.json 存在则读取
    if os.path.exists(key_path):
        try:
            with open(key_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                api_key = data.get(key_name)
        except Exception:
            pass

    # 2. 没找到 key，需要用户输入
    if not api_key:
        print(f"[需要] 请输入 {key_name}:")
        api_key = input(">>> ").strip()

        # 准备写入数据
        data = {}
        if os.path.exists(key_path):
            try:
                with open(key_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        data[key_name] = api_key

        with open(key_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"[已保存] API Key 已写入: {key_path}")

    return api_key