import os, base64
from openai import OpenAI
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを取得
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_with_gpt4o(image_path: str) -> str:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "画像に写っている男性、女性、子供の人数だけを教えてください。"},
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

if __name__ == "__main__":
    # 解析したい画像ファイルのパスを指定
    image_path = "dataset/test.jpg"  # ここを判定したい画像ファイル名に変更
    try:
        result = analyze_with_gpt4o(image_path)
        print("=== 解析結果 ===")
        print(result)
        print("================")
    except Exception as e:
        print("GPT-4o 呼び出しエラー:", e)