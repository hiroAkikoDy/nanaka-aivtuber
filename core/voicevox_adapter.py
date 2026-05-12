import json
import os
import io

import requests
import soundfile
import yaml


def load_settings():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class VoicevoxAdapter:
    def __init__(self) -> None:
        settings = load_settings()
        vv = settings["voicevox"]
        self.url = f"http://{vv['host']}:{vv['port']}/"
        self.speaker_id = vv["speaker_id"]

    def __create_audio_query(self, text: str, speaker_id: int) -> dict:
        item_data = {
            "text": text,
            "speaker": speaker_id,
        }
        response = requests.post(self.url + "audio_query", params=item_data)
        return response.json()

    def __create_request_audio(self, query_data, speaker_id: int) -> bytes:
        a_params = {"speaker": speaker_id}
        headers = {"accept": "audio/wav", "Content-Type": "application/json"}
        res = requests.post(self.url + "synthesis", params=a_params, data=json.dumps(query_data), headers=headers)
        print(res.status_code)
        return res.content

    def get_voice(self, text: str, speaker_id: int = None, speed: float = 1.0, pitch: float = 0.0):
        """
        音声を生成する

        Args:
            text: 読み上げるテキスト
            speaker_id: VOICEVOXのspeaker_id（Noneの場合はデフォルト値を使用）
            speed: 話速（1.0が標準）
            pitch: ピッチ（0.0が標準）

        Returns:
            tuple: (data, sample_rate)
        """
        if speaker_id is None:
            speaker_id = self.speaker_id  # 既存のデフォルト値

        query_data = self.__create_audio_query(text, speaker_id=speaker_id)
        query_data["speedScale"] = speed
        query_data["pitchScale"] = pitch
        audio_bytes = self.__create_request_audio(query_data, speaker_id=speaker_id)
        audio_stream = io.BytesIO(audio_bytes)
        data, sample_rate = soundfile.read(audio_stream)
        return data, sample_rate


if __name__ == "__main__":
    voicevox = VoicevoxAdapter()
    data, sample_rate = voicevox.get_voice("こんにちは")
    print(sample_rate)
