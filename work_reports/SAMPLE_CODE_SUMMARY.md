# サンプルコード要約 — AITuber書籍（aituber_python_programing_example）

## 全体アーキテクチャ

```
YouTube Liveコメント
       ↓
YoutubeCommentAdapter.get_comment()
       ↓
OpenAIAdapter.create_chat(comment)
       ↓
VoicevoxAdapter.get_voice(response_text) → (audio_data, sample_rate)
       ↓
PlaySound.play_sound(data, rate) → 音声出力
       ↑
OBSAdapter.set_question / set_answer → 画面表示
```

**メインループ**: `run.py` が5秒間隔で `AITuberSystem.talk_with_comment()` を呼び出す。

---

## ファイル一覧

### run.py — エントリーポイント
```python
import time
from aituber_system import AITuberSystem
import traceback

aituber_system = AITuberSystem()
while True:
    try:
        aituber_system.talk_with_comment()
        time.sleep(5)
    except Exception as e:
        print("エラーが発生しました")
        print(traceback.format_exc())
        print(e)
        exit(200)
```
- 5秒ポーリングでコメント取得→応答生成→音声出力を繰り返す
- 例外発生時はトレースバックを出力して終了（exit code 200）

---

### aituber_system.py — 統合クラス（オーケストレーター）
```python
class AITuberSystem:
    def __init__(self) -> None:
        video_id = os.getenv("YOUTUBE_VIDEO_ID")
        self.youtube_comment_adapter = YoutubeCommentAdapter(video_id)
        self.openai_adapter = OpenAIAdapter()
        self.voice_adapter = VoicevoxAdapter()
        self.obs_adapter = OBSAdapter()
        self.play_sound = PlaySound(output_device_name="CABLE Input")

    def talk_with_comment(self) -> bool:
        comment = self.youtube_comment_adapter.get_comment()
        if comment == None:
            return False
        response_text = self.openai_adapter.create_chat(comment)
        data, rate = self.voice_adapter.get_voice(response_text)
        self.obs_adapter.set_question(comment)
        self.obs_adapter.set_answer(response_text)
        self.play_sound.play_sound(data, rate)
        return True
```
- `.env` から `YOUTUBE_VIDEO_ID` を取得
- 全adapterを初期化・順次呼び出し
- コメントなし → False を返す（呼び出し側は5秒後にリトライ）

---

### openai_adapter.py — LLM応答生成
```python
class OpenAIAdapter:
    SAVE_PREVIOUS_CHAT_NUM = 5  # 過去5往復を保持

    def __init__(self):
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            self.system_prompt = f.read()
        self.chat_log = []

    def create_chat(self, question):
        messages = self._get_messages()           # system + 過去ログ
        messages.append({"role": "user", "content": question})
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        answer = res["choices"][0]["message"]["content"]
        self._update_messages(question, answer)
        return answer
```
- **旧SDK**: `openai==0.28.1`（`ChatCompletion.create` 形式）
- **会話履歴**: 直近5往復（question/answerペア）を保持・自動ローテーション
- **プロンプト**: `system_prompt.txt` から読み込み
- `.env` の `OPENAI_API_KEY` を使用

**会話履歴の構造**:
```python
chat_log = [
    {"question": "...", "answer": "..."},
    # 最大5件（超過したらpop(0)で古いものを削除）
]
```

**messagesの組み立て**:
```
[system_prompt] → [user:Q1, assistant:A1] → ... → [user:最新質問]
```

---

### voicevox_adapter.py — 音声合成
```python
class VoicevoxAdapter:
    URL = 'http://127.0.0.1:50021/'

    def get_voice(self, text: str):
        speaker_id = 3
        query_data = self.__create_audio_query(text, speaker_id)
        audio_bytes = self.__create_request_audio(query_data, speaker_id)
        audio_stream = io.BytesIO(audio_bytes)
        data, sample_rate = soundfile.read(audio_stream)
        return data, sample_rate
```

**VOICEVOX APIの2段POST処理**:
1. `POST /audio_query` → テキスト→クエリJSON（発音・アクセント等）
2. `POST /synthesis` → クエリJSON→WAVバイナリ

**パラメータ**:
- `speaker_id = 3`（VOICEVOXの話者ID）
- 出力: `(numpy配列, サンプリングレート)` のタプル

**話者ID一覧（参考）**: 1=四国めたん、2=ずんだもん、3=四国めたん（あまあま）、等

---

### youtube_comment_adapter.py — YouTube Liveコメント取得
```python
class YoutubeCommentAdapter:
    def __init__(self, video_id) -> None:
        self.chat = pytchat.create(video_id=video_id, interruptable=False)

    def get_comment(self):
        comments = self.__get_comments()
        if comments == None:
            return None
        comment = comments[-1]  # 最新のコメントを取得
        return comment.get("message")
```
- **pytchat** ライブラリを使用
- `get().json()` → コメント一覧をJSON取得
- 最新コメント1件の `message` フィールドのみ返す
- 配信が終了/未開始 → `is_alive() == False` → `None` を返す

---

### obs_adapter.py — OBS画面表示
```python
class OBSAdapter:
    def __init__(self) -> None:
        self.ws = obs.ReqClient(host=host, port=port, password=password)

    def set_question(self, text: str):
        self.ws.set_input_settings(name="Question", settings={"text": text}, overlay=True)

    def set_answer(self, text: str):
        self.ws.set_input_settings(name="Answer", settings={"text": text}, overlay=True)
```
- **obsws-python** でOBS WebSocketに接続
- OBS側に "Question" / "Answer" というテキストソースが必要
- `.env` から `OBS_WS_PASSWORD`, `OBS_WS_HOST`, `OBS_WS_PORT` を取得

---

### play_sound.py — 音声再生
```python
class PlaySound:
    def __init__(self, output_device_name="CABLE Input") -> None:
        output_device_id = self._search_output_device_id(output_device_name)
        sd.default.device = [0, output_device_id]

    def play_sound(self, data, rate) -> bool:
        sd.play(data, rate)
        sd.wait()
        return True
```
- **sounddevice** で音声再生
- デフォルト出力: "CABLE Input"（OBS用仮想オーディオケーブル）
- `sd.play()` → `sd.wait()` で同期再生（再生完了までブロック）

---

### system_prompt.txt — キャラクター設定
```
[指示]
あなたは「蛍」という名前の16歳の女性です。
私が話しかけたら、短めの返答をします。

[蛍についての情報]
職業：学生
趣味：睡眠、夜の散歩
性格：他人思い、優柔不断、おっちょこちょい
出身：東京
好きな食べ物：おすし
嫌いな食べ物：なす
（茄子の煮物失敗エピソード付き）
```

---

## 依存パッケージ一覧（requirements.txt）

| パッケージ | バージョン | 用途 |
|---|---|---|
| `openai` | 0.28.1 | LLM API（旧SDK） |
| `pytchat` | 0.5.5 | YouTube Liveコメント取得 |
| `obsws-python` | 1.6.0 | OBS WebSocket連携 |
| `requests` | 2.31.0 | VOICEVOX API呼び出し |
| `soundfile` | 0.12.1 | WAV読み込み |
| `sounddevice` | 0.4.6 | 音声再生 |
| `python-dotenv` | 1.0.0 | .env読み込み |
| `numpy` | 1.26.0 | 音声データ配列 |

---

## 環境変数（.env必要項目）

```env
OPENAI_API_KEY=sk-...
YOUTUBE_VIDEO_ID=xxxxx
OBS_WS_PASSWORD=xxxxx
OBS_WS_HOST=localhost
OBS_WS_PORT=4455
```

---

## STEP1移行時の修正ポイント

1. **OpenAI SDK更新**: `openai==0.28.1`（旧）→ 新SDK（`openai>=1.0`）対応 or Z.ai BYOK設定
2. **モデル変更**: `gpt-3.5-turbo` → `gpt-4o-mini`
3. **system_prompt.txt**: 「蛍」→ 農家AIVTuber「ナナカ」設定に書き換え
4. **config/settings.yaml**: APIキー等を集約管理（.envからの移行）
5. **YouTube/OBS**: STEP1では不要 → ダミーコメントでVOIEVOX音声出力まで確認
