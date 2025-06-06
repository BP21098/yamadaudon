import cv2, os, base64, platform
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを取得
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_with_gpt4o(image_path: str) -> str:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "画像に写っている男性、女性、子供の人数だけを教えてください。"},
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
    return resp.choices[0].message.content.strip()

def capture_and_analyze(device_index=0,
                        output_dir="captures",
                        key_save="c",
                        key_quit="q"):
    system = platform.system()
    if system == "Windows":
        cap = cv2.VideoCapture(device_index, cv2.CAP_DSHOW)
    elif system == "Darwin":
        cap = cv2.VideoCapture(device_index, cv2.CAP_AVFOUNDATION)
    else:
        cap = cv2.VideoCapture(device_index)

    if not cap.isOpened():
        print(f"カメラを開けませんでした (OS={system}, index={device_index})")
        return

    os.makedirs(output_dir, exist_ok=True)
    cv2.namedWindow("Camera")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("フレーム取得に失敗しました")
            break

        cv2.imshow("Camera", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(key_save):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(output_dir, f"cap_{ts}.jpg")
            cv2.imwrite(path, frame)
            print(f"[Saved] {path}")

            try:
                print("→ GPT-4o に属性解析を依頼中 …")
                print("=== 解析結果 ===")
                print(analyze_with_gpt4o(path))
                print("================")
            except Exception as e:
                print("GPT-4o 呼び出しエラー:", e)

        elif key == ord(key_quit):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # 必要に応じて index を変える
    capture_and_analyze(device_index=0)
