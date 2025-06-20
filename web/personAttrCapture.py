import os, base64
from openai import OpenAI
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを取得
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_with_gpt4o(image_path: str) -> str:
    """画像ファイルをGPT-4oで解析する関数"""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "画像に写っている男性、女性、子供の人数だけを教えてください。出力は"},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64}"
                        }
                    }
                ]
            }
        ]
    )
    return resp.choices[0].message.content.strip()