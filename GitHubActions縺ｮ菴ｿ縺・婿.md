# GitHub Actionsで自動ビルドする完全ガイド

## 概要

GitHub Actionsを使うと、コードをGitHubにアップロードするだけで、**Windows、Mac、Linux用の実行ファイルが自動的にビルド**されます。

## 前提条件

- ✅ GitHubアカウントを持っている
- ✅ Gitがインストールされている（[ダウンロード](https://git-scm.com/)）

Gitがインストールされているか確認：
```bash
git --version
```

## 手順1: GitHubでリポジトリを作成

### 1-1. GitHubにログイン

[GitHub](https://github.com/) にアクセスしてログイン

### 1-2. 新しいリポジトリを作成

1. 右上の「+」→「New repository」をクリック
2. 以下を入力：
   - **Repository name**: `real-estate-scraper`（任意の名前）
   - **Description**: `不動産スクレイピングツール`（任意）
   - **Public** を選択（無料でGitHub Actionsを使うため）
   - ✅ **Add a README file** のチェックは**外す**
3. 「Create repository」をクリック

### 1-3. リポジトリのURLをコピー

作成されたページに表示される以下のようなURLをコピー：
```
https://github.com/YOUR_USERNAME/real-estate-scraper.git
```

## 手順2: コードをアップロード

### 2-1. プロジェクトフォルダに移動

コマンドプロンプト（Windows）またはターミナル（Mac/Linux）で、プロジェクトフォルダに移動：

```bash
cd C:\Users\YOUR_NAME\Desktop\プロジェクトフォルダ
```

プロジェクトフォルダには以下のファイルが必要です：
```
プロジェクトフォルダ/
├── .github/
│   └── workflows/
│       └── build.yml
├── scraper_gui.py
├── requirements.txt
├── README.md
└── .gitignore
```

### 2-2. Gitの初期設定（初回のみ）

初めてGitを使う場合、以下を実行：

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2-3. Gitリポジトリを初期化

```bash
git init
```

### 2-4. ファイルをステージング

```bash
git add .
```

これで、すべてのファイルがGitの管理下に追加されます。

### 2-5. コミット

```bash
git commit -m "Initial commit"
```

### 2-6. リモートリポジトリを追加

手順1-3でコピーしたURLを使用：

```bash
git remote add origin https://github.com/YOUR_USERNAME/real-estate-scraper.git
```

**YOUR_USERNAME** を自分のGitHubユーザー名に置き換えてください。

### 2-7. ブランチ名を変更（必要に応じて）

```bash
git branch -M main
```

### 2-8. プッシュ（アップロード）

```bash
git push -u origin main
```

初回は、GitHubのユーザー名とパスワード（またはトークン）の入力を求められます。

**注意:** パスワード認証は廃止されているため、**Personal Access Token**を使用する必要があります。

#### Personal Access Tokenの作成方法

1. GitHub → 右上のアイコン → Settings
2. 左メニュー → Developer settings → Personal access tokens → Tokens (classic)
3. 「Generate new token」→「Generate new token (classic)」
4. 以下を設定：
   - **Note**: `Git操作用`（任意の名前）
   - **Expiration**: `90 days`（有効期限）
   - **Select scopes**: ✅ `repo`（すべてにチェック）
5. 「Generate token」をクリック
6. 表示されたトークンをコピー（**このページを閉じると二度と表示されません**）

プッシュ時のパスワード入力で、このトークンを貼り付けます。

## 手順3: GitHub Actionsの実行を確認

### 3-1. GitHubのリポジトリページを開く

ブラウザで以下にアクセス：
```
https://github.com/YOUR_USERNAME/real-estate-scraper
```

### 3-2. Actionsタブを開く

上部メニューの「Actions」をクリック

### 3-3. ビルドの実行を確認

「Build Executables」というワークフローが実行されているはずです。

- 🟡 **黄色（実行中）**: ビルド中
- 🟢 **緑（成功）**: ビルド成功
- 🔴 **赤（失敗）**: ビルド失敗

ビルドには **5〜10分** かかります。

### 3-4. ビルドが完了するまで待つ

すべてのジョブ（Windows、macOS、Linux）が緑色になるまで待ちます。

## 手順4: 実行ファイルをダウンロード

### 4-1. 完了したワークフローをクリック

Actionsタブで、完了した「Build Executables」をクリック

### 4-2. Artifactsセクションを確認

ページ下部の「Artifacts」セクションに、以下の3つのファイルが表示されます：

- **Windows** - Windows用実行ファイル
- **macOS** - Mac用実行ファイル
- **Linux** - Linux用実行ファイル

### 4-3. ダウンロード

必要なファイルをクリックしてダウンロード（ZIPファイル）

### 4-4. 解凍

ダウンロードしたZIPファイルを解凍すると、実行ファイルが入っています：

- **Windows**: `不動産スクレイパー.exe`
- **macOS**: `不動産スクレイパー`
- **Linux**: `不動産スクレイパー`

## 手順5: 配布

解凍した実行ファイルを配布すれば完了です！

## コードを更新した場合

コードを修正した場合、以下の手順で再度ビルドできます：

```bash
# 変更をステージング
git add .

# コミット
git commit -m "修正内容の説明"

# プッシュ
git push
```

プッシュすると、自動的にGitHub Actionsが実行され、新しい実行ファイルがビルドされます。

## トラブルシューティング

### ビルドが失敗する（赤色）

1. Actionsタブで失敗したワークフローをクリック
2. 失敗したジョブ（Windows/macOS/Linux）をクリック
3. エラーメッセージを確認

よくあるエラー：
- **ファイルが見つからない**: `scraper_gui.py` がアップロードされているか確認
- **依存関係のエラー**: `requirements.txt` が正しいか確認

### プッシュできない

**エラー例:**
```
remote: Support for password authentication was removed
```

**解決方法:** Personal Access Tokenを使用してください（手順2-8参照）

### Actionsタブが表示されない

リポジトリが **Public** になっているか確認してください。Private リポジトリの場合、無料プランではGitHub Actionsの利用時間に制限があります。

## まとめ

1. ✅ GitHubでリポジトリを作成
2. ✅ コードをアップロード（`git push`）
3. ✅ GitHub Actionsが自動実行
4. ✅ 実行ファイルをダウンロード
5. ✅ 配布

これで、Mac環境がなくてもMac用の実行ファイルが作成できます！

## 参考リンク

- [GitHub公式ドキュメント](https://docs.github.com/ja)
- [Git入門](https://git-scm.com/book/ja/v2)
- [GitHub Actions公式ドキュメント](https://docs.github.com/ja/actions)

