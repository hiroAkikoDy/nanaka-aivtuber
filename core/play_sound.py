import sounddevice as sd


class PlaySound:
    def __init__(self, output_device_name="CABLE Input") -> None:
        self.available = False
        if output_device_name is None:
            print("[PlaySound] 音声出力デバイス未指定。音声をスキップします")
            return
        output_device_id = self._search_output_device_id(output_device_name)
        if output_device_id is None:
            print(f"[PlaySound] 出力デバイス '{output_device_name}' が見つかりません。音声をスキップします")
            return
        sd.default.device = [None, output_device_id]
        sd.default.channels = [None, 2]
        self.available = True
        print(f"[PlaySound] 音声出力デバイス: index={output_device_id}")

    def _search_output_device_id(self, output_device_name, output_device_host_api=0):
        devices = sd.query_devices()
        for device in devices:
            if (output_device_name in device["name"]
                    and device["hostapi"] == output_device_host_api
                    and device["max_output_channels"] > 0):
                return device["index"]
        return None

    def play_sound(self, data, rate) -> bool:
        if not self.available or data is None:
            return False
        try:
            if data.ndim == 1:
                import numpy as np
                data = np.column_stack([data, data])
            sd.play(data, rate)
            sd.wait()
            return True
        except Exception as e:
            print(f"[PlaySound] 音声再生エラー: {e}")
            return False