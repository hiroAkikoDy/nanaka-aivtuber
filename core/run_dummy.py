import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_adapter import LangChainAdapter
from agents.emotion_agent import EmotionAgent
from memory.memory_agent import MemoryAgent
from voicevox_adapter import VoicevoxAdapter
from play_sound import PlaySound
import yaml


def load_settings():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    settings = load_settings()

    dummy_comments = [
        {"viewer": "太郎", "text": "ナナカちゃん可愛い！"},
        {"viewer": "花子", "text": "クレソンの育て方教えて"},
        {"viewer": "太郎", "text": "今日も元気だね！"},
        {"viewer": "次郎", "text": "熊本出身です！"},
        {"viewer": "花子", "text": "前回の育て方ありがとう！"},
    ]

    langchain_adapter = LangChainAdapter()
    emotion_agent = EmotionAgent()
    memory_agent = MemoryAgent()
    voicevox_adapter = VoicevoxAdapter()
    play_sound = PlaySound(output_device_name=settings["audio"]["output_device_name"])

    for i, item in enumerate(dummy_comments):
        viewer_name = item["viewer"]
        comment = item["text"]
        print(f"\n--- コメント {i + 1}/{len(dummy_comments)} [{viewer_name}] ---")
        print(f"視聴者: {comment}")

        memory = memory_agent.get_memory(viewer_name)
        print(f"[記憶取得] {viewer_name}: {len(memory)}文字")

        emotion_result = emotion_agent.analyze(comment)
        emotion = emotion_result["emotion"]
        speed = emotion_result["speed"]
        pitch = emotion_result["pitch"]
        print(f"[感情分析] {emotion} (speed={speed}, pitch={pitch})")

        response_text = langchain_adapter.create_chat(comment, emotion=emotion, memory=memory)
        print(f"ナナカ: {response_text}")

        data, rate = voicevox_adapter.get_voice(response_text, speed=speed, pitch=pitch)
        play_sound.play_sound(data, rate)

        memory_agent.save_interaction(viewer_name, comment, emotion, response_text)
        print(f"[記憶保存] {viewer_name} の会話を保存しました")

    memory_agent.close()
    print("\n全てのダミーコメント処理が完了しました。")


if __name__ == "__main__":
    main()
