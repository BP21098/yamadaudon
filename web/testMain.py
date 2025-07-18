from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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

# datasetフォルダ作成
os.makedirs("dataset", exist_ok=True)

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

def capture_and_analyze_async(table_id, session_id, people):
    """写真を撮影し、バックグラウンドで解析を開始"""
    if camera is None:
        print("カメラが利用できません。モック撮影を実行します。")
        # モック画像ファイルを作成（1x1の白い画像）
        mock_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        filename = f"dataset/mock_photo_{int(time.time())}.jpg"
        cv2.imwrite(filename, mock_image)
        print(f"モック写真を保存しました: {filename}")
    else:
        ret, frame = camera.read()
        if ret:
            filename = f"dataset/photo_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"写真を保存しました: {filename}")
        else:
            print("カメラから画像を取得できませんでした。モック撮影を実行します。")
            # モック画像ファイルを作成
            mock_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
            filename = f"dataset/mock_photo_{int(time.time())}.jpg"
            cv2.imwrite(filename, mock_image)
            print(f"モック写真を保存しました: {filename}")

    # バックグラウンドで解析を開始
    analysis_thread = threading.Thread(
        target=background_analyze, args=(filename, table_id, session_id, people)
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

# --- 店員用ルート（ダッシュボードのみ） ---

@app.route("/")
def staff_dashboard():
    """店員用ダッシュボード：テーブル状況と案内入力"""
    return render_template("test/staff_dashboard.html", tables=tables)

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
    
    # 写真撮影・バックグラウンド解析開始
    analysis_status = capture_and_analyze_async(table_id=table_id, session_id=session_id, people=people)

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

# --- Flaskアプリ起動 ---
if __name__ == "__main__":
    try:
        app.run(debug=True, host="0.0.0.0", port=5002)
    finally:
        if camera is not None:
            camera.release()
            print("カメラリソースを解放しました。")