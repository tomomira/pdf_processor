# PDF to Text + Image Conversion & AI Analysis

PDFファイルからテキストと画像を抽出し、AIで分析するPythonスクリプト群

## スクリプト構成

- **`pdf_processor.py`**: PDFからテキスト・画像を抽出
- **`pdf_analyzer.py`**: 抽出データをClaudeで分析
- **`config.json`**: 分析設定ファイル
- **`analysis_templates/`**: カスタム分析テンプレート

## クイックスタート

基本的な使用方法は [QUICK_START.md](QUICK_START.md) を参照してください。

## 1. PDF処理機能（pdf_processor.py）

### 機能
- PDFファイルを自動検出して処理
- ページごとのテキスト抽出（.txt形式）
- ページ全体の画像化（.png形式）
- 埋め込み画像の個別抽出
- 処理済みファイルの自動スキップ機能

### 使用方法

#### 1. 必要なライブラリをインストール
```bash
pip install PyMuPDF pymupdf4llm
```

#### 2. PDFファイルを配置
```
input/
├── document1.pdf
├── document2.pdf
└── ...
```

#### 3. スクリプト実行
```bash
python3 pdf_processor.py
```

#### 4. 結果確認
```
output/
├── document1/
│   ├── extraction_results.json
│   ├── page_001.png
│   ├── page_001.txt
│   ├── page_001_img_001.png
│   └── ...
└── document2/
    ├── extraction_results.json
    ├── page_001.png
    ├── page_001.txt
    └── ...
```

## 2. AI分析機能（pdf_analyzer.py）

### 機能
- 抽出データを Claude で分析
- 設定ファイルによる一括管理
- 年次選択機能（最新年/指定年/全年）
- 拡張可能な分析タイプ（テンプレートベース）
- 複数テンプレート組み合わせ分析
- モデル選択（Sonnet/Haiku）

### 前提条件

#### 1. 必要なライブラリをインストール
```bash
pip install langchain-anthropic python-dotenv
```

#### 2. APIキー設定
`.env`ファイルにClaude APIキーを設定：
```env
ANTHROPIC_API_KEY=your_api_key_here
```

### 設定ファイル（config.json）

```json
{
  "default_behavior": "latest",
  "model": "haiku",
  "analysis_type": "summary",
  "output_format": "markdown",
  "retry_settings": {
    "max_attempts": 3,
    "wait_time_multiplier": 30
  },
  "models": {
    "sonnet": "claude-3-5-sonnet-20241022",
    "haiku": "claude-3-5-haiku-20241022"
  },
  "behaviors": {
    "latest": {
      "description": "最新年分析（デフォルト）",
      "action": "analyze_latest_year"
    },
    "specified": {
      "description": "指定年分析", 
      "action": "analyze_specified_years"
    },
    "all": {
      "description": "全年分析",
      "action": "analyze_all_years"
    }
  }
}
```

#### 設定項目説明
- **`default_behavior`**: デフォルトの動作（`"latest"`, `"all"`）
- **`model`**: 使用モデル（`"haiku"`: 軽量・高速, `"sonnet"`: 高性能・詳細）
- **`analysis_type`**: 分析タイプ（`"summary"`, `"trends"`, `"general"`）
- **`retry_settings`**: リトライ設定（API過負荷対策）

### 使用方法

#### 基本実行（設定ファイル通り）
```bash
# config.jsonの設定で実行
python3 pdf_analyzer.py
```

#### コマンドライン引数で設定上書き
```bash
# 最新年分析（デフォルト）
python3 pdf_analyzer.py

# 指定年分析
python3 pdf_analyzer.py --years 2016,2017,2018

# 全年分析
python3 pdf_analyzer.py --all-years

# モデル・分析タイプ指定
python3 pdf_analyzer.py --model sonnet --analysis-type trends

# 結果ファイル名指定
python3 pdf_analyzer.py --output my_analysis.md

# 異なる設定ファイル使用
python3 pdf_analyzer.py --config my_config.json
```

#### 分析タイプ

##### 基本分析
- **`summary`**: 要約分析（主要ポイント抽出）
- **`trends`**: 傾向分析（年次比較・トレンド）
- **`general`**: 一般分析（多角的分析）

##### 拡張可能な分析タイプ（将来実装予定）

**業界特化分析**
- **`financial_analysis`**: 財務指標特化分析
- **`esg_analysis`**: ESG観点での分析
- **`risk_assessment`**: リスク評価特化
- **`market_analysis`**: 市場分析特化
- **`operational_analysis`**: 運営効率分析

**比較分析**
- **`competitive_analysis`**: 競合比較分析
- **`benchmark_analysis`**: ベンチマーク比較
- **`year_over_year`**: 前年同期比較
- **`industry_comparison`**: 業界比較
- **`peer_analysis`**: 同業他社比較

**専門分析**
- **`technical_analysis`**: 技術的分析
- **`regulatory_compliance`**: 規制遵守チェック
- **`sustainability_report`**: 持続可能性レポート
- **`investment_analysis`**: 投資判断支援
- **`strategic_analysis`**: 戦略分析

**複合分析**
- **`comprehensive_audit`**: 包括的監査
- **`strategic_planning`**: 戦略計画支援
- **`due_diligence`**: デューデリジェンス
- **`scenario_analysis`**: シナリオ分析
- **`swot_analysis`**: SWOT分析

**カスタム分析**
- **`custom_template`**: カスタムテンプレート分析
- **`multi_perspective`**: 多角的視点分析
- **`deep_dive`**: 深掘り調査分析

#### モデル選択
- **`haiku`**: 軽量・高速・低負荷（推奨）
- **`sonnet`**: 高性能・詳細分析・高負荷

### 実行例

#### 設定ファイルで全年傾向分析
```json
{
  "default_behavior": "all",
  "model": "sonnet", 
  "analysis_type": "trends"
}
```
```bash
python3 pdf_analyzer.py  # 全年の傾向分析を高性能モデルで実行
```

#### 特定用途で一時的に設定変更
```bash
# 普段はconfig.jsonで最新年・要約分析、特別に全年・傾向分析したい場合
python3 pdf_analyzer.py --all-years --analysis-type trends
```

## 3. ファイル構成

```
PDF_to_text+image_conversion/
├── pdf_processor.py          # PDF抽出スクリプト
├── pdf_analyzer.py           # AI分析スクリプト  
├── config.json               # 分析設定ファイル
├── .env                      # APIキー設定（要手動作成）
├── README.md                 # このファイル
├── QUICK_START.md            # クイックスタートガイド
├── USAGE.md                  # 使用ガイド
├── ANALYSIS_TYPES.md         # 分析タイプ詳細
├── TEMPLATE_GUIDE.md         # テンプレート追加ガイド
├── config_examples.md        # 設定例集
├── analysis_templates/       # 分析テンプレートフォルダ
│   ├── financial_analysis.txt
│   ├── esg_analysis.txt
│   ├── risk_assessment.txt
│   ├── competitive_analysis.txt
│   ├── investment_analysis.txt
│   ├── comprehensive_audit.txt
│   ├── due_diligence.txt
│   ├── scenario_analysis.txt
│   └── custom_template.txt
├── input/                    # PDF配置フォルダ
│   ├── document1.pdf
│   └── document2.pdf
└── output/                   # 抽出結果フォルダ
    ├── document1/
    │   ├── extraction_results.json
    │   ├── page_001.txt
    │   ├── page_001.png
    │   └── ...
    └── document2/
        └── ...
```

## 4. システム要件

- Python 3.7以上
- PyMuPDF
- pymupdf4llm（オプション）
- langchain-anthropic
- python-dotenv
- Claude API キー

## 5. ライセンス

MIT License
