import os, base64, json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_with_gpt4o(image_path: str, table_id: int = None) -> dict:
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
    save_to_json(result, image_path, table_id)
    return result

def save_to_json(data: dict, image_path: str, table_id: int = None, seat_end_time: str = None):
    """分析結果をJSONファイルに保存する関数"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"analysis_result_{timestamp}.json"
    
    # 画像パス情報と卓番号、席を空けた時間も含める
    output_data = {
        "image_path": image_path,
        "table_id": table_id,
        "seat_start_time": timestamp,  # 席に着いた時間
        "seat_end_time": seat_end_time,  # 席を空けた時間（最初はNone）
        "analysis_result": data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"結果をJSONファイルに保存しました: {filename}")

def update_seat_end_time(table_id: int):
    """指定されたテーブルIDの最新のJSONファイルに席を空けた時間を追記する関数"""
    import glob
    
    # 最新のJSONファイルを取得
    json_files = glob.glob("analysis_result_*.json")
    if not json_files:
        print("更新対象のJSONファイルが見つかりません")
        return
    
    # 最新のファイルを特定
    json_files.sort(reverse=True)
    
    # 指定されたテーブルIDの最新のファイルを探す
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # テーブルIDが一致し、まだ席を空けた時間が記録されていない場合
            if data.get("table_id") == table_id and data.get("seat_end_time") is None:
                # 席を空けた時間を追記
                data["seat_end_time"] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                
                # ファイルを更新
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"テーブル{table_id}の席を空けた時間を記録しました: {json_file}")
                return
                
        except Exception as e:
            print(f"ファイル処理エラー: {json_file}, {e}")
            continue
    
    print(f"テーブル{table_id}の更新対象ファイルが見つかりませんでした")

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
