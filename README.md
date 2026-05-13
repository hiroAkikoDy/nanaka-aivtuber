# 🌿 ナナカ AIVTuber

農家AIVTuber「ナナカ」とシェフAIVTuber「リョウ」が YouTube Live で視聴者と対話する配信システム。

VOICEVOX × LangGraph × Neo4j を組み合わせ、**感情連動音声・視聴者記憶・マルチペルソナ対話**を実現しています。

## ✨ 主な機能

| 機能 | 説明 |
|------|------|
| **感情連動音声** | コメントの感情（嬉しい/ワクワク/驚き/悲しい/普通）を分析し、VOICEVOXのspeed/pitchを動的調整 |
| **視聴者記憶** | Neo4jに視聴者ごとの会話履歴を保存。「前回〇〇さんが質問した件ですが」が可能 |
| **マルチペルソナ対話** | ナナカ（クレソン農家）とリョウ（シェフ）が視聴者コメントに対して交互に会話 |
| **YouTube Live連携** | YouTube Data API v3でリアルタイムコメント取得（OAuth 2.0認証） |
| **OBS連携** | WebSocket経由でシーン切り替え・キャラクター画像の感情連動表示 |
| **ダミーモード** | YouTube APIを使わずにローカルで動作確認可能 |

## 🏗️ アーキテクチャ

```
YouTube Live コメント
        ↓
YouTubeAgent（OAuth 2.0 / コメント取得 / 重複排除）
        ↓
EmotionAgent（感情分析 → speed/pitch/pitch算出）
        ↓
DialogueCoordinator（ナナカ↔リョウの対話生成）
        ↓
VoicevoxAdapter（感情パラメータ適用・音声合成）
        ↓
PlaySound（音声出力）+ OBSAgent（キャラクター画像・テキスト表示）
```

## 📁 ディレクトリ構成

```
nanaka-aivtuber/
├── agents/
│   ├── emotion_agent.py          # 感情分析エージェント
│   ├── persona_agent.py          # ペルソナエージェント（ナナカ/リョウ）
│   ├── dialogue_coordinator.py   # 対話調整コーディネーター
│   ├── youtube_agent.py          # YouTube Live コメント取得
│   └── obs_agent.py              # OBS WebSocket連携
├── core/
│   ├── aituber_system.py         # システム統合クラス
│   ├── run_live.py               # 配信モード実行スクリプト
│   ├── voicevox_adapter.py       # VOICEVOX音声合成
│   ├── langchain_adapter.py      # LangChain LLM連携
│   └── ...
├── memory/
│   └── memory_agent.py           # Neo4j視聴者記憶
├── config/
│   └── settings.yaml             # 設定ファイル
├── assets/
│   └── characters/               # キャラクター画像（感情別5種×2人）
├── credentials/                   # OAuth 2.0認証情報（.gitignore対象）
├── output/                        # OBS用テキストファイル出力
└── tests/
```

## 🚀 クイックスタート

### 前提条件

- Python 3.11+
- [VOICEVOX](https://voicevox.hiroshiba.jp/) （port 50021）
- [Neo4j](https://neo4j.com/) （port 7474/7687）
- OpenAI API Key（gpt-4o-mini）

### 1. セットアップ

```bash
git clone https://github.com/hiroAkikoDy/nanaka-aivtuber.git
cd nanaka-aivtuber
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env` ファイルをプロジェクトルートに作成：

```env
OPENAI_API_KEY=sk-...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### 3. YouTube API認証（ライブモードの場合）

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
2. YouTube Data API v3 を有効化
3. OAuth 2.0 クライアント ID（デスクトップアプリ）を作成
4. JSONをダウンロードして `credentials/client_secret.json` に配置

### 4. 実行

```bash
# ダミーモード（YouTube API不要）
python core/run_live.py

# ライブモード（config/settings.yaml で mode: "live" に設定後）
python core/run_live.py
```

## ⚙️ 設定

`config/settings.yaml` で以下を管理：

```yaml
llm:
  model: "gpt-4o-mini"

voicevox:
  host: "127.0.0.1"
  port: 50021

multi_persona:
  enabled: true
  turn_limit: 4

youtube:
  mode: "dummy"  # "dummy" or "live"

obs:
  websocket:
    enabled: false  # trueでOBS WebSocket連携

characters:
  nanaka:
    emotions:
      通常: "normal.png"
      嬉しい: "happy.png"
      ワクワク: "excited.png"
      驚き: "surprised.png"
      悲しい: "sad.png"
```

## 📚 参考書籍

1. **「AITuberを作ってみたら生成AIプログラミングがよくわかった件」**（日経・Python）
2. **「LangChain と LangGraph による RAG・AI エージェント実践入門」**（技評）

## 🔗 関連プロジェクト

- **クレソンAI（前プロジェクト）**: https://github.com/hiroAkikoDy/hiroAkikoDy-watercress_cheff_ai
- **Zenn ブログ**: https://zenn.dev/hiroakikody

## 📝 実装ステップ

| STEP | 内容 | 状態 |
|------|------|------|
| STEP 1 | 最小構成AIVTuber | ✅ |
| STEP 2 | LangChain プロンプト管理 | ✅ |
| STEP 3 | LangGraph 感情状態管理 | ✅ |
| STEP 3.5 | add_conditional_edges 実践 | ✅ |
| STEP 4 | Neo4j 視聴者記憶 | ✅ |
| STEP 5 | マルチペルソナ配信 | ✅ |
| STEP 6 | YouTube Live 配信連携 | ✅ |
| STEP 7 | OBS ウェブソケット連携・キャラクター画像 | ✅ |

## 👤 開発者

- **古閑 弘晃**（こが ひろあき）
- クレソン農家（ナナカファーム・熊本県）× 大学院生
- Neo4j 5年・Python・形式手法（KAOS・Alloy）

## 📜 ライセンス

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
