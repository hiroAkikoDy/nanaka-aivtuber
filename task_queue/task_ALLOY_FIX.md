# タスク依頼：Alloyモデル3のターン順序ファクト修正

## 前提確認
AGENTS.mdを読んでください。
次に以下のファイルを参照してください：
- docs/formal_verification.md（修正対象のAlloyモデルが記載）

---

## 作業概要
`docs/formal_verification.md` のAlloyモデル3（マルチペルソナ会話の整合性）に
論理的な誤りが発見されました。
モデルを修正し、再検証結果をレポートに反映してください。

**Pythonの実装コードは変更しません。**
修正対象は `docs/formal_verification.md` のみです。

---

## 誤りの内容

### 問題のあるファクト（現在）
```alloy
fact turn_order_nanaka_ryou {
    all d: Dialogue, t: d.turns |
    (t.seq = 1 implies t.persona = Nanaka) and
    (rem[t.seq, 2] = 1 implies t.persona = Ryou) and  // ← バグ
    (rem[t.seq, 2] = 0 implies t.persona = Nanaka)
}
```

### 問題の説明
`seq=1` は `rem[1, 2] = 1` を満たすため、
以下の2つの条件に**同時に**当てはまります：

- `t.seq = 1 implies t.persona = Nanaka`（ターン1はナナカ）
- `rem[t.seq, 2] = 1 implies t.persona = Ryou`（奇数ターンはリョウ）

この矛盾により `AlternatingTurnOrder` アサーションが
正しく検証できない状態になっています。

---

## 修正内容

### 修正後のファクト
```alloy
fact turn_order_nanaka_ryou {
    all d: Dialogue, t: d.turns |
    (rem[t.seq, 2] = 1 implies t.persona = Nanaka) and  // 奇数ターン: ナナカ
    (rem[t.seq, 2] = 0 implies t.persona = Ryou)         // 偶数ターン: リョウ
}
```

### 修正の根拠
| seq | rem[seq, 2] | 担当ペルソナ |
|---|---|---|
| 1（奇数） | 1 | ナナカ ✅ |
| 2（偶数） | 0 | リョウ ✅ |
| 3（奇数） | 1 | ナナカ ✅ |
| 4（偶数） | 0 | リョウ ✅ |

`dialogue_coordinator.py` の実装と一致することを確認してください：
- ターン1, 3 → ナナカが発言
- ターン2, 4 → リョウが発言

---

## レポートへの反映

`docs/formal_verification.md` の以下の箇所を更新してください。

### 更新箇所1：Alloyコード本体
モデル3の `fact turn_order_nanaka_ryou` を修正後のコードに差し替える。

### 更新箇所2：検証結果テーブル
```markdown
# 変更前
| AlternatingTurnOrder | ✅ 反例なし | ... |

# 変更後
| AlternatingTurnOrder | ✅ 反例なし（モデル修正後に再検証済み） |
  修正前：seq=1の矛盾によりファクト自体が不整合 |
  修正後：rem[seq,2]による奇偶判定に統一し再検証、反例なし |
```

### 更新箇所3：実装上の発見セクションに追記
```markdown
**モデル修正履歴**:
- 修正前: `t.seq = 1` と `rem[t.seq, 2] = 1` が競合し
  AlternatingTurnOrderアサーションの検証が不完全だった
- 修正後: `rem[t.seq, 2]` による奇偶判定に統一
  dialogue_coordinator.pyの実装と完全に対応することを確認
```

### 更新箇所4：ファイル末尾に修正ログを追加
```markdown
---

## 修正ログ
| 日時 | 対象 | 内容 |
|---|---|---|
| YYYY-MM-DD | モデル3 turn_order_nanaka_ryou | rem[seq,2]競合バグを修正・再検証実施 |
```

---

## 完了条件
- [ ] `docs/formal_verification.md` のモデル3ファクトが修正されている
- [ ] 検証結果テーブルが「モデル修正後に再検証済み」に更新されている
- [ ] 実装上の発見セクションに修正履歴が追記されている
- [ ] ファイル末尾に修正ログが追加されている
- [ ] Pythonの実装ファイルに変更がないこと
- [ ] `task_queue/done_ALLOY_FIX.md` を作成する
- [ ] `work_reports/WORK_REPORT_YYYYMMDD_HHMM.md` を作成する

## 参照ファイル
- AGENTS.md
- docs/formal_verification.md
- agents/dialogue_coordinator.py（実装との対応確認用）