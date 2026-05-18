# タスク依頼：実食検証システム（Human-in-the-loop）実装

## 前提確認
AGENTS.mdを読んでください。
次に以下のファイルを参照してください：
- memory/memory_agent.py（AuraDB接続済み）
- config/settings.yaml
- .env
- docs/formal_verification.md

---

## 作業概要
LangGraphのHuman-in-the-loopを使い、
AIVTuberが提案したレシピを配信後に
簡易WebUIで実食評価してAuraDBに保存する
最小構成システムを実装してください。

**今回のスコープ：1品だけ動く最小構成**
複数品対応・配信リアルタイム連携はスコープ外です。

---

## 実装内容

### 1. 状態定義
`agents/recipe_validation_agent.py` を新規作成：

```python
from typing import TypedDict

class RecipeValidationState(TypedDict):
    # レシピ情報
    recipe_name: str
    recipe_id: str
    ai_suggestion: str

    # 実食評価（Human-in-the-loop）
    taste_score: float       # 味 0.0〜5.0
    appearance_score: float  # 見た目 0.0〜5.0
    difficulty_score: float  # 難易度 0.0〜5.0（低いほど簡単）
    feedback_text: str       # 自由記述

    # 自動計算
    overall_score: float     # 加重平均（taste×0.6 + appearance×0.2 + difficulty×0.2）

    # 処理状態
    neo4j_updated: bool
    validated_at: str
```

### 2. LangGraphのグラフ構造
[fetch_recipe]
↓
[suggest_cooking]    AIがコメントを生成
↓
[await_evaluation]   Human-in-the-loop（WebUIで入力待ち）
↓
[calculate_score]    overall_scoreを自動計算
↓
[update_neo4j]       AuraDBのRecipeノードを更新
↓
[END]

### 3. WebUI（Flask）
`core/validation_ui.py` を新規作成：

- アクセス先：`http://localhost:5001`
- 画面構成：
  - レシピ名表示
  - AIの提案コメント表示
  - スライダー or 数値入力（taste/appearance/difficulty）
  - 自由記述テキストエリア
  - 「送信」ボタン
- 送信後：LangGraphの
  `await_evaluation` ノードに値を渡す
- ポート：5001
  （クレソンAI本番との衝突を避けるため）

### 4. AuraDBへの書き込み
`memory/memory_agent.py` に
`save_validation()` メソッドを追加：

```python
def save_validation(self, recipe_name: str, state: dict):
    cypher = """
    MATCH (r:Recipe {name: $recipe_name})
    SET r.taste_score = $taste_score,
        r.appearance_score = $appearance_score,
        r.difficulty_score = $difficulty_score,
        r.overall_score = $overall_score,
        r.validated = true,
        r.validated_at = datetime(),
        r.validation_note = $feedback_text,
        r.validation_count = coalesce(r.validation_count, 0) + 1
    RETURN r.name
    """
```

### 5. 動作確認用スクリプト
`core/run_validation.py` を新規作成：

```python
# 使い方
# 1. python core/run_validation.py を実行
# 2. ブラウザで http://localhost:5001 を開く
# 3. スコアを入力して送信
# 4. AuraDBにRecipeノードが更新されることを確認

# テスト用レシピ名（AuraDBに存在するもの）
TEST_RECIPE = "クレソンサラダ"
```

---

## ディレクトリ構成（追加分）
nanaka-aivtuber/
├── agents/
│   └── recipe_validation_agent.py  ← 新規
├── core/
│   ├── validation_ui.py            ← 新規
│   └── run_validation.py           ← 新規
└── templates/
└── validation.html             ← 新規（FlaskのHTML）

---

## 完了条件
- [ ] `python core/run_validation.py` を実行すると
      `http://localhost:5001` が起動する
- [ ] ブラウザでスコアを入力・送信できる
- [ ] AuraDBの該当Recipeノードに
      `taste_score` / `overall_score` / `validated: true`
      が書き込まれることをNeo4j Browserで確認
- [ ] `run_dummy.py` の既存動作が維持されていること
- [ ] `task_queue/done_VALIDATION_UI.md` を作成する
- [ ] `work_reports/WORK_REPORT_YYYYMMDD_HHMM.md`
      を作成する

## 注意事項
- AuraDBに `Recipe {name: "クレソンサラダ"}` が
  存在しない場合は `MERGE` で作成してよい
- Flask のポートは **5001** を使用する
- LangGraphの `interrupt()` を使って
  WebUIからの入力を待機する設計にすること
- 既存ファイル（memory_agent.py等）への
  変更は最小限にすること

## 参照ファイル
- AGENTS.md
- agents/emotion_agent.py（LangGraph実装の参考）
- memory/memory_agent.py（AuraDB接続の参考）
- config/settings.yaml