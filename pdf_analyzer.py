#!/usr/bin/env python3
"""
PDF分析スタンドアロンスクリプト
outputフォルダのデータをClaudeで分析
"""

import os
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

try:
    from langchain_anthropic import ChatAnthropic
    LANGCHAIN_ANTHROPIC_AVAILABLE = True
except ImportError:
    LANGCHAIN_ANTHROPIC_AVAILABLE = False
    print("警告: langchain-anthropicがインストールされていません。")
    print("インストール方法: pip install langchain-anthropic")

try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("警告: python-dotenvがインストールされていません。")
    print("インストール方法: pip install python-dotenv")


class PDFAnalyzer:
    """PDF抽出データ分析クラス"""
    
    def __init__(self, output_dir: str = "output", config_file: str = "config.json"):
        """
        初期化
        
        Args:
            output_dir: PDF抽出データの出力ディレクトリ
            config_file: 設定ファイルのパス
        """
        self.output_dir = Path(output_dir)
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.config = self.load_config(config_file)
        self.model = self.get_model_name(self.config.get("model", "haiku"))
        
        # Claude APIキーの確認
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            self.logger.warning("ANTHROPIC_API_KEYが設定されていません。.envファイルを確認してください。")
        
        # LLMの初期化
        if LANGCHAIN_ANTHROPIC_AVAILABLE and self.api_key:
            # モデルに応じてmax_tokensを調整
            max_tokens = 4000 if "sonnet" in self.model else 2000
            
            self.llm = ChatAnthropic(
                model=self.model,
                api_key=self.api_key,
                temperature=0.3,
                max_tokens=max_tokens,
                max_retries=5
            )
        else:
            self.llm = None
            self.logger.warning("Claude LLMが利用できません。")
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info(f"設定ファイル読み込み: {config_file}")
                return config
            else:
                self.logger.warning(f"設定ファイルが見つかりません: {config_file}")
                return self.get_default_config()
        except Exception as e:
            self.logger.error(f"設定ファイル読み込みエラー: {str(e)}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を取得"""
        return {
            "default_behavior": "latest",
            "model": "haiku",
            "analysis_type": "summary",
            "retry_settings": {
                "max_attempts": 3,
                "wait_time_multiplier": 30
            },
            "models": {
                "sonnet": "claude-3-5-sonnet-20241022",
                "haiku": "claude-3-5-haiku-20241022"
            }
        }
    
    def get_model_name(self, model_alias: str) -> str:
        """モデルエイリアスから実際のモデル名を取得"""
        models = self.config.get("models", {})
        return models.get(model_alias, "claude-3-5-haiku-20241022")
    
    def get_available_years(self) -> List[str]:
        """利用可能な年のリストを取得"""
        if not self.output_dir.exists():
            self.logger.error(f"出力ディレクトリが存在しません: {self.output_dir}")
            return []
        
        years = []
        for item in self.output_dir.iterdir():
            if item.is_dir():
                # ディレクトリ名から年を抽出
                year_match = re.search(r'(\d{4})', item.name)
                if year_match:
                    years.append(year_match.group(1))
        
        return sorted(set(years), reverse=True)
    
    def get_latest_year(self) -> Optional[str]:
        """最新年を取得"""
        years = self.get_available_years()
        return years[0] if years else None
    
    def get_folders_by_years(self, years: List[str]) -> List[Path]:
        """指定年に対応するフォルダを取得"""
        folders = []
        for item in self.output_dir.iterdir():
            if item.is_dir():
                for year in years:
                    if year in item.name:
                        folders.append(item)
                        break
        return sorted(folders)
    
    def load_extraction_data(self, folder_path: Path) -> Optional[Dict[str, Any]]:
        """抽出データを読み込み"""
        results_file = folder_path / "extraction_results.json"
        if not results_file.exists():
            self.logger.warning(f"抽出結果ファイルが見つかりません: {results_file}")
            return None
        
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"ファイル読み込みエラー {results_file}: {str(e)}")
            return None
    
    def collect_text_content(self, data: Dict[str, Any]) -> str:
        """テキストコンテンツを収集"""
        text_parts = []
        
        # メタデータ情報
        metadata = data.get('metadata', {})
        if metadata.get('title'):
            text_parts.append(f"タイトル: {metadata['title']}")
        if metadata.get('author'):
            text_parts.append(f"著者: {metadata['author']}")
        
        # ページごとのテキスト
        pages = data.get('pages', [])
        for page in pages:
            text_content = page.get('text_content', '').strip()
            if text_content:
                text_parts.append(f"--- ページ {page.get('page_number', '?')} ---")
                text_parts.append(text_content)
        
        return '\n\n'.join(text_parts)
    
    def load_analysis_template(self, analysis_type: str) -> str:
        """分析タイプ別のプロンプトテンプレートを読み込み"""
        
        # config.jsonからテンプレートパスを取得
        templates = self.config.get("analysis_templates", {})
        template_path = templates.get(analysis_type)
        
        if template_path and Path(template_path).exists():
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                
                # テンプレート変数の置換
                variables = self.config.get("template_variables", {}).get(analysis_type, {})
                for key, value in variables.items():
                    template = template.replace(f"{{{key}}}", str(value))
                
                self.logger.info(f"テンプレート読み込み: {template_path}")
                return template
                
            except Exception as e:
                self.logger.error(f"テンプレート読み込みエラー {template_path}: {str(e)}")
                return self.get_default_prompt(analysis_type)
        
        # フォールバック: デフォルトプロンプト
        return self.get_default_prompt(analysis_type)

    def get_default_prompt(self, analysis_type: str) -> str:
        """デフォルトプロンプトを取得（テンプレートファイルがない場合）"""
        
        if analysis_type == "summary":
            return """以下のPDFドキュメントの内容を分析し、要約を作成してください。

【分析対象】
{text_content}

【要求事項】
1. 文書の主要なテーマと目的を特定
2. 重要なポイントを3-5個抜き出し
3. 数値データや統計がある場合は特に注目
4. 文書の結論や提言があれば明記
5. 1000文字程度で要約

【回答形式】
## 文書概要
[文書の種類・目的・期間等]

## 主要ポイント
1. [ポイント1]
2. [ポイント2]
...

## 重要な数値・データ
[該当する場合のみ]

## 結論・提言
[該当する場合のみ]
"""
        
        elif analysis_type == "trends":
            return """以下のPDFドキュメントの内容から、傾向やトレンドを分析してください。

【分析対象】
{text_content}

【分析観点】
1. 時系列での変化や成長傾向
2. 業績や指標の推移
3. 市場環境や競合状況の変化
4. 課題や機会の変遷
5. 戦略や取り組みの進化

【回答形式】
## 主要トレンド
[特定できたトレンドを列挙]

## 数値的変化
[具体的な数値の変化があれば]

## 戦略的変化
[戦略や方針の変化があれば]

## 今後の展望
[文書から読み取れる将来の方向性]
"""
        
        else:  # general analysis
            return """以下のPDFドキュメントの内容を詳細に分析してください。

【分析対象】
{text_content}

【分析要求】
文書の内容を多角的に分析し、構造化された形で報告してください。
重要な情報、数値データ、傾向、課題、機会などを含めてください。
"""

    def analyze_with_claude(self, text_content: str, analysis_type: str = "summary") -> Optional[str]:
        """Claudeで分析実行"""
        if not self.llm:
            self.logger.error("Claude LLMが利用できません。")
            return None
        
        # テンプレートからプロンプトを生成
        prompt_template = self.load_analysis_template(analysis_type)
        prompt = prompt_template.format(text_content=text_content)
        
        import time
        
        retry_settings = self.config.get("retry_settings", {})
        max_attempts = retry_settings.get("max_attempts", 3)
        wait_multiplier = retry_settings.get("wait_time_multiplier", 30)
        
        for attempt in range(max_attempts):
            try:
                response = self.llm.invoke(prompt)
                return response.content
            except Exception as e:
                if "overloaded" in str(e).lower() and attempt < max_attempts - 1:
                    wait_time = (attempt + 1) * wait_multiplier
                    self.logger.warning(f"サーバー過負荷 (試行 {attempt + 1}/{max_attempts}): {wait_time}秒後に再試行")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"Claude分析エラー: {str(e)}")
                    return None
        
        return None
    
    def analyze_single_year(self, year: str, analysis_type: str = "summary") -> Optional[str]:
        """単一年の分析"""
        folders = self.get_folders_by_years([year])
        if not folders:
            self.logger.warning(f"{year}年のデータが見つかりません。")
            return None
        
        all_analysis = []
        
        for folder in folders:
            self.logger.info(f"分析中: {folder.name}")
            
            # データ読み込み
            data = self.load_extraction_data(folder)
            if not data:
                continue
            
            # テキスト収集
            text_content = self.collect_text_content(data)
            if not text_content.strip():
                self.logger.warning(f"テキストコンテンツが空です: {folder.name}")
                continue
            
            # Claude分析
            analysis = self.analyze_with_claude(text_content, analysis_type)
            if analysis:
                all_analysis.append(f"=== {folder.name} ===\n{analysis}")
        
        return '\n\n' + '='*80 + '\n\n'.join(all_analysis) if all_analysis else None
    
    def analyze_with_multiple_templates(self, target_years: List[str], analysis_type: str) -> Optional[str]:
        """複数テンプレートで包括的分析"""
        
        # 複数テンプレート設定を取得
        multi_templates = self.config.get("multi_template_analysis", {})
        template_list = multi_templates.get(analysis_type, [analysis_type])
        
        self.logger.info(f"複数テンプレート分析開始: {template_list}")
        
        # 年数に応じて分析対象データを準備
        all_content = {}
        for year in target_years:
            folders = self.get_folders_by_years([year])
            year_content = []
            
            for folder in folders:
                data = self.load_extraction_data(folder)
                if data:
                    text_content = self.collect_text_content(data)
                    if text_content.strip():
                        year_content.append(text_content)
            
            if year_content:
                all_content[year] = '\n\n'.join(year_content)
        
        if not all_content:
            self.logger.warning("分析対象のデータが見つかりません。")
            return None
        
        # 全データを統合
        combined_text = '\n\n' + '='*80 + '\n\n'.join([
            f"【{year}年】\n{content}" for year, content in sorted(all_content.items())
        ])
        
        # 各テンプレートで分析実行
        results = []
        for i, template_type in enumerate(template_list):
            self.logger.info(f"分析実行中 ({i+1}/{len(template_list)}): {template_type}")
            
            try:
                result = self.analyze_with_claude(combined_text, template_type)
                if result:
                    results.append(f"## {template_type.upper().replace('_', ' ')}分析結果\n{result}")
                
                # API負荷軽減のため待機（最後以外）
                if i < len(template_list) - 1:
                    import time
                    time.sleep(3)
                    
            except Exception as e:
                self.logger.error(f"テンプレート分析エラー {template_type}: {str(e)}")
                continue
        
        if results:
            header = f"# 包括分析レポート ({analysis_type})\n分析対象年: {', '.join(target_years)}\n実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            return header + "\n\n" + "="*100 + "\n\n".join(results)
        
        return None
    
    def analyze_multiple_years(self, years: List[str], analysis_type: str = "trends") -> Optional[str]:
        """複数年の比較分析"""
        all_content = {}
        
        # 各年のデータを収集
        for year in years:
            folders = self.get_folders_by_years([year])
            year_content = []
            
            for folder in folders:
                data = self.load_extraction_data(folder)
                if data:
                    text_content = self.collect_text_content(data)
                    if text_content.strip():
                        year_content.append(f"【{folder.name}】\n{text_content}")
            
            if year_content:
                all_content[year] = '\n\n'.join(year_content)
        
        if not all_content:
            self.logger.warning("分析対象のデータが見つかりません。")
            return None
        
        # 複数年比較プロンプト
        combined_text = '\n\n' + '='*80 + '\n\n'.join([
            f"【{year}年】\n{content}" for year, content in sorted(all_content.items())
        ])
        
        prompt = f"""以下は複数年にわたるPDFドキュメントの内容です。年次比較分析を実行してください。

{combined_text}

【分析要求】
1. 年次変化の傾向分析
2. 成長や改善の指標
3. 課題の変遷
4. 戦略的変化
5. 将来への示唆

【回答形式】
## 年次比較サマリー
[各年の主要な特徴]

## 主要トレンド
[継続的な変化や傾向]

## 成長指標
[定量的な変化があれば]

## 戦略的変化
[方針や取り組みの変化]

## 課題と機会
[年次を通じて見える課題と機会]

## 将来への示唆
[トレンドから読み取れる将来の方向性]
"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            self.logger.error(f"複数年分析エラー: {str(e)}")
            return None
    
    def save_analysis_result(self, result: str, filename: str, target_years: List[str] = None):
        """分析結果を保存（企業別・年度別フォルダ構造）"""
        try:
            # 企業名と年度を抽出してフォルダ構造を作成
            if target_years and len(target_years) == 1:
                # 単一年度の場合
                company_name, year = self._extract_company_and_year(target_years[0])
                analysis_dir = Path("analysis_results") / company_name / year
            elif target_years and len(target_years) > 1:
                # 複数年度の場合
                company_name = self._extract_company_name_from_years(target_years)
                analysis_dir = Path("analysis_results") / company_name / "multi_year"
            else:
                # 年度情報がない場合はデフォルト
                analysis_dir = Path("analysis_results") / "unknown"
            
            # ディレクトリを作成
            analysis_dir.mkdir(parents=True, exist_ok=True)
            
            # ファイル名を調整（パスが指定されている場合はファイル名のみ取得）
            if Path(filename).parent != Path('.'):
                filename = Path(filename).name
            
            output_file = analysis_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# PDF分析結果\n")
                f.write(f"分析実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if target_years:
                    f.write(f"対象年度: {', '.join(target_years)}\n")
                f.write(f"保存場所: {output_file}\n\n")
                f.write(result)
            self.logger.info(f"分析結果を保存: {output_file}")
        except Exception as e:
            self.logger.error(f"ファイル保存エラー: {str(e)}")
    
    def _extract_company_and_year(self, year: str) -> tuple:
        """年度から企業名と年度を抽出"""
        # outputディレクトリから該当年度のフォルダを探す
        for item in self.output_dir.iterdir():
            if item.is_dir() and year in item.name:
                # フォルダ名から企業名を抽出（例: "YAL-Annual-Report-2016" -> "YAL"）
                company_match = re.match(r'^([^-]+)', item.name)
                if company_match:
                    return company_match.group(1), year
        return "unknown", year
    
    def _extract_company_name_from_years(self, years: List[str]) -> str:
        """複数年度から企業名を抽出（最初に見つかった企業名を使用）"""
        for year in years:
            company_name, _ = self._extract_company_and_year(year)
            if company_name != "unknown":
                return company_name
        return "unknown"


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='PDF抽出データ分析ツール')
    parser.add_argument('--years', type=str, help='分析対象年（例: 2016,2017,2018）')
    parser.add_argument('--all-years', action='store_true', help='全年のデータを分析')
    parser.add_argument('--analysis-type', choices=[
        'summary', 'trends', 'general',
        'financial_analysis', 'esg_analysis', 'risk_assessment', 
        'competitive_analysis', 'investment_analysis', 'comprehensive_audit',
        'due_diligence', 'scenario_analysis', 'custom_template',
        'comprehensive_analysis', 'investment_review', 'due_diligence_full'
    ], help='分析タイプ（設定ファイルより優先）')
    parser.add_argument('--model', choices=['sonnet', 'haiku'], 
                        help='使用するClaudeモデル（設定ファイルより優先）')
    parser.add_argument('--config', type=str, default='config.json', help='設定ファイルのパス')
    parser.add_argument('--output', type=str, help='結果保存ファイル名')
    
    args = parser.parse_args()
    
    print("PDF分析スクリプト開始")
    print("="*50)
    
    # 必要なライブラリの確認
    if not LANGCHAIN_ANTHROPIC_AVAILABLE:
        print("エラー: langchain-anthropicがインストールされていません。")
        print("インストール: pip install langchain-anthropic")
        return
    
    # 分析インスタンスを作成
    analyzer = PDFAnalyzer(config_file=args.config)
    
    # コマンドライン引数で設定を上書き
    if args.model:
        analyzer.model = analyzer.get_model_name(args.model)
    
    config_analysis_type = args.analysis_type if args.analysis_type else analyzer.config.get("analysis_type", "summary")
    config_behavior = analyzer.config.get("default_behavior", "latest")
    
    # 利用可能年の確認
    available_years = analyzer.get_available_years()
    if not available_years:
        print("分析対象データが見つかりません。")
        return
    
    print(f"利用可能年: {', '.join(available_years)}")
    
    # 分析対象年の決定（コマンドライン引数優先、次に設定ファイル）
    if args.all_years:
        target_years = available_years
        print(f"全年分析: {', '.join(target_years)}")
    elif args.years:
        target_years = [year.strip() for year in args.years.split(',')]
        # 利用可能年との交差を確認
        target_years = [year for year in target_years if year in available_years]
        if not target_years:
            print("指定された年のデータが見つかりません。")
            return
        print(f"指定年分析: {', '.join(target_years)}")
    else:
        # 設定ファイルのdefault_behaviorに基づく
        if config_behavior == "all":
            target_years = available_years
            print(f"設定ファイル（全年分析）: {', '.join(target_years)}")
        else:  # "latest" or その他
            latest_year = analyzer.get_latest_year()
            target_years = [latest_year] if latest_year else []
            print(f"設定ファイル（最新年分析）: {latest_year}")
    
    if not target_years:
        print("分析対象が特定できませんでした。")
        return
    
    # 分析実行
    try:
        print(f"\n分析開始 (タイプ: {config_analysis_type}, モデル: {analyzer.config.get('model', 'haiku')})")
        print("-" * 30)
        
        # 複数テンプレート分析の確認
        multi_templates = analyzer.config.get("multi_template_analysis", {})
        if config_analysis_type in multi_templates:
            result = analyzer.analyze_with_multiple_templates(target_years, config_analysis_type)
        elif len(target_years) == 1:
            result = analyzer.analyze_single_year(target_years[0], config_analysis_type)
        else:
            result = analyzer.analyze_multiple_years(target_years, config_analysis_type)
        
        if result:
            print("\n" + "="*50)
            print("分析結果")
            print("="*50)
            print(result)
            
            # ファイル保存
            if args.output:
                analyzer.save_analysis_result(result, args.output, target_years)
            else:
                # デフォルトファイル名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                default_filename = f"analysis_{timestamp}.md"
                analyzer.save_analysis_result(result, default_filename, target_years)
        else:
            print("分析結果を取得できませんでした。")
            
    except Exception as e:
        print(f"\nエラーが発生しました: {str(e)}")
        return


if __name__ == "__main__":
    main()