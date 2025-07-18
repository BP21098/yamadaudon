import os, base64, json
import csv
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_with_gpt4o(image_path: str, table_id: int = None, people: int = None) -> dict:
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
                
                Classify as follows:
                - Gender: male, female
                - Age group: child (0-12), teenager (13-19), young_adult (20-39), middle_aged (40-59), senior (60+)

                Please analyze the people in the image in detail.

                Classify as follows:

                Gender: male, female
                Age group: child (0-12), teenager (13-19), young_adult (20-39), middle_aged (40-59), senior (60+)
                Output the result in the following JSON format:
                {
                "total_count": total number of people,
                "gender_breakdown": {
                "men": number of males,
                "women": number of females,
                },
                "age_breakdown": {
                "children": number of children,
                "teenagers": number of teenagers,
                "young_adults": number of young adults,
                "middle_aged": number of middle-aged,
                "seniors": number of seniors,
                },
                "detailed_analysis": [
                    {
                      "person_id": 1,
                      "gender": "male or female",
                      "estimated_age_range": "estimated age range",
                      "age_category": "child/teenager/young_adult/middle_aged/senior",
                      "confidence": "high/medium/low"
                    }
                  ],
                  "analysis_notes": "Any special notes or caveats"
                }
                
                Notes:
                - If a person cannot be clearly identified, state so in analysis_notes.
                - Age estimation is based on appearance.
                - If confidence is low, state so clearly.
                """
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please analyze the gender and age group of the people in this image in detail."
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
    # CSVにも保存（日付ごとのディレクトリに保存）
    date_str = datetime.now().strftime("%Y-%m-%d")
    csv_path = f"analysis_results/{date_str}/analysis_result_{date_str}.csv"
    save_analysis_as_csv(
        {
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
        },
        csv_path,
        selected_people=people  # ボタンで選択された人数
    )
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

                # --- ここでCSVも更新 ---
                date_str = datetime.now().strftime("%Y-%m-%d")
                csv_path = f"analysis_results/{date_str}/analysis_result_{date_str}.csv"
                update_seat_end_time_in_csv(
                    table_id,
                    data["seat_end_time"],
                    csv_path
                )
                return
                
        except Exception as e:
            print(f"ファイル処理エラー: {json_file}, {e}")
            continue
    
    print(f"テーブル{table_id}の更新対象ファイルが見つかりませんでした")

def update_seat_end_time_in_csv(table_id, seat_end_time, csv_path):
    """
    指定されたtable_idの最新行のseat_end_timeをCSVでも更新する
    """
    import tempfile
    import shutil
    
    if not os.path.exists(csv_path):
        print(f"CSVファイルが見つかりません: {csv_path}")
        print("CSV更新をスキップします")
        return

    try:
        # 一時ファイルを使用してCSVを安全に更新
        temp_file = None
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', newline='') as temp_file:
            temp_path = temp_file.name
            
            # 元ファイルを読み込み
            rows = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                
                # 更新対象の行を探しながらデータを読み込み
                target_row_index = -1
                for i, row in enumerate(reader):
                    if (str(row.get("table_id")) == str(table_id) and 
                        (not row.get("seat_end_time") or row.get("seat_end_time").strip() == "")):
                        target_row_index = i
                    rows.append(row)
            
            # 一時ファイルに書き込み
            writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, row in enumerate(rows):
                if i == target_row_index:
                    row["seat_end_time"] = seat_end_time
                writer.writerow(row)
        
        # 一時ファイルを元ファイルに置き換え
        if target_row_index >= 0:
            # ディレクトリが存在することを確認
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            shutil.move(temp_path, csv_path)
            print(f"CSVのseat_end_timeも更新しました（table_id={table_id}）")
        else:
            os.unlink(temp_path)  # 一時ファイルを削除
            print("CSVで更新対象の行が見つかりませんでした")
            
    except PermissionError as e:
        print(f"CSVファイルへのアクセス権限がありません: {e}")
        print("ファイルが他のアプリケーションで開かれている可能性があります")
        if temp_file and os.path.exists(temp_path):
            os.unlink(temp_path)
    except Exception as e:
        print(f"CSV処理でエラーが発生しました: {e}")
        if temp_file and os.path.exists(temp_path):
            os.unlink(temp_path)

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

def save_analysis_as_csv(json_data, csv_path, selected_people=None):
    """
    analysis_resultのdetailed_analysisをCSVで保存
    selected_people: ボタンで選択された人数（int）
    """
    import time
    
    try:
        analysis = json_data["analysis_result"]
        detailed = analysis.get("detailed_analysis", [])
        total_count = analysis.get("total_count", None)
        # 差分を計算
        people_diff = None
        if selected_people is not None and total_count is not None:
            people_diff = int(selected_people) - int(total_count)
        # seat_end_timeもjson_dataから取得
        seat_end_time = json_data.get("seat_end_time")
        # CSVのヘッダー
        fieldnames = [
            "image_path", "table_id", "seat_start_time", "seat_end_time",
            "selected_people", "camera_total", "people_diff",
            "person_id", "gender", "estimated_age_range", "age_category", "confidence"
        ]
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        # ファイルロックを回避するために少し待機
        max_retries = 3
        for attempt in range(max_retries):
            try:
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
                            "seat_end_time": seat_end_time,  # ここでseat_end_timeも記録
                            "selected_people": selected_people,
                            "camera_total": total_count,
                            "people_diff": people_diff,
                            "person_id": person.get("person_id"),
                            "gender": person.get("gender"),
                            "estimated_age_range": person.get("estimated_age_range"),
                            "age_category": person.get("age_category"),
                            "confidence": person.get("confidence"),
                        })
                print(f"CSV分析結果を保存しました: {csv_path}")
                break  # 成功したのでループを抜ける
                
            except PermissionError as e:
                if attempt < max_retries - 1:
                    print(f"CSVファイルがロックされています。再試行します... ({attempt + 1}/{max_retries})")
                    time.sleep(1)  # 1秒待機してリトライ
                else:
                    print(f"CSVファイルへのアクセス権限がありません: {e}")
                    print("ファイルが他のアプリケーションで開かれている可能性があります")
            except Exception as e:
                print(f"CSV保存でエラーが発生しました: {e}")
                break
                
    except Exception as e:
        print(f"CSV保存の準備でエラーが発生しました: {e}")
        print("CSV保存をスキップしました")

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
