import requests
import json

url = "https://jisunews.market.alicloudapi.com/news/channel"
appcode = "e810d8eeff8a4ad5b5fe09d01d837aa4"

headers = {
    "Authorization": f"APPCODE {appcode}",
    "Content-Type": "application/json; charset=UTF-8"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, ensure_ascii=False, indent=2))
else:
    print("请求失败:", response.status_code, response.text)
