import os, base64, json
import csv
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
                "content": """画像に写っている人物を詳細に分析してください。
                
                以下の基準で分類してください：
                - 性別：男性、女性
                - 年齢層：子供(0-12歳)、青少年(13-19歳)、若年成人(20-39歳)、中年(40-59歳)、高齢者(60歳以上)
                
                結果を以下のJSON形式で出力してください：
                {
                  "total_count": 総人数,
                  "gender_breakdown": {
                    "men": 男性の総数,
                    "women": 女性の総数
                  },
                  "age_breakdown": {
                    "children": 子供の人数,
                    "teenagers": 青少年の人数,
                    "young_adults": 若年成人の人数,
                    "middle_aged": 中年の人数,
                    "seniors": 高齢者の人数
                  },
                  "detailed_analysis": [
                    {
                      "person_id": 1,
                      "gender": "男性 or 女性",
                      "estimated_age_range": "推定年齢範囲",
                      "age_category": "年齢カテゴリ",
                      "confidence": "推定の確信度(high/medium/low)"
                    }
                  ],
                  "analysis_notes": "特記事項や分析時の注意点"
                }
                
                注意：
                - 人物が明確に判別できない場合は、その旨を analysis_notes に記載してください
                - 年齢推定は外見的特徴に基づく推定であることを理解してください
                - 確信度が低い場合は、その旨を明記してください"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "この画像に写っている人物の性別と年齢層を詳細に分析してください。"
                    },
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
    # ★ここでCSVにも保存
    save_analysis_as_csv({
        "image_path": image_path,
        "table_id": table_id,
        "seat_start_time": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        "seat_end_time": None,
        "analysis_result": result,
        "metadata": {
            "analyzed_at": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "model_used": "gpt-4o",
            "analysis_version": "v2.0_detailed_age"
        }
    }, "analysis_results/analysis_result.csv")
    return result

def save_to_json(data: dict, image_path: str, table_id: int = None, seat_end_time: str = None):
    """分析結果をJSONファイルに保存する関数"""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    date_str = now.strftime("%Y-%m-%d")
    
    # 日付ごとのディレクトリを作成
    date_dir = f"analysis_results/{date_str}"
    os.makedirs(date_dir, exist_ok=True)
    
    filename = f"{date_dir}/analysis_result_{timestamp}.json"
    
    # 画像パス情報と卓番号、席を空けた時間も含める
    output_data = {
        "image_path": image_path,
        "table_id": table_id,
        "seat_start_time": timestamp,
        "seat_end_time": seat_end_time,
        "analysis_result": data,
        "metadata": {
            "analyzed_at": timestamp,
            "model_used": "gpt-4o",
            "analysis_version": "v2.0_detailed_age"
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"詳細分析結果をJSONファイルに保存しました: {filename}")

def update_seat_end_time(table_id: int):
    """指定されたテーブルIDの最新のJSONファイルに席を空けた時間を追記する関数"""
    import glob
    
    # 今日の日付のディレクトリから最新のJSONファイルを取得
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = f"analysis_results/{today}"
    
    if not os.path.exists(today_dir):
        print(f"今日の日付のディレクトリが見つかりません: {today_dir}")
        return
    
    json_files = glob.glob(f"{today_dir}/analysis_result_*.json")
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

def print_analysis_summary(result: dict):
    """分析結果をわかりやすく表示する関数"""
    print("\n" + "="*50)
    print("人物分析結果サマリー")
    print("="*50)
    
    print(f"総人数: {result.get('total_count', 0)}人")
    
    # 性別内訳
    gender = result.get('gender_breakdown', {})
    print(f"\n【性別内訳】")
    print(f"  男性: {gender.get('men', 0)}人")
    print(f"  女性: {gender.get('women', 0)}人")
    
    # 年齢層内訳
    age = result.get('age_breakdown', {})
    print(f"\n【年齢層内訳】")
    print(f"  子供 (0-12歳): {age.get('children', 0)}人")
    print(f"  青少年 (13-19歳): {age.get('teenagers', 0)}人")
    print(f"  若年成人 (20-39歳): {age.get('young_adults', 0)}人")
    print(f"  中年 (40-59歳): {age.get('middle_aged', 0)}人")
    print(f"  高齢者 (60歳以上): {age.get('seniors', 0)}人")
    
    # 詳細分析
    details = result.get('detailed_analysis', [])
    if details:
        print(f"\n【個別分析】")
        for person in details:
            print(f"  人物{person.get('person_id')}: "
                  f"{person.get('gender')} / "
                  f"{person.get('estimated_age_range')} / "
                  f"確信度: {person.get('confidence')}")
    
    # 特記事項
    notes = result.get('analysis_notes', '')
    if notes:
        print(f"\n【特記事項】")
        print(f"  {notes}")
    
    print("="*50)

def save_analysis_as_csv(json_data, csv_path):
    """
    analysis_resultのdetailed_analysisをCSVで保存
    """
    analysis = json_data["analysis_result"]
    detailed = analysis.get("detailed_analysis", [])
    # CSVのヘッダー
    fieldnames = [
        "image_path", "table_id", "seat_start_time", "seat_end_time",
        "person_id", "gender", "estimated_age_range", "age_category", "confidence"
    ]
    # ファイルがなければヘッダーを書き込む
    write_header = not os.path.exists(csv_path)
    with open(csv_path, "a", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for person in detailed:
            writer.writerow({
                "image_path": json_data.get("image_path"),
                "table_id": json_data.get("table_id"),
                "seat_start_time": json_data.get("seat_start_time"),
                "seat_end_time": json_data.get("seat_end_time"),
                "person_id": person.get("person_id"),
                "gender": person.get("gender"),
                "estimated_age_range": person.get("estimated_age_range"),
                "age_category": person.get("age_category"),
                "confidence": person.get("confidence"),
            })

# 直接実行時のテスト（インポート時は実行されない）
if __name__ == "__main__":
    # テスト用の画像パスを指定
    test_image_path = "test_image.jpg"
    
    if os.path.exists(test_image_path):
        try:
            result = analyze_with_gpt4o(test_image_path, table_id=1)
            print_analysis_summary(result)
        except Exception as e:
            print(f"エラー: {e}")
    else:
        print("テスト画像ファイルが見つかりません")
        print("使用例:")
        print("result = analyze_with_gpt4o('path/to/image.jpg', table_id=1)")
