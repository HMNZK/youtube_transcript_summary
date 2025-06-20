#!/bin/bash

# スクリプトのディレクトリに移動
cd "/Users/ryosuke/projects/python/youtube_transcript_summary"

# 仮想環境を有効化
source venv/bin/activate

# 引数をmain.pyに渡して実行
python main.py "$@" 