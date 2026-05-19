# done_FLYWHEEL.md

## タスク：RAG重み付け組み込み（フライホイール完成）

### 完了日時
2026-05-18 17:05

### Phase 3：save_validation() final_score自動更新
- [x] memory_agent.py の save_validation() に `r.final_score = $overall_score / 5.0` 追加
- [x] クレソンの白和え テスト: overall=3.8 → final_score=0.76 計算成功

### Phase 2：クレソンAI Retriever final_score並び替え
- [x] app/rag.py に rerank_by_final_score() 追加（Chunk→Recipeトラバースでfinal_score取得・再ソート）
- [x] app/rag.py format_docs() に検証スコア・実食マーク表示追加
- [x] app/rag.py RAGチェーンに rerank ステップ追加（retriever | rerank | format_docs）
- [x] app/routes/chat.py /chat ルートに rerank_by_final_score 適用
- [x] app/routes/chat.py /chat_stream TYPE_3 ルートに rerank_by_final_score 適用

### フライホイール完成確認テスト
- [x] クレソンサラダ: final_score=0.86（実食済み★）
- [x] クレソンの白和え: final_score=0.76（実食済み★）
- [x] 未検証レシピ: final_score=0.45（下位）
- [x] 実食済みレシピが上位にソートされることを確認

### 注意事項
- Render本番へのデプロイは行わない（ローショナル確認のみ）
- Chunk検索ロジックは変更なし
