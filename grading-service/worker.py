# grading-service/worker.py
import os
from redis import Redis
from rq import Worker, Queue
from main import process_grading  # 載入你之前寫好的 Gemini 評分函數
from dotenv import load_dotenv
import time

load_dotenv()

# 1. 連接 Redis
redis_conn = Redis(host='localhost', port=6379)
listen_queues = ['grading_tasks']


# 2. 定義 Worker 要執行的任務包裝
def process_grading_task(user_id, transcript):
    print(f"📦 [Worker] 領取任務: 使用者 {user_id}")
    print(f"📝 轉寫內容: {transcript[:50]}...")
    
    try:
        # 🌟 只呼叫一次，並將結果存入變數 report
        report = process_grading(user_id, transcript)
        
        # 檢查一下 report 是不是空的
        if report is None:
            print(f"⚠️ [Worker] 警告: process_grading 回傳了 None")
            return {"error": "AI grading returned no data"}

        print(f"✅ [Worker] 任務完成: {user_id}")
        
        # 🌟 關鍵：將結果回傳給 Redis 存檔
        return report

    except Exception as e:
        print(f"❌ [Worker] 處理失敗: {str(e)}")
        return {"error": str(e)}

# 3. 啟動 Worker 監聽
if __name__ == '__main__':
    print("🚀 Grading Worker 已啟動，正在等待任務...")

    listen_queue = Queue('grading_tasks', connection=redis_conn)

    # 建立 Worker 並直接傳入 connection
    worker = Worker([listen_queue], connection=redis_conn)
    worker.work()