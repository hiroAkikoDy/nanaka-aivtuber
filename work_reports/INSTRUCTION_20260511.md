# 明日の作業指示書

**作成日**: 2026-05-11
**対象**: 古閑 弘晃（開発者）
**プロジェクト**: nanaka-aivtuber（農家AIVTuber開発）

---

## 📊 現在の状況（2026-05-11 終了時点）

### 完了済みステップ
| STEP | 内容 | 完了日時 |
|------|------|---------|
| ✅ STEP 1 | 最小構成AIVTuber | — |
| ✅ STEP 2 | LangChainプロンプト管理 | 2026-05-08 19:56 |
| ✅ STEP 3 | 感情状態管理（LangGraph） | 2026-05-09 12:32 |
| ✅ STEP 3.5 | add_conditional_edges実践 | 2026-05-10 00:01 |
| ✅ STEP 4 | Neo4j視聴者記憶 | 2026-05-11 12:22 |

### 実装済み機能
- ✅ VOICEVOX音声合成（感情別パラメータ調整付き）
- ✅ OpenAI LLM連携（emotion/memory変数注入）
- ✅ 感情分析（5種類：嬉しい/ワクワク/驚き/悲しい/普通）
- ✅ Neo4j視聴者記憶（過去3件の会話履歴保持）
- ✅ Gitコミット完了（コミットID: e84bb1e）

### プロジェクト管理状態
- ✅ done_0001.md 〜 done_0004.md 作成済み
- ✅ AGENTS.md 更新済み（STEP4完了まで反映）
- ✅ 全変更がGitコミット済み

---

## 🎯 明日の作業目標

### STEP5: マルチペルソナ配信機能の実装
**目的**: 農家AIVTuber（ナナカ）とシェフAIVTuber（リョウ）が会話する機能を実装

**期待される成果物**:
1. 2つのペルソナが交互に会話するシステム
2. ペルソナごとに異なる声（VOICEVOX speaker_id）
3. 役割分担（ナナカ=栽培、リョウ=料理）が明確な会話

---

## 📋 明日やるべきこと

### 手順1: 環境確認（作業開始前）
```bash
# 1. プロジェクトディレクトリに移動
cd "C:\Users\Koga Hiroaki\Desktop\hiroaki_\workingFolder\nanaka-aivtuber"

# 2. Gitの状態確認（cleanであることを確認）
git status

# 3. 最新コミット確認
git log -1 --oneline

# 4. VOICEVOX起動確認
# → デスクトップからVOICEVOXを起動
# → ブラウザで http://localhost:50021/docs にアクセスして動作確認

# 5. Neo4j起動確認
# → Neo4j Desktopを起動
# → nanaka-aivtuber データベースを起動
# → ブラウザで http://localhost:7474 にアクセスして動作確認
```

### 手順2: task_0005.mdをkilocodeに送信
1. `task_queue/task_0005.md` を開く
2. 内容を確認（今日作成済み）
3. kilocodeに全文を送信
4. 「このタスクを実装してください」と指示

### 手順3: kilokode作業中の確認ポイント
以下のファイルが作成・変更されているか随時確認：

**新規作成されるファイル**:
- [ ] `config/personas.yaml`
- [ ] `agents/persona_agent.py`
- [ ] `agents/dialogue_coordinator.py`

**変更されるファイル**:
- [ ] `config/settings.yaml` — multi_persona設定追加
- [ ] `core/voicevox_adapter.py` — speaker_id動的指定対応
- [ ] `core/aituber_system.py` — マルチペルソナモード追加
- [ ] `core/run_dummy.py` — マルチペルソナ対応コメント

### 手順4: 動作確認（kilokode完了後）
```bash
# 単独モードの動作確認（既存機能が壊れていないか）
cd core
python run_dummy.py
# → ナナカのみが話す（STEP4と同じ動作）

# マルチペルソナモードの動作確認
# → config/settings.yaml で multi_persona.enabled: true に変更
python run_dummy.py
# → ナナカとリョウが交互に話す
# → 異なる声で音声が再生される
```

### 手順5: 完了確認
- [ ] ダミーコメント5件すべてで音声出力成功
- [ ] ナナカとリョウの会話が自然
- [ ] 役割分担が明確（ナナカ=栽培、リョウ=料理）
- [ ] done_0005.md が作成されている
- [ ] WORK_REPORT_YYYYMMDD_HHMM.md が作成されている

### 手順6: Gitコミット
```bash
git status
git add .
git commit -m "feat: STEP5 マルチペルソナ配信機能の実装

- PersonaAgent実装（ナナカ・リョウ）
- DialogueCoordinator実装（会話調整）
- personas.yaml追加（ペルソナ定義）
- VOICEVOX speaker_id動的指定対応
- マルチペルソナモード/単独モード切り替え

動作確認:
- 単独モード: 既存機能が正常動作
- マルチペルソナモード: 4ターンの会話生成成功
- 異なる声（speaker_id）での音声再生成功

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## ⚠️ 注意事項

### VOICEVOX speaker_idについて
- **ナナカ**: 46（四国めたん）— 既存
- **リョウ**: 推奨は 3（ずんだもん）または 8（春日部つむぐ）
- **確認方法**: http://localhost:50021/speakers でspeaker一覧を確認

### kilokodeへの指示のコツ
- タスクが大きいので、エラーが出たら焦らず対処
- 「このエラーを修正してください」と具体的に指示
- 途中経過を定期的に確認する

### つまずきそうなポイント
1. **speaker_idの指定ミス**
   - VOICEVOXが起動していないとspeaker一覧が取得できない
   - 存在しないspeaker_idを指定すると音声生成エラー

2. **会話が不自然**
   - personas.yamlのsystem_promptを調整
   - 「相手の発言を踏まえて応答してください」を追加

3. **ターン数の制御**
   - turn_limitを超えないようにループを確認
   - 無限ループに注意

---

## 📚 参考情報

### 前プロジェクト「クレソンAI」
- URL: https://github.com/hiroAkikoDy/hiroAkikoDy-watercress_cheff_ai
- Phase 4b でマルチペルソナ実装済み
- 必要に応じて参考にする

### LangChain Ch12 の学習ポイント
- マルチエージェント設計
- コンテキスト管理（会話履歴の引き継ぎ）
- ペルソナエンジニアリング

### AGENTS.md の重要情報
- プロジェクト概要
- 開発者情報（あなたのスキル・経験）
- コーディングルール
- 作業レポート作成方法

---

## 💡 作業開始時のチェックリスト

作業開始前に以下を確認してください：

- [ ] VOICEVOX が起動している（port 50021）
- [ ] Neo4j が起動している（port 7474/7687）
- [ ] `git status` がclean
- [ ] `task_queue/task_0005.md` の内容を理解している
- [ ] 今日の体調・集中力は良好
- [ ] 作業時間の確保（推奨: 2〜3時間）

---

## 🚀 STEP5完了後の展望

STEP5が完了すると、以下が実現します：

### 機能面
- 単一AIVTuberから複数AIVTuberへの進化
- より深い情報提供（栽培×料理の両視点）
- 娯楽性の向上（会話のやりとり）

### 技術面
- LangChain Ch12 の習得
- マルチエージェント設計の実践
- ペルソナエンジニアリングの理解

### 次のステップ（STEP6以降）
- YouTube Live 配信連携
- OBS連携（画面表示）
- リアルタイムコメント取得
- 3人以上のペルソナ追加

---

## 📝 作業中のメモ欄

作業中に気づいたこと、改善案、疑問点をここにメモしてください：

```
【メモ】




【改善案】




【疑問点・調査事項】




```

---

## 📞 困ったときは

### エラーが解決しない場合
1. エラーメッセージをkilocodeに送る
2. 「このエラーを修正してください」と指示
3. それでも解決しない場合は、AGENTS.mdを再確認

### 時間がかかりすぎる場合
- STEP5は大きなタスクなので、1日で完了しなくてもOK
- 途中経過をwork_reportに記録
- 翌日に続きを実施

### 実装の方向性が不安な場合
- 前プロジェクト「クレソンAI」を参考にする
- task_0005.mdの「学習ポイント」を再確認

---

## ✅ 作業終了時のチェックリスト

作業終了時に以下を確認してください：

- [ ] done_0005.md が作成されている
- [ ] WORK_REPORT_YYYYMMDD_HHMM.md が作成されている
- [ ] Gitコミットが完了している
- [ ] AGENTS.md が更新されている（STEP5完了を反映）
- [ ] 動作確認が完了している（単独モード・マルチペルソナモード両方）
- [ ] 明日以降の作業が必要な場合、メモを残している

---

頑張ってください！ナナカとリョウの楽しい会話を実現しましょう！🌱👨‍🍳
