# PDF分析システム 使用ガイド

## クイックスタート

### 1. 基本セットアップ
```bash
# ライブラリインストール
pip install PyMuPDF pymupdf4llm langchain-anthropic python-dotenv

# APIキー設定（.envファイル）
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

### 2. 最速実行
```bash
# PDFを input/ フォルダに配置後
python3 pdf_processor.py    # PDF抽出
python3 pdf_analyzer.py     # AI分析（config.json設定使用）

# 結果は企業別・年度別に自動整理
# analysis_results/企業名/年度/analysis_YYYYMMDD_HHMMSS.md
```

---

## ワークフロー

### Step 1: PDF処理
```bash
python3 pdf_processor.py
```
- `input/`フォルダのPDFを自動処理
- `output/`フォルダに抽出データを保存（企業名-報告書名-年度形式）
- 処理済みファイルは自動スキップ

### Step 2: AI分析
```bash
python3 pdf_analyzer.py
```
- `output/`フォルダのデータを分析
- `config.json`の設定に従って実行
- 結果を`analysis_results/企業名/年度/`に企業別・年度別で自動整理保存

---

## 設定による使い分け

### 日常使用（軽量・高速）
**config.json**:
```json
{
  "default_behavior": "latest",
  "model": "haiku",
  "analysis_type": "summary"
}
```
**実行**: `python3 pdf_analyzer.py`

### 詳細分析（高性能）
**config.json**:
```json
{
  "default_behavior": "latest", 
  "model": "sonnet",
  "analysis_type": "general"
}
```
**実行**: `python3 pdf_analyzer.py`

### 全年比較分析
**config.json**:
```json
{
  "default_behavior": "all",
  "model": "sonnet", 
  "analysis_type": "trends"
}
```
**実行**: `python3 pdf_analyzer.py`

---

## コマンドライン活用

### 一時的な設定変更
```bash
# 設定ファイルは日常用、特別な時だけ詳細分析
python3 pdf_analyzer.py --model sonnet --analysis-type general

# 特定年だけ分析
python3 pdf_analyzer.py --years 2017,2018

# 全年分析（設定ファイル無視）
python3 pdf_analyzer.py --all-years
```

### 結果ファイル指定
```bash
python3 pdf_analyzer.py --output monthly_report_2024.md
```

---

## 実用的な使用例

### 例1: 毎日の情報チェック
**設定**: latest + haiku + summary
```bash
python3 pdf_analyzer.py  # 30秒程度で最新年の概要取得
```

### 例2: 週次レポート作成
**設定**: latest + sonnet + trends
```bash
python3 pdf_analyzer.py --output weekly_report.md
```

### 例3: 月次包括分析
**設定**: all + sonnet + trends
```bash
python3 pdf_analyzer.py --output monthly_analysis.md
```

### 例4: 特定期間の詳細調査
```bash
python3 pdf_analyzer.py --years 2016,2017 --model sonnet --analysis-type general --output investigation_2016-2017.md
```

---

## トラブルシューティング

### API過負荷エラー時
1. **軽量モデルに変更**:
   ```bash
   python3 pdf_analyzer.py --model haiku
   ```

2. **設定でリトライ強化**:
   ```json
   {
     "retry_settings": {
       "max_attempts": 5,
       "wait_time_multiplier": 60
     }
   }
   ```

3. **時間を空けて再実行**

### データが見つからない場合
```bash
# 利用可能データの確認
ls output/
python3 pdf_analyzer.py --help
```

### 設定ファイルエラー
```bash
# デフォルト設定で実行
python3 pdf_analyzer.py --config /dev/null
```

---

## 新しい分析タイプの追加

### 簡単2ステップでカスタム分析を追加
```bash
# Step 1: テンプレートファイル作成
echo "your analysis template" > analysis_templates/your_analysis.txt

# Step 2: config.jsonに追加
# "analysis_templates": {"your_analysis": "analysis_templates/your_analysis.txt"}

# Step 3: 実行
python3 pdf_analyzer.py --analysis-type your_analysis
```

詳細は [TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md) を参照

---

## 効率的な運用方法

### 1. 設定ファイルの使い分け
```bash
# 用途別設定ファイル準備
config_daily.json      # 日常チェック用
config_weekly.json     # 週次レポート用  
config_monthly.json    # 月次分析用

# 使い分け
python3 pdf_analyzer.py --config config_weekly.json
```

### 2. バッチ処理
```bash
# 複数分析の自動化例
python3 pdf_analyzer.py --output latest_summary.md
python3 pdf_analyzer.py --all-years --analysis-type trends --output full_trends.md
```

### 3. 結果の整理
```bash
# 分析結果を日付別フォルダに整理
mkdir -p results/$(date +%Y%m%d)
python3 pdf_analyzer.py --output results/$(date +%Y%m%d)/analysis.md
```

---

## パフォーマンス最適化

### 高速実行
- **model**: `haiku`
- **analysis_type**: `summary`
- **behavior**: `latest`

### 高品質分析
- **model**: `sonnet`
- **analysis_type**: `general`
- **retry強化**

### バランス型
- **model**: `sonnet`
- **analysis_type**: `summary`
- **behavior**: `latest`