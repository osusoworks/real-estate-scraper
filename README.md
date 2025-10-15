# 不動産スクレイピングツール

不動産サイトから物件情報と画像を自動的に取得するGUIアプリケーションです。

## 機能

- ✅ 物件情報の自動取得（価格、間取り、所在地など）
- ✅ 物件画像の自動ダウンロード
- ✅ CSV/JSON形式でデータ出力
- ✅ 使いやすいGUIインターフェース
- ✅ リアルタイム進捗表示

## ダウンロード

[Releases](../../releases) ページから、お使いのOSに対応した実行ファイルをダウンロードしてください。

- **Windows**: `不動産スクレイパー.exe`
- **macOS**: `不動産スクレイパー`
- **Linux**: `不動産スクレイパー`

## 使い方

### 実行ファイル版

1. ダウンロードした実行ファイルをダブルクリック
2. GUIウィンドウが開く
3. 取得件数を入力（デフォルト: 15件）
4. 「スクレイピング開始」ボタンをクリック
5. 完了後、以下のファイルが生成される：
   - `export.csv` - 物件情報（Excel対応）
   - `export.json` - 物件情報（JSON形式）
   - `images/` - 物件画像フォルダ

### Pythonスクリプト版

```bash
# 必要なライブラリをインストール
pip install -r requirements.txt

# アプリを起動
python scraper_gui.py
```

## 開発

### 必要な環境

- Python 3.11以上
- pip

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# 依存関係をインストール
pip install -r requirements.txt

# アプリを起動
python scraper_gui.py
```

### 実行ファイルのビルド

```bash
# PyInstallerをインストール
pip install pyinstaller

# ビルド実行
pyinstaller --onefile --windowed --name "不動産スクレイパー" scraper_gui.py
```

生成された実行ファイルは `dist/` フォルダ内にあります。

## 自動ビルド

GitHub Actionsを使用して、Windows/macOS/Linux用の実行ファイルを自動的にビルドします。

コードをpushすると、自動的にビルドが実行され、Actionsタブからダウンロードできます。

## ライセンス

MIT License

## 注意事項

- インターネット接続が必要です
- スクレイピング対象サイトの利用規約を確認してください
- サーバーに負荷をかけないよう、適切な間隔でアクセスしています

