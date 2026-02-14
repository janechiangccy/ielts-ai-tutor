import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def test_stt_via_chat():
    # 讀取音檔並轉為 Base64 (Gemini 接收多模態數據的一種方式)
    with open("real_test.mp3", "rb") as f:
        audio_data = base64.b64encode(f.read()).decode("utf-8")

    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash-lite-preview-09-2025",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Please transcribe this audio accurately."},
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_data,
                                "format": "mp3"
                            }
                        }
                    ],
                }
            ],
        )
        print("✅ Gemini 多模態轉寫結果:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    test_stt_via_chat()