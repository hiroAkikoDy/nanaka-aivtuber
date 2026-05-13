# タスク依頼：形式検証結果に基づく高優先度バグ修正

## 前提確認
AGENTS.mdを読んでください。
次に以下のファイルを参照してください：
- docs/formal_verification.md（修正根拠となる検証レポート）
- core/voicevox_adapter.py
- memory/memory_agent.py
- core/run_live.py

---

## 作業概要
`docs/formal_verification.md` のKAOS・Alloy検証で発見された
高優先度4件の修正を実施してください。
**既存の動作を壊さないこと**を最優先とします。

---

## 修正内容

### 修正1：VOICEVOXにtimeout設定を追加
**該当箇所：** `core/voicevox_adapter.py:28-29`
**検証根拠：** KAOSゴールツリー1「VOICEVOXサーバーが応答しない」

```python
# 変更前
response = requests.post(url, ...)

# 変更後
response = requests.post(url, ..., timeout=10)
```

- audio_query・synthesisの両POSTにtimeout=10を追加
- タイムアウト発生時はRequestsExceptionをraiseせず
  ログ出力してNoneを返す graceful degradation を実装
- 呼び出し元でNoneチェックを追加し音声をスキップする

---

### 修正2：speed/pitchパラメータの範囲クランプ
**該当箇所：** `core/voicevox_adapter.py:55-56`
**検証根拠：** Alloyモデル2「speed/pitchパラメータ範囲外リスク」

```python
# 変更前
def create_voice(self, text, speaker_id=None, speed=1.0, pitch=0.0):
    # 範囲チェックなし

# 変更後
SPEED_MIN, SPEED_MAX = 0.5, 2.0
PITCH_MIN, PITCH_MAX = -0.5, 0.5

def create_voice(self, text, speaker_id=None, speed=1.0, pitch=0.0):
    speed = max(SPEED_MIN, min(SPEED_MAX, speed))
    pitch = max(PITCH_MIN, min(PITCH_MAX, pitch))
```

- クランプ時はWARNINGログを出力する
  （例：`[WARNING] speed=2.5 はVOICEVOX許容範囲外。2.0にクランプしました`）
- 定数はファイル先頭に定義する

---

### 修正3：Neo4j接続失敗時のインメモリフォールバック
**該当箇所：** `memory/memory_agent.py:15`
**検証根拠：** KAOSゴールツリー1「Neo4jサーバーが停止する」

```python
# 変更前
def __init__(self):
    self.driver = GraphDatabase.driver(uri, auth=...)
    # エラーハンドリングなし

# 変更後
def __init__(self):
    self._fallback_memory = {}  # インメモリフォールバック
    self._use_fallback = False
    try:
        self.driver = GraphDatabase.driver(uri, auth=...)
        self.driver.verify_connectivity()
    except Exception as e:
        print(f"[WARNING] Neo4j接続失敗: {e}")
        print("[WARNING] インメモリフォールバックで動作します")
        self._use_fallback = True
```

- フォールバック時の `save_interaction()` と `get_memory()` は
  `self._fallback_memory` dict に対して動作する
- フォールバック中はセッション内記憶のみ保持（永続化なし）
- Neo4j復旧時の自動切り戻しは**今回は実装しない**
  （設計が複雑になるため）

---

### 修正4：run_live.pyのコメント処理をtry-exceptでラップ
**該当箇所：** `core/run_live.py:124-162`
**検証根拠：** KAOSゴールツリー1「個別コメント例外がループ全体を停止させる」

```python
# 変更前
for comment in comments:
    viewer_name = comment["author"]
    text = comment["text"]
    # 処理...（例外発生でループ全体が停止）

# 変更後
for comment in comments:
    try:
        viewer_name = comment["author"]
        text = comment["text"]
        # 処理...
    except Exception as e:
        print(f"[ERROR] コメント処理中にエラー: {e}")
        print(f"[ERROR] スキップして次のコメントへ: {comment}")
        continue  # ループを継続
```

- ログにはコメント内容も含める（デバッグ用）
- DummyLiveStreamingSystemにも同様の修正を適用する

---

## 完了条件
- [ ] `core/voicevox_adapter.py` にtimeout=10が追加されている
- [ ] `core/voicevox_adapter.py` にspeed/pitchクランプ処理が追加されている
- [ ] `memory/memory_agent.py` にインメモリフォールバックが実装されている
- [ ] `core/run_live.py` のforループがtry-exceptでラップされている
- [ ] `python core/run_dummy.py` が正常動作すること（既存動作の維持）
- [ ] `python core/run_live.py`（ダミーモード）が正常動作すること
- [ ] `task_queue/done_HOTFIX_formal.md` を作成する
- [ ] `work_reports/WORK_REPORT_YYYYMMDD_HHMM.md` を作成する

## 参照ファイル
- AGENTS.md
- docs/formal_verification.md（修正根拠・詳細はこちら）
- core/voicevox_adapter.py
- memory/memory_agent.py
- core/run_live.py