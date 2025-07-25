本プログラムは`config.json`を読み込んで処理するプログラムです。

以下の点で`config.json`を使用している。

1. **初期化時の設定ファイル読み込み**（37行目）：
   - `__init__`メソッドで`config_file: str = "config.json"`をデフォルト引数として受け取る
   - `self.config = self.load_config(config_file)`で設定ファイルを読み込む

2. **設定ファイル読み込み機能**（77-88行目）：
   - `load_config`メソッドで指定されたJSONファイルを読み込む
   - ファイルが存在しない場合はデフォルト設定を使用

3. **config.jsonから読み込む設定項目**：
   - `model`: 使用するClaudeモデル（"haiku", "sonnet"など）
   - `analysis_type`: 分析タイプ（"summary", "trends"など）
   - `default_behavior`: デフォルト動作（"latest", "all"など）
   - `retry_settings`: リトライ設定
   - `models`: モデル名のマッピング
   - `analysis_templates`: 分析テンプレートのパス
   - `template_variables`: テンプレート変数
   - `multi_template_analysis`: 複数テンプレート分析設定

4. **コマンドライン引数での設定ファイル指定**（554行目）：
   - `--config`オプションで設定ファイルのパスを指定可能

このプログラムは、PDF抽出データをClaude AIで分析するツールで、`config.json`を通じて動作をカスタマイズできる設計になっています。


flowchart TD
    A["プログラム開始<br/>main()"] --> B["コマンドライン引数解析<br/>--years, --all-years, --analysis-type等"]
    B --> C["必要ライブラリ確認<br/>langchain-anthropic"]
    C --> D["PDFAnalyzer初期化<br/>__init__()"]
    
    D --> E["設定ファイル読み込み<br/>config.json"]
    E --> F["Claude API設定<br/>ANTHROPIC_API_KEY"]
    F --> G["LLMインスタンス作成<br/>ChatAnthropic"]
    
    G --> H["利用可能年取得<br/>get_available_years()"]
    H --> I{"分析対象年決定"}
    
    I --> J["--all-years指定?"]
    J -->|Yes| K["全年分析"]
    J -->|No| L["--years指定?"]
    L -->|Yes| M["指定年分析"]
    L -->|No| N["設定ファイル確認<br/>default_behavior"]
    
    N --> O{"latest or all?"}
    O -->|latest| P["最新年のみ"]
    O -->|all| K
    
    K --> Q["分析実行判定"]
    M --> Q
    P --> Q
    
    Q --> R{"複数テンプレート分析?"}
    R -->|Yes| S["analyze_with_multiple_templates()"]
    R -->|No| T{"単一年 or 複数年?"}
    
    T -->|単一年| U["analyze_single_year()"]
    T -->|複数年| V["analyze_multiple_years()"]
    
    S --> W["各テンプレートで分析実行"]
    U --> X["データ読み込み<br/>load_extraction_data()"]
    V --> Y["各年データ収集"]
    
    X --> Z["テキスト収集<br/>collect_text_content()"]
    Y --> AA["年次比較プロンプト生成"]
    W --> BB["テンプレート読み込み<br/>load_analysis_template()"]
    
    Z --> CC["Claude分析実行<br/>analyze_with_claude()"]
    AA --> CC
    BB --> CC
    
    CC --> DD["プロンプト生成"]
    DD --> EE["LLM.invoke()でClaude呼び出し"]
    EE --> FF{"API成功?"}
    
    FF -->|No| GG["リトライ処理<br/>max_attempts回まで"]
    GG --> EE
    FF -->|Yes| HH["分析結果取得"]
    
    HH --> II["結果表示"]
    II --> JJ["ファイル保存<br/>save_analysis_result()"]
    JJ --> LL["企業名・年度抽出<br/>_extract_company_and_year()"]
    LL --> MM["フォルダ構造作成<br/>analysis_results/企業名/年度/"]
    MM --> NN["ファイル保存<br/>analysis_YYYYMMDD_HHMMSS.md"]
    NN --> KK["処理完了"]
    
    style A fill:#e1f5fe
    style D fill:#f3e5f5
    style E fill:#fff3e0
    style CC fill:#e8f5e8
    style KK fill:#ffebee
    

はい、このプログラムの処理の流れを図解いたします。
Ran tool
このプログラムの処理フローは以下のような流れになっています：

## 主要な処理段階

1. **初期化段階**
   - コマンドライン引数の解析
   - 必要ライブラリの確認
   - 設定ファイル（config.json）の読み込み
   - Claude APIの設定とLLMインスタンス作成

2. **分析対象決定段階**
   - 利用可能な年の取得（outputディレクトリから）
   - コマンドライン引数または設定ファイルに基づく分析対象年の決定

3. **分析実行段階**
   - 複数テンプレート分析、単一年分析、複数年比較分析の選択
   - PDFデータの読み込みとテキスト抽出
   - 分析プロンプトの生成

4. **Claude分析段階**
   - Claude APIへのリクエスト送信
   - エラー時のリトライ処理
   - 分析結果の取得

5. **結果出力段階**
   - 分析結果の表示
   - 企業名・年度の自動抽出
   - 企業別・年度別フォルダ構造の自動作成
   - マークダウンファイルとして整理保存（analysis_results/企業名/年度/）

このプログラムは、config.jsonの設定に基づいて柔軟に動作し、複数の分析タイプとモデルに対応した包括的なPDF分析ツールとなっています。

