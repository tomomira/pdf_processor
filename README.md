# PDF to Text + Image Conversion

PDFファイルからテキストと画像を抽出するPythonスクリプト

## 機能

- PDFファイルを自動検出して処理
- ページごとのテキスト抽出（.txt形式）
- ページ全体の画像化（.png形式）
- 埋め込み画像の個別抽出
- 処理済みファイルの自動スキップ機能

## 使用方法

### 1. 必要なライブラリをインストール

```bash
pip install PyMuPDF pymupdf4llm
```

### 2. PDFファイルを配置

```
input/
├── document1.pdf
├── document2.pdf
└── ...
```

### 3. スクリプト実行

```bash
python3 pdf_processor.py
```

### 4. 結果確認

```
output/
├── document1/
│   ├── page_001.png
│   ├── page_001.txt
│   ├── page_001_img_001.png
│   └── ...
└── document2/
    ├── page_001.png
    ├── page_001.txt
    └── ...
```

## 特徴

- **自動検出**: inputフォルダ内の全PDFファイルを自動処理
- **効率的**: 処理済みファイルは自動的にスキップ
- **詳細ログ**: 処理状況を10ページごとに表示
- **エラーハンドリング**: 問題があるページも続行して処理

## システム要件

- Python 3.7以上
- PyMuPDF
- pymupdf4llm（オプション）

## ライセンス

MIT License