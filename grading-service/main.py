import os
from typing import List
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, Field
from openai import OpenAI

app = FastAPI(title="IELTS Grading Engine")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. 定義 AI 回傳的結構化資料模型 (Schema)
class DetailedScores(BaseModel):
    fluency_and_coherence: float = Field(..., ge=0, le=9.0)
    lexical_resource: float = Field(..., ge=0, le=9.0)
    grammatical_range_and_accuracy: float = Field(..., ge=0, le=9.0)
    pronunciation: float = Field(..., ge=0, le=9.0)

class AIFeedback(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    improved_transcript: str

class GradingReport(BaseModel):
    assessment_id: str
    overall_band: float
    detailed_scores: DetailedScores
    ai_feedback: AIFeedback

# 2. 核心 AI 邏輯：利用 LLM 進行評分
def process_grading(assessment_id: str, transcript: str):
    # 這裡實作 RAG 或直接調用 LLM
    # 使用 OpenAI 的 Response Format (JSON Mode) 確保輸出穩定
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a professional IELTS examiner. Grade the transcript based on official criteria."},
            {"role": "user", "content": f"Assess this transcript: {transcript}"}
        ],
        response_format=GradingReport,
    )
    
    report = response.choices[0].message.parsed
    # 這裡可以接上 Database 存檔邏輯 (例如 PostgreSQL)
    print(f"Report for {assessment_id} generated: {report.overall_band}")

# 3. API Endpoint
@app.post("/internal/v1/grade", status_code=202)
async def trigger_grading(assessment_id: str, transcript: str, background_tasks: BackgroundTasks):
    # 使用 FastAPI 的 BackgroundTasks 模擬異步處理
    # 在真實的 K8s 環境中，這裡通常是由 Consumer 監聽 Message Queue 後觸發
    background_tasks.add_task(process_grading, assessment_id, transcript)
    return {"message": "Grading process started", "assessment_id": assessment_id}