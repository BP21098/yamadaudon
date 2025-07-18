from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import cv2
import os
import time
import threading
import queue
import uuid
import numpy as np
from personAttrCapture import analyze_with_gpt4o, update_seat_end_time

# --- 店員用アプリのみ ---
app = Flask(__name__)
app.secret_key = "your_staff_secret_key"

# テーブル情報
tables = [
    # カウンター席（1〜16番）
    {"id": 1, "type": "カウンター", "is_available": True},
    {"id": 2, "type": "カウンター", "is_available": True},
    {"id": 3, "type": "カウンター", "is_available": True},
    {"id": 4, "type": "カウンター", "is_available": True},
    {"id": 5, "type": "カウンター", "is_available": True},
    {"id": 6, "type": "カウンター", "is_available": True},
    {"id": 7, "type": "カウンター", "is_available": True},
    {"id": 8, "type": "カウンター", "is_available": True},
    {"id": 9, "type": "カウンター", "is_available": True},
    {"id": 10, "type": "カウンター", "is_available": True},
    {"id": 11, "type": "カウンター", "is_available": True},
    {"id": 12, "type": "カウンター", "is_available": True},
    {"id": 13, "type": "カウンター", "is_available": True},
    {"id": 14, "type": "カウンター", "is_available": True},
    {"id": 15, "type": "カウンター", "is_available": True},
    {"id": 16, "type": "カウンター", "is_available": True},
    # テーブル席（17, 19, 21, 24, 25, 26, 27, 28番）
    {"id": 17, "type": "テーブル", "is_available": True},
    {"id": 19, "type": "テーブル", "is_available": True},
    {"id": 21, "type": "テーブル", "is_available": True},
    {"id": 24, "type": "テーブル", "is_available": True},
    {"id": 25, "type": "テーブル", "is_available": True},
    {"id": 26, "type": "テーブル", "is_available": True},
    {"id": 27, "type": "テーブル", "is_available": True},
    {"id": 28, "type": "テーブル", "is_available": True}
]

# カメラ起動
try:
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("警告: カメラが見つかりません。モック撮影モードで動作します。")
        camera = None
    else:
        print("カメラが正常に起動しました。")
except Exception as e:
    print(f"カメラ初期化エラー: {e}")
    print("モック撮影モードで動作します。")
    camera = None

# datasetフォルダ作成（webディレクトリ内に作成）
dataset_dir = os.path.join(os.path.dirname(__file__), "dataset")
os.makedirs(dataset_dir, exist_ok=True)
print(f"Dataset ディレクトリ: {dataset_dir}")

# 解析結果を保存するためのキュー
analysis_queue = queue.Queue()

def background_analyze(filename, table_id, session_id, people):
    """バックグラウンドで画像解析を実行"""
    try:
        print("→ GPT-4o に属性解析を依頼中 …")
        analysis_result = analyze_with_gpt4o(filename, table_id, people)
        print("=== 解析結果 ===")
        print(analysis_result)
        print("================")
        
        # 解析結果をキューに保存（セッションIDと一緒に）
        if isinstance(analysis_result, dict):
            analysis_queue.put((session_id, analysis_result))
        else:
            analysis_queue.put((session_id, {"error": "解析結果の形式が不正です", "raw_result": str(analysis_result)}))
            
    except Exception as e:
        error_msg = f"解析エラー: {str(e)}"
        print("GPT-4o 呼び出しエラー:", e)
        analysis_queue.put((session_id, {"error": error_msg}))

def capture_and_analyze_async(table_id, session_id, people, image_path):
    """既存画像ファイルでバックグラウンド解析を開始"""
    # 新規撮影は行わず、image_pathをそのまま使う
    print(f"解析対象画像: {image_path}")
    analysis_thread = threading.Thread(
        target=background_analyze, args=(image_path, table_id, people, session_id)
    )
    analysis_thread.daemon = True
    analysis_thread.start()
    return {"status": "analyzing", "message": "解析中です..."}

def find_best_table(seat_type):
    """隣が使用中でない空席を優先して返す"""
    filtered = [t for t in tables if t["type"] == seat_type]
    
    # カウンター席の場合は連番で隣接する席を考慮
    if seat_type == "カウンター":
        counter_tables = sorted(filtered, key=lambda x: x["id"])
        # 隣が空いている席を優先
        for i, table in enumerate(counter_tables):
            if not table["is_available"]:
                continue
            left_ok = (i == 0) or counter_tables[i-1]["is_available"]
            right_ok = (i == len(counter_tables)-1) or counter_tables[i+1]["is_available"]
            if left_ok and right_ok:
                return table["id"]
        # なければ任意の空席
        for table in counter_tables:
            if table["is_available"]:
                return table["id"]
    
    # テーブル席の場合は任意の空席
    else:
        for table in filtered:
            if table["is_available"]:
                return table["id"]
    
    return None

def update_table_id_in_existing_files(from_table_id, to_table_id):
    """既存のJSONとCSVファイルで卓番号のみを更新する"""
    import glob
    import json
    import csv
    import tempfile
    import shutil
    from datetime import datetime
    
    # 今日の日付のディレクトリから最新のJSONファイルを取得
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = f"analysis_results/{today}"
    
    if not os.path.exists(today_dir):
        print(f"今日の日付のディレクトリが見つかりません: {today_dir}")
        return
    
    # JSONファイルの更新
    json_files = glob.glob(f"{today_dir}/analysis_result_*.json")
    json_files.sort(reverse=True)
    
    # 指定されたテーブルIDの最新のファイルを探して更新
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # テーブルIDが一致し、まだ席を空けた時間が記録されていない場合
            if data.get("table_id") == from_table_id and data.get("seat_end_time") is None:
                # 卓番号を新しいテーブルIDに更新
                data["table_id"] = to_table_id
                # ファイルを更新
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"JSONファイルの卓番号を {from_table_id} から {to_table_id} に更新しました: {json_file}")
                break
                
        except Exception as e:
            print(f"JSONファイル処理エラー: {json_file}, {e}")
            continue
    
    # CSVファイルの更新
    csv_path = f"{today_dir}/analysis_result_{today}.csv"
    if os.path.exists(csv_path):
        try:
            # 一時ファイルを使用してCSVを安全に更新
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
                        if (str(row.get("table_id")) == str(from_table_id) and 
                            (not row.get("seat_end_time") or row.get("seat_end_time").strip() == "")):
                            target_row_index = i
                        rows.append(row)
                
                # 一時ファイルに書き込み
                writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                writer.writeheader()
                
                for i, row in enumerate(rows):
                    if i == target_row_index:
                        row["table_id"] = to_table_id
                    writer.writerow(row)
            
            # 一時ファイルを元ファイルに置き換え
            if target_row_index >= 0:
                shutil.move(temp_path, csv_path)
                print(f"CSVファイルの卓番号を {from_table_id} から {to_table_id} に更新しました")
            else:
                os.unlink(temp_path)  # 一時ファイルを削除
                print("CSVで更新対象の行が見つかりませんでした")
                
        except Exception as e:
            print(f"CSV処理でエラーが発生しました: {e}")
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
    else:
        print(f"CSVファイルが見つかりません: {csv_path}")

# --- 店員用ルート（ダッシュボードのみ） ---

@app.route("/")
def staff_dashboard():
    """店員用ダッシュボード：テーブル状況と案内入力"""
    photo_dir = os.path.join(os.path.dirname(__file__), "dataset")
    photo_files = []
    
    if os.path.exists(photo_dir):
        # ファイル名（photo_タイムスタンプ.jpg）で昇順ソート
        jpg_files = [fname for fname in os.listdir(photo_dir) if fname.lower().endswith(".jpg")]
        jpg_files.sort(key=lambda x: os.path.getmtime(os.path.join(photo_dir, x)), reverse=True)
        
        for fname in jpg_files:
            photo_files.append({"filename": fname})
        
        print(f"見つかった写真ファイル: {len(photo_files)}個")
    else:
        print(f"写真ディレクトリが見つかりません: {photo_dir}")
    
    return render_template("test/staff_dashboard.html", tables=tables, photos=photo_files)

@app.route("/quick_seat", methods=["POST"])
def quick_seat_assignment():
    """ダッシュボードからの直接案内"""
    people = int(request.form.get("people"))
    seat_type = request.form.get("seat_type")
    table_id = int(request.form.get("table_id"))
    
    # テーブルが空いているかチェック
    selected_table = next((t for t in tables if t["id"] == table_id), None)
    if not selected_table or not selected_table["is_available"]:
        return redirect(url_for("staff_dashboard"))
    
    # 席種と人数の整合性チェック
    if seat_type == "カウンター" and people not in [1, 2, 3]:
        return redirect(url_for("staff_dashboard"))
    if seat_type == "テーブル" and people not in [1, 2, 3, 4]:
        return redirect(url_for("staff_dashboard"))

    # 席を使用中にする
    for table in tables:
        if table["id"] == table_id:
            table["is_available"] = False
            break

    # セッションIDを生成
    session_id = str(uuid.uuid4())
    
    # 案内完了メッセージと共にダッシュボードにリダイレクト
    return render_template("test/staff_dashboard.html", 
                         tables=tables, 
                         success=f"{people}名様を{seat_type}{table_id}番テーブルにご案内しました")

@app.route("/quick_table_action", methods=["POST"])
def quick_table_action():
    """ダッシュボードからの直接テーブル操作"""
    table_id = int(request.form.get("table_id"))
    action = request.form.get("action")
    
    for table in tables:
        if table["id"] == table_id:
            if action == "release":
                table["is_available"] = True
                update_seat_end_time(table_id)
            elif action == "occupy":
                table["is_available"] = False
            break
    
    return redirect(url_for("staff_dashboard"))

@app.route("/move_table", methods=["POST"])
def move_table():
    """席移動処理 - 既存ファイルの卓番号のみ更新"""
    from_table_id = int(request.form.get("from_table_id"))
    to_table_id = int(request.form.get("to_table_id"))
    people = int(request.form.get("people"))
    
    # 移動元テーブルの確認
    from_table = next((t for t in tables if t["id"] == from_table_id), None)
    if not from_table or from_table["is_available"]:
        return redirect(url_for("staff_dashboard"))
    
    # 移動先テーブルの確認
    to_table = next((t for t in tables if t["id"] == to_table_id), None)
    if not to_table or not to_table["is_available"]:
        return redirect(url_for("staff_dashboard"))
    
    # 席種と人数の整合性チェック
    if to_table["type"] == "カウンター" and people not in [1, 2, 3]:
        return redirect(url_for("staff_dashboard"))
    if to_table["type"] == "テーブル" and people not in [1, 2, 3, 4]:
        return redirect(url_for("staff_dashboard"))
    
    # 既存ファイルの卓番号を更新
    update_table_id_in_existing_files(from_table_id, to_table_id)
    
    # 移動元の席を空ける
    from_table["is_available"] = True
    
    # 移動先の席を使用中にする
    to_table["is_available"] = False
    
    return render_template("test/staff_dashboard.html", 
                         tables=tables, 
                         success=f"{people}名様を{from_table['type']}{from_table_id}番から{to_table['type']}{to_table_id}番テーブルに移動しました")

@app.route("/get_analysis_result")
def get_analysis_result():
    """解析結果を取得するAPI"""
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"status": "no_session"})
    
    # キューから該当するセッションの結果を探す
    temp_results = []
    while not analysis_queue.empty():
        try:
            stored_session_id, result = analysis_queue.get_nowait()
            if stored_session_id == session_id:
                return jsonify({"status": "complete", "result": result})
            else:
                temp_results.append((stored_session_id, result))
        except queue.Empty:
            break
    
    # 他のセッションの結果をキューに戻す
    for item in temp_results:
        analysis_queue.put(item)
    
    return jsonify({"status": "analyzing"})

@app.route("/take_photo", methods=["POST"])
def take_photo():
    """写真を撮影してdatasetフォルダに保存"""
    dataset_dir = os.path.join(os.path.dirname(__file__), "dataset")
    
    if camera is not None:
        ret, frame = camera.read()
        if ret:
            filename = os.path.join(dataset_dir, f"photo_{int(time.time())}.jpg")
            cv2.imwrite(filename, frame)
            print(f"写真を保存しました: {filename}")
        else:
            print("カメラから画像を取得できませんでした")
    else:
        # カメラが利用できない場合はモック画像を作成
        mock_image = np.ones((200, 200, 3), dtype=np.uint8) * 255
        # 簡単な模様を追加
        cv2.rectangle(mock_image, (50, 50), (150, 150), (200, 200, 200), -1)
        cv2.putText(mock_image, "MOCK", (70, 105), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
        filename = os.path.join(dataset_dir, f"mock_{int(time.time())}.jpg")
        cv2.imwrite(filename, mock_image)
        print(f"モック写真を保存しました: {filename}")
    
    return redirect(url_for("staff_dashboard"))

@app.route("/assign_photo", methods=["POST"])
def assign_photo():
    photo_filename = request.form.get("photo_filename")
    people = int(request.form.get("people"))
    table_id = int(request.form.get("table_id"))
    session_id = str(uuid.uuid4())
    
    # ファイルパスを正しく構築
    dataset_dir = os.path.join(os.path.dirname(__file__), "dataset")
    
    # HTMLから "dataset/filename.jpg" の形式で送られてくる場合の処理
    if photo_filename.startswith("dataset/"):
        filename_only = photo_filename.replace("dataset/", "")
        full_image_path = os.path.join(dataset_dir, filename_only)
    else:
        # ファイル名のみの場合
        full_image_path = os.path.join(dataset_dir, photo_filename)
    
    print(f"解析対象画像パス: {full_image_path}")
    print(f"ファイル存在確認: {os.path.exists(full_image_path)}")
    
    # ファイルの存在確認
    if not os.path.exists(full_image_path):
        print(f"エラー: 画像ファイルが見つかりません: {full_image_path}")
        return redirect(url_for("staff_dashboard"))
    
    # 解析開始
    analysis_status = capture_and_analyze_async(
        table_id=table_id, 
        session_id=session_id, 
        people=people, 
        image_path=full_image_path
    )
    
    # 席状態更新など
    for table in tables:
        if table["id"] == table_id:
            table["is_available"] = False

    # 解析ボタン押下時に dataset フォルダ内の写真をすべて削除
    for fname in os.listdir(dataset_dir):
        if fname.lower().endswith(".jpg"):
            try:
                file_to_delete = os.path.join(dataset_dir, fname)
                os.remove(file_to_delete)
                print(f"写真を削除しました: {file_to_delete}")
            except Exception as e:
                print(f"写真削除エラー: {fname} - {e}")

    return redirect(url_for("staff_dashboard"))

@app.route('/dataset/<path:filename>')
def dataset_file(filename):
    """dataset フォルダから画像ファイルを配信"""
    dataset_dir = os.path.join(os.path.dirname(__file__), "dataset")
    file_path = os.path.join(dataset_dir, filename)
    
    if os.path.exists(file_path):
        print(f"画像ファイルを配信: {file_path}")
        return send_from_directory(dataset_dir, filename)
    else:
        print(f"画像ファイルが見つかりません: {file_path}")
        return "画像が見つかりません", 404

# --- Flaskアプリ起動 ---
if __name__ == "__main__":
    try:
        app.run(debug=True, host="0.0.0.0", port=5002)
    finally:
        if camera is not None:
            camera.release()
            print("カメラリソースを解放しました。")