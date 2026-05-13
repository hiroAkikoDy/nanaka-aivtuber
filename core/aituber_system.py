import random
import sys
import os
import yaml
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from obs_adapter import OBSAdapter
from voicevox_adapter import VoicevoxAdapter
from langchain_adapter import LangChainAdapter
from agents.emotion_agent import EmotionAgent
from memory.memory_agent import MemoryAgent
from youtube_comment_adapter import YoutubeCommentAdapter
from play_sound import PlaySound
from dotenv import load_dotenv
load_dotenv()


def load_settings():
    """settings.yaml を読み込む"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class AITuberSystem:
    def __init__(self) -> None:
        video_id = os.getenv("YOUTUBE_VIDEO_ID")
        self.youtube_comment_adapter = YoutubeCommentAdapter(video_id) if video_id else None
        self.langchain_adapter = LangChainAdapter()
        self.emotion_agent = EmotionAgent()
        self.memory_agent = MemoryAgent()
        self.voice_adapter = VoicevoxAdapter()
        try:
            self.obs_adapter = OBSAdapter()
        except Exception:
            self.obs_adapter = None
            print("[AITuberSystem] OBS接続なし（テキストファイル出力モード）")
        self.play_sound = PlaySound(output_device_name="CABLE Input")

        # マルチペルソナ設定の読み込み
        settings = load_settings()
        self.multi_persona_enabled = settings.get("multi_persona", {}).get("enabled", False)

        if self.multi_persona_enabled:
            from agents.dialogue_coordinator import DialogueCoordinator
            self.dialogue_coordinator = DialogueCoordinator()

    def talk_with_comment(self, viewer_name: str, comment: str) -> bool:
        # 1. 記憶取得（既存）
        memory = self.memory_agent.get_memory(viewer_name)
        print(f"[記憶取得] {viewer_name}: {len(memory)}文字")

        # 2. 感情分析（既存）
        emotion_result = self.emotion_agent.analyze(comment)
        emotion = emotion_result["emotion"]
        speed = emotion_result["speed"]
        pitch = emotion_result["pitch"]
        print(f"[感情分析] {emotion} (speed={speed}, pitch={pitch})")

        # 3. マルチペルソナモード分岐
        if self.multi_persona_enabled:
            # マルチペルソナ: 複数AIが会話
            dialogue = self.dialogue_coordinator.coordinate_dialogue(comment, emotion)

            for turn in dialogue:
                print(f"[{turn['persona']}] {turn['text']}")
                data, rate = self.voice_adapter.get_voice(
                    turn['text'],
                    speaker_id=turn['speaker_id'],
                    speed=speed,
                    pitch=pitch
                )
                if data is not None:
                    self.play_sound.play_sound(data, rate)

            # OBS表示: 最初のナナカの発言
            nanaka_turns = [t for t in dialogue if t['persona'] == 'nanaka']
            if nanaka_turns:
                first_nanaka_response = nanaka_turns[0]['text']
                if self.obs_adapter:
                    self.obs_adapter.set_question(comment)
                    self.obs_adapter.set_answer(first_nanaka_response)

            # 記憶保存: 最後のナナカの発言を保存
            if nanaka_turns:
                last_nanaka_response = nanaka_turns[-1]['text']
                self.memory_agent.save_interaction(viewer_name, comment, emotion, last_nanaka_response)
                print(f"[記憶保存] {viewer_name} の会話を保存しました")
        else:
            # 単独モード（既存のロジック）
            response_text = self.langchain_adapter.create_chat(comment, emotion=emotion, memory=memory)
            print(f"[応答] {response_text}")
            data, rate = self.voice_adapter.get_voice(response_text, speed=speed, pitch=pitch)
            if self.obs_adapter:
                self.obs_adapter.set_question(comment)
                self.obs_adapter.set_answer(response_text)
            if data is not None:
                self.play_sound.play_sound(data, rate)
            self.memory_agent.save_interaction(viewer_name, comment, emotion, response_text)
            print(f"[記憶保存] {viewer_name} の会話を保存しました")

        return True

    def get_dialogue_response(self, viewer_name: str, comment: str) -> list[dict]:
        """
        マルチペルソナモードの会話を取得（音声再生なし）

        Args:
            viewer_name: 視聴者名
            comment: コメント内容

        Returns:
            list[dict]: [
                {"persona": "nanaka", "text": "...", "speaker_id": 46, "emotion": "嬉しい"},
                {"persona": "ryou", "text": "...", "speaker_id": 3, "emotion": "通常"},
                ...
            ]
        """
        if not self.multi_persona_enabled:
            return []

        memory = self.memory_agent.get_memory(viewer_name)

        emotion_result = self.emotion_agent.analyze(comment)
        emotion = emotion_result["emotion"]

        dialogue = self.dialogue_coordinator.coordinate_dialogue(comment, emotion)

        # 各ターンに感情情報を追加
        for turn in dialogue:
            if "emotion" not in turn:
                turn["emotion"] = emotion  # コメントの感情をデフォルトとして設定

        nanaka_turns = [t for t in dialogue if t['persona'] == 'nanaka']
        if nanaka_turns:
            last_nanaka_response = nanaka_turns[-1]['text']
            self.memory_agent.save_interaction(viewer_name, comment, emotion, last_nanaka_response)

        return dialogue