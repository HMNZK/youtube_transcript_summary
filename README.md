# YouTube字幕取得スクリプト

YouTubeの動画から字幕を取得し、クリップボードにコピーするPythonスクリプトです。

## 機能

- YouTubeのURLから動画IDを自動抽出（複数のURL形式に対応）
- 手動作成字幕と自動生成字幕の両方に対応
- 日本語と英語の字幕を優先的に取得
- 字幕テキストの自動クリーニング（効果音表記や音符記号の除去）
- MacOSのクリップボードへの自動コピー
- **新機能**: youtube-transcript-api 1.1.0の新APIに対応
- **新機能**: IP制限・レート制限への対応強化
- **新機能**: プロキシサポート（開発中）
- **新機能**: より詳細なエラーハンドリングと解決方法の提示

## 必要な環境

- Python 3.8以上
- macOS（pbcopyコマンドを使用）

## インストール

1. リポジトリをクローンまたはダウンロード
```bash
git clone <repository-url>
cd youtube_transcript_summary
```

2. 必要なパッケージをインストール
```bash
pip install youtube-transcript-api
```

## 使用方法

### 基本的な使用方法

```bash
python main.py "YouTube_URL"
```

### プロキシを使用する場合（IP制限回避）

```bash
python main.py "YouTube_URL" --proxy "http://proxy.example.com:8080"
```

### 実行例

```bash
# 基本的な使用
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# プロキシを使用（開発中）
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --proxy "http://proxy.example.com:8080"
```

### 対応URL形式

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## 出力例

```
字幕言語: ja (手動作成)
字幕テキストをクリップボードにコピーしました。

処理結果:
こんにちは今日はYouTubeの使い方について説明します...
```

## 対応する字幕形式

1. **手動作成字幕**（優先）
   - 日本語 (ja)
   - 英語 (en)

2. **自動生成字幕**（手動作成が利用できない場合）
   - 日本語 (ja)
   - 英語 (en)

## 字幕テキストのクリーニング機能

- `[音楽]`、`[拍手]`などの効果音表記を削除
- `♪`記号を削除
- 余分な空白文字を削除

## エラーハンドリング

- 無効なYouTube URLの検出
- 字幕が利用できない動画の処理
- クリップボードへのコピー失敗時の通知
- ネットワークエラーの処理

## 注意事項

- このスクリプトはmacOS専用です（pbcopyコマンドを使用）
- 字幕が利用できない動画では実行できません
- **2024年以降、IP制限が強化されています**（特にクラウドプロバイダーIP）
- YouTube APIの利用制限に注意してください
- プロキシ使用時は、プロバイダーの利用規約も確認してください

## トラブルシューティング

### よくあるエラー

1. **"no element found: line 1, column 0"**
   - XMLパースエラー（最も一般的）
   - YouTube側の一時的な制限
   - IP制限（クラウドプロバイダーのIPからのアクセス）
   - ネットワーク接続の問題
   - 動画の字幕データの問題

2. **"リクエストがブロックされました (RequestBlocked/IpBlocked)"**
   - IP制限が発生している
   - クラウドプロバイダー（AWS、GCP、Azure等）のIPからのアクセス
   - 住宅用プロキシの使用が推奨

3. **"YouTubeリクエストが失敗しました"**
   - ネットワーク問題またはレート制限
   - YouTube側の一時的な制限
   - 自動的に待機時間を設けてリトライ

4. **"この動画では字幕が無効になっています"**
   - 動画の投稿者が字幕を無効にしている
   - プライベート動画や制限付き動画

5. **"この動画には字幕が見つかりませんでした"**
   - 動画に字幕が存在しない
   - 対応言語（日本語・英語）の字幕がない

6. **"有効なYouTube URLではありません"**
   - URLの形式が正しくない
   - 動画IDが11文字でない

7. **"クリップボードへのコピーに失敗しました"**
   - pbcopyコマンドが利用できない
   - システムの権限問題

### 解決方法

#### XMLパースエラーの場合
- スクリプトは自動的に3回リトライします（ランダムな待機時間付き）
- 数秒間隔をあけて再実行してください
- youtube-transcript-apiライブラリを最新版に更新：
  ```bash
  pip install --upgrade youtube-transcript-api
  ```
- 他の動画で試してみてください

#### IP制限・レート制限の場合
- **住宅用プロキシの使用**（推奨）：
  ```bash
  python main.py "YouTube_URL" --proxy "http://residential-proxy.com:8080"
  ```
- **VPNの使用**：住宅用IPアドレスに変更
- **時間をおいて再実行**：制限が解除されるまで待機
- **複数のIPアドレスでのローテーション**（大規模利用の場合）

#### ライブラリの更新
```bash
# 最新版への更新
pip install --upgrade youtube-transcript-api

# 特定バージョンの指定
pip install youtube-transcript-api==1.1.0
```

#### その他の問題
- インターネット接続を確認
- YouTube URLの形式を確認
- Pythonのバージョンを確認（3.8以上）
- 別の動画で試してみる

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能改善の提案は、GitHubのIssuesでお知らせください。 