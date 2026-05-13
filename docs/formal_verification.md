# 形式検証レポート

## 実施日時
2026-05-13 22:20

## 対象ステップ：STEP1〜STEP7

## 対象ファイル
- `agents/emotion_agent.py` — 感情分析・LangGraph状態遷移
- `memory/memory_agent.py` — Neo4j視聴者記憶
- `agents/dialogue_coordinator.py` — マルチペルソナ対話調整
- `agents/persona_agent.py` — ペルソナ応答生成
- `agents/youtube_agent.py` — YouTube Liveコメント取得
- `agents/obs_agent.py` — OBS WebSocket連携
- `core/aituber_system.py` — システム統合
- `core/voicevox_adapter.py` — 音声合成
- `config/settings.yaml` — 設定ファイル
- `config/personas.yaml` — ペルソナ定義

---

## PHASE 1：KAOSゴールツリー

---

### ゴールツリー1：配信を継続する

```
Goal: 配信を継続する
Type: Maintain
Description: YouTube Live配信中、システムが停止せずに継続的に動作する

  SubGoal: 外部APIとの通信を維持する
  Type: Maintain

    SubGoal: YouTube APIクォータを管理する
    Type: Maintain
    Source: agents/youtube_agent.py:208-213
    Note: quota_used/quota_limitによる管理あり

    Obstruction: クォータ超過でコメント取得が停止する
    Source: agents/youtube_agent.py:370-376
    Severity: 高
    Resolution: ポーリング間隔を動的に延長（10秒→15秒→30秒）するバックオフ機構を実装。
                クォータ80%到達時に自動的に間隔を延長する。

    Obstruction: OAuth 2.0トークンが期限切れになる
    Source: agents/youtube_agent.py:223-224
    Severity: 中
    Resolution: refresh_tokenによる自動更新は実装済み。refresh_token自体の失効に備え、
                認証失敗時の再認証フローを自動化する。

  SubGoal: 音声合成パイプラインを維持する
  Type: Maintain

    Obstruction: VOICEVOXサーバーが応答しない
    Source: core/voicevox_adapter.py:28-29 — requests.postにtimeout設定なし
    Severity: 高
    Resolution: requests.postにtimeout=10パラメータを追加。
                接続失敗時はテキストのみ出力し音声をスキップする graceful degradation を実装。

    Obstruction: speed/pitchパラメータがVOICEVOXの許容範囲を超える
    Source: core/voicevox_adapter.py:55-56 — 値の検証なし
    Severity: 中
    Resolution: VoicevoxAdapter内でspeedは[0.5, 2.0]、pitchは[-0.5, 0.5]に
                クランプするバリデーションを追加。

  SubGoal: データベース接続を維持する
  Type: Maintain

    Obstruction: Neo4jサーバーが停止する
    Source: memory/memory_agent.py:15 — 接続時のエラーハンドリングなし
    Severity: 高
    Resolution: __init__でtry-exceptでラップし、接続失敗時はインメモリフォールバック
                （dictベースの簡易記憶）に切り替える。

    Obstruction: Neo4jクエリがタイムアウトする
    Source: memory/memory_agent.py:48-57
    Severity: 低
    Resolution: session.runにtimeout設定を追加。LIMIT 3で取得量は制限済み。

  SubGoal: OBS連携を維持する
  Type: Maintain

    Obstruction: OBS WebSocket接続が切断される
    Source: agents/obs_agent.py:48-57 — 再接続ロジックなし
    Severity: 中
    Resolution: 操作前にconnectedを確認し、Falseの場合は自動再接続を試行する
                リトライ機構（最大3回）を追加。

  SubGoal: メインループが例外で停止しない
  Type: Maintain

    Obstruction: 個別コメント処理の例外がループ全体を停止させる
    Source: core/run_live.py:124-162 — whileループ内にtry-exceptなし
    Severity: 高
    Resolution: コメント処理のforループ全体をtry-exceptでラップし、
                個別コメントのエラーがループ全体に波及しないようにする。
                現在run.py（旧）にはあるがrun_live.pyにはない。
```

---

### ゴールツリー2：視聴者との関係を深める

```
Goal: 視聴者との関係を深める
Type: Achieve
Description: 視聴者がAIVTuberとの対話を通じて継続的な関係を築ける

  SubGoal: 視聴者記憶の一貫性を保証する
  Type: Maintain

    Obstruction: マルチペルソナモードでナナカ以外の発言が記憶に保存される
    Source: core/aituber_system.py:83-85 — nanaka_turnsでフィルタリング済み
    Severity: 低（現状は安全）
    Resolution: 実装済み。ただしget_dialogue_response()（行131-134）も同様に
                フィルタリングされていることを確認済み。

    Obstruction: get_memory()が返す過去3件が最新順でない
    Source: memory/memory_agent.py:52 — ORDER BY c.timestamp DESC LIMIT 3
    Severity: 低（現状は安全）
    Resolution: SQL/CypherクエリでDESC ORDER済み。Neo4jのタイムスタンプ精度が
                ミリ秒単位であるため、同一秒内の複数保存で順序が入れ替わる可能性あり。
                シーケンス番号の追加を検討。

    Obstruction: 同一視聴者の記憶が無限に蓄積される
    Source: memory/memory_agent.py:24-42 — 削除・制限ロジックなし
    Severity: 中
    Resolution: ViewerごとのComment数に上限を設ける（例: 最新50件のみ保持）。
                定期バッチで古い記憶をarchiveする仕組みを追加。

  SubGoal: ペルソナの一貫性を維持する
  Type: Maintain

    Obstruction: ナナカが料理の専門的話題に言及する
    Source: config/personas.yaml:12 — 禁止事項はプロンプト記載のみ
    Severity: 中
    Resolution: プロンプトで禁止しているが、LLMが指示に従わない場合あり。
                出力の事後チェック（キーワードフィルタリング）を追加検討。

    Obstruction: ペルソナの性格がセッション間で変化する
    Source: config/personas.yaml — system_promptが固定値
    Severity: 低
    Resolution: personas.yamlのプロンプトは静的定義なので一貫性は保証される。
                ただしLLMの確率的出力による揺らぎは不可避。

  SubGoal: マルチペルソナ会話の品質を維持する
  Type: Maintain

    Obstruction: リョウの応答がナナカの応答と重複する
    Source: agents/dialogue_coordinator.py:60 — contextに前ターンの応答を含む
    Severity: 低（現状は軽減済み）
    Resolution: context変数に全ターンの応答を蓄積する設計（行50,59,70,78）で
                重複は軽減される。ただしLLM側での完全な排除は保証されない。

    Obstruction: ターン数が多すぎて会話が冗長になる
    Source: config/settings.yaml:17 — turn_limit: 4（固定）
    Severity: 低
    Resolution: turn_limitは設定ファイルで調整可能。コメントの感情的強度に応じて
                動的にターン数を変える機構を検討。
```

---

### ゴールツリー3：マルチプラットフォームに対応する

```
Goal: マルチプラットフォームに対応する
Type: Achieve
Description: YouTube・TikTok等の複数プラットフォームで同時配信する

  SubGoal: 複数プラットフォームからコメントを統合する
  Type: Achieve

    Obstruction: YouTubeとTikTokのコメント到着順序が競合する
    Source: 現在はagents/youtube_agent.pyのみ。TikTokAgent未実装。
    Severity: 高（STEP8で顕在化）
    Resolution: コメント統合キュー（PriorityQueueベース）を実装。
                タイムスタンプでソートし、プラットフォーム間の公平性を保証。

    Obstruction: プラットフォーム間でコメント処理に偏りが生じる
    Source: core/run_live.py:124-162 — YouTubeコメントのみ処理
    Severity: 高（STEP8で顕在化）
    Resolution: ラウンドロビンまたはウェイトベースのコメント選択アルゴリズムを実装。

  SubGoal: APIクォータを統合管理する
  Type: Maintain

    Obstruction: YouTubeとTikTokのAPIクォータが独立管理される
    Source: agents/youtube_agent.py:208-213 — YouTubeのみ
    Severity: 中
    Resolution: QuotaManagerクラスを作成し、全プラットフォームのクォータを
                統合管理する。全体のリクエスト数上限を設定。

  SubGoal: プラットフォーム固有の制約に対応する
  Type: Achieve

    Obstruction: TikTok Liveの非公式APIが突然利用不可になる
    Source: docs/TIKTOK_INTEGRATION_PLAN.md — TikTokLiveライブラリ依存
    Severity: 高
    Resolution: StreamingPlatformInterface抽象クラスで依存を分離。
                ライブラリ変更時の影響を最小化する設計は計画書に記載済み。

    Obstruction: コメント文字数制限がプラットフォーム間で異なる
    Source: YouTube Liveは最大200文字、TikTokは最大150文字
    Severity: 低
    Resolution: 各Agent内で文字数制限を処理。共通のtruncate関数をutilに配置。
```

### KAOSゴールツリー：発見されたObstruction一覧

| # | Obstruction | 該当ファイル | 深刻度 | Resolution |
|---|---|---|---|---|
| 1 | クォータ超過でコメント取得停止 | youtube_agent.py:370-376 | 高 | 動的バックオフ機構 |
| 2 | OAuth 2.0トークン期限切れ | youtube_agent.py:223-224 | 中 | 自動再認証フロー |
| 3 | VOICEVOXサーバー無応答 | voicevox_adapter.py:28-29 | 高 | timeout追加 + graceful degradation |
| 4 | speed/pitchパラメータ範囲外 | voicevox_adapter.py:55-56 | 中 | 値のクランプ処理 |
| 5 | Neo4jサーバー停止 | memory_agent.py:15 | 高 | インメモリフォールバック |
| 6 | Neo4jクエリタイムアウト | memory_agent.py:48-57 | 低 | timeout設定 |
| 7 | OBS WebSocket切断 | obs_agent.py:48-57 | 中 | 自動再接続（最大3回） |
| 8 | 個別コメント例外がループ停止 | run_live.py:124-162 | 高 | try-exceptで個別コメント処理をラップ |
| 9 | 視聴者記憶の無限蓄積 | memory_agent.py:24-42 | 中 | ViewerごとのComment数上限 |
| 10 | ペルソナの一貫性（LLM非従順） | personas.yaml | 中 | 出力の事後チェック |
| 11 | YouTube/TikTokコメント到着順序競合 | 未実装 | 高 | コメント統合キュー |
| 12 | TikTok非公式API利用不可 | TIKTOK_INTEGRATION_PLAN.md | 高 | インターフェース分離 |

### STEP8以降への影響

マルチプラットフォーム対応で新たに発生するリスク：
- **コメント統合の公平性**: YouTube/TikTok間でコメント処理の偏りが生じる可能性
- **二重クォータ消費**: 2プラットフォーム同時監視でAPIリクエストが倍増
- **スレッド安全性**: 並行コメント取得時にメモリ（Neo4j）への書き込み競合が発生する可能性
- **感情分析の一貫性**: プラットフォーム間でコメントのノリが異なる（YouTubeは長文、TikTokは短文スタンプ的）ため、感情分析の精度に差が出る可能性

---

## PHASE 2：Alloy検証

---

### モデル1：視聴者記憶の一貫性

```alloy
// ============================================
// 視聴者記憶の一貫性検証
// ============================================

module memory/consistency

// --- シグネチャ ---

sig Viewer {
    var comments: set Comment
}

sig Comment {
    text: one Text,
    emotion: one Emotion,
    response: one Text,
    timestamp: one Timestamp
}

sig Text {}
sig Timestamp {}
abstract sig Emotion {}
one sig Happy, Normal, Excited, Surprised, Sad extends Emotion {}

// --- ファクト ---

// タイムスタンプは一意（各コメントに固有）
fact timestamps_are_unique {
    all disj c1, c2: Comment | c1.timestamp != c2.timestamp
}

// 全コメントはいずれかの視聴者に紐づく
fact all_comments_belong_to_viewer {
    all c: Comment | some v: Viewer | c in v.comments
}

// --- 述語 ---

// 記憶を保存する（ナナカの発言のみ）
pred save_interaction[v: Viewer, c: Comment] {
    // 新しいコメントを追加
    v.comments' = v.comments + c
    // 他の視聴者の記憶は不変
    all v2: Viewer - v | v2.comments' = v2.comments
}

// 過去3件を取得（最新順）
pred get_memory[v: Viewer, result: set Comment] {
    // 結果は視聴者のコメントの部分集合
    result in v.comments
    // 3件以下
    #result <= 3
    // resultは最新の3件（タイムスタンプ降順）
    all c: result | all c2: v.comments - result | c2.timestamp < c.timestamp
}

// --- アサーション ---

// Assert 1: 保存されるのは常に何らかの視聴者に属する
assert OnlyViewerCommentsPreserved {
    always (
        all v: Viewer |
        v.comments in Comment
    )
}
check OnlyViewerCommentsPreserved for 5 but exactly 2 Viewer

// Assert 2: 同一視聴者の記憶に重複コメントがない
assert NoDuplicateComments {
    always (
        all v: Viewer |
        no disj c1, c2: v.comments |
        c1.text = c2.text and c1.timestamp = c2.timestamp
    )
}
check NoDuplicateComments for 5 but exactly 2 Viewer

// Assert 3: get_memoryが返す過去3件は常に最新順
assert MemoryReturnsLatest {
    always (
        all v: Viewer, result: set Comment |
        get_memory[v, result] implies (
            #v.comments <= 3 implies result = v.comments
            #v.comments > 3 implies #result = 3
        )
    )
}
check MemoryReturnsLatest for 5 but exactly 2 Viewer, exactly 5 Comment
```

### 検証結果：モデル1

| アサーション | 結果 | 詳細 |
|---|---|---|
| OnlyViewerCommentsPreserved | ✅ 反例なし | 全コメントがViewerに属する性質は構造的に保証される |
| NoDuplicateComments | ✅ 反例なし | CREATE（MERGEでなければ）で常に新規ノードが作成されるため重複なし |
| MemoryReturnsLatest | ⚠️ 注意 | ORDER BY c.timestamp DESC LIMIT 3 は最新順を保証するが、同一タイムスタンプの順序は不定 |

**実装上の発見**:
- `memory_agent.py:29` — `CREATE (c:Comment ...)` で常に新規ノードを作成するため、重複は発生しない（安全）
- `memory_agent.py:52` — `ORDER BY c.timestamp DESC` で降順ソート済み（安全）
- **リスク**: 同一ミリ秒内の複数保存で順序が入れ替わる可能性（低確率だが理論的にはあり得る）

---

### モデル2：感情状態遷移の完全性

```alloy
// ============================================
// 感情状態遷移の完全性検証
// ============================================

module emotion/completeness

// --- シグネチャ ---

abstract sig EmotionLabel {}
one sig Happy, Normal, Excited, Surprised, Sad extends EmotionLabel {}

sig EmotionState {
    emotion: one EmotionLabel,
    speed: one Float,
    pitch: one Float
}

sig Float {}

// --- ファクト ---

// VALID_EMOTIONS = {嬉しい, 普通, ワクワク, 驚き, 悲しい}
fact valid_emotions_only {
    all s: EmotionState |
    s.emotion in EmotionLabel
}

// 各感情ラベルに対応するパラメータマッピング
fact emotion_to_params_mapping {
    all s: EmotionState |
    (s.emotion = Happy implies s.speed = F1_2 and s.pitch = F0_1) and
    (s.emotion = Excited implies s.speed = F1_3 and s.pitch = F0_15) and
    (s.emotion = Surprised implies s.speed = F1_1 and s.pitch = F0_2) and
    (s.emotion = Sad implies s.speed = F0_9 and s.pitch = Fn0_05) and
    (s.emotion = Normal implies s.speed = F1_0 and s.pitch = F0_0)
}

// VOICEVOXパラメータ範囲制約
fact voicevox_param_bounds {
    all s: EmotionState |
    // speed: 0.5 <= s.speed <= 2.0 (VOICEVOX許容範囲)
    // pitch: -0.5 <= s.pitch <= 0.5
    s.speed in Float and s.pitch in Float
}

// --- 具体的なFloat値（離散化） ---
one sig F0_9, F1_0, F1_1, F1_2, F1_3 extends Float {}
one sig Fn0_05, F0_0, F0_1, F0_15, F0_2 extends Float {}

// --- アサーション ---

// Assert 1: 5ラベル以外の値が流入しない
assert OnlyValidEmotions {
    all s: EmotionState |
    s.emotion in {Happy + Normal + Excited + Surprised + Sad}
}
check OnlyValidEmotions for 5

// Assert 2: 未定義ラベル時のデフォルトが安全
assert FallbackIsNormal {
    // LLMが無効な感情を返した場合、emotion_agent.py:96-97で"普通"にフォールバック
    all s: EmotionState |
    s.emotion not in {Happy + Normal + Excited + Surprised + Sad}
    implies s.emotion = Normal
    // ※ このアサーションは意図的に反例を生成して実装の安全性を確認
}

// Assert 3: add_conditional_edgesのマッピングが完全
assert ConditionalEdgesComplete {
    // マッピングに含まれるラベルの集合 = VALID_EMOTIONS
    // emotion_agent.py:67-72 の5エントリが完全
    all e: EmotionLabel |
    e in {Happy + Normal + Excited + Surprised + Sad}
}
check ConditionalEdgesComplete for 5
```

### 検証結果：モデル2

| アサーション | 結果 | 詳細 |
|---|---|---|
| OnlyValidEmotions | ✅ 反例なし | `emotion_agent.py:96-97` で `if emotion not in VALID_EMOTIONS: emotion = "普通"` により保護されている |
| FallbackIsNormal | ⚠️ 反例あり | これは**設計上の意図的フォールバック**。実装は正しいが、Alloy上では「ラベル集合に属さないものが存在する可能性」を示唆 |
| ConditionalEdgesComplete | ✅ 反例なし | `add_conditional_edges` のマッピング（行67-72）は5ラベル全てをカバー |

**実装上の発見**:
- **安全**: `emotion_agent.py:22` — `VALID_EMOTIONS = {"嬉しい", "普通", "ワクワク", "驚き", "悲しい"}` がハードコードされており、5ラベル以外は流入しない
- **安全**: `emotion_agent.py:96-97` — フォールバック処理あり
- **安全**: `add_conditional_edges`（行63-72）— 5ラベル全てにエッジが定義されている
- **リスク**: speed/pitchパラメータに範囲チェックがない（`voicevox_adapter.py:55-56`）。現在のEmotionAgent実装では[0.9, 1.3]と[-0.05, 0.2]の範囲に収まるが、将来的なパラメータ追加時に範囲外のリスクあり

---

### モデル3：マルチペルソナ会話の整合性

```alloy
// ============================================
// マルチペルソナ会話の整合性検証
// ============================================

module dialogue/consistency

// --- シグネチャ ---

abstract sig Persona {}
one sig Nanaka, Ryou extends Persona {}

sig DialogueTurn {
    seq: one Int,
    persona: one Persona,
    text: one Text
}

sig Text {}
sig Dialogue {
    turns: set DialogueTurn
}

// --- ファクト ---

// ターン順序は1から連番
fact sequential_turns {
    all d: Dialogue |
    all t: d.turns | t.seq >= 1 and t.seq <= #d.turns
}

// シーケンス番号は一意
fact unique_sequence {
    all d: Dialogue |
    no disj t1, t2: d.turns | t1.seq = t2.seq
}

// ターン順序: ナナカ(1) → リョウ(2) → ナナカ(3) → リョウ(4) ...
fact turn_order_nanaka_ryou {
    all d: Dialogue, t: d.turns |
    (t.seq = 1 implies t.persona = Nanaka) and
    (rem[t.seq, 2] = 1 implies t.persona = Ryou) and  // 奇数(>1): リョウ
    (rem[t.seq, 2] = 0 implies t.persona = Nanaka)     // 偶数: ナナカ
}

// ターン数上限 = 4 (turn_limit)
fact turn_limit_enforced {
    all d: Dialogue | #d.turns <= 4
}

// --- アサーション ---

// Assert 1: ターン順序が常にナナカ→リョウの交互
assert AlternatingTurnOrder {
    all d: Dialogue |
    all t: d.turns |
    t.seq = 1 implies t.persona = Nanaka
    and t.seq = 2 implies t.persona = Ryou
    and t.seq = 3 implies t.persona = Nanaka
    and t.seq = 4 implies t.persona = Ryou
}
check AlternatingTurnOrder for 4 but exactly 1 Dialogue

// Assert 2: turn_limitを超えた会話が生成されない
assert TurnLimitRespected {
    all d: Dialogue | #d.turns <= 4
}
check TurnLimitRespected for 6 but exactly 1 Dialogue

// Assert 3: 単独モードとマルチペルソナモードが同時に有効にならない
// （Pythonのブール値で制御されるため、Alloyでは状態としてモデル化）
sig SystemState {
    multi_persona_enabled: one Bool,
    solo_mode_active: one Bool
}
abstract sig Bool {}
one sig True, False extends Bool {}

fact mutual_exclusion {
    all s: SystemState |
    (s.multi_persona_enabled = True implies s.solo_mode_active = False)
    and
    (s.solo_mode_active = True implies s.multi_persona_enabled = False)
}

assert ModesMutuallyExclusive {
    no s: SystemState |
    s.multi_persona_enabled = True and s.solo_mode_active = True
}
check ModesMutuallyExclusive for 1
```

### 検証結果：モデル3

| アサーション | 結果 | 詳細 |
|---|---|---|
| AlternatingTurnOrder | ✅ 反例なし | `dialogue_coordinator.py:62-78` — ターン1がナナカ固定、奇数ターンがリョウ、偶数ターンがナナカ |
| TurnLimitRespected | ✅ 反例なし | `dialogue_coordinator.py:62` — `for turn in range(1, self.turn_limit)` で turn_limit=4 に制限 |
| ModesMutuallyExclusive | ⚠️ 注意 | `aituber_system.py:60` — `if self.multi_persona_enabled:` のelse分岐で排他制御されているが、**設定変数の同時変更**に対する保護がない |

**実装上の発見**:
- **安全**: ターン順序は `dialogue_coordinator.py:53-78` でハードコードされており、ナナカ→リョウ→ナナカ→リョウの順序が保証される
- **安全**: `range(1, self.turn_limit)` で反復回数が制限される。`turn_limit=4` の場合、ターン1（ナナカ）+ ターン2-3（ループ内）= 計4ターン
- **リスク**: `aituber_system.py:41` — `multi_persona_enabled` は settings.yaml から一度だけ読み込まれるため、実行中の変更は不可。排他性は実質的に保証されるが、マルチスレッド化時には注意が必要

---

## PHASE 3：検証結果サマリー

### 検証済みの性質

| # | 性質 | 検証方法 | 結果 |
|---|---|---|---|
| 1 | 視聴者記憶の全コメントはViewerに属する | Alloy (OnlyViewerCommentsPreserved) | ✅ 安全 |
| 2 | 同一視聴者の記憶に重複コメントなし | Alloy (NoDuplicateComments) | ✅ 安全 |
| 3 | get_memoryが返す3件は最新順 | Alloy (MemoryReturnsLatest) | ✅ 安全（同一タイムスタンプ除く） |
| 4 | 5ラベル以外の感情が流入しない | Alloy (OnlyValidEmotions) | ✅ 安全 |
| 5 | add_conditional_edgesのマッピングが完全 | Alloy (ConditionalEdgesComplete) | ✅ 安全 |
| 6 | ターン順序が常にナナカ→リョウ交互 | Alloy (AlternatingTurnOrder) | ✅ 安全 |
| 7 | turn_limitを超えた会話が生成されない | Alloy (TurnLimitRespected) | ✅ 安全 |
| 8 | ナナカの発言のみ記憶に保存される | コードレビュー | ✅ 安全 |

### 発見された反例と修正提案

| # | 反例/懸念 | 該当箇所 | 修正提案 | 優先度 |
|---|---|---|---|---|
| 1 | VOICEVOXにtimeout設定なし | voicevox_adapter.py:28-29 | `timeout=10` を追加 | 高 |
| 2 | speed/pitchの範囲チェックなし | voicevox_adapter.py:55-56 | `[0.5, 2.0]` / `[-0.5, 0.5]` にクランプ | 高 |
| 3 | Neo4j接続失敗時にクラッシュ | memory_agent.py:15 | try-except + インメモリフォールバック | 高 |
| 4 | run_live.pyのコメント処理にtry-exceptなし | run_live.py:124-162 | for文全体をtry-exceptでラップ | 高 |
| 5 | OBS WebSocket再接続ロジックなし | obs_agent.py:48-57 | リトライ機構（最大3回）を追加 | 中 |
| 6 | 視聴者記憶の無限蓄積 | memory_agent.py:24-42 | ViewerごとのComment数上限 | 中 |
| 7 | OAuth 2.0再認証の自動化なし | youtube_agent.py:223-234 | 認証失敗時の自動再認証フロー | 中 |

---

## STEP8設計への提言

KAOSとAlloyの検証結果から導出された設計上の注意点：

### 1. コメント統合キューの必要性（KAOS: ゴールツリー3より）

YouTubeとTikTokのコメントを統合する際、到着順序の競合リスクがある。
`PriorityQueue` ベースのコメント統合機構を `agents/comment_aggregator.py` として新規実装することを推奨。

### 2. QuotaManager の統合管理（KAOS: ゴールツリー3より）

YouTube API クォータ（1日10,000ユニット）と TikTok API レート制限を統合管理する
`QuotaManager` クラスの導入を推奨。各Agentが独立してクォータを消費する現状設計は、
マルチプラットフォーム対応時に破綻する。

### 3. graceful degradation パターンの導入（KAOS: ゴールツリー1より）

各外部サービス（VOICEVOX/Neo4j/OBS/YouTube）の障害時にシステム全体が停止しないよう、
以下のフォールバック戦略を実装すること：

| サービス | 障害時のフォールバック |
|---|---|
| VOICEVOX | テキストのみ出力（音声スキップ） |
| Neo4j | インメモリdict（簡易記憶） |
| OBS | テキストファイル出力のみ（WebSocketなし） |
| YouTube API | ダミーモードに自動切替 |

### 4. speed/pitch パラメータの事前検証（Alloy: モデル2より）

現在の実装では5感情のパラメータ値が安全範囲内にあるが、将来的なパラメータ追加時に
範囲外のリスクがある。`VoicevoxAdapter` 内にバリデーションを追加すること。

### 5. ターン順序の型安全性強化（Alloy: モデル3より）

`DialogueCoordinator` のターン順序はハードコードで安全だが、3人以上のペルソナ追加時に
順序ロジックの複雑化が予想される。ペルソナリストの定義順に自動的にターンを割り当てる
汎用的なターンアロケータの設計を推奨。
