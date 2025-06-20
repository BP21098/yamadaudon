from flask import Flask, render_template, request, redirect, url_for, session
import cv2
import os
import time
import threading
from personAttrCapture import analyze_with_gpt4o  # 解析機能をインポート

app = Flask(__name__)
app.secret_key = "your_secret_key"

# テーブル情報
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


@app.route("/", methods=["GET", "POST"])
def select_people():
    if request.method == "POST":
        # 人数ボタンが押された瞬間に写真を撮影・解析
        analysis_result = capture_and_analyze()
        
        people = int(request.form.get("people", 0))
        if people in [1, 2]:
            seat_type = "カウンター"
        elif people in [3, 4]:
            seat_type = "テーブル"
        else:
            seat_type = "該当なし"
            
        available_table_id = None
        for table in tables:
            if table["type"] == seat_type and table["is_available"]:
                available_table_id = table["id"]
                table["is_available"] = False
                break
                
        session["seat_type"] = seat_type
        session["available_table_id"] = available_table_id
        session["analysis_result"] = analysis_result  # 解析結果をセッションに保存
        return redirect(url_for("show_result"))
    return render_template("select_people_design.html")

@app.route("/result")
def show_result():
    seat_type = session.get("seat_type")
    available_table_id = session.get("available_table_id")
    analysis_result = session.get("analysis_result", "解析結果なし")
    return render_template("result.html", 
                         seat_type=seat_type, 
                         available_table_id=available_table_id,
                         analysis_result=analysis_result)

if __name__ == "__main__":
    try:
        app.run(debug=True, host="0.0.0.0", port=5001)
    finally:
        camera.release()