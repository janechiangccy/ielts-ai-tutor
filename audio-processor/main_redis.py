## redis version
# audio-service/main.py
from redis import Redis
from rq import Queue

import httpx 
from fastapi import FastAPI, UploadFile, File, HTTPException
import os
from openai import OpenAI
import base64

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Audio Processor Service")

redis_conn = Redis(host='localhost', port=6379)
q = Queue('grading_tasks', connection=redis_conn)
# 設定 Grading Service 的網址
# 注意：在 Podman 內，我們會用 localhost 或 container name 通訊
# 設定環境變數
API_KEY = os.getenv("OPENAI_API_KEY")
GRADING_SERVICE_URL = os.getenv("GRADING_SERVICE_URL", "http://localhost:8000/internal/v1/grade")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


@app.post("/transcribe-and-grade")
async def process_audio(file: UploadFile = File(...), user_id: str = "test_user"):
    print(f"🎤 收到來自 {user_id} 的音檔: {file.filename}")
    try:
        # --- 階段 1: 真實 STT (Speech to Text) ---
        # 讀取二進位音檔內容
        audio_content = await file.read()
        audio_b64 = base64.b64encode(audio_content).decode("utf-8")
        
        # 呼叫 Gemini 進行轉寫 (利用 Gemini 1.5 Flash 的多模態能力)
        # 這裡我們直接把音檔當成 context 餵給模型
        # 注意：在真實 SRE 環境，大型音檔會先存到 S3，這裡我們先用簡單的 Memory 處理
        print("🚀 正在呼叫 Gemini 進行語音轉寫...")
        stt_response = client.chat.completions.create(
            model="gemini-2.5-flash-lite-preview-09-2025",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Please transcribe this audio accurately."},
                        {
                            "type": "input_audio",
                            "input_audio": {"data": audio_b64, "format": "mp3"}
                        }
                    ],
                }
            ],
        )
        transcript = stt_response.choices[0].message.content
        print(f"📝 轉寫結果: {transcript}")

        # --- 階段 2: 呼叫 Grading Service (Microservice Communication) ---
        print(f"🔗 正在將文字傳送至評分服務: {GRADING_SERVICE_URL}")
        job = q.enqueue(
        "worker.process_grading_task", # 遠端 Worker 要執行的函數名
        args=(user_id, transcript),
        job_id=f"grading_{user_id}_{os.urandom(4).hex()}"
        )

        return {
            "status": "queued",
            "job_id": job.get_id(),
            "message": "Your speaking is being assessed. Check back later!"
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))