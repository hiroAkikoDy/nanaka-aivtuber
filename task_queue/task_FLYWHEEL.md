# タスク依頼：RAG重み付け組み込み（フライホイール完成）
# Phase 2・Phase 3 実装

## 前提確認
以下を読んでください：
- watercress_cheff_ai/ の AGENTS.md（INV確認必須）
- app/routes/review.py（既存レビュー画面の構造）
- agents/base.py（エージェント共通基盤）

---

## 背景・現状

### AuraDBの現状（2026-05-18時点）
- RecipeノードのPhase 1スコア設定は完了済み
  - 実食済み：`final_score = overall_score / 5.0`
  - 未検証：`final_score = confidence × 0.7`（0.6相当）
- クレソンサラダ（実食済み）:
  `overall_score: 4.3, final_score: 0.86, validated: true`
- その他レシピ（未検証）:
  `confidence: 0.9, final_score: 0.63, validated: false`

### 目標
AIVTuberで実食評価した高スコアレシピが
クレソンAIのRAG検索で優先して返されるように
フライホイールを完成させる。

---

## Phase 2：クレソンAIのRetriever修正

### 対象ファイルの確認
まず以下を確認してください：
- クレソンAIのRAG検索処理ファイル
  （app/routes/ または langchain_study/ 配下）
- Retrieverの実装箇所（Neo4jとベクトル検索の
  組み合わせ部分）

### 変更内容

#### Step 2-1：Recipeノードの検索にfinal_scoreを追加

既存のCypherクエリに `final_score` による
並び替えを追加してください：

```cypher
# 変更前（イメージ）
MATCH (r:Recipe)
WHERE r.name CONTAINS $keyword
RETURN r

# 変更後（イメージ）
MATCH (r:Recipe)
WHERE r.name CONTAINS $keyword
RETURN r
ORDER BY
  CASE WHEN r.validated = true
    THEN r.final_score
    ELSE coalesce(r.final_score, 0.45)
  END DESC
LIMIT 10
```

#### Step 2-2：ハイブリッド検索への組み込み

ChunkとRecipeを組み合わせた検索で
final_scoreが考慮されるよう修正：

- Chunk検索（ベクトル類似度）：変更なし
- Recipe検索：final_score順で並び替えを追加
- 両方の結果を統合する際、
  実食済みRecipeは上位に配置する

#### Step 2-3：動作確認クエリ

```cypher
# 確認用：final_score順のRecipe一覧
MATCH (r:Recipe)
RETURN r.name, r.validated,
       r.final_score, r.overall_score
ORDER BY r.final_score DESC
LIMIT 10
```

### ローカル確認手順
```bash
# ローカル起動（Render本番に影響しない）
python scripts/run_review_local.py

# ブラウザで動作確認
# http://localhost:5001
# クレソンサラダを検索して
# 上位に表示されることを確認
```

---

## Phase 3：save_validation()のfinal_score自動更新

### 対象ファイル
`nanaka-aivtuber/memory/memory_agent.py`
の `save_validation()` メソッド

### 変更内容

実食評価が保存されるたびに
`final_score` を自動計算・更新する：

```python
# save_validation()に追記
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
        r.validation_count =
            coalesce(r.validation_count, 0) + 1,
        r.final_score = $overall_score / 5.0
    RETURN r.name
    """
```

### 動作確認手順
```bash
# AIVTuber側
python core/run_validation.py

# ブラウザで http://localhost:5001 を開く
# 「クレソンの白和え」でスコアを入力・送信

# Neo4j Browserで確認
MATCH (r:Recipe {name: "クレソンの白和え"})
RETURN r.final_score, r.validated
# → final_score が設定されていること
```

---

## フライホイール完成確認テスト

Phase 2・3の実装後に以下を確認してください：

### テスト手順
1. `run_validation.py` で「クレソンの白和え」を
   評価（overall_score: 4.0想定）
2. Neo4j Browserで
   `final_score = 4.0 / 5.0 = 0.8` になることを確認
3. クレソンAIをローカル起動し「クレソン 白和え」
   で検索
4. 「クレソンの白和え」が上位に表示されることを確認

### 成功条件
実食前：クレソンの白和え final_score=0.63（未検証）
実食後：クレソンの白和え final_score=0.80（検証済み）
検索結果：0.80のレシピが上位に表示される ✅

---

## 完了条件
- [ ] Phase 2：Retrieverにfinal_score並び替えが追加されている
- [ ] Phase 2：ローカルで「クレソンサラダ」が
      検索上位に表示されることを確認
- [ ] Phase 3：save_validation()が
      final_scoreを自動更新する
- [ ] フライホイール完成確認テストが通る
- [ ] Render本番への変更は**行わない**
      （ローカル確認のみ）
- [ ] `task_queue/done_FLYWHEEL.md` を作成する
- [ ] `work_reports/WORK_REPORT_YYYYMMDD_HHMM.md`
      を作成する

## 注意事項
- INV番号（INV_1〜INV_18）は変更前に
  必ずAGENTS.mdで確認すること
- Render本番（watercress-cheff-ai.onrender.com）への
  デプロイは今回は行わない
- StagedChange・BackfillTaskノードは変更しない
- 既存のChunk検索ロジックは変更しない

## 参照ファイル
- watercress_cheff_ai/AGENTS.md
- watercress_cheff_ai/app/routes/review.py
- watercress_cheff_ai/agents/base.py
- nanaka-aivtuber/memory/memory_agent.py
- nanaka-aivtuber/core/run_validation.py