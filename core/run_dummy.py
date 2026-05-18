import sys
import os
import io

# Windows環境でのUTF-8出力対応
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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

    # マルチペルソナ対応のダミーコメント
    dummy_comments = [
        {"viewer": "太郎", "text": "クレソンってどんな味なの？"},
        {"viewer": "花子", "text": "クレソンを使ったおすすめレシピ教えて！"},
        {"viewer": "次郎", "text": "クレソンの栽培って難しいの？"},
        {"viewer": "美咲", "text": "クレソンの栄養価について知りたい！"},
        {"viewer": "太郎", "text": "前回の話ありがとう！もっと詳しく聞きたい"},
    ]

    # マルチペルソナ設定の確認
    multi_persona_enabled = settings.get("multi_persona", {}).get("enabled", False)
    print(f"\n[モード] {'マルチペルソナモード' if multi_persona_enabled else '単独モード'}")

    emotion_agent = EmotionAgent()
    memory_agent = MemoryAgent()
    voicevox_adapter = VoicevoxAdapter()
    play_sound = PlaySound(output_device_name=settings["audio"]["output_device_name"])

    if multi_persona_enabled:
        # マルチペルソナモード
        from agents.dialogue_coordinator import DialogueCoordinator
        dialogue_coordinator = DialogueCoordinator()

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

            # マルチペルソナ会話生成
            dialogue = dialogue_coordinator.coordinate_dialogue(comment, emotion)

            for turn_num, turn in enumerate(dialogue, 1):
                print(f"[ターン{turn_num}] [{turn['persona']}] {turn['text']}")
                data, rate = voicevox_adapter.get_voice(
                    turn['text'],
                    speaker_id=turn['speaker_id'],
                    speed=speed,
                    pitch=pitch
                )
                if data is not None:
                    play_sound.play_sound(data, rate)

            # 最後のナナカの発言を記憶に保存
            nanaka_turns = [t for t in dialogue if t['persona'] == 'nanaka']
            if nanaka_turns:
                last_nanaka_response = nanaka_turns[-1]['text']
                memory_agent.save_interaction(viewer_name, comment, emotion, last_nanaka_response)
                print(f"[記憶保存] {viewer_name} の会話を保存しました")
    else:
        # 単独モード（既存のロジック）
        langchain_adapter = LangChainAdapter()

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
            if data is not None:
                play_sound.play_sound(data, rate)

            memory_agent.save_interaction(viewer_name, comment, emotion, response_text)
            print(f"[記憶保存] {viewer_name} の会話を保存しました")

    memory_agent.close()
    print("\n全てのダミーコメント処理が完了しました。")


if __name__ == "__main__":
    main()
