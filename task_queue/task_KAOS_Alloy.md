Kilocode向け KAOS・Alloy検証プロンプト
markdown# タスク依頼：KAOS・Alloy による要件検証

## 前提確認
AGENTS.md を読んでください。
次に以下のファイルを参照してください：
- work_reports/ 配下の全WORK_REPORT（STEP1〜7の実装経緯）
- agents/emotion_agent.py
- memory/memory_agent.py
- agents/dialogue_coordinator.py
- agents/youtube_agent.py
- config/settings.yaml
- config/personas.yaml
- core/aituber_system.py

---

## 作業内容

### PHASE 1：KAOSゴールツリーの作成

以下の3つのトップゴールについて、KAOSゴールツリーをMarkdown形式で作成してください。

**トップゴール1：配信を継続する**
- サブゴールに分解（YouTube API・VOICEVOX・Neo4j・OBSの各障害モードを含む）
- Obstruction（障害）を現在の実装から洗い出す
- 各Obstructionに対するResolution（対処策）を提案する

**トップゴール2：視聴者との関係を深める**
- 視聴者記憶の一貫性
- ペルソナの一貫性（ナナカ・リョウの役割分担）
- マルチペルソナ会話の品質

**トップゴール3：マルチプラットフォームに対応する**
- YouTube・TikTok同時配信時の競合リスク
- APIクォータ管理
- プラットフォーム間のコメント処理の公平性

**出力形式：**
ゴールツリー：[トップゴール名]
Goal: [ゴール名]

Type: Achieve / Maintain / Avoid
Description: [説明]
SubGoal: [サブゴール名]

...

Obstruction: [障害名]

Source: [該当ファイル・該当箇所]
Resolution: [対処策]




---

### PHASE 2：Alloy仕様の作成と検証

以下の3つのモデルをAlloy言語で記述し、検証してください。

**モデル1：視聴者記憶の一貫性**
検証したい性質：

マルチペルソナモードでナナカの発言のみ保存される仕様は
常に成立するか
同一視聴者の記憶が重複なく蓄積されるか
get_memory()が返す過去3件は常に最新順か


**モデル2：感情状態遷移の完全性**
検証したい性質：

EmotionAgentが返す5ラベル以外の値が
システムに流入しないか
add_conditional_edgesのマッピングに
未定義ラベルが来たときの挙動は安全か
speed/pitchパラメータが
VOICEVOXの許容範囲を超えないか


**モデル3：マルチペルソナ会話の整合性**
検証したい性質：

DialogueCoordinatorのターン順序が
常にナナカ→リョウの交互になるか
turn_limitを超えた会話が
生成されないか
単独モードとマルチペルソナモードが
同時に有効にならないか


**出力形式：**
各モデルについて以下を出力してください。
1. Alloyコード（sig・fact・assert・check）
2. 検証結果（counterexample の有無）
3. 反例が見つかった場合：該当する実装箇所と修正提案
4. 反例がない場合：検証済みの性質として記録

---

### PHASE 3：検証結果サマリーの作成

以下の内容を含む `docs/formal_verification.md` を作成してください。

```markdown
# 形式検証レポート
## 実施日時
## 対象ステップ：STEP1〜7

## KAOSゴールツリー
### 発見されたObstruction一覧
| Obstruction | 該当ファイル | 深刻度 | Resolution |
|---|---|---|---|

### STEP8以降への影響
（マルチプラットフォーム対応で新たに発生するリスク）

## Alloy検証結果
### 検証済みの性質
### 発見された反例と修正提案

## STEP8設計への提言
（KAOSとAlloyの結果から導出された設計上の注意点）
```

---

## 完了条件
- [ ] `docs/formal_verification.md` を作成する
- [ ] KAOSゴールツリー3本が記述されている
- [ ] Alloyモデル3本のコードと検証結果が記載されている
- [ ] STEP8設計への提言が含まれている
- [ ] `task_queue/done_KAOS_Alloy.md` を作成する
- [ ] `work_reports/WORK_REPORT_YYYYMMDD_HHMM.md` を作成する

## 参照ファイル
- AGENTS.md
- work_reports/（全WORK_REPORT）
- agents/（全エージェント）
- config/settings.yaml
- config/personas.yaml
- core/aituber_system.py