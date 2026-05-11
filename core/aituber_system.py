import random
import sys
import os
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

class AITuberSystem:
    def __init__(self) -> None:
        video_id = os.getenv("YOUTUBE_VIDEO_ID")
        self.youtube_comment_adapter = YoutubeCommentAdapter(video_id)
        self.langchain_adapter = LangChainAdapter()
        self.emotion_agent = EmotionAgent()
        self.memory_agent = MemoryAgent()
        self.voice_adapter = VoicevoxAdapter()
        self.obs_adapter = OBSAdapter()
        self.play_sound = PlaySound(output_device_name="CABLE Input")
        pass

    def talk_with_comment(self, viewer_name: str, comment: str) -> bool:
        memory = self.memory_agent.get_memory(viewer_name)
        print(f"[記憶取得] {viewer_name}: {len(memory)}文字")
        emotion_result = self.emotion_agent.analyze(comment)
        emotion = emotion_result["emotion"]
        speed = emotion_result["speed"]
        pitch = emotion_result["pitch"]
        print(f"[感情分析] {emotion} (speed={speed}, pitch={pitch})")
        response_text = self.langchain_adapter.create_chat(comment, emotion=emotion, memory=memory)
        data,rate = self.voice_adapter.get_voice(response_text, speed=speed, pitch=pitch)
        self.obs_adapter.set_question(comment)
        self.obs_adapter.set_answer(response_text)
        self.play_sound.play_sound(data,rate)
        self.memory_agent.save_interaction(viewer_name, comment, emotion, response_text)
        print(f"[記憶保存] {viewer_name} の会話を保存しました")
        return True