from flask import Flask, render_template, request, redirect, url_for, session
import cv2
import os
import time
import threading

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

def capture_and_save():
    ret, frame = camera.read()
    if ret:
        filename = f"dataset/photo_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        print(f"写真を保存しました: {filename}")
    else:
        print("カメラから画像を取得できませんでした")

@app.route("/", methods=["GET", "POST"])
def select_people():
    if request.method == "POST":
        # 人数ボタンが押された瞬間に写真を撮影
        capture_and_save()
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
        return redirect(url_for("show_result"))
    return render_template("select_people_design.html")

@app.route("/result")
def show_result():
    seat_type = session.get("seat_type")
    available_table_id = session.get("available_table_id")
    return render_template("result.html", seat_type=seat_type, available_table_id=available_table_id)

if __name__ == "__main__":
    try:
        app.run(debug=True, host="0.0.0.0", port=5001)
    finally:
        camera.release()



'''
from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)
app.secret_key = "your_secret_key"  # セッション用の秘密鍵を追加

# テーブル情報のリスト（辞書のリスト）
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









@app.route("/", methods=["GET", "POST"])
def select_people():
    if request.method == "POST":
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
        # セッションに保存
        session["seat_type"] = seat_type
        session["available_table_id"] = available_table_id
        return redirect(url_for("show_result"))
    #return render_template("select_people_design.html")
    return render_template("camera.html")

@app.route("/result")
def show_result():
    seat_type = session.get("seat_type")
    available_table_id = session.get("available_table_id")
    return render_template("result.html", seat_type=seat_type, available_table_id=available_table_id)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
'''





# アクセスできるURL： http://127.0.0.1:5001