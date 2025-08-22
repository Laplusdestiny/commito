# encoding: utf-8
"""
commito.py

"""

import json
import subprocess
import sys
import urllib.request
import argparse
import tomllib
from pathlib import Path

def _load_config():
    """
    同じディレクトリにある config.yaml を読み込み、設定を返す。
    ファイルが存在しない場合はデフォルト値を返す。
    """
    config_path = Path.home() / ".config/commito/commito.toml"
    if config_path.is_file():
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
    else:
        config = {
            "ollama_api_url": "http://127.0.0.1:11434/api/chat",
            "model_name": "gpt-oss:20b",
        }

    global OLLAMA_API_URL, MODEL_NAME
    OLLAMA_API_URL = config.get("ollama_api_url", "http://127.0.0.1:11434/api/chat")
    MODEL_NAME = config.get("model_name", "gpt-oss:20b")

def run_git_diff(staged: bool = False) -> str:
    """
    Git の差分を取得する関数。

    Parameters
    ----------
    staged : bool
        True の場合、ステージ済みの差分（--staged）を取得。

    Returns
    -------
    str
        Git diff の結果（文字列）。
    """
    cmd = ["git", "diff", "--staged"] if staged else ["git", "diff"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("git diff の取得に失敗しました。", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def generate_commit_message(diff_text: str) -> str:
    """
    Ollama API を使ってコミットメッセージを生成する関数。

    Parameters
    ----------
    diff_text : str
        Git の差分テキスト。

    Returns
    -------
    str
        生成されたコミットメッセージ。
    """
    system_prompt = (
        "あなたは優れたソフトウェアエンジニアです。"
        "以下の Git diff から、Conventional Commits に準拠した簡潔なコミットメッセージを日本語で作成してください。\n"
        "- 1行目は <type>: <subject>（72文字以内）\n"
        "- 2行目は空行\n"
        "- 3行目以降に詳細な説明（必要なら箇条書き）\n"
    )

    user_prompt = f"以下の差分を要約してコミットメッセージを作成してください:\n```\n{diff_text}\n```"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }

    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("message", {}).get("content", "").strip()
    except Exception as e:
        print(f"Ollama API 呼び出しに失敗しました: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    CLI エントリーポイント。
    """
    _load_config()
    parser = argparse.ArgumentParser(description="Git diff からコミットメッセージを生成（Ollama 使用）")
    parser.add_argument("--staged", action="store_true", help="ステージ済みの差分を対象にする")
    args = parser.parse_args()

    diff_text = run_git_diff(staged=args.staged)
    if not diff_text:
        print("差分がありません。", file=sys.stderr)
        sys.exit(0)

    message = generate_commit_message(diff_text)
    print("\n=== 生成されたコミットメッセージ ===\n")
    print(message)


if __name__ == "__main__":
    main()
