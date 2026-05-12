# AGENTS.md - nanaka-aivtuber

## プロジェクト概要
農家AIVTuber開発（VOICEVOX × LangGraph × Neo4j）
参考書籍：「AITuberを作ってみたら〜」「LangChain と LangGraph による〜」

## 開発者情報
- 名前：古閑 弘晃（こが ひろあき）
- 職業：クレソン農家（ナナカファーム・熊本県）× 大学院生
- 技術スタック：Neo4j 5年・Python・形式手法（KAOS・Alloy）
- Zenn：@hiroakikody（71記事以上）
- 開発環境：Windows・VSCode・Kilo Code × Z.ai BYOK

## 前プロジェクト：クレソンAI（完成済み）
- 本番URL：https://hiroakikody-watercress-cheff-ai.onrender.com
- リポジトリ：https://github.com/hiroAkikoDy/hiroAkikoDy-watercress_cheff_ai
- Phase 3b〜4b 本番稼働済み（Tool Selector / マルチペルソナ / 非同期レポート）
- INV_1〜INV_18 は前プロジェクトの履歴（本プロジェクトでは参照不要）

## 本プロジェクトの目標機能
1. 視聴者記憶（Neo4j + LangChain Ch6）—「前回〇〇さんが質問した件ですが」✅ 実装済み
2. 感情状態管理（LangGraph Ch9）— コメント感情 → AIVTuber感情変化 → VOICEVOX連動 ✅ 実装済み
3. マルチペルソナ配信（LangChain Ch12）— 農家AIVTuber × シェフAIVTuberが議論 ✅ 実装済み

## 実装済み機能一覧（STEP1〜STEP6）
- 基本AIVTuber機能（VOICEVOX連携・音声合成）
- プロンプトテンプレート管理（LangChain）
- 感情状態管理（EmotionAgent / ParameterAdapter）
- 感情に応じたVOICEVOXパラメータ動的調整
- Neo4j視聴者記憶（ViewerMemoryAgent）
- マルチペルソナ対話（ナナカ・リョウの会話）
- ペルソナエージェント（PersonaAgent）
- 対話調整（DialogueCoordinator）
- 動的speaker_id切り替え
- YouTube Live配信連携（YouTubeAgent / LiveStreamingSystem）
- OBS連携テキストファイル出力（current_speaker.txt / current_text.txt）
- ダミーモード / ライブモード切替

## 実装ステップ
- STEP 1：最小構成AIVTuber（書籍コードベース）✅ 完了
- STEP 2：LangChain Ch4〜5 プロンプト管理 ✅ 完了
- STEP 3：LangGraph Ch9 感情状態管理 ✅ 完了（2026-05-09 12:32）
- STEP 3.5：add_conditional_edges 実践（感情→VOICEVOXパラメータ分岐）✅ 完了（2026-05-10 00:01）
- STEP 4：Neo4j Ch6 視聴者記憶 ✅ 完了（2026-05-11 12:22）
- STEP 5：LangChain Ch12 マルチペルソナ ✅ 完了（2026-05-12）
- STEP 6：YouTube Live配信連携 ✅ 完了（2026-05-12）

## 参考書籍・リポジトリ
1. 「AITuberを作ってみたら生成AIプログラミングがよくわかった件」（日経・Python）
   - GitHub: aituber_python_programing_example
   - voicevox_adapter.py・youtube_comment_adapter.py・obs_adapter.py 含む
2. 「LangChain と LangGraph による RAG・AI エージェント実践入門」（技評）

## Zennブログ公開状況
| 弾 | タイトル | 状態 |
|---|---|---|
| Vol.1〜4 | 公開済み | ✅ |
| Vol.5 | Neo4j × LangChain × Z.aiでRAGを作った | ✅ 公開済み |
| Vol.6 | 要求工学でTool Selectorを設計した | 📝 下書き完成・公開待ち |
| Vol.7 | 要求工学でAIに会話力を持たせた | 📝 下書き完成・公開待ち |

## コーディングルール
- コミット: fix: / feat: / docs: プレフィックス
- 作業完了後は work_reports/WORK_REPORT_YYYYMMDD_HHMM.md を作成
- 変更前に必ずこのAGENTS.mdを参照すること
---

【作業完了後：Claudeへの報告用マークダウンを作成する】

作業完了後に以下の内容で
WORK_REPORT_YYYYMMDD_HHMI.md を作成してください。
（日時は実際の完了時刻に置き換える）

保存先：
“C:\Users\Koga Hiroaki\Desktop\hiroaki_\workingFolder\nanaka-aivtuber\work_reports"
ファイルの内容：

# 作業レポート

## 実施日時
（完了時刻を記入）

## 目標
（このプロンプトの【目標】セクションをコピー）

## 実施した変更

### 変更ファイル一覧
| ファイル | 変更内容 | 行番号 |
|---------|---------|------|
（実際に変更したファイルを記入）

### 変更前後の比較
（重要な変更箇所を変更前→変更後の形式で記載）

## 発生したエラーと対処
（エラーが発生した場合のみ）
| エラー内容 | 原因 | 対処法 |
|-----------|------|------|

## Git操作
- コミットメッセージ：
- コミットID：
- ブランチ：
- push状況：

## 動作確認結果
（ローカルで確認した内容を記入）

## Claudeへの質問・相談事項
（不明点・改善案・次のステップへの疑問があれば記入）

---

- 変更前に必ずこのAGENTS.mdを参照すること

## 現在のSTEP1スコープ（これ以外は実装しない）
- 書籍付属コードをcoreに移植
- VOICEVOX起動確認
- ダミーコメントで音声出力まで通す
- YouTube・OBS連携はSTEP1では不要

## 環境
- OS: Windows
- Python: 3.x
- VOICEVOX: ローカル起動（port 50021）
- LLM: OpenAI gpt-4o-mini（Z.ai BYOK）