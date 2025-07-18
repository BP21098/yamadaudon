# セットアップガイド

## 必要なパッケージのインストール

以下のコマンドでパッケージをインストールできます：

```bash
pip install -r requirements.txt
```

## 環境設定

1. `.env`ファイルにOpenAI APIキーを設定してください：
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

2. カメラが接続されていることを確認してください。

## アプリケーションの実行

### 店員用ダッシュボード
```bash
python web/testMain.py
```

### メインアプリケーション
```bash
python web/main.py
```

## 使用されているパッケージ

- **Flask**: Webアプリケーションフレームワーク
- **opencv-python**: カメラ機能とコンピュータビジョン
- **openai**: GPT-4oによる画像解析
- **python-dotenv**: 環境変数管理
- **pandas**: CSV データ処理

## 注意事項

- カメラが認識されない場合は、デバイスマネージャーでカメラドライバを確認してください
- OpenAI APIキーは有効なものを設定する必要があります
- `analysis_results`と`dataset`ディレクトリは自動作成されます
