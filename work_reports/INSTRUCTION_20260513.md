# 明日の作業指示書

**作成日**: 2026-05-12
**対象**: 古閑 弘晃（開発者）
**プロジェクト**: nanaka-aivtuber（農家AIVTuber開発）

---

## 📊 現在の状況（2026-05-12 終了時点）

### 完了済みステップ
| STEP | 内容 | 完了日時 |
|------|------|---------|
| ✅ STEP 1 | 最小構成AIVTuber | — |
| ✅ STEP 2 | LangChainプロンプト管理 | 2026-05-08 19:56 |
| ✅ STEP 3 | 感情状態管理（LangGraph） | 2026-05-09 12:32 |
| ✅ STEP 3.5 | add_conditional_edges実践 | 2026-05-10 00:01 |
| ✅ STEP 4 | Neo4j視聴者記憶 | 2026-05-11 12:22 |
| ✅ STEP 5 | マルチペルソナ配信機能 | — |
| ✅ STEP 6 | YouTube Live配信連携 | 2026-05-12 22:14 |

### ⚠️ 重要: Git コミット未実施
**STEP6の実装は完了しましたが、Gitコミットがまだされていません。**
明日の作業で最初に必ず実施してください。

### 実装済み機能
- ✅ VOICEVOX音声合成（感情別パラメータ調整付き）
- ✅ OpenAI LLM連携（emotion/memory変数注入）
- ✅ 感情分析（5種類：嬉しい/ワクワク/驚き/悲しい/普通）
- ✅ Neo4j視聴者記憶（過去3件の会話履歴保持）
- ✅ マルチペルソナ配信（ナナカ・リョウ）
- ✅ YouTube Live配信連携（OAuth 2.0認証、コメント取得、重複排除）
- ✅ OBS用テキストファイル出力（current_speaker.txt, current_text.txt）
- ✅ ダミーモード動作確認完了

### 変更ファイル一覧（未コミット）
**新規作成**:
- `agents/youtube_agent.py` (198行)
- `core/run_live.py` (163行)
- `task_queue/done_0006.md`

**変更**:
- `requirements.txt` — pyyaml, google-api-python-client等を追加
- `.gitignore` — credentials/, output/の除外ルール追加
- `config/settings.yaml` — youtube/obs設定追加
- `core/aituber_system.py` — get_dialogue_response()メソッド追加
- `AGENTS.md` — STEP6完了記録追加

### プロジェクト管理状態
- ✅ done_0001.md 〜 done_0006.md 作成済み
- ✅ WORK_REPORT_20260512_1450.md 作成済み
- ⚠️ **Gitコミット未実施**（最優先タスク）
- ⚠️ YouTube API認証テスト未実施
- ⚠️ リアルタイム配信モード未確認
- ⚠️ OBS連携テスト未実施

---

## 🎯 明日の作業目標

### 優先度1: Gitコミット（最優先）
**目的**: STEP6の実装を保護するため、すべての変更をコミット

**期待される成果物**:
- 全変更ファイルのGitコミット完了
- done_0006.mdとWORK_REPORTの記録

### 優先度2: YouTube API認証準備
**目的**: Google Cloud ConsoleでYouTube Data API v3を有効化し、OAuth 2.0認証情報を取得

**期待される成果物**:
- Google Cloud Consoleプロジェクト作成
- YouTube Data API v3有効化
- client_secret.jsonのダウンロード・配置
- 初回OAuth認証完了（token.json生成）

### 優先度3: リアルタイム配信モードテスト（YouTube API準備完了後）
**目的**: 実際のYouTube Live配信でコメント取得・応答を確認

**期待される成果物**:
- settings.yamlでmode: "live"に変更
- 実際の配信でコメント取得成功
- AIVTuberの応答動作確認

### 優先度4: OBS連携テスト
**目的**: OBSでテキストファイルを読み込み、配信画面に表示

**期待される成果物**:
- OBSテキストソース設定完了（2つ）
- current_speaker.txt / current_text.txt の画面表示
- 配信画面での動作確認

---

## 📋 明日やるべきこと

### 手順1: 環境確認（作業開始前）
```bash
# 1. プロジェクトディレクトリに移動
cd "C:\Users\Koga Hiroaki\Desktop\hiroaki_\workingFolder\nanaka-aivtuber"

# 2. Gitの状態確認（変更ファイルを確認）
git status
# → agents/youtube_agent.py
# → core/run_live.py
# → task_queue/done_0006.md
# → requirements.txt
# → .gitignore
# → config/settings.yaml
# → core/aituber_system.py
# → AGENTS.md
# が表示されるはず

# 3. 最新コミット確認
git log -1 --oneline
# → e84bb1e feat: STEP1〜STEP4 初期コミット（ナナカAIVTuber基盤実装）
# が表示されるはず

# 4. VOICEVOX起動確認
# → デスクトップからVOICEVOXを起動
# → ブラウザで http://localhost:50021/docs にアクセスして動作確認

# 5. Neo4j起動確認
# → Neo4j Desktopを起動
# → nanaka-aivtuber データベースを起動
# → ブラウザで http://localhost:7474 にアクセスして動作確認
```

### 手順2: Gitコミット（最優先）

**重要**: STEP6の実装が失われないよう、最初に必ずコミットしてください。

```bash
# 1. 変更内容を再確認
git status
git diff

# 2. done_0006.mdが存在することを確認
ls task_queue/done_0006.md
# → task_queue/done_0006.md が表示されればOK

# 3. WORK_REPORT_20260512_1450.mdが存在することを確認
ls work_reports/WORK_REPORT_20260512_1450.md
# → work_reports/WORK_REPORT_20260512_1450.md が表示されればOK

# 4. すべての変更をステージング
git add .

# 5. コミット実行
git commit -m "feat: STEP6 YouTube Live配信連携の実装

- YouTubeAgent実装（OAuth 2.0認証、コメント取得、重複排除）
- LiveStreamingSystem実装（リアルタイム配信モード）
- DummyLiveStreamingSystem実装（ダミーモード）
- OBS用テキストファイル出力（current_speaker.txt, current_text.txt）
- YouTube API認証設定（credentials_path, polling_interval）
- クォータ管理機能（daily_limit: 10000, warning_threshold: 0.8）

新規作成:
- agents/youtube_agent.py (198行)
- core/run_live.py (163行)
- task_queue/done_0006.md

変更:
- requirements.txt: pyyaml, google-api-python-client等を追加
- .gitignore: credentials/, output/の除外ルール追加
- config/settings.yaml: youtube/obs設定追加
- core/aituber_system.py: get_dialogue_response()メソッド追加
- AGENTS.md: STEP6完了記録追加

動作確認:
- ダミーモード動作確認完了（3コメント処理成功）
- マルチペルソナ対話正常（ナナカ・リョウが4ターンずつ会話）
- Neo4j視聴者記憶正常（太郎325文字/花子315文字/次郎299文字）
- VOICEVOX音声合成正常（感情分析: ワクワク検出）
- OBS用テキストファイル出力正常

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# 6. コミット確認
git log -1 --oneline
# → 新しいコミットIDが表示されればOK
```

### 手順3: YouTube API認証準備

#### 3-1. Google Cloud Consoleでプロジェクト作成
1. https://console.cloud.google.com/ にアクセス
2. 右上の「プロジェクトを選択」→「新しいプロジェクト」
3. プロジェクト名: `nanaka-aivtuber` または任意の名前
4. 「作成」をクリック

#### 3-2. YouTube Data API v3を有効化
1. 左メニュー「APIとサービス」→「ライブラリ」
2. 検索ボックスに「YouTube Data API v3」と入力
3. 「YouTube Data API v3」を選択
4. 「有効にする」をクリック

#### 3-3. OAuth 2.0クライアントID作成
1. 左メニュー「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「OAuthクライアントID」
3. 「同意画面を構成」をクリック（初回のみ）
   - User Type: 「外部」を選択
   - アプリ名: `nanaka-aivtuber`
   - ユーザーサポートメール: 自分のGmailアドレス
   - デベロッパーの連絡先情報: 自分のGmailアドレス
   - 「保存して次へ」を3回クリック
4. 再度「認証情報を作成」→「OAuthクライアントID」
5. アプリケーションの種類: 「デスクトップアプリ」
6. 名前: `nanaka-aivtuber-desktop`
7. 「作成」をクリック

#### 3-4. client_secret.jsonダウンロード・配置
1. 作成されたOAuthクライアントIDの右側のダウンロードアイコン（↓）をクリック
2. `client_secret_XXXXX.json` がダウンロードされる
3. ファイル名を `client_secret.json` にリネーム
4. プロジェクトの `credentials/` フォルダに配置

```bash
# credentialsフォルダ確認
ls credentials/
# → client_secret.json が表示されればOK

# ファイル内容確認（JSONとして正しいか）
cat credentials/client_secret.json
# → {"installed": {"client_id": "...", ...}} のような内容が表示されればOK
```

### 手順4: 初回OAuth認証テスト

```bash
# 1. ダミーモードで動作確認（既存機能が壊れていないか）
cd core
python run_live.py
# → "ダミーモードで起動します" と表示される
# → 3コメント処理成功でCtrl+Cで終了

# 2. settings.yamlをリアルタイム配信モードに変更
# config/settings.yaml を開き、以下を変更:
# youtube:
#   mode: "live"  # "dummy" から "live" に変更

# 3. リアルタイム配信モードで認証テスト
python run_live.py
# → ブラウザが自動的に開き、Google OAuth認証画面が表示される
# → Googleアカウントでログイン
# → 「nanaka-aivtuberがYouTubeアカウントへのアクセスをリクエストしています」と表示される
# → 「許可」をクリック
# → 「認証が完了しました。このウィンドウを閉じて構いません。」と表示される
# → ターミナルに "OAuth 2.0認証が完了しました" と表示される
# → credentials/token.json が自動生成される

# 4. token.json生成確認
ls ../credentials/token.json
# → credentials/token.json が表示されればOK
```

**重要**:
- 初回のみブラウザでの認証が必要です
- 2回目以降は`token.json`が自動的に使われます
- `token.json`は絶対にGitにコミットしないでください（.gitignoreに含まれています）

### 手順5: リアルタイム配信モードテスト（YouTube Live配信が必要）

#### 5-1. YouTube Live配信を開始

1. YouTube Studioにアクセス（https://studio.youtube.com/）
2. 右上「作成」→「ライブ配信を開始」
3. 配信設定:
   - タイトル: テスト配信（任意）
   - 公開設定: 「限定公開」または「非公開」（テストなので公開しない）
   - カテゴリ: その他
4. 「ライブ配信を開始」をクリック
5. 配信URLをコピー（例: `https://www.youtube.com/watch?v=XXXXXXXXXXXXX`）
6. Video IDを取得（例: `XXXXXXXXXXXXX`）

#### 5-2. settings.yamlにVideo IDを設定

```yaml
# config/settings.yaml
youtube:
  mode: "live"
  video_id: "XXXXXXXXXXXXX"  # ←ここに実際のVideo IDを入力
  credentials_path: "credentials/client_secret.json"
  polling_interval: 5
  max_results: 5
```

**重要**: `video_id`を設定しない場合、YouTubeAgentが自動的にアクティブな配信を検出します。

#### 5-3. リアルタイム配信モードで実行

```bash
cd core
python run_live.py
# → "リアルタイム配信モードで起動します"
# → "ライブチャットID: XXXXX を取得しました"
# → "コメント監視を開始します..."

# ブラウザで配信ページを開き、コメントを投稿してテスト
# 例: 「こんにちは！」
# → ターミナルに "[視聴者] ユーザー名: こんにちは！" と表示される
# → ナナカとリョウが応答する
# → output/current_speaker.txt と output/current_text.txt が更新される
```

#### 5-4. 動作確認ポイント

- [ ] コメントが取得される
- [ ] 重複コメントが排除される（同じコメントが2回処理されない）
- [ ] マルチペルソナ対話が動作する（ナナカ・リョウが交互に話す）
- [ ] VOICEVOX音声合成が動作する
- [ ] Neo4j視聴者記憶が動作する
- [ ] OBS用テキストファイルが更新される
- [ ] APIクォータ警告が表示される（80%超過時）

### 手順6: OBS連携テスト

#### 6-1. OBS起動・テキストソース追加

1. OBSを起動
2. 「ソース」パネルの「+」→「テキスト (GDI+)」を選択
3. 名前: `発言者名`
4. 「ファイルから読み取り」にチェック
5. 「参照」→ `C:\Users\Koga Hiroaki\Desktop\hiroaki_\workingFolder\nanaka-aivtuber\output\current_speaker.txt` を選択
6. 「OK」をクリック

7. 再度「ソース」パネルの「+」→「テキスト (GDI+)」を選択
8. 名前: `テキスト`
9. 「ファイルから読み取り」にチェック
10. 「参照」→ `C:\Users\Koga Hiroaki\Desktop\hiroaki_\workingFolder\nanaka-aivtuber\output\current_text.txt` を選択
11. 「OK」をクリック

#### 6-2. テキストソースのプロパティ設定

**発言者名**:
- フォント: メイリオ Bold
- サイズ: 48
- 色: #FFFFFF（白）
- 背景色: #000000（黒）、不透明度: 180
- 配置: 画面左上

**テキスト**:
- フォント: メイリオ Regular
- サイズ: 32
- 色: #FFFFFF（白）
- 背景色: #000000（黒）、不透明度: 180
- 配置: 画面下部中央
- 縦揃え: 上揃え
- 横揃え: 中央揃え
- 折り返し: 有効

#### 6-3. 動作確認

```bash
# run_live.pyを実行（ダミーモードまたはリアルタイム配信モード）
cd core
python run_live.py
```

OBS画面で確認:
- [ ] コメント受信時に「発言者名」が更新される（例: `太郎: クレソンってどんな味なの？`）
- [ ] 「テキスト」が更新される（例: `ナナカ: クレソンはシャキシャキとした食感で...`）
- [ ] AIVTuberの応答ごとに表示が切り替わる
- [ ] 応答完了後に両方のテキストが空になる

### 手順7: 完了確認

- [ ] Gitコミット完了
- [ ] done_0006.mdが存在する
- [ ] WORK_REPORT_20260512_HHMM.mdが存在する
- [ ] client_secret.jsonが配置されている
- [ ] token.jsonが生成されている
- [ ] リアルタイム配信モードでコメント取得成功
- [ ] OBS連携テスト完了（画面表示確認）
- [ ] AGENTS.md更新（必要に応じて）

---

## ⚠️ 注意事項

### Gitコミットについて
- **必ず最初に実行**してください
- STEP6の実装が失われないようにコミットが最優先です
- done_0006.mdとWORK_REPORT_20260512_1450.mdが存在することを確認してからコミット

### YouTube API認証について
- **初回のみブラウザでの認証が必要**
- `token.json`は自動生成されます（.gitignoreに含まれています）
- **client_secret.jsonは絶対にGitにコミットしないこと**（.gitignoreに含まれています）
- 認証エラーが出た場合は、`credentials/token.json`を削除して再度認証

### YouTube API クォータについて
- **YouTube Data API v3は1日10,000ユニット**
- `liveChatMessages.list`: 5ユニット/回
- ポーリング間隔5秒の場合、約2.7時間（2000リクエスト × 5ユニット = 10,000ユニット）で上限
- **テスト時はダミーモードを活用**してクォータを節約
- 80%超過時に警告が表示されます
- クォータ超過後は翌日（太平洋標準時0時）まで待つ必要があります

### OBSについて
- **OBSが起動していなくてもrun_live.pyは動作します**
- テキストファイル出力は常に行われます（`output/current_speaker.txt`, `output/current_text.txt`）
- OBS側でファイル読み込み設定が必要（「ファイルから読み取り」）
- テキストソースのプロパティで「ファイルを監視」が有効になっていることを確認

### Video IDについて
- **settings.yamlで`video_id`を設定しない場合**、YouTubeAgentが自動的にアクティブな配信を検出します
- 自動検出は`liveBroadcasts.list`を使用します（1ユニット/回）
- 手動で`video_id`を設定することで、自動検出のクォータ消費を回避できます

### ポーリング間隔について
- **デフォルト: 5秒**（`config/settings.yaml`の`polling_interval`）
- 間隔を短くすると応答性が向上しますが、APIクォータを多く消費します
- 間隔を長くするとクォータを節約できますが、応答が遅れます
- テスト時は10秒程度に設定することを推奨

---

## 📚 参考情報

### YouTube Data API v3 公式ドキュメント
- **概要**: https://developers.google.com/youtube/v3/getting-started
- **LiveChatMessages.list**: https://developers.google.com/youtube/v3/live/docs/liveChatMessages/list
- **クォータ**: https://developers.google.com/youtube/v3/determine_quota_cost

### OAuth 2.0認証フロー
- **Google OAuth 2.0**: https://developers.google.com/identity/protocols/oauth2
- **デスクトップアプリ用**: https://developers.google.com/identity/protocols/oauth2/native-app

### 前プロジェクト「クレソンAI」
- **URL**: https://github.com/hiroAkikoDy/hiroAkikoDy-watercress_cheff_ai
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
- [ ] `git status` で変更ファイルを確認（未コミットファイルがあることを確認）
- [ ] `task_queue/done_0006.md` が存在することを確認
- [ ] `work_reports/WORK_REPORT_20260512_1450.md` が存在することを確認
- [ ] 今日の体調・集中力は良好
- [ ] 作業時間の確保（推奨: 2〜3時間）

---

## 🚀 STEP6完了後の展望

STEP6のテストが完了すると、以下が実現します：

### 機能面
- YouTube Live配信でリアルタイムにコメント取得
- AIVTuberが自動的に応答（マルチペルソナ対話）
- OBS連携で画面にテキスト表示
- 視聴者との双方向コミュニケーション

### 技術面
- YouTube Data API v3の習得
- OAuth 2.0認証フローの理解
- リアルタイムポーリングシステムの実装
- OBS連携テキストファイル出力

### 次のステップ（STEP7以降）
- OBSウェブソケット連携（obs-websocket-py）
- シーン切り替え自動化
- キャラクター画像表示（VTuberアバター）
- 音声出力のOBS連携（仮想オーディオデバイス）
- 3人以上のペルソナ追加
- 感情に応じた表情変化

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

### Gitコミットエラーが出る場合
1. `git status` でファイル一覧を確認
2. Claude Codeに「Gitコミットを実行してください」と指示
3. コミットメッセージは上記の手順2を参考にする

### YouTube API認証エラーが出る場合
1. `client_secret.json`のパスが正しいか確認
   ```bash
   ls credentials/client_secret.json
   ```
2. YouTube Data API v3が有効になっているか確認（Google Cloud Console）
3. OAuth同意画面が設定されているか確認（Google Cloud Console）
4. `credentials/token.json`を削除して再度認証
   ```bash
   rm credentials/token.json
   python core/run_live.py
   ```

### コメント取得エラーが出る場合
1. Video IDが正しいか確認
   - 配信URL: `https://www.youtube.com/watch?v=XXXXXXXXXXXXX`
   - Video ID: `XXXXXXXXXXXXX`
2. 配信が開始されているか確認（YouTube Studio）
3. ライブチャットが有効になっているか確認（配信設定）
4. `video_id`を設定せずに自動検出を試す
   ```yaml
   # config/settings.yaml
   youtube:
     mode: "live"
     # video_id: ""  # コメントアウト
   ```

### クォータ超過エラーが出る場合
1. 現在のクォータ使用量を確認
   - Google Cloud Console → APIとサービス → YouTube Data API v3 → 割り当て
2. 翌日（太平洋標準時0時）まで待つ
3. **ダミーモードで開発を継続**
   ```yaml
   # config/settings.yaml
   youtube:
     mode: "dummy"  # リアルタイム配信モードから切り替え
   ```
4. ポーリング間隔を長くする（例: 10秒）
   ```yaml
   # config/settings.yaml
   youtube:
     polling_interval: 10  # 5秒から10秒に変更
   ```

### OBS連携エラーが出る場合
1. テキストファイルが生成されているか確認
   ```bash
   ls output/current_speaker.txt
   ls output/current_text.txt
   ```
2. OBSのテキストソース設定を確認
   - 「ファイルから読み取り」がチェックされているか
   - ファイルパスが正しいか（絶対パス）
3. OBSのログを確認（ヘルプ → ログファイル → 現在のログファイルを表示）

### 時間がかかりすぎる場合
- STEP6のテストは大きなタスクなので、1日で完了しなくてもOK
- 途中経過をwork_reportに記録
- 翌日に続きを実施

### 実装の方向性が不安な場合
- `task_queue/done_0006.md`の内容を再確認
- `work_reports/WORK_REPORT_20260512_1450.md`を参照
- 前プロジェクト「クレソンAI」を参考にする

---

## ✅ 作業終了時のチェックリスト

作業終了時に以下を確認してください：

- [ ] Gitコミットが完了している（最優先）
- [ ] done_0006.md が存在している
- [ ] WORK_REPORT_20260512_HHMM.md が存在している
- [ ] client_secret.json が配置されている
- [ ] token.json が生成されている（初回認証完了後）
- [ ] リアルタイム配信モードでコメント取得成功（YouTube Live配信がある場合）
- [ ] OBS連携テスト完了（画面表示確認）
- [ ] AGENTS.md が更新されている（必要に応じて）
- [ ] 明日以降の作業が必要な場合、メモを残している

---

## 🎉 最後に

STEP6の実装、お疲れ様でした！YouTube Live配信連携とOBS連携の準備ができました。
明日は認証テストとリアルタイム配信テストを頑張ってください！

**最重要**: 必ず最初にGitコミットを実行して、STEP6の実装を保護してください。

頑張ってください！ナナカとリョウのライブ配信を実現しましょう！
