# 設定ファイル（config.json）使用例

## 新しい分析タイプの追加方法

### 基本的な追加
```json
{
  "analysis_templates": {
    "existing_analysis": "analysis_templates/existing.txt",
    "new_analysis": "analysis_templates/new_analysis.txt"
  }
}
```

### 変数付きテンプレート
```json
{
  "analysis_templates": {
    "custom_analysis": "analysis_templates/custom_template.txt"
  },
  "template_variables": {
    "custom_analysis": {
      "industry": "製造業",
      "focus_area": "デジタル変革",
      "stakeholder": "経営陣"
    }
  }
}
```

### 複数テンプレート組み合わせ
```json
{
  "multi_template_analysis": {
    "comprehensive_review": [
      "financial_analysis",
      "market_analysis", 
      "risk_assessment"
    ]
  }
}
```

詳細な手順は [TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md) を参照してください。

---

## 基本設定

### 最新年要約分析（デフォルト）
```json
{
  "default_behavior": "latest",
  "model": "haiku",
  "analysis_type": "summary",
  "retry_settings": {
    "max_attempts": 3,
    "wait_time_multiplier": 30
  }
}
```
**実行**: `python3 pdf_analyzer.py`  
**動作**: 最新年のデータを軽量モデルで要約分析

---

## パフォーマンス重視設定

### 軽量・高速分析
```json
{
  "default_behavior": "latest",
  "model": "haiku",
  "analysis_type": "summary",
  "retry_settings": {
    "max_attempts": 5,
    "wait_time_multiplier": 10
  }
}
```
**特徴**: 短時間で基本的な分析を完了

### 高性能・詳細分析
```json
{
  "default_behavior": "latest",
  "model": "sonnet",
  "analysis_type": "general",
  "retry_settings": {
    "max_attempts": 3,
    "wait_time_multiplier": 60
  }
}
```
**特徴**: 時間はかかるが詳細で高品質な分析

---

## 用途別設定

### 年次レポート作成用
```json
{
  "default_behavior": "all",
  "model": "sonnet",
  "analysis_type": "trends",
  "retry_settings": {
    "max_attempts": 3,
    "wait_time_multiplier": 45
  }
}
```
**用途**: 全年のトレンド分析でレポート作成
**実行**: `python3 pdf_analyzer.py`

### 日常的な概要把握用
```json
{
  "default_behavior": "latest",
  "model": "haiku",
  "analysis_type": "summary",
  "retry_settings": {
    "max_attempts": 3,
    "wait_time_multiplier": 20
  }
}
```
**用途**: 毎日の最新情報確認
**実行**: `python3 pdf_analyzer.py`

### 特定期間の詳細調査用
```json
{
  "default_behavior": "latest",
  "model": "sonnet", 
  "analysis_type": "general",
  "retry_settings": {
    "max_attempts": 2,
    "wait_time_multiplier": 30
  }
}
```
**用途**: 特定年の詳細調査
**実行**: `python3 pdf_analyzer.py --years 2017,2018`

---

## API負荷対策設定

### 高負荷時（API制限時）
```json
{
  "default_behavior": "latest",
  "model": "haiku",
  "analysis_type": "summary",
  "retry_settings": {
    "max_attempts": 5,
    "wait_time_multiplier": 60
  }
}
```
**特徴**: 長い待機時間で確実に分析完了

### 通常時（安定時）
```json
{
  "default_behavior": "latest",
  "model": "sonnet",
  "analysis_type": "trends", 
  "retry_settings": {
    "max_attempts": 3,
    "wait_time_multiplier": 20
  }
}
```
**特徴**: 高性能モデルで効率的に分析

---

## カスタム設定例

### 月次レポート用
```json
{
  "default_behavior": "latest",
  "model": "sonnet",
  "analysis_type": "summary",
  "output_format": "markdown",
  "retry_settings": {
    "max_attempts": 3,
    "wait_time_multiplier": 30
  },
  "custom": {
    "report_type": "monthly",
    "focus_areas": ["financial", "operational"]
  }
}
```

### 比較分析用
```json
{
  "default_behavior": "all",
  "model": "sonnet",
  "analysis_type": "trends",
  "output_format": "markdown",
  "retry_settings": {
    "max_attempts": 2,
    "wait_time_multiplier": 45
  },
  "custom": {
    "comparison_focus": true,
    "highlight_changes": true
  }
}
```

---

## 設定の使い分け

### 現在利用可能
| 状況 | behavior | model | analysis_type | 用途 |
|------|----------|-------|---------------|------|
| 日常チェック | latest | haiku | summary | 最新情報の概要把握 |
| 週次レポート | latest | sonnet | trends | 詳細な傾向分析 |
| 月次レポート | all | sonnet | trends | 全体的なトレンド把握 |
| 特別調査 | 指定年 | sonnet | general | 深掘り分析 |
| 緊急確認 | latest | haiku | summary | 高速な概要確認 |

### 将来拡張予定
| 状況 | behavior | model | analysis_type | 用途 |
|------|----------|-------|---------------|------|
| 財務監査 | all | sonnet | financial_analysis | 財務指標の包括分析 |
| ESG評価 | latest | sonnet | esg_analysis | 持続可能性評価 |
| 投資判断 | all | sonnet | investment_analysis | 投資価値評価 |
| リスク管理 | latest | sonnet | risk_assessment | リスク要因特定 |
| 競合分析 | latest | sonnet | competitive_analysis | 競争力評価 |
| M&A検討 | all | sonnet | due_diligence | 統合効果分析 |

## 設定変更の手順

1. **設定ファイル編集**: `config.json`を用途に応じて編集
2. **実行**: `python3 pdf_analyzer.py`
3. **一時的変更**: コマンドライン引数で部分的に上書き可能

### 例：普段は軽量、特別な時だけ高性能
```bash
# 普段（config.jsonでhaiku設定）
python3 pdf_analyzer.py

# 特別な時だけ高性能モデル使用
python3 pdf_analyzer.py --model sonnet --analysis-type general
```