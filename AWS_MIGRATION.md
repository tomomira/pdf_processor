# PDF分析システム - AWSサーバレス移行計画

## 概要

このドキュメントは、現在のPDF分析システムをAWSサーバレス環境に移行するための包括的な計画書です。
定期的に更新し、移行に関する最新情報を維持します。

**更新日**: 2025-08-05  
**ステータス**: 移行検討中  
**移行可能性**: ✅ **高い**

---

## 現在のシステム構成

### アプリケーション構成
```
├── pdf_processor.py          # PDF抽出処理（PyMuPDF、pymupdf4llm）
├── pdf_analyzer.py           # AI分析処理（langchain-anthropic、Claude API）
├── config.json               # 設定管理
├── .env                      # Claude APIキー
├── analysis_templates/       # 分析テンプレート群（9種類）
├── input/                    # PDF配置フォルダ
├── output/                   # PDF抽出データ
└── analysis_results/         # 分析結果（企業別・年度別）
```

### 技術スタック
- **言語**: Python 3.7+
- **PDF処理**: PyMuPDF, pymupdf4llm
- **AI分析**: langchain-anthropic (Claude 3.5 Sonnet/Haiku)
- **設定管理**: JSON + 環境変数
- **データ保存**: ローカルファイルシステム

### 処理フロー
```
PDFアップロード → PDF抽出処理 → テキスト・画像保存 → AI分析実行 → 結果保存
```

---

## AWSサーバレス移行可能性評価

### ✅ 移行可能性: **高い**

#### 対応可能な要素
- **Python 3.7+**: Lambda完全対応
- **外部API連携**: Claude API（HTTP通信）
- **JSON設定管理**: Parameter Store/Secrets Manager対応
- **テキスト処理**: 純粋なPython処理
- **ファイル入出力**: S3で代替可能

#### 対応要検討の要素
- **PyMuPDF**: Lambda Layerまたはコンテナ対応必要
- **大容量ファイル処理**: Lambda実行時間制限（15分）への対策
- **メモリ使用量**: Lambda最大10GB制限（通常は問題なし）

---

## 推奨AWSアーキテクチャ

### パターン1: 完全サーバレス構成（推奨）

```
┌─────────────┐    S3イベント    ┌─────────────────┐
│   S3 Bucket │ ─────────────→ │ Lambda Function │
│(PDF保存)    │                │(pdf_processor)  │
└─────────────┘                └─────────────────┘
                                        │
                                        ▼ S3保存
┌─────────────┐                ┌─────────────────┐
│   S3 Bucket │ ←────────────── │抽出データ        │
│(抽出データ)  │                │                │
└─────────────┘                └─────────────────┘
       │                                
       │ S3イベント                      
       ▼                                
┌─────────────────┐              ┌─────────────────┐    
│ Lambda Function │ ─────────→ │   S3 Bucket     │
│(pdf_analyzer)   │   結果保存   │(分析結果)       │
└─────────────────┘              └─────────────────┘
       ▲                                
       │                                
┌─────────────────┐                      
│  API Gateway    │                      
│(REST API)       │                      
└─────────────────┘                      
```

#### 構成要素
- **S3**: PDFファイル、抽出データ、分析結果の保存
- **Lambda**: pdf_processor、pdf_analyzer の実行
- **API Gateway**: REST API提供
- **Parameter Store**: 設定管理
- **Secrets Manager**: APIキー管理
- **CloudWatch**: ログ・監視

### パターン2: ハイブリッド構成（大容量対応）

```
┌─────────────┐              ┌─────────────────┐
│   S3 Bucket │ ─────────→ │  ECS Fargate    │
│(PDF保存)    │   大容量     │(pdf_processor)  │
└─────────────┘              └─────────────────┘
                                     │
                                     ▼ S3保存
┌─────────────┐              ┌─────────────────┐
│   S3 Bucket │ ←─────────── │抽出データ        │
│(抽出データ)  │              │                │
└─────────────┘              └─────────────────┘
       │                            
       │ S3イベント                  
       ▼                            
┌─────────────────┐          ┌─────────────────┐
│ Lambda Function │ ───────→│   S3 Bucket     │
│(pdf_analyzer)   │  軽量処理 │(分析結果)       │
└─────────────────┘          └─────────────────┘
```

---

## 詳細移行計画

### Phase 1: インフラ構築（1-2週間）

#### S3バケット設計
```
pdf-analysis-system-{env}/
├── input/               # PDFファイル保存
├── extracted/           # 抽出データ保存
├── analysis-results/    # 分析結果保存
└── templates/           # 分析テンプレート
```

#### Lambda関数設計
```
1. pdf-processor-function
   - Runtime: Python 3.11
   - Memory: 3GB
   - Timeout: 15分
   - Trigger: S3 PUT event

2. pdf-analyzer-function  
   - Runtime: Python 3.11
   - Memory: 1GB
   - Timeout: 10分
   - Trigger: S3 PUT event / API Gateway
```

#### IAM Role設計
```yaml
pdf-processor-role:
  - S3: GetObject, PutObject (input, extracted buckets)
  - CloudWatch: CreateLogGroup, CreateLogStream, PutLogEvents

pdf-analyzer-role:
  - S3: GetObject, PutObject (extracted, analysis-results buckets)
  - Parameter Store: GetParameter
  - Secrets Manager: GetSecretValue
  - CloudWatch: CreateLogGroup, CreateLogStream, PutLogEvents
```

### Phase 2: コードリファクタリング（2-3週間）

#### ファイルI/O変更
```python
# Before (ローカルファイル)
with open('input/file.pdf', 'rb') as f:
    data = f.read()

# After (S3)
import boto3
s3 = boto3.client('s3')
obj = s3.get_object(Bucket='bucket', Key='input/file.pdf')
data = obj['Body'].read()
```

#### 設定管理変更
```python
# Before (config.json)
with open('config.json', 'r') as f:
    config = json.load(f)

# After (Parameter Store)
import boto3
ssm = boto3.client('ssm')
config = json.loads(
    ssm.get_parameter(Name='/pdf-analysis/config')['Parameter']['Value']
)
```

#### PyMuPDF対応
```dockerfile
# Lambda Layer用Dockerfile
FROM public.ecr.aws/lambda/python:3.11
RUN pip install PyMuPDF pymupdf4llm -t /opt/python
```

#### エラーハンドリング強化
```python
def lambda_handler(event, context):
    try:
        # 処理実行
        result = process_pdf(event)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        logger.error(f"処理エラー: {str(e)}")
        # CloudWatch Alarms連携
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### Phase 3: テスト・デプロイ（1-2週間）

#### テスト戦略
```
1. 単体テスト
   - 各Lambda関数の個別テスト
   - モックS3での動作確認

2. 統合テスト  
   - S3 → Lambda → S3 フローテスト
   - API Gateway経由のテスト

3. 性能テスト
   - 大容量PDFでの処理時間測定
   - 同時実行数テスト
   - メモリ使用量監視

4. 障害テスト
   - 異常ファイルでのエラーハンドリング
   - API制限時の挙動確認
```

#### デプロイ戦略
```
1. Blue/Green デプロイ
   - 新環境での並行運用
   - 段階的トラフィック移行

2. カナリアリリース
   - 一部処理での先行テスト
   - 問題なければ全体展開

3. ロールバック計画
   - 問題発生時の迅速な切り戻し
   - データ整合性の確保
```

---

## 移行のメリット・デメリット

### ✅ メリット

#### 運用面
- **自動スケール**: 処理量に応じた自動拡張・縮小
- **メンテナンスフリー**: サーバー管理・OS更新不要
- **高可用性**: AWSマネージドサービスの99.9%以上の可用性
- **監視・ログ**: CloudWatchによる統合監視

#### コスト面
- **従量課金**: 使用した分だけの支払い
- **初期コスト削減**: サーバー購入・設定不要
- **運用コスト削減**: インフラ管理人員不要
- **リソース効率**: 処理時間に応じた課金

#### セキュリティ面
- **IAM**: 細かい権限制御
- **VPC**: ネットワーク分離
- **暗号化**: 保存時・転送時の暗号化
- **監査ログ**: CloudTrailによる操作履歴

### ⚠️ デメリット・制約

#### 技術制約
- **実行時間制限**: Lambda 15分（大型PDF処理要注意）
- **メモリ制限**: Lambda 10GB（通常は問題なし）
- **コールドスタート**: 初回実行時の遅延
- **ベンダーロックイン**: AWS依存度向上

#### 運用制約
- **デバッグ難易度**: 分散環境でのトラブルシューティング
- **学習コスト**: AWSサービス習得必要
- **料金予測**: 従量課金での費用予測困難

---

## コスト試算

### 想定処理量
- **月間PDF処理数**: 1,000件
- **平均ファイルサイズ**: 10MB
- **平均処理時間**: 
  - PDF抽出: 2分
  - AI分析: 1分

### AWS料金試算（月額）

#### Lambda
```
pdf-processor (3GB, 2分実行):
1,000件 × 2分 × $0.0000166667/GB秒 × 3GB = $10

pdf-analyzer (1GB, 1分実行):  
1,000件 × 1分 × $0.0000166667/GB秒 × 1GB = $1

リクエスト料金:
2,000リクエスト × $0.0000002 = $0.4

Lambda合計: 約$11.4
```

#### S3
```
ストレージ (Standard):
- PDF: 1,000件 × 10MB = 10GB = $2.3
- 抽出データ: 10GB × 2 = 20GB = $4.6  
- 分析結果: 5GB = $1.15

リクエスト料金:
- PUT: 3,000回 = $0.15
- GET: 5,000回 = $0.02

S3合計: 約$8.22
```

#### その他
```
API Gateway: 1,000リクエスト = $3.5
Parameter Store: $0
Secrets Manager: $4 (1シークレット)
CloudWatch Logs: $5

その他合計: 約$12.5
```

#### **月額コスト合計: 約$32（約4,800円）**

### 従来環境との比較
```
現在（仮想サーバー想定）:
- EC2 t3.medium: $30/月
- EBS 100GB: $10/月  
- 運用保守: $100/月
合計: $140/月 (約21,000円)

削減効果: 約$108/月 (約16,200円) = 77%削減
```

---

## リスク評価と対策

### 🔴 高リスク

#### 1. PyMuPDF Lambda対応
**リスク**: ライブラリがLambda環境で動作しない可能性
**対策**: 
- 事前検証環境での動作確認
- コンテナイメージ利用によるフォールバック
- 代替ライブラリ（pdf2image等）の検討

#### 2. 大容量PDF処理
**リスク**: Lambda 15分制限での処理不可
**対策**:
- 事前に大容量ファイルをECS Fargateに振り分け
- PDFページ分割処理の実装
- Step Functionsでの並列処理

### 🟡 中リスク

#### 3. API制限
**リスク**: Claude API制限による処理失敗
**対策**:
- SQS + DLQでのリトライ機構
- API制限情報の監視・アラート
- 複数APIキーでの負荷分散

#### 4. データ移行
**リスク**: 既存データの移行時トラブル
**対策**:
- 段階的移行（新データから開始）
- 移行前バックアップ
- 移行検証手順の策定

### 🟢 低リスク

#### 5. 学習コスト
**リスク**: チーム のAWS習得に時間
**対策**:
- AWS研修・認定取得
- 段階的な機能追加
- 外部コンサルタント活用

---

## 実装タスク詳細

### タスク管理
```
□ Phase 1: インフラ構築（1-2週間）
  □ AWSアカウント・権限設定
  □ S3バケット作成・設定
  □ Lambda関数基盤作成
  □ API Gateway設定
  □ CloudWatch設定

□ Phase 2: コード移植（2-3週間）  
  □ pdf_processor Lambda化
  □ pdf_analyzer Lambda化
  □ S3操作への変更
  □ 設定管理変更
  □ エラーハンドリング実装

□ Phase 3: テスト・デプロイ（1-2週間）
  □ 単体テスト実施
  □ 統合テスト実施
  □ 性能テスト実施
  □ セキュリティテスト
  □ 本番デプロイ

□ Phase 4: 運用最適化（継続）
  □ 監視・アラート設定
  □ コスト最適化
  □ 性能チューニング
  □ ドキュメント整備
```

### 必要スキル・リソース
```
技術スキル:
- AWS Lambda, S3, API Gateway
- Python/boto3
- Infrastructure as Code (CloudFormation/CDK)
- Docker（コンテナ利用時）

人的リソース:
- AWSエンジニア: 1名（フルタイム 4-6週間）
- アプリエンジニア: 1名（パートタイム 2-4週間）
- テストエンジニア: 1名（パートタイム 1-2週間）
```

### マイルストーン
```
Week 1-2: インフラ構築完了
Week 3-5: コード移植完了
Week 6-7: テスト・デプロイ完了
Week 8+: 運用最適化・監視強化
```

---

## 技術検証項目

### 重要検証項目

#### 1. PyMuPDF Lambda動作確認
```python
# 検証コード例
import fitz
import pymupdf4llm

def test_pymupdf_on_lambda():
    # PDFファイル読み込みテスト
    doc = fitz.open('test.pdf')
    text = pymupdf4llm.to_markdown('test.pdf')
    return len(text) > 0
```

#### 2. 大容量PDF処理性能
```
テスト対象:
- 10MB PDF: 処理時間・メモリ使用量
- 50MB PDF: Lambda制限内処理可否  
- 100MB PDF: ECS Fargate移行判定
```

#### 3. 同時実行性能
```
テスト項目:
- 10件同時処理
- 100件同時処理  
- Lambda同時実行制限設定
- コスト影響評価
```

#### 4. エラー処理・リトライ
```
テスト項目:
- ファイル破損時の挙動
- API制限時のリトライ
- メモリ不足時の処理
- タイムアウト時の処理
```

---

## 運用監視計画

### CloudWatch監視項目

#### Lambda監視
```
メトリクス:
- Duration: 実行時間
- Errors: エラー率
- Throttles: 実行制限
- Memory Utilization: メモリ使用率
- Cold Start Duration: コールドスタート時間

アラーム設定:
- エラー率 > 5%
- 実行時間 > 10分
- メモリ使用率 > 90%
```

#### S3監視
```
メトリクス:
- NumberOfObjects: オブジェクト数
- BucketSizeBytes: バケットサイズ
- AllRequests: リクエスト数

アラーム設定:
- リクエストエラー > 1%
- ストレージ使用量 > 閾値
```

#### API Gateway監視
```
メトリクス:
- Count: リクエスト数  
- Latency: レイテンシ
- 4XXError: クライアントエラー
- 5XXError: サーバーエラー

アラーム設定:
- エラー率 > 3%
- レイテンシ > 30秒
```

### ログ管理
```
CloudWatch Logs設定:
- 保存期間: 90日
- ログレベル: INFO以上
- 構造化ログ（JSON形式）
- 機密情報のマスキング
```

### ダッシュボード
```
CloudWatch Dashboard構成:
1. システム全体KPI
   - 処理成功率
   - 平均処理時間
   - エラー発生数

2. リソース使用状況
   - Lambda実行数・時間
   - S3ストレージ使用量
   - API Gateway呼び出し数

3. コスト監視
   - 日次・月次コスト推移
   - サービス別コスト内訳
   - 予算アラート
```

---

## セキュリティ設計

### データ保護

#### 暗号化
```
保存時暗号化:
- S3: SSE-S3（デフォルト）
- Parameter Store: SecureString
- Secrets Manager: 自動暗号化

転送時暗号化:
- HTTPS/TLS 1.2以上
- API Gateway: SSL証明書
- Lambda間通信: VPC Endpoint利用
```

#### アクセス制御
```yaml
IAM Policy例:
LambdaExecutionRole:
  Effect: Allow
  Action:
    - s3:GetObject
    - s3:PutObject
  Resource: 
    - arn:aws:s3:::pdf-analysis-bucket/*
  Condition:
    StringEquals:
      's3:x-amz-server-side-encryption': 'AES256'
```

### ネットワークセキュリティ

#### VPC設計
```
プライベートサブネット:
- Lambda関数配置
- VPC Endpoint経由でAWSサービス接続

パブリックサブネット:
- NAT Gateway（外部API接続用）
- ALB（必要に応じて）

セキュリティグループ:
- 最小権限の原則
- 必要なポートのみ開放
```

#### API セキュリティ
```
API Gateway設定:
- API Key認証
- Usage Plan設定
- Rate Limiting
- CORS設定
- WAF統合（DDoS対策）
```

### 監査・コンプライアンス
```
CloudTrail設定:
- API呼び出し履歴記録
- S3アクセスログ
- 管理イベント・データイベント

Config Rules:
- セキュリティグループ設定チェック
- S3バケット暗号化チェック
- IAM権限過大付与チェック
```

---

## 継続的改善計画

### 性能最適化

#### Lambda最適化
```
1. コールドスタート削減
   - Provisioned Concurrency活用
   - 共通ライブラリのレイヤー化
   - 初期化処理の最適化

2. メモリ・CPU最適化  
   - Lambda Power Tuning実行
   - 適切なメモリサイズ選択
   - 並列処理の活用

3. タイムアウト調整
   - 処理時間分析
   - 適切なタイムアウト設定
   - 段階的処理への分割
```

#### ストレージ最適化
```
S3ライフサイクル設定:
- 30日後: Standard-IA移行
- 90日後: Glacier移行  
- 7年後: Deep Archive移行
- 不要データ: 自動削除

データ圧縮:
- テキストファイル圧縮
- 画像最適化
- 重複データ削除
```

### 機能拡張計画

#### 短期（3ヶ月以内）
```
- バッチ処理機能
- 処理状況確認API
- 異常終了時の自動復旧
- 詳細ログ・監視強化
```

#### 中期（6ヶ月以内）
```
- 複数ファイル一括処理
- 処理優先度制御
- キャッシュ機能
- パフォーマンス自動調整
```

#### 長期（1年以内）
```
- マルチリージョン対応
- AI精度向上（学習機能）
- リアルタイム分析
- 外部システム連携強化
```

### 運用成熟度向上
```
レベル1（基本運用）:
- 監視・アラート
- 基本的なバックアップ
- 手動デプロイ

レベル2（自動化）:  
- CI/CD パイプライン
- 自動テスト
- Infrastructure as Code

レベル3（最適化）:
- 自動スケーリング調整
- コスト最適化自動化
- 予測的監視・対応

レベル4（自律運用）:
- 自己修復機能
- AI活用した運用最適化
- ゼロダウンタイム運用
```

---

## 更新履歴

| 日付 | バージョン | 更新内容 | 更新者 |
|------|------------|----------|--------|
| 2025-08-05 | 1.0 | 初版作成 | Claude |

---

## 参考資料・関連ドキュメント

### AWS公式ドキュメント
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [Amazon S3 User Guide](https://docs.aws.amazon.com/s3/)
- [Amazon API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/)

### ベストプラクティス
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Serverless Application Lens](https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/)

### 社内関連ドキュメント
- [CLAUDE.md](./CLAUDE.md) - システム全体設計書
- [config.json](./config.json) - 現在の設定ファイル
- [analysis_templates/](./analysis_templates/) - 分析テンプレート

---

**注意**: このドキュメントは定期的に更新し、最新の技術動向と要件変更を反映していきます。
移行実施前には、最新版の確認と関係者レビューを必ず実施してください。