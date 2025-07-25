# PDF分析システム - Claude開発メモ

## プロジェクト概要
PDFファイルからテキスト・画像を抽出し、Claude AIで多角的分析を行うシステム。
テンプレートベースの拡張可能な分析フレームワークを採用。

## 主要ファイル構成
```
├── pdf_processor.py          # PDF抽出（独立動作）
├── pdf_analyzer.py           # AI分析（テンプレートベース）
├── config.json               # 設定管理
├── .env                      # Claude APIキー
├── analysis_templates/       # 分析テンプレート群
│   ├── financial_analysis.txt
│   ├── esg_analysis.txt
│   └── ... (9種類)
├── input/                    # PDF配置フォルダ
├── output/                   # PDF抽出データ
└── analysis_results/         # 分析結果（企業別・年度別）
    ├── [企業名]/
    │   ├── [年度]/           # 単一年度分析
    │   └── multi_year/       # 複数年度分析
    └── ...
```

## 核心アーキテクチャ

### 1. テンプレートベース分析システム
- **設計思想**: プログラム修正なしで新分析タイプ追加
- **実装**: `load_analysis_template()` + config.json設定
- **拡張性**: 無限の分析タイプ対応可能

### 2. 設定駆動実行
- **config.json**: 全設定の中央管理
- **コマンドライン**: 一時的設定上書き可能
- **柔軟性**: 用途別設定ファイル対応

### 3. 複数年・複数テンプレート分析
- **年次選択**: latest/specified/all
- **テンプレート組み合わせ**: multi_template_analysis
- **包括分析**: 一度の実行で多角的評価

### 4. 企業別・年度別ファイル管理システム
- **自動企業名抽出**: PDFファイル名から企業名を自動識別
- **年度別分類**: 単一年度は[企業名]/[年度]/、複数年度は[企業名]/multi_year/
- **整理された保存**: analysis_results/フォルダ下に企業別に整理
- **他企業対応**: 新しい企業のPDFを追加しても自動的に適切なフォルダ構造を作成

## 重要な実装詳細

### テンプレート読み込み機能
```python
def load_analysis_template(self, analysis_type: str) -> str:
    # config.jsonからパス取得 → ファイル読み込み → 変数置換
```

### 複数テンプレート分析
```python
def analyze_with_multiple_templates(self, target_years: List[str], analysis_type: str):
    # 設定された複数テンプレートを順次実行し統合レポート生成
```

### 企業別・年度別保存機能
```python
def save_analysis_result(self, result: str, filename: str, target_years: List[str] = None):
    # 企業名・年度を自動抽出してフォルダ構造を作成し保存
    # 例: analysis_results/Sony/2023/analysis_YYYYMMDD_HHMMSS.md
```

### フォールバック機能
- テンプレートファイル不在時のデフォルトプロンプト
- 設定ファイル不在時のデフォルト設定
- エラー時の継続処理

## 技術スタック
- **PDF処理**: PyMuPDF, pymupdf4llm
- **AI分析**: langchain-anthropic (Claude 3.5 Sonnet/Haiku)
- **設定管理**: JSON + 環境変数
- **言語**: Python 3.7+

## 実装済み分析タイプ

### 基本分析 (3種類)
- summary, trends, general

### 専門分析 (9種類)
- financial_analysis, esg_analysis, risk_assessment
- competitive_analysis, investment_analysis, comprehensive_audit
- due_diligence, scenario_analysis, custom_template

### 複合分析 (3種類)
- comprehensive_analysis, investment_review, due_diligence_full

## 開発・運用のベストプラクティス

### 新しい分析タイプ追加
1. **テンプレートファイル作成**: `analysis_templates/new_type.txt`
2. **config.json設定**: `"analysis_templates"` に追加
3. **テスト実行**: `--analysis-type new_type`

### API負荷対策
- リトライ機能: 設定可能な回数・間隔
- モデル選択: haiku(軽量) vs sonnet(高性能)
- 複数分析時の待機時間: 3秒間隔

### エラーハンドリング
- ファイル不在時のフォールバック
- API過負荷時の自動リトライ
- テンプレート読み込みエラー時の継続処理

## よく使うコマンドパターン

### 日常運用
```bash
# デフォルト実行（最新年・要約）
python3 pdf_analyzer.py

# 財務分析（高性能モデル）
python3 pdf_analyzer.py --analysis-type financial_analysis --model sonnet

# 包括分析（全年・複数テンプレート）
python3 pdf_analyzer.py --analysis-type comprehensive_analysis --all-years

# 特定企業の特定年度分析（結果は企業別フォルダに自動保存）
python3 pdf_analyzer.py --years 2023 --analysis-type financial_analysis
```

### 開発・テスト
```bash
# 新テンプレートテスト
python3 pdf_analyzer.py --analysis-type new_template --model haiku

# 設定ファイルテスト
python3 pdf_analyzer.py --config test_config.json

# ヘルプ確認
python3 pdf_analyzer.py --help
```

## トラブルシューティング

### API過負荷 (Error 529)
- モデルをhaikuに変更
- リトライ設定強化: max_attempts=5, wait_time_multiplier=60
- 時間を空けて再実行

### テンプレート関連
- ファイルパス確認: `ls analysis_templates/`
- JSON構文確認: `python3 -m json.tool config.json`
- フォールバック動作確認

### 設定ファイル
- デフォルト設定での実行: `--config /dev/null`
- 段階的設定確認: 最小設定から開始

## 将来の拡張予定

### 機能拡張
- 外部データ連携 (業界ベンチマーク等)
- テンプレート継承機能
- 動的プロンプト生成
- 結果の可視化 (グラフ・チャート)

### 分析タイプ拡張
- 業界特化分析 (製造業、金融業、小売業等)
- 地域特化分析 (日本、米国、EU等)
- 時系列特化分析 (季節性、周期性等)

## 設計原則

1. **拡張性優先**: プログラム修正なしでの機能追加
2. **設定駆動**: コードではなく設定での動作制御  
3. **フォールバック**: エラー時の安定した動作
4. **ユーザビリティ**: 複雑さを隠した簡単な操作
5. **保守性**: 明確な責任分離と文書化

## 注意事項

### セキュリティ
- APIキーは.envファイルで管理
- 機密情報のログ出力禁止
- テンプレートファイルの検証

### パフォーマンス
- 大量データ処理時のメモリ管理
- API rate limit考慮
- 複数分析時の時間コスト

### 互換性
- Python 3.7+ 対応
- 依存ライブラリの version lock
- config.json schema の後方互換性

---

このメモは Claude Code での効率的な開発継続のために作成されています。
プロジェクトの context として活用し、一貫性のある開発を支援します。