# クイックスタートガイド

## 基本的な使用方法

### 1. セットアップ
```bash
# ライブラリインストール
pip install PyMuPDF pymupdf4llm langchain-anthropic python-dotenv

# APIキー設定
echo "ANTHROPIC_API_KEY=your_api_key" > .env
```

### 2. PDF処理と分析
```bash
# PDF処理（inputフォルダにPDFを配置後）
python3 pdf_processor.py

# AI分析（config.jsonの設定で実行）
python3 pdf_analyzer.py
```

---

## 利用可能な分析タイプ

### 基本分析（すぐに使用可能）
```bash
python3 pdf_analyzer.py --analysis-type summary           # 要約分析
python3 pdf_analyzer.py --analysis-type trends            # 傾向分析
python3 pdf_analyzer.py --analysis-type general           # 一般分析
```

### 専門分析（テンプレートベース）
```bash
python3 pdf_analyzer.py --analysis-type financial_analysis    # 財務分析
python3 pdf_analyzer.py --analysis-type esg_analysis         # ESG分析
python3 pdf_analyzer.py --analysis-type risk_assessment      # リスク評価
python3 pdf_analyzer.py --analysis-type competitive_analysis # 競合分析
python3 pdf_analyzer.py --analysis-type investment_analysis  # 投資分析
```

### 複合分析（複数テンプレート組み合わせ）
```bash
python3 pdf_analyzer.py --analysis-type comprehensive_analysis  # 包括分析
python3 pdf_analyzer.py --analysis-type investment_review       # 投資レビュー
python3 pdf_analyzer.py --analysis-type due_diligence_full     # 完全DD
```

---

## カスタム分析の追加

### 簡単3ステップ
```bash
# 1. テンプレート作成
cat > analysis_templates/market_analysis.txt << 'EOF'
以下のPDFドキュメントの内容から市場分析を実行してください。

【分析対象】
{text_content}

【市場分析観点】
1. 市場規模・成長率
2. 競合状況
3. 顧客動向
4. 将来予測

【回答形式】
## 市場概況
## 競合分析
## 成長機会
## リスク要因
EOF

# 2. config.json編集（analysis_templatesに追加）
# "market_analysis": "analysis_templates/market_analysis.txt"

# 3. 実行
python3 pdf_analyzer.py --analysis-type market_analysis
```

---

## よく使う設定パターン

### 日常チェック用
```json
{
  "default_behavior": "latest",
  "model": "haiku", 
  "analysis_type": "summary"
}
```

### 詳細分析用
```json
{
  "default_behavior": "latest",
  "model": "sonnet",
  "analysis_type": "financial_analysis"
}
```

### 包括レビュー用
```json
{
  "default_behavior": "all",
  "model": "sonnet",
  "analysis_type": "comprehensive_analysis"
}
```

---

## トラブルシューティング

### API過負荷エラー時
```bash
# 軽量モデルに変更
python3 pdf_analyzer.py --model haiku

# 時間を空けて再実行
sleep 60 && python3 pdf_analyzer.py
```

### 設定ファイルエラー時
```bash
# JSON構文チェック
python3 -m json.tool config.json

# デフォルト設定で実行
python3 pdf_analyzer.py --config /dev/null
```

---

## 次のステップ

- 詳細な使用方法: [USAGE.md](USAGE.md)
- 分析タイプの詳細: [ANALYSIS_TYPES.md](ANALYSIS_TYPES.md)  
- カスタムテンプレート作成: [TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md)
- 設定例集: [config_examples.md](config_examples.md)