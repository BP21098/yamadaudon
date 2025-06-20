from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import cv2
import os
import time
import threading
import queue
import uuid
from personAttrCapture import analyze_with_gpt4o, update_seat_end_time  # update_seat_end_timeをインポート

# --- お客様用アプリ ---
app = Flask(__name__)
app.secret_key = "your_secret_key"

# --- 店員用アプリ ---
staff_app = Flask(__name__)
staff_app.secret_key = "your_staff_secret_key"

# テーブル情報（両アプリで共有）
tables = [
    {"id": 1, "type": "カウンター", "is_available": True},
    {"id": 2, "type": "カウンター", "is_available": True},
    {"id": 3, "type": "カウンター", "is_available": True},
    {"id": 4, "type": "カウンター", "is_available": True},
    {"id": 5, "type": "テーブル", "is_available": True},
    {"id": 6, "type": "テーブル", "is_available": True},
    {"id": 7, "type": "テーブル", "is_available": True},
    {"id": 8, "type": "テーブル", "is_available": True},
    {"id": 9, "type": "テーブル", "is_available": True},
    {"id": 10, "type": "テーブル", "is_available": True}
]

# カメラ起動
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    raise RuntimeError("カメラが見つかりません")

# datasetフォルダ作成
os.makedirs("dataset", exist_ok=True)

def capture_and_save():
    ret, frame = camera.read()
    if ret:
        filename = f"dataset/photo_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        print(f"写真を保存しました: {filename}")
    else:
        print("カメラから画像を取得できませんでした")

# 解析結果を保存するためのキュー
analysis_queue = queue.Queue()

def background_analyze(filename, table_id, session_id):
    """バックグラウンドで画像解析を実行"""
    try:
        print("→ GPT-4o に属性解析を依頼中 …")
        analysis_result = analyze_with_gpt4o(filename, table_id)
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

def capture_and_analyze_async(table_id, session_id):
    """写真を撮影し、バックグラウンドで解析を開始"""
    ret, frame = camera.read()
    if ret:
        filename = f"dataset/photo_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        print(f"写真を保存しました: {filename}")
        
        # バックグラウンドで解析を開始
        analysis_thread = threading.Thread(target=background_analyze, args=(filename, table_id, session_id))
        analysis_thread.daemon = True
        analysis_thread.start()
        
        return {"status": "analyzing", "message": "解析中です..."}
    else:
        print("カメラから画像を取得できませんでした")
        return {"error": "カメラエラー"}

@app.route("/", methods=["GET", "POST"])
def select_people():
    if request.method == "POST":
        seat_type = request.form.get("seat_type")
        people = int(request.form.get("people", 0))

        # 席種と人数の整合性チェック
        if seat_type == "カウンター" and people not in [1, 2, 3]:
            return render_template("select_people_design.html", error="カウンターは1～3人のみです")
        if seat_type == "テーブル" and people not in [1, 2, 3, 4]:
            return render_template("select_people_design.html", error="テーブルは1～4人のみです")

        # ここでavailable_table_idを決定
        available_table_id = None
        for table in tables:
            if table["type"] == seat_type and table["is_available"]:
                available_table_id = table["id"]
                table["is_available"] = False
                break

        # セッションIDを生成
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id

        # 写真撮影・バックグラウンド解析開始
        analysis_status = capture_and_analyze_async(table_id=available_table_id, session_id=session_id)

        session["seat_type"] = seat_type
        session["available_table_id"] = available_table_id
        session["analysis_status"] = analysis_status  # 解析ステータスをセッションに保存
        return redirect(url_for("show_result"))
    return render_template("select_people_design.html")

@app.route("/get_analysis_result")
def get_analysis_result():
    """解析結果を取得するAPI"""
    session_id = session.get("session_id")
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

@app.route("/result")
def show_result():
    seat_type = session.get("seat_type")
    available_table_id = session.get("available_table_id")
    analysis_status = session.get("analysis_status", {})
    return render_template("result.html", 
                         seat_type=seat_type, 
                         available_table_id=available_table_id,
                         analysis_status=analysis_status)

# --- 店員用ルート ---

@staff_app.route("/", methods=["GET", "POST"])
def staff_index():
    if request.method == "POST":
        table_id = int(request.form.get("table_id"))
        for table in tables:
            if table["id"] == table_id:
                table["is_available"] = True  # 空き状態にする
                # 席を空けた時間をJSONファイルに記録
                update_seat_end_time(table_id)
                break
        return redirect(url_for("staff_index"))
    return render_template("table.html", tables=tables)



'''
def capture_and_analyze():
    """写真を撮影し、GPT-4oで解析する"""
    ret, frame = camera.read()
    if ret:
        filename = f"dataset/photo_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        print(f"写真を保存しました: {filename}")
        
        # 画像解析を実行
        try:
            print("→ GPT-4o に属性解析を依頼中 …")
            analysis_result = analyze_with_gpt4o(filename)
            print("=== 解析結果 ===")
            print(analysis_result)
            print("================")
            
            # 解析結果が辞書形式かどうか確認
            if isinstance(analysis_result, dict):
                return analysis_result
            else:
                return {"error": "解析結果の形式が不正です", "raw_result": str(analysis_result)}
                
        except Exception as e:
            error_msg = f"解析エラー: {str(e)}"
            print("GPT-4o 呼び出しエラー:", e)
            return {"error": error_msg}
    else:
        print("カメラから画像を取得できませんでした")
        return {"error": "カメラエラー"}
'''
def capture_and_analyze(table_id=None):
    """写真を撮影し、GPT-4oで解析する"""
    ret, frame = camera.read()
    if ret:
        filename = f"dataset/photo_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        print(f"写真を保存しました: {filename}")
        try:
            print("→ GPT-4o に属性解析を依頼中 …")
            analysis_result = analyze_with_gpt4o(filename, table_id)
            print("=== 解析結果 ===")
            print(analysis_result)
            print("================")
            if isinstance(analysis_result, dict):
                return analysis_result
            else:
                return {"error": "解析結果の形式が不正です", "raw_result": str(analysis_result)}
        except Exception as e:
            error_msg = f"解析エラー: {str(e)}"
            print("GPT-4o 呼び出しエラー:", e)
            return {"error": error_msg}
    else:
        print("カメラから画像を取得できませんでした")
        return {"error": "カメラエラー"}


# --- Flaskアプリ2つを同時起動 ---
def run_customer():
    try:
        app.run(debug=False, host="0.0.0.0", port=5001)
    finally:
        camera.release()

def run_staff():
    staff_app.run(debug=False, host="0.0.0.0", port=5002)

if __name__ == "__main__":
    t1 = threading.Thread(target=run_customer)
    t2 = threading.Thread(target=run_staff)
    t1.start()
    t2.start()
    t1.join()
    t2.join()







# アクセスできるURL： 
# http://127.0.0.1:5001  # お客様用アプリ
# http://127.0.0.1:5002  # 店員用アプリ