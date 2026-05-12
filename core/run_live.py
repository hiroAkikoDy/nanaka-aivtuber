"""
YouTube Live 配信モード実行スクリプト

リアルタイムでYouTube Liveコメントを取得し、
マルチペルソナAIVTuberが応答する。
"""

import time
import os
import sys
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.youtube_agent import YouTubeAgent
from core.aituber_system import AITuberSystem


class LiveStreamingSystem:
    """YouTube Live 配信システム"""

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.youtube_agent = YouTubeAgent(config_path)

        self.aituber_system = AITuberSystem()

        self.obs_config = self.config.get("obs", {})
        self.obs_enabled = self.obs_config.get("enabled", True)
        self.output_dir = self.obs_config.get("output_dir", "output")
        self.speaker_file = self.obs_config.get("speaker_file", "current_speaker.txt")
        self.text_file = self.obs_config.get("text_file", "current_text.txt")
        self.max_text_length = self.obs_config.get("max_text_length", 100)

        os.makedirs(self.output_dir, exist_ok=True)

    def update_obs_display(self, speaker: str, text: str):
        if not self.obs_enabled:
            return

        if len(text) > self.max_text_length:
            text = text[:self.max_text_length] + "..."

        speaker_path = os.path.join(self.output_dir, self.speaker_file)
        text_path = os.path.join(self.output_dir, self.text_file)

        with open(speaker_path, "w", encoding="utf-8") as f:
            f.write(speaker)

        with open(text_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"[OBS] 更新: {speaker} - {text}")

    def clear_obs_display(self):
        self.update_obs_display("", "")

    def run(self, video_id: str = None):
        print("=" * 50)
        print("YouTube Live 配信モード起動")
        print("=" * 50)

        self.youtube_agent.start_monitoring(video_id)

        if self.youtube_agent.live_chat_id is None:
            print("配信が見つかりません。終了します。")
            return

        print("\n配信モニタリング開始...")
        print("（Ctrl+C で終了）\n")

        try:
            while True:
                comments = self.youtube_agent.fetch_comments()

                for comment in comments:
                    viewer_name = comment["author"]
                    comment_text = comment["text"]

                    print(f"\n[視聴者] {viewer_name}: {comment_text}")

                    self.update_obs_display(viewer_name, comment_text)
                    time.sleep(2)

                    if self.config.get("multi_persona", {}).get("enabled", False):
                        dialogue = self.aituber_system.get_dialogue_response(viewer_name, comment_text)

                        for turn in dialogue:
                            persona = turn["persona"]
                            text = turn["text"]

                            print(f"[{persona}] {text}")

                            self.update_obs_display(persona, text)

                            time.sleep(len(text) * 0.3)
                    else:
                        self.aituber_system.talk_with_comment(viewer_name, comment_text)
                        self.update_obs_display("ナナカ", "応答を生成しました")

                    self.clear_obs_display()

                time.sleep(self.youtube_agent.polling_interval)

        except KeyboardInterrupt:
            print("\n\n配信モードを終了します")
            self.clear_obs_display()


class DummyLiveStreamingSystem(LiveStreamingSystem):
    """ダミー配信システム（テスト用）"""

    def run(self, video_id: str = None):
        print("=" * 50)
        print("ダミー配信モード起動")
        print("=" * 50)

        dummy_comments = [
            {"author": "太郎", "text": "クレソンってどんな味なの？"},
            {"author": "花子", "text": "クレソンを使ったおすすめレシピ教えて！"},
            {"author": "次郎", "text": "クレソンの栽培って難しいの？"},
        ]

        print("\nダミーコメント処理開始...\n")

        for comment in dummy_comments:
            viewer_name = comment["author"]
            comment_text = comment["text"]

            print(f"\n[視聴者] {viewer_name}: {comment_text}")
            self.update_obs_display(viewer_name, comment_text)
            time.sleep(2)

            self.aituber_system.talk_with_comment(viewer_name, comment_text)

            self.clear_obs_display()
            time.sleep(3)

        print("\nダミーモード完了")


if __name__ == "__main__":
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config",
        "settings.yaml"
    )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    youtube_mode = config.get("youtube", {}).get("mode", "dummy")

    if youtube_mode == "live":
        system = LiveStreamingSystem(config_path)
        system.run()
    else:
        system = DummyLiveStreamingSystem(config_path)
        system.run()
