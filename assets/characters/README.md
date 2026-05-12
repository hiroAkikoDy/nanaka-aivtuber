# キャラクター画像管理

このディレクトリには、VTuberキャラクターの画像ファイルを配置します。

## ディレクトリ構造

```
assets/characters/
├── nanaka/           # ナナカの画像
│   ├── normal.png    # 通常
│   ├── happy.png     # 嬉しい
│   ├── excited.png   # ワクワク
│   ├── surprised.png # 驚き
│   └── sad.png       # 悲しい
├── ryou/             # リョウの画像
│   ├── normal.png    # 通常
│   ├── happy.png     # 嬉しい
│   ├── excited.png   # ワクワク
│   ├── surprised.png # 驚き
│   └── sad.png       # 悲しい
└── README.md         # このファイル
```

## 画像ファイルの準備

### 1. 画像の推奨仕様

- **形式**: PNG（透過背景推奨）
- **サイズ**: 1920x1080 または 1280x720
- **アスペクト比**: 16:9（横長）または 1:1（正方形）
- **ファイルサイズ**: 5MB以下

### 2. 感情別の表情

各キャラクターについて、以下の5つの感情表現を用意してください：

| 感情 | ファイル名 | 説明 |
|------|-----------|------|
| 通常 | normal.png | デフォルトの表情 |
| 嬉しい | happy.png | 笑顔、喜んでいる表情 |
| ワクワク | excited.png | 興奮している、期待している表情 |
| 驚き | surprised.png | 驚いている、びっくりしている表情 |
| 悲しい | sad.png | 悲しい、落ち込んでいる表情 |

### 3. 画像の配置方法

1. ナナカの画像を`nanaka/`フォルダに配置
2. リョウの画像を`ryou/`フォルダに配置
3. ファイル名は上記の表に従って命名

例:
```bash
assets/characters/nanaka/normal.png
assets/characters/nanaka/happy.png
...
assets/characters/ryou/normal.png
assets/characters/ryou/happy.png
...
```

## OBS設定

### 1. OBSに画像ソースを追加

1. OBSを起動
2. 「ソース」パネルの「+」→「画像」を選択
3. 名前: `ナナカ画像`（settings.yamlの`obs.sources.nanaka_image`と一致）
4. 画像ファイル: `assets/characters/nanaka/normal.png`を選択
5. 「OK」をクリック

6. 同様に、リョウの画像ソースも追加
7. 名前: `リョウ画像`（settings.yamlの`obs.sources.ryou_image`と一致）
8. 画像ファイル: `assets/characters/ryou/normal.png`を選択

### 2. settings.yamlの設定

`config/settings.yaml`で、OBSソース名を設定します：

```yaml
obs:
  websocket:
    enabled: true
    host: "localhost"
    port: 4455
    password: ""

  sources:
    nanaka_image: "ナナカ画像"  # OBS側の画像ソース名と一致させる
    ryou_image: "リョウ画像"    # OBS側の画像ソース名と一致させる
```

### 3. OBS WebSocketプラグインのインストール

OBS Studio 28.0以降にはWebSocketプラグインが標準搭載されています。

**有効化手順**:
1. OBS → 「ツール」→「obs-websocket 設定」
2. 「WebSocketサーバーを有効にする」にチェック
3. ポート番号を確認（デフォルト: 4455）
4. パスワードを設定（オプション）
5. 「OK」をクリック

## 動作確認

### 1. ダミーモードでテスト

```bash
cd core
python run_live.py
```

### 2. 確認ポイント

- [ ] OBS WebSocket接続成功のメッセージが表示される
- [ ] コメント受信時にキャラクター画像が切り替わる
- [ ] 感情に応じて画像が変わる（通常→嬉しい→ワクワクなど）
- [ ] ナナカとリョウの画像が交互に表示される

## トラブルシューティング

### 画像が表示されない

1. **画像ファイルが存在するか確認**
   ```bash
   ls assets/characters/nanaka/
   ls assets/characters/ryou/
   ```

2. **OBSソース名が一致しているか確認**
   - settings.yamlの`obs.sources.nanaka_image`
   - OBS側の画像ソース名

3. **OBS WebSocketが有効か確認**
   - OBS → 「ツール」→「obs-websocket 設定」

### 画像が切り替わらない

1. **OBSAgentの接続状態を確認**
   - コンソールに「[OBS] WebSocket接続成功」と表示されているか

2. **settings.yamlでWebSocketが有効か確認**
   ```yaml
   obs:
     websocket:
       enabled: true  # falseになっていないか
   ```

3. **画像ファイルのパスが正しいか確認**
   - 絶対パスが正しく生成されているか

## カスタマイズ

### 新しい感情を追加

1. `config/settings.yaml`に感情を追加
   ```yaml
   characters:
     nanaka:
       emotions:
         通常: "normal.png"
         嬉しい: "happy.png"
         怒り: "angry.png"  # 新しい感情
   ```

2. 画像ファイルを追加
   ```bash
   assets/characters/nanaka/angry.png
   assets/characters/ryou/angry.png
   ```

3. 感情分析（EmotionAgent）を拡張
   - `agents/emotion_agent.py`で新しい感情を検出

### キャラクターを追加

1. `config/settings.yaml`にキャラクターを追加
   ```yaml
   characters:
     takeshi:  # 新しいキャラクター
       name: "タケシ"
       image_dir: "assets/characters/takeshi"
       emotions:
         通常: "normal.png"
         嬉しい: "happy.png"
   ```

2. ディレクトリと画像を追加
   ```bash
   mkdir assets/characters/takeshi
   # 画像ファイルを配置
   ```

3. OBSにソースを追加
   - 名前: `タケシ画像`

4. `config/settings.yaml`でソースを設定
   ```yaml
   obs:
     sources:
       takeshi_image: "タケシ画像"
   ```

## 参考資料

- [OBS Studio 公式サイト](https://obsproject.com/)
- [obs-websocket プロトコル仕様](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md)
- [VTuber画像の作成方法](https://www.pixiv.net/howto/drawing/vtuber)
