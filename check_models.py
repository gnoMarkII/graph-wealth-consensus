"""Utility script to list available Google generative AI models."""

import os
from dotenv import load_dotenv
from google import genai

def list_text_models() -> list[str]:
    """Return a list of text-capable Google generative AI model names."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY is not set in .env")

    client = genai.Client(api_key=api_key)
    models = client.models.list()
    
    text_models = []
    for m in models:
        # 🌟 ปรับการกรองใหม่: ดึงมาเฉพาะชื่อที่มีคำว่า "gemini" 
        # (เพราะ SDK ใหม่เปลี่ยนโครงสร้าง properties ไปแล้ว)
        if "gemini" in m.name.lower():
            text_models.append(m.name)
            
    return text_models


def main() -> None:
    """Run the model listing utility and print available text generation models."""
    try:
        model_names = list_text_models()
        print("✅ รายชื่อโมเดลที่คุณสามารถใช้งานได้ (อัปเดต SDK ใหม่):")
        print("-" * 40)
        for name in model_names:
            print(f"- {name}")
        print("-" * 40)
        print(f"รวมทั้งหมด {len(model_names)} โมเดล")
    except Exception as exc:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ: {exc}")


if __name__ == "__main__":
    main()