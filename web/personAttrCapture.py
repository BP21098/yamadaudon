import os, base64, json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_with_gpt4o(image_path: str) -> dict:
    """画像ファイルをGPT-4oで解析してJSON形式で結果を返す関数"""
    # ファイルの存在確認
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")
    
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    
    resp = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system", 
                "content": "画像に写っている男性、女性、子供の人数を分析してください。結果を以下のJSON形式で出力してください: {\"men\": 数値, \"women\": 数値, \"children\": 数値, \"total\": 数値}"
            },
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
    
    # JSONレスポンスをパース
    result = json.loads(resp.choices[0].message.content.strip())
    
    # JSONファイルに保存
    save_to_json(result, image_path)
    
    return result

def save_to_json(data: dict, image_path: str):
    """分析結果をJSONファイルに保存する関数"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"analysis_result_{timestamp}.json"
    
    # 画像パス情報も含める
    output_data = {
        "timestamp": timestamp,
        "image_path": image_path,
        "analysis_result": data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"結果をJSONファイルに保存しました: {filename}")

# 直接実行時のテスト（インポート時は実行されない）
if __name__ == "__main__":
    # テスト用の画像パスを指定
    test_image_path = "test_image.jpg"  # 実際のファイルがある場合のみ
    
    if os.path.exists(test_image_path):
        try:
            result = analyze_with_gpt4o(test_image_path)
            print("分析結果:", result)
        except Exception as e:
            print(f"エラー: {e}")
    else:
        print("テスト画像ファイルが見つかりません")
