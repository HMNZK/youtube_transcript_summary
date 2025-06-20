#!/usr/bin/env python3
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound, 
    VideoUnavailable,
    YouTubeRequestFailed
)

# バージョン互換性のためのエラークラス定義
try:
    from youtube_transcript_api._errors import RequestBlocked, IpBlocked
except ImportError:
    # 古いバージョンでは存在しないエラークラス
    class RequestBlocked(Exception):
        pass
    
    class IpBlocked(Exception):
        pass

import subprocess
import re
import sys
import time
import random
from urllib.parse import urlparse

def extract_video_id(url):
    """YouTubeのURLから動画IDを抽出"""
    pattern = r'(?:v=|\/|embed\/|watch\?v=|youtu\.be\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def clean_transcript(text):
    """字幕テキストをクリーニング"""
    text = re.sub(r'\[.*?\]', '', text)  # [音楽]などの効果音表記を削除
    text = re.sub(r'♪+', '', text)       # 音符記号を削除
    text = re.sub(r'\s+', '', text)       # 空白文字を削除
    return text.strip()

def copy_to_clipboard(text):
    """MacOSのクリップボードにテキストをコピー"""
    try:
        process = subprocess.Popen(
            'pbcopy', 
            env={'LANG': 'ja_JP.UTF-8'},
            stdin=subprocess.PIPE
        )
        process.communicate(text.encode('utf-8'))
        return True
    except Exception as e:
        print(f"クリップボードへのコピーに失敗しました: {str(e)}")
        return False

def get_video_transcript_with_retry(video_id, max_retries=3):
    """
    字幕を取得する関数（リトライ機能付き、新旧API対応）
    """
    for attempt in range(max_retries):
        try:
            print(f"字幕を取得中... (試行 {attempt + 1}/{max_retries})")
            
            # 新しいAPI (1.1.0+) を試す
            try:
                api = YouTubeTranscriptApi()
                
                # 言語優先順位: 日本語 > 英語
                languages = ['ja', 'en']
                
                for lang in languages:
                    try:
                        fetched_transcript = api.fetch(video_id, languages=[lang])
                        
                        print(f"字幕言語: {fetched_transcript.language} ({fetched_transcript.language_code})")
                        print(f"字幕タイプ: {'自動生成' if fetched_transcript.is_generated else '手動作成'}")
                        
                        # 字幕テキストを結合
                        full_text = ''.join(
                            clean_transcript(snippet.text)
                            for snippet in fetched_transcript.snippets
                            if clean_transcript(snippet.text)
                        )
                        
                        if full_text.strip():
                            return full_text
                            
                    except NoTranscriptFound:
                        continue
                
                # 他の言語も試す
                try:
                    fetched_transcript = api.fetch(video_id)
                    print(f"字幕言語: {fetched_transcript.language} ({fetched_transcript.language_code})")
                    print(f"字幕タイプ: {'自動生成' if fetched_transcript.is_generated else '手動作成'}")
                    
                    full_text = ''.join(
                        clean_transcript(snippet.text)
                        for snippet in fetched_transcript.snippets
                        if clean_transcript(snippet.text)
                    )
                    
                    if full_text.strip():
                        return full_text
                        
                except Exception:
                    pass
                    
            except Exception as new_api_error:
                print(f"新API失敗、旧APIにフォールバック: {str(new_api_error)}")
                
                # 旧APIにフォールバック
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # 利用可能な字幕言語を表示
                available_languages = []
                for transcript in transcript_list:
                    lang_info = f"{transcript.language} ({transcript.language_code})"
                    if transcript.is_generated:
                        lang_info += " [自動生成]"
                    else:
                        lang_info += " [手動作成]"
                    available_languages.append(lang_info)
                
                print(f"利用可能な字幕: {', '.join(available_languages)}")
                
                # 字幕を取得（優先順位: 日本語手動 > 英語手動 > 日本語自動 > 英語自動）
                transcript = None
                transcript_type = ""
                
                try:
                    # 手動作成字幕を優先
                    transcript = transcript_list.find_transcript(['ja', 'en'])
                    transcript_type = "手動作成"
                except NoTranscriptFound:
                    try:
                        # 自動生成字幕を取得
                        transcript = transcript_list.find_generated_transcript(['ja', 'en'])
                        transcript_type = "自動生成"
                    except NoTranscriptFound:
                        # 他の言語も試す
                        for t in transcript_list:
                            transcript = t
                            transcript_type = "自動生成" if t.is_generated else "手動作成"
                            break
                
                if not transcript:
                    raise NoTranscriptFound(video_id, [], [])
                
                print(f"字幕言語: {transcript.language} ({transcript.language_code}) - {transcript_type}")
                
                # 字幕テキストを取得
                transcript_data = transcript.fetch()
                
                if not transcript_data:
                    raise Exception("字幕データが空です")
                
                # 字幕テキストを結合
                full_text = ''.join(
                    clean_transcript(tr['text'])
                    for tr in transcript_data
                    if clean_transcript(tr['text'])
                )
                
                if not full_text.strip():
                    raise Exception("有効な字幕テキストが見つかりませんでした")
                
                return full_text
            
            raise Exception("有効な字幕テキストが見つかりませんでした")
            
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
            raise e  # これらのエラーはリトライしない
            
        except (RequestBlocked, IpBlocked) as e:
            print(f"試行 {attempt + 1} 失敗: リクエストがブロックされました ({type(e).__name__})")
            print("IP制限が発生している可能性があります。プロキシの使用を検討してください。")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5 + random.uniform(1, 3)
                print(f"{wait_time:.1f}秒待機してリトライします...")
                time.sleep(wait_time)
                continue
                
        except YouTubeRequestFailed as e:
            print(f"試行 {attempt + 1} 失敗: YouTubeリクエストが失敗しました")
            print("ネットワーク問題またはレート制限が発生している可能性があります。")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10 + random.uniform(2, 5)
                print(f"{wait_time:.1f}秒待機してリトライします...")
                time.sleep(wait_time)
                continue
                
        except Exception as e:
            error_msg = str(e)
            print(f"試行 {attempt + 1} 失敗: {error_msg}")
            
            # XMLパースエラーの場合の特別な処理
            if "no element found" in error_msg.lower() or "xml" in error_msg.lower():
                print("XMLパースエラーが発生しました。これは以下の原因が考えられます:")
                print("- YouTube側の一時的な制限")
                print("- IP制限（クラウドプロバイダーのIPからのアクセス）")
                print("- ネットワーク接続の問題")
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3 + random.uniform(1, 2)
                    print(f"{wait_time:.1f}秒待機してリトライします...")
                    time.sleep(wait_time)
                    continue
    
    return None

def get_video_transcript(video_id, proxy_config=None, max_retries=3):
    """
    字幕を取得する関数（プロキシサポート付き）
    """
    try:
        transcript = get_video_transcript_with_retry(video_id, max_retries)
        
        if transcript:
            if copy_to_clipboard(transcript):
                print("字幕テキストをクリップボードにコピーしました。")
            return transcript
        else:
            raise Exception("字幕の取得に失敗しました")
            
    except TranscriptsDisabled:
        print(f"エラー: この動画では字幕が無効になっています (動画ID: {video_id})")
        print("解決方法: 字幕が有効な別の動画を試してください")
        
        # GitHub issuesの情報を参考に追加の解決方法を提示
        print("\n追加の解決方法:")
        print("- この問題はクラウドマシン（AWS、GCP、Azure等）で頻繁に発生します")
        print("- ローカル環境では動作する可能性があります")
        print("- 住宅用プロキシまたはVPNの使用を検討してください")
        sys.exit(1)
        
    except NoTranscriptFound:
        print(f"エラー: この動画には字幕が見つかりませんでした (動画ID: {video_id})")
        print("解決方法: 字幕が存在する別の動画を試してください")
        sys.exit(1)
        
    except VideoUnavailable:
        print(f"エラー: 動画が利用できません (動画ID: {video_id})")
        print("解決方法: 動画URLが正しいか確認し、公開されている動画を試してください")
        sys.exit(1)
        
    except Exception as e:
        error_msg = str(e)
        print(f"最終エラー: {error_msg}")
        print("\n解決方法:")
        print("1. インターネット接続を確認してください")
        print("2. しばらく時間をおいてから再試行してください")
        print("3. 別の動画で試してみてください")
        print("4. youtube-transcript-apiライブラリを最新版に更新してください:")
        print("   pip install --upgrade youtube-transcript-api")
        print("5. IP制限が疑われる場合は、プロキシの使用を検討してください")
        sys.exit(1)

def print_usage():
    """使用方法を表示"""
    print("YouTube字幕取得スクリプト")
    print("使用方法: python main.py 'YouTube_URL' [--proxy PROXY_URL]")
    print("\n例:")
    print("  python main.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'")
    print("  python main.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' --proxy 'http://proxy.example.com:8080'")
    print("\n対応URL形式:")
    print("  - https://www.youtube.com/watch?v=VIDEO_ID")
    print("  - https://youtu.be/VIDEO_ID")
    print("  - https://www.youtube.com/embed/VIDEO_ID")

if __name__ == "__main__":
    try:
        # コマンドライン引数の解析
        if len(sys.argv) < 2:
            print_usage()
            sys.exit(1)
        
        youtube_url = sys.argv[1]
        proxy_config = None
        
        # プロキシ設定の確認
        if len(sys.argv) > 3 and sys.argv[2] == '--proxy':
            proxy_url = sys.argv[3]
            print(f"プロキシを使用: {proxy_url}")
            # プロキシ設定は新APIでサポート予定
            # 現在は警告のみ表示
            print("注意: プロキシサポートは開発中です")
        
        if video_id := extract_video_id(youtube_url):
            print(f"動画ID: {video_id}")
            print(f"動画URL: {youtube_url}")
            
            transcript = get_video_transcript(video_id, proxy_config)
            
            print("\n処理結果:")
            print(f"字幕テキスト長: {len(transcript)}文字")
            print("=" * 50)
            print(transcript[:500] + "..." if len(transcript) > 500 else transcript)
        else:
            print("エラー: 有効なYouTube URLではありません")
            print_usage()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n処理を中断しました")
        sys.exit(0)
    except Exception as e:
        print(f"予期しないエラーが発生しました: {str(e)}")
        sys.exit(1)