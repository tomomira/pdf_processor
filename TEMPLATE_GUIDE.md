# 分析テンプレート追加ガイド

## 概要

このシステムでは、**プログラム修正なし**で新しい分析タイプを追加できます。
テンプレートファイルの作成とconfig.jsonの設定だけで、カスタム分析が可能になります。

## 新しい分析タイプ追加手順

### Step 1: テンプレートファイル作成

`analysis_templates/` フォルダに新しいテンプレートファイルを作成します。

**例**: 市場分析テンプレート
```bash
# ファイル作成
analysis_templates/market_analysis.txt
```

**テンプレート内容例**:
```text
以下のPDFドキュメントの内容から市場分析を実行してください。

【分析対象】
{text_content}

【市場分析フレームワーク】
1. 市場規模・成長率の分析
   - 市場全体の規模とセグメント別内訳
   - 過去3-5年の成長率トレンド
   - 将来成長予測と成長ドライバー

2. 競合状況の評価
   - 主要競合企業の特定
   - 市場シェア分析
   - 競争優位性の評価

3. 顧客セグメント分析
   - 主要顧客層の特定
   - 顧客ニーズ・購買行動
   - 顧客満足度・ロイヤリティ

4. 市場トレンド・将来予測
   - 技術革新の影響
   - 規制環境の変化
   - 消費者行動の変化

【回答形式】
## 市場概況
[市場規模・成長率の現状]

## 競合分析
[主要競合と競争環境の評価]

## 顧客分析
[顧客セグメントと行動パターン]

## 市場トレンド
[重要なトレンドと将来予測]

## 成長機会
[特定された成長機会と戦略提案]

## リスク要因
[市場リスクと対策の必要性]
```

### Step 2: config.jsonに設定追加

**基本追加**:
```json
{
  "analysis_templates": {
    "financial_analysis": "analysis_templates/financial_analysis.txt",
    "esg_analysis": "analysis_templates/esg_analysis.txt",
    "market_analysis": "analysis_templates/market_analysis.txt"
  }
}
```

### Step 3: 実行テスト

```bash
# 新しい分析タイプの実行
python3 pdf_analyzer.py --analysis-type market_analysis

# ヘルプで選択肢に表示されることを確認
python3 pdf_analyzer.py --help
```

---

## 高度な設定例

### 1. 変数置換機能付きテンプレート

**テンプレートファイル**: `analysis_templates/industry_specific.txt`
```text
以下のPDFドキュメントの内容を{industry}業界の観点で分析してください。

【分析対象】
{text_content}

【{industry}業界特化分析】
重点領域: {focus_area}
分析期間: {analysis_period}
対象ステークホルダー: {stakeholder}
```

**config.json設定**:
```json
{
  "analysis_templates": {
    "mining_analysis": "analysis_templates/industry_specific.txt"
  },
  "template_variables": {
    "mining_analysis": {
      "industry": "鉱業",
      "focus_area": "資源開発・生産効率",
      "analysis_period": "過去5年間",
      "stakeholder": "投資家・規制当局"
    }
  }
}
```

### 2. 複数テンプレート組み合わせ

**config.json設定**:
```json
{
  "multi_template_analysis": {
    "complete_market_analysis": [
      "market_analysis",
      "competitive_analysis", 
      "financial_analysis"
    ],
    "investment_evaluation": [
      "financial_analysis",
      "market_analysis",
      "risk_assessment",
      "esg_analysis"
    ]
  }
}
```

**実行方法**:
```bash
# 複数テンプレートによる包括分析
python3 pdf_analyzer.py --analysis-type complete_market_analysis
```

---

## テンプレート作成のベストプラクティス

### 1. **明確な構造化**
```text
【分析対象】
{text_content}

【分析フレームワーク】
1. 観点1
2. 観点2
3. 観点3

【回答形式】
## セクション1
## セクション2
## セクション3
```

### 2. **具体的な指示**
```text
❌ 悪い例: "分析してください"
✅ 良い例: "収益性指標（ROE、ROA、売上高利益率）を算出し、業界平均と比較評価してください"
```

### 3. **出力形式の統一**
```text
【回答形式】
## セクション名
[具体的な内容指示]

## 数値分析
[定量的な分析結果]

## 改善提案
[具体的なアクションプラン]
```

### 4. **変数活用**
```text
# 汎用性を高める変数
{industry}     # 業界名
{focus_area}   # 重点分析領域  
{stakeholder}  # 対象ステークホルダー
{objective}    # 分析目的
```

---

## 業界特化テンプレート例

### 製造業分析テンプレート
```text
【製造業特化分析フレームワーク】
1. 生産効率・品質管理
2. サプライチェーン最適化
3. 技術革新・自動化
4. 環境・持続可能性対応
```

### 金融業分析テンプレート  
```text
【金融業特化分析フレームワーク】
1. 資産健全性・信用リスク
2. 収益構造・手数料収入
3. 規制対応・コンプライアンス
4. デジタル化・フィンテック対応
```

### 小売業分析テンプレート
```text
【小売業特化分析フレームワーク】
1. 店舗効率・売場生産性
2. 在庫管理・物流最適化
3. 顧客体験・オムニチャネル
4. デジタル変革・EC強化
```

---

## トラブルシューティング

### よくある問題

**1. テンプレートが読み込まれない**
```bash
# ファイルパスの確認
ls analysis_templates/your_template.txt

# config.jsonの構文確認
python3 -m json.tool config.json
```

**2. 変数が置換されない**
```json
// 正しい変数定義
"template_variables": {
  "your_analysis": {
    "variable_name": "variable_value"
  }
}
```

**3. 新しい分析タイプが選択肢に表示されない**
- プログラムの再起動
- help表示で確認: `python3 pdf_analyzer.py --help`

---

## まとめ

1. **テンプレートファイル作成** → `analysis_templates/new_type.txt`
2. **config.json設定** → `"analysis_templates"` に追加
3. **実行テスト** → `--analysis-type new_type`

この手順により、プログラム修正なしで無限に分析タイプを拡張できます！