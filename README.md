# commito

**commito** は、Git の差分を自動で解析し、Ollama を使って Conventional Commits に沿ったコミットメッセージを生成する CLI ツールです。
Python 3.11 以降で動作します。

---

## 1. 目的

- 手作業でコミットメッセージを書く手間を省く
- 一貫したコミットメッセージ（Conventional Commits）を保つ
- 日本語の説明を含むコミットメッセージを簡潔に生成

---

## 2. 依存関係

| ライブラリ | バージョン | インストール方法 |
|------------|------------|-----------------|
| **toml**   | 任意       | `pip install toml`（Python 3.11 以前） |
| **tomllib**| Python 3.11+ |  標準ライブラリで利用可 |

> **注意**
> Python 3.11 以上では `tomllib` が標準で入っています。
> それ以前のバージョンを使う場合は `toml` パッケージが必要です。

---

## 3. インストール

```bash
# 1. コードを取得
git clone https://github.com/Laplusdestiny/commito.git
cd commito

# 2. 依存関係をインストール
pip install toml
```

> 既に `tomllib` がある場合は `pip install toml` は不要です。

---

## 4. 設定ファイル

`commito` は `~/.config/commito/commito.toml` から設定を読み込みます。
ファイルが存在しない場合は自動でデフォルト値で作成されます。

```toml
# ~/.config/commito/commito.toml
ollama_api_url = "http://endpoint_url:11434/api/chat"
model_name     = "gpt-oss:20b"
```

- `ollama_api_url`: Ollama のチャット API エンドポイント
- `model_name`: 使用するモデル名（例: `gpt-oss:20b`）

---

## 5. 使い方

```bash
# 現在のリポジトリで
python src/commito/commito.py [--staged]
```

- `--staged` オプションを付けると、**ステージ済み**の差分だけを対象にします。
- オプション無しの場合は **現在の作業ツリー**の差分を使用します。

### 例

```bash
# 作業ツリーの差分からコミットメッセージを生成
python src/commito/commito.py

# ステージ済みの差分から生成
python src/commito/commito.py --staged
```

出力例:

```
=== 生成されたコミットメッセージ ===

feat: ユーザー登録機能を追加

- ユーザー情報の取得・登録処理を実装
- バリデーションを追加
- テストを更新
```

---

## 6. 仕組み

1. **差分取得**
   `git diff`（または `git diff --staged`）で差分を取得。

2. **プロンプト生成**
   *system_prompt* で「Conventional Commits」形式を明示し、
   *user_prompt* に差分を埋め込みます。

3. **Ollama API 呼び出し**
   POST で `/api/chat` にリクエストし、返却されたメッセージを取得。

4. **結果表示**
   生成したコミットメッセージを標準出力に表示。

---

## 7. カスタマイズ

- **プロンプト変更**
  `commito.py` 内の `system_prompt` を編集して、要望に合わせてプロンプトを調整できます。

- **ローカルモデル使用**
  `commito.toml` の `ollama_api_url` をローカルサーバーに合わせて変更。

- **Python 3.10 以下で実行**
  `tomllib` が無いので、`toml` パッケージをインストールし、`tomllib` を `toml` に置き換えてください。

---

## 8. トラブルシューティング

| 症状 | 原因 | 対応 |
|------|------|------|
|  `Ollama API 呼び出しに失敗しました` | ネットワーク、API URL が間違っている | `commito.toml` を確認、`curl` でエンドポイントが通るか試す |
|  `git diff の取得に失敗しました` | Git がインストールされていない、リポジトリでない | Git をインストール、正しいディレクトリで実行 |
|  `config.toml が作成されない` | 書き込み権限が無い | `~/.config/commito/` の権限を確認 |

---

## 9. 貢献

1. Fork → `git clone`
2. `git checkout -b feature/xyz`
3. コードを修正/追加
4. Pull Request を送信

---

## 10. ライセンス

MIT License © 2025 Laplusdestiny

---