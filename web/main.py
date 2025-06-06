from flask import Flask, render_template, request

app = Flask(__name__)

# テーブル情報のリスト（辞書のリスト）
tables = [
    {"id": 1, "type": "カウンター", "is_available": True},
    {"id": 2, "type": "テーブル", "is_available": True},
    {"id": 3, "type": "テーブル", "is_available": True},
    # ...他の卓
]

@app.route("/", methods=["GET", "POST"])
def select_people():
    seat_type = None
    available_table_id = None
    if request.method == "POST":
        people = int(request.form.get("people", 0))
        if people in [1, 2]:
            seat_type = "カウンター"
        elif people in [3, 4]:
            seat_type = "テーブル"
        else:
            seat_type = "該当なし"
        # 空いている席を検索
        for table in tables:
            if table["type"] == seat_type and table["is_available"]:
                available_table_id = table["id"]
                table["is_available"] = False
                break
    return render_template("select_people.html", seat_type=seat_type, available_table_id=available_table_id)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

# アクセスできるURL： http://127.0.0.1:5001