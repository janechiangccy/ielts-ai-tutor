import os
from openai import OpenAI

# 設定 Client 指向 Google
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

print("正在詢問 Google 目前可用的模型清單...")

try:
    # 呼叫 List Models API
    models = client.models.list()
    
    print("\n=== 你的 API Key 可以使用的模型如下 ===")
    found_any = False
    for m in models:
        # 過濾掉一些不相關的模型，只顯示 gemini 開頭的
        if "gemini" in m.id:
            print(f"- {m.id}")
            found_any = True
            
    if not found_any:
        print("(沒有找到 gemini 開頭的模型，顯示全部):")
        for m in models:
            print(f"- {m.id}")
            
except Exception as e:
    print(f"\n發生錯誤: {e}")
    print("請檢查你的 .env 檔案中的 OPENAI_API_KEY 是否正確 (應該是 AIzaSy 開頭)")