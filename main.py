from youtube_transcript_api import YouTubeTranscriptApi
import pyperclip
import re
import sys

def extract_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'  # YouTubeのビデオID抽出パターン
    match = re.search(pattern, url)
    return match.group(1) if match else None

def clean_transcript(text):
    text = re.sub(r'\[.*?\]', '', text)  # [音楽]などの効果音表記を削除
    text = re.sub(r'♪+', '', text)       # 音符記号を削除
    text = re.sub(r'\s+', '', text)       # 空白文字を削除
    return text.strip()

def get_video_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    
    try:
        transcript = transcript_list.find_transcript(['en', 'ja'])
        transcript_type = "手動作成"
    except:
        transcript = transcript_list.find_generated_transcript(['en', 'ja'])
        transcript_type = "自動生成"
    
    print(f"字幕言語: {transcript.language_code} ({transcript_type})")
    
    # 字幕テキストを結合
    full_text = ''.join(
        clean_transcript(tr['text'])
        for tr in transcript.fetch()
        if clean_transcript(tr['text'])
    )
    
    pyperclip.copy(full_text)
    return full_text

if __name__ == "__main__":
    try:
        youtube_url = input("YouTubeのURLを入力してください: ")
        if video_id := extract_video_id(youtube_url):
            transcript = get_video_transcript(video_id)
            print("字幕テキストをクリップボードにコピーしました。")
            print("\n処理結果:")
            print(transcript)
        else:
            print("エラー: 有効なYouTube URLではありません")
            sys.exit(1)
    except Exception as e:
        print(f"エラー: 字幕を取得できませんでした - {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n処理を中断しました")
        sys.exit(0)