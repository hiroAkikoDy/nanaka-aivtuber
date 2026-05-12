"""
OBSウェブソケット連携エージェント

OBS Studio と WebSocket 経由で通信し、以下の機能を提供：
- シーン切り替え
- ソース表示・非表示制御
- 画像ソース更新（キャラクター画像切り替え）
- テキストソース更新
"""

import os
from typing import Optional, Dict, Any
from obswebsocket import obsws, requests as obs_requests


class OBSAgent:
    """OBSウェブソケット連携エージェント"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: OBS設定（settings.yamlから読み込み）
        """
        self.config = config
        self.obs_config = config.get("obs", {})
        self.websocket_config = self.obs_config.get("websocket", {})

        self.enabled = self.websocket_config.get("enabled", False)
        self.host = self.websocket_config.get("host", "localhost")
        self.port = self.websocket_config.get("port", 4455)
        self.password = self.websocket_config.get("password", "")

        self.scenes = self.obs_config.get("scenes", {})
        self.sources = self.obs_config.get("sources", {})

        self.ws: Optional[obsws] = None
        self.connected = False

        if self.enabled:
            self.connect()

    def connect(self) -> bool:
        """OBSウェブソケットに接続"""
        if self.connected:
            return True

        try:
            self.ws = obsws(self.host, self.port, self.password)
            self.ws.connect()
            self.connected = True
            print(f"[OBS] WebSocket接続成功: {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[OBS] WebSocket接続失敗: {e}")
            print("[OBS] OBSが起動していない、またはWebSocketプラグインが有効化されていない可能性があります")
            self.connected = False
            return False

    def disconnect(self):
        """OBSウェブソケットから切断"""
        if self.ws and self.connected:
            try:
                self.ws.disconnect()
                self.connected = False
                print("[OBS] WebSocket切断")
            except Exception as e:
                print(f"[OBS] WebSocket切断エラー: {e}")

    def set_current_scene(self, scene_name: str) -> bool:
        """
        現在のシーンを切り替え

        Args:
            scene_name: シーン名

        Returns:
            成功した場合True
        """
        if not self.enabled or not self.connected:
            return False

        try:
            self.ws.call(obs_requests.SetCurrentProgramScene(sceneName=scene_name))
            print(f"[OBS] シーン切り替え: {scene_name}")
            return True
        except Exception as e:
            print(f"[OBS] シーン切り替えエラー: {e}")
            return False

    def set_scene_by_key(self, scene_key: str) -> bool:
        """
        設定ファイルのキーでシーンを切り替え

        Args:
            scene_key: 設定ファイルのシーンキー（例: "waiting", "streaming", "ending"）

        Returns:
            成功した場合True
        """
        scene_name = self.scenes.get(scene_key)
        if not scene_name:
            print(f"[OBS] シーンキー '{scene_key}' が設定に見つかりません")
            return False

        return self.set_current_scene(scene_name)

    def set_source_visibility(self, source_name: str, visible: bool) -> bool:
        """
        ソースの表示・非表示を制御

        Args:
            source_name: ソース名
            visible: True=表示, False=非表示

        Returns:
            成功した場合True
        """
        if not self.enabled or not self.connected:
            return False

        try:
            # 現在のシーン名を取得
            current_scene_response = self.ws.call(obs_requests.GetCurrentProgramScene())
            scene_name = current_scene_response.datain['currentProgramSceneName']

            # ソースの表示・非表示を設定
            self.ws.call(obs_requests.SetSceneItemEnabled(
                sceneName=scene_name,
                sceneItemId=self._get_scene_item_id(scene_name, source_name),
                sceneItemEnabled=visible
            ))

            status = "表示" if visible else "非表示"
            print(f"[OBS] ソース '{source_name}' を{status}に設定")
            return True
        except Exception as e:
            print(f"[OBS] ソース表示制御エラー: {e}")
            return False

    def _get_scene_item_id(self, scene_name: str, source_name: str) -> int:
        """
        シーンアイテムIDを取得

        Args:
            scene_name: シーン名
            source_name: ソース名

        Returns:
            シーンアイテムID
        """
        try:
            response = self.ws.call(obs_requests.GetSceneItemId(
                sceneName=scene_name,
                sourceName=source_name
            ))
            return response.datain['sceneItemId']
        except Exception as e:
            print(f"[OBS] シーンアイテムID取得エラー: {e}")
            return -1

    def update_image_source(self, source_name: str, image_path: str) -> bool:
        """
        画像ソースの画像ファイルを更新

        Args:
            source_name: 画像ソース名
            image_path: 新しい画像ファイルのパス（絶対パス）

        Returns:
            成功した場合True
        """
        if not self.enabled or not self.connected:
            return False

        if not os.path.exists(image_path):
            print(f"[OBS] 画像ファイルが見つかりません: {image_path}")
            return False

        try:
            # 画像ソースの設定を更新
            self.ws.call(obs_requests.SetInputSettings(
                inputName=source_name,
                inputSettings={"file": image_path}
            ))
            print(f"[OBS] 画像ソース '{source_name}' を更新: {os.path.basename(image_path)}")
            return True
        except Exception as e:
            print(f"[OBS] 画像ソース更新エラー: {e}")
            return False

    def update_text_source(self, source_name: str, text: str) -> bool:
        """
        テキストソースの内容を更新

        Args:
            source_name: テキストソース名
            text: 新しいテキスト

        Returns:
            成功した場合True
        """
        if not self.enabled or not self.connected:
            return False

        try:
            self.ws.call(obs_requests.SetInputSettings(
                inputName=source_name,
                inputSettings={"text": text}
            ))
            print(f"[OBS] テキストソース '{source_name}' を更新")
            return True
        except Exception as e:
            print(f"[OBS] テキストソース更新エラー: {e}")
            return False

    def show_character(self, character_name: str, emotion: str = "通常") -> bool:
        """
        キャラクターを表示（画像ソース更新 + 表示制御）

        Args:
            character_name: キャラクター名（例: "nanaka", "ryou"）
            emotion: 感情（例: "通常", "嬉しい", "ワクワク", "驚き", "悲しい"）

        Returns:
            成功した場合True
        """
        if not self.enabled or not self.connected:
            return False

        # キャラクター設定を取得
        characters_config = self.config.get("characters", {})
        character_config = characters_config.get(character_name)

        if not character_config:
            print(f"[OBS] キャラクター '{character_name}' の設定が見つかりません")
            return False

        # 画像パスを構築
        image_dir = character_config.get("image_dir")
        emotions_map = character_config.get("emotions", {})
        image_filename = emotions_map.get(emotion, emotions_map.get("通常", "normal.png"))

        # プロジェクトルートからの絶対パスを生成
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, image_dir, image_filename)

        # OBSソース名を取得
        source_key = f"{character_name}_image"
        source_name = self.sources.get(source_key)

        if not source_name:
            print(f"[OBS] ソースキー '{source_key}' が設定に見つかりません")
            return False

        # 画像ソースを更新
        success = self.update_image_source(source_name, image_path)

        if success:
            # ソースを表示
            self.set_source_visibility(source_name, True)

        return success

    def hide_character(self, character_name: str) -> bool:
        """
        キャラクターを非表示

        Args:
            character_name: キャラクター名（例: "nanaka", "ryou"）

        Returns:
            成功した場合True
        """
        if not self.enabled or not self.connected:
            return False

        source_key = f"{character_name}_image"
        source_name = self.sources.get(source_key)

        if not source_name:
            print(f"[OBS] ソースキー '{source_key}' が設定に見つかりません")
            return False

        return self.set_source_visibility(source_name, False)

    def switch_character(self, from_character: str, to_character: str, emotion: str = "通常") -> bool:
        """
        キャラクターを切り替え（前のキャラクターを非表示 → 新しいキャラクターを表示）

        Args:
            from_character: 現在のキャラクター名
            to_character: 切り替え先のキャラクター名
            emotion: 切り替え先の感情

        Returns:
            成功した場合True
        """
        if not self.enabled or not self.connected:
            return False

        # 前のキャラクターを非表示
        if from_character:
            self.hide_character(from_character)

        # 新しいキャラクターを表示
        return self.show_character(to_character, emotion)
