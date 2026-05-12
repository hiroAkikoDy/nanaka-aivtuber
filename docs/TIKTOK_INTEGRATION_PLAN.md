# TikTokライブ配信連携 実装計画書

## 📋 概要

本ドキュメントは、nanaka-aivtuberプロジェクトにTikTokライブ配信連携機能を追加するための実装計画書です。

**作成日**: 2026-05-13
**対象バージョン**: STEP8以降
**前提条件**: STEP7（OBSウェブソケット連携・キャラクター画像表示）完了済み

---

## 🎯 目標

YouTube Liveに加えて、TikTok Liveでもリアルタイムにコメントを取得し、AIVTuberが自動応答する機能を実装する。

### 実現したいこと

1. TikTok Liveのコメントをリアルタイムで取得
2. AIVTuberが自動的に応答（マルチペルソナ対話）
3. YouTube Live / TikTok Live を切り替えて配信可能
4. 将来的には同時配信（OBSマルチストリーミング）

---

## 🔍 TikTok Live API の現状調査

### 公式API（TikTok for Developers）

**提供状況**: ❌ 個人開発者向けには提供されていない

**特徴**:
- 企業向けパートナープログラムが必要
- TikTok Business Account が必要
- 厳格な審査プロセス
- ライブコメント取得APIは限定的

**申請条件**:
- 企業登録
- 月間アクティブユーザー数が一定以上
- 利用目的の明確化

**結論**: 個人開発者には**現実的ではない**

---

### 非公式ライブラリ

#### 1. TikTokLive（Python）

**GitHub**: https://github.com/isaackogan/TikTokLive

**特徴**:
- ✅ リアルタイムでコメント取得可能
- ✅ Pythonで実装済み（導入が容易）
- ✅ アクティブにメンテナンスされている（2024年更新）
- ⚠️ 非公式（利用規約違反のリスク）
- ⚠️ TikTokの仕様変更で動作しなくなる可能性

**インストール**:
```bash
pip install TikTokLive
```

**基本的な使い方**:
```python
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent

client = TikTokLiveClient(unique_id="@username")

@client.on("comment")
async def on_comment(event: CommentEvent):
    print(f"{event.user.nickname}: {event.comment}")

client.run()
```

**メリット**:
- すぐに実装可能
- YouTube Liveと同じアーキテクチャで実装できる
- コメント取得以外のイベントも取得可能（ギフト、いいね、フォローなど）

**デメリット**:
- 利用規約違反のリスク
- アカウント停止の可能性
- 安定性が保証されない

#### 2. TikTokLiveSharp（C#）

**GitHub**: https://github.com/frankvHoof93/TikTokLiveSharp

**特徴**:
- C#実装（Python版と同等の機能）
- 本プロジェクトではPythonを使用しているため対象外

---

## 📐 アーキテクチャ設計

### 1. マルチプラットフォーム対応のインターフェース設計

既存の`YouTubeAgent`を参考に、統一インターフェースを設計します。

#### 1-1. StreamingPlatformInterface（抽象基底クラス）

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class StreamingPlatformInterface(ABC):
    """配信プラットフォームの統一インターフェース"""

    @abstractmethod
    def start_monitoring(self, stream_id: Optional[str] = None) -> None:
        """
        配信モニタリング開始

        Args:
            stream_id: 配信ID（Noneの場合は自動検出）
        """
        pass

    @abstractmethod
    def fetch_comments(self) -> List[Dict[str, str]]:
        """
        コメントを取得

        Returns:
            [
                {"author": "ユーザー名", "text": "コメント内容"},
                ...
            ]
        """
        pass

    @abstractmethod
    def stop_monitoring(self) -> None:
        """配信モニタリング停止"""
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        """プラットフォーム名を取得"""
        pass
```

#### 1-2. YouTubeAgent（既存）をリファクタリング

```python
from agents.streaming_platform_interface import StreamingPlatformInterface

class YouTubeAgent(StreamingPlatformInterface):
    """YouTube Live 配信エージェント"""

    def start_monitoring(self, stream_id: Optional[str] = None) -> None:
        # 既存の実装をそのまま使用
        pass

    def fetch_comments(self) -> List[Dict[str, str]]:
        # 既存の実装をそのまま使用
        pass

    def stop_monitoring(self) -> None:
        # 新規実装
        pass

    def get_platform_name(self) -> str:
        return "YouTube"
```

#### 1-3. TikTokAgent（新規実装）

```python
from agents.streaming_platform_interface import StreamingPlatformInterface
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent
import asyncio
from typing import List, Dict, Optional

class TikTokAgent(StreamingPlatformInterface):
    """TikTok Live 配信エージェント"""

    def __init__(self, config: Dict):
        self.config = config
        self.tiktok_config = config.get("tiktok", {})
        self.username = self.tiktok_config.get("username", "@username")
        self.client: Optional[TikTokLiveClient] = None
        self.comments: List[Dict[str, str]] = []
        self.processed_comment_ids = set()

    def start_monitoring(self, stream_id: Optional[str] = None) -> None:
        """配信モニタリング開始"""
        username = stream_id or self.username
        self.client = TikTokLiveClient(unique_id=username)

        @self.client.on("comment")
        async def on_comment(event: CommentEvent):
            comment_id = event.id  # 重複排除用
            if comment_id not in self.processed_comment_ids:
                self.comments.append({
                    "author": event.user.nickname,
                    "text": event.comment
                })
                self.processed_comment_ids.add(comment_id)

        print(f"[TikTok] モニタリング開始: {username}")

    def fetch_comments(self) -> List[Dict[str, str]]:
        """コメントを取得"""
        comments = self.comments.copy()
        self.comments.clear()
        return comments

    def stop_monitoring(self) -> None:
        """配信モニタリング停止"""
        if self.client:
            self.client.stop()
            print("[TikTok] モニタリング停止")

    def get_platform_name(self) -> str:
        return "TikTok"

    def run(self):
        """非同期実行（メインループ）"""
        if self.client:
            self.client.run()
```

---

### 2. 設定ファイル（settings.yaml）の拡張

```yaml
# 配信プラットフォーム設定
streaming:
  platform: "youtube"  # youtube / tiktok / multi（将来実装）

# YouTube設定（既存）
youtube:
  enabled: true
  mode: "dummy"  # live / dummy
  credentials_path: "credentials/client_secret.json"
  token_path: "credentials/token.json"
  video_id: null
  polling_interval: 5
  max_results: 10
  quota_limit_per_day: 10000
  quota_warning_threshold: 8000

# TikTok設定（新規）
tiktok:
  enabled: false  # true: TikTok Live連携有効 / false: 無効
  mode: "dummy"   # live: リアルタイム / dummy: ダミーモード
  username: "@your_tiktok_username"  # TikTokユーザー名（@付き）
  reconnect_on_disconnect: true      # 切断時に自動再接続
  timeout: 30                        # 接続タイムアウト（秒）
```

---

### 3. LiveStreamingSystem のリファクタリング

#### 3-1. プラットフォームエージェントの動的切り替え

```python
class LiveStreamingSystem:
    """マルチプラットフォーム配信システム"""

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # プラットフォーム選択
        self.platform = self.config.get("streaming", {}).get("platform", "youtube")

        # プラットフォームエージェントを初期化
        if self.platform == "youtube":
            from agents.youtube_agent import YouTubeAgent
            self.streaming_agent = YouTubeAgent(config_path)
        elif self.platform == "tiktok":
            from agents.tiktok_agent import TikTokAgent
            self.streaming_agent = TikTokAgent(self.config)
        else:
            raise ValueError(f"未対応のプラットフォーム: {self.platform}")

        self.aituber_system = AITuberSystem()
        self.obs_agent = OBSAgent(self.config)
        # ... その他の初期化

    def run(self, stream_id: str = None):
        """配信モード実行"""
        print(f"[{self.streaming_agent.get_platform_name()}] 配信モード起動")

        self.streaming_agent.start_monitoring(stream_id)

        try:
            while True:
                comments = self.streaming_agent.fetch_comments()

                for comment in comments:
                    viewer_name = comment["author"]
                    comment_text = comment["text"]

                    print(f"\n[視聴者] {viewer_name}: {comment_text}")

                    # ... 既存の処理（AIVTuber応答・OBS更新など）

                time.sleep(5)  # ポーリング間隔

        except KeyboardInterrupt:
            print("\n\n配信モードを終了します")
            self.streaming_agent.stop_monitoring()
```

---

## 🚀 実装ステップ

### STEP8-1: 基盤実装（1〜2時間）

1. **StreamingPlatformInterface 作成**
   - `agents/streaming_platform_interface.py`
   - 抽象基底クラスの定義

2. **YouTubeAgent リファクタリング**
   - `StreamingPlatformInterface`を継承
   - `stop_monitoring()`メソッド追加
   - `get_platform_name()`メソッド追加

3. **settings.yaml 拡張**
   - `streaming.platform`設定追加
   - `tiktok`セクション追加

4. **動作確認**
   - YouTube Liveでの既存機能が動作することを確認

---

### STEP8-2: TikTokAgent 実装（2〜3時間）

1. **TikTokLive ライブラリインストール**
   ```bash
   pip install TikTokLive
   ```

2. **TikTokAgent 作成**
   - `agents/tiktok_agent.py`
   - `StreamingPlatformInterface`を実装

3. **ダミーモード実装**
   - `DummyTikTokAgent`クラス
   - テスト用のダミーコメント生成

4. **動作確認**
   - ダミーモードでの動作確認

---

### STEP8-3: マルチプラットフォーム対応（1〜2時間）

1. **LiveStreamingSystem リファクタリング**
   - プラットフォームエージェントの動的切り替え
   - `run()`メソッドの共通化

2. **run_live.py 更新**
   - コマンドライン引数でプラットフォーム選択
   ```bash
   python run_live.py --platform youtube
   python run_live.py --platform tiktok
   ```

3. **動作確認**
   - YouTube / TikTok の切り替えが正常に動作するか

---

### STEP8-4: リアルタイムモード実装（2〜3時間）

1. **TikTokAgent のリアルタイムモード実装**
   - 非同期処理（asyncio）
   - コメント取得・重複排除

2. **エラーハンドリング**
   - 接続エラー時の再接続
   - タイムアウト処理

3. **動作確認**
   - 実際のTikTok Liveで動作確認

---

### STEP8-5: 同時配信対応（将来実装）

1. **MultiPlatformStreamingSystem 実装**
   - 複数のプラットフォームエージェントを同時実行
   - コメントをマージして処理

2. **OBSマルチストリーミング設定**
   - OBS → 設定 → 配信 → 「カスタム」
   - YouTube / TikTok 両方に同時配信

3. **動作確認**
   - 両プラットフォームからのコメントが正常に取得できるか

---

## ⚠️ リスクと対策

### リスク1: 利用規約違反

**内容**: TikTokLiveは非公式ライブラリのため、利用規約違反の可能性

**対策**:
- 個人利用・教育目的に限定
- 商用利用は避ける
- 公式APIがリリースされた場合は速やかに移行

---

### リスク2: アカウント停止

**内容**: TikTokがスクレイピングを検出してアカウント停止する可能性

**対策**:
- テスト用のサブアカウントを使用
- リクエスト頻度を制限（ポーリング間隔を長めに設定）
- 本番配信では公式API待ち

---

### リスク3: ライブラリの仕様変更

**内容**: TikTokLiveがメンテナンス停止、または仕様変更で動作しなくなる可能性

**対策**:
- GitHub Issuesを定期的に確認
- 代替ライブラリの調査（TikTokLiveConnector等）
- 最悪の場合はTikTok対応を一時停止

---

## 📊 工数見積もり

| ステップ | 内容 | 工数 | 優先度 |
|---------|------|------|--------|
| STEP8-1 | 基盤実装 | 1〜2時間 | 高 |
| STEP8-2 | TikTokAgent実装 | 2〜3時間 | 高 |
| STEP8-3 | マルチプラットフォーム対応 | 1〜2時間 | 中 |
| STEP8-4 | リアルタイムモード実装 | 2〜3時間 | 中 |
| STEP8-5 | 同時配信対応 | 3〜4時間 | 低 |

**合計工数**: 約9〜14時間（1〜2日）

---

## 🎯 実装優先度

### 優先度 高（すぐに実装）

1. StreamingPlatformInterface 作成
2. YouTubeAgent リファクタリング
3. TikTokAgent ダミーモード実装

### 優先度 中（様子を見て実装）

1. TikTokAgent リアルタイムモード実装
2. マルチプラットフォーム対応

### 優先度 低（将来実装）

1. 同時配信対応（YouTube + TikTok 同時）
2. Twitch対応
3. ニコニコ生放送対応

---

## 📚 参考資料

### TikTokLive（Python）

- **GitHub**: https://github.com/isaackogan/TikTokLive
- **ドキュメント**: https://tiktok-live.readthedocs.io/
- **Examples**: https://github.com/isaackogan/TikTokLive/tree/master/examples

### TikTok for Developers（公式）

- **公式サイト**: https://developers.tiktok.com/
- **API Documentation**: https://developers.tiktok.com/doc/

### OBSマルチストリーミング

- **OBS Multi RTMP Plugin**: https://github.com/sorayuki/obs-multi-rtmp
- **OBS公式ドキュメント**: https://obsproject.com/docs/

---

## ✅ まとめ

TikTokライブ配信連携は、非公式ライブラリ（TikTokLive）を使用することで技術的には実装可能です。ただし、利用規約違反のリスクがあるため、**個人利用・教育目的に限定**し、商用利用は避けるべきです。

公式APIがリリースされ次第、速やかに移行することを推奨します。

---

**作成者**: Claude Sonnet 4.5
**最終更新**: 2026-05-13
