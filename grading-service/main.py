import os
import json
from typing import List
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="IELTS Grading Engine")

# 1. 修改 Client 設定：讓 OpenAI SDK 連去 Google
# 注意：這裡使用環境變數 OPENAI_API_KEY，但填入的是 Gemini 的 Key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# --- 資料模型定義 (保持不變) ---
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

class GradingRequest(BaseModel):
    assessment_id: str
    transcript: str

# 2. 核心 AI 邏輯修正
def process_grading(assessment_id: str, transcript: str):
    print(f"Starting grading for {assessment_id} using Gemini...")
    
    # 取得 Pydantic 的 JSON Schema 字串，放入 Prompt 讓 Gemini 知道格式
    schema_instruction = json.dumps(GradingReport.model_json_schema(), indent=2)

    try:
        # 改用標準的 .create (比 .beta.parse 更相容於 Gemini)
        response = client.chat.completions.create(
            model="gemini-2.5-flash-lite-preview-09-2025",  # 改用 Google 的模型
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a professional IELTS examiner. "
                        "Grade the transcript based on official criteria. "
                        "You MUST output raw JSON matching this schema:\n"
                        f"{schema_instruction}"
                    )
                },
                {"role": "user", "content": f"Assess this transcript: {transcript}"}
            ],
            response_format={"type": "json_object"}, # 強制輸出 JSON
            temperature=0.3
        )
        
        # 解析回傳結果
        raw_content = response.choices[0].message.content
        report_data = json.loads(raw_content)
        report = GradingReport(**report_data)
        
        print(f"✅ Report for {assessment_id} generated: {report.overall_band}")

    except Exception as e:
        print(f"Error grading {assessment_id}: {str(e)}")

# 3. API Endpoint (保持你修改後的正確版本)
@app.post("/internal/v1/grade", status_code=202)
async def trigger_grading(request: GradingRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_grading, request.assessment_id, request.transcript)
    return {"message": "Grading process started", "assessment_id": request.assessment_id}