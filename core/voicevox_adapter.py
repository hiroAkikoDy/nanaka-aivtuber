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
    SPEED_MIN, SPEED_MAX = 0.5, 2.0
    PITCH_MIN, PITCH_MAX = -0.5, 0.5
    TIMEOUT = 10

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
        response = requests.post(self.url + "audio_query", params=item_data, timeout=self.TIMEOUT)
        return response.json()

    def __create_request_audio(self, query_data, speaker_id: int) -> bytes:
        a_params = {"speaker": speaker_id}
        headers = {"accept": "audio/wav", "Content-Type": "application/json"}
        res = requests.post(self.url + "synthesis", params=a_params, data=json.dumps(query_data), headers=headers, timeout=self.TIMEOUT)
        print(res.status_code)
        return res.content

    def get_voice(self, text: str, speaker_id: int = None, speed: float = 1.0, pitch: float = 0.0):
        if speaker_id is None:
            speaker_id = self.speaker_id

        if speed < self.SPEED_MIN or speed > self.SPEED_MAX:
            clamped = max(self.SPEED_MIN, min(self.SPEED_MAX, speed))
            print(f"[WARNING] speed={speed} はVOICEVOX許容範囲外。{clamped}にクランプしました")
            speed = clamped
        if pitch < self.PITCH_MIN or pitch > self.PITCH_MAX:
            clamped = max(self.PITCH_MIN, min(self.PITCH_MAX, pitch))
            print(f"[WARNING] pitch={pitch} はVOICEVOX許容範囲外。{clamped}にクランプしました")
            pitch = clamped

        try:
            query_data = self.__create_audio_query(text, speaker_id=speaker_id)
            query_data["speedScale"] = speed
            query_data["pitchScale"] = pitch
            audio_bytes = self.__create_request_audio(query_data, speaker_id=speaker_id)
            audio_stream = io.BytesIO(audio_bytes)
            data, sample_rate = soundfile.read(audio_stream)
            return data, sample_rate
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] VOICEVOX通信エラー: {e}")
            print("[WARNING] 音声をスキップします")
            return None, None


if __name__ == "__main__":
    voicevox = VoicevoxAdapter()
    data, sample_rate = voicevox.get_voice("こんにちは")
    print(sample_rate)
