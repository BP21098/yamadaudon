from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def select_people():
    return render_template("select_people.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)

# アクセスできるURL： http://127.0.0.1:5001