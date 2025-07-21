#!/usr/bin/env python3
"""
PDF処理スタンドアロンスクリプト
inputフォルダのPDFファイルからテキスト・画像を抽出し、outputフォルダに保存
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("警告: PyMuPDFがインストールされていません。")
    print("インストール方法: pip install PyMuPDF")

try:
    import pymupdf4llm
    PYMUPDF4LLM_AVAILABLE = True
except ImportError:
    PYMUPDF4LLM_AVAILABLE = False
    print("警告: pymupdf4llmがインストールされていません。")
    print("インストール方法: pip install pymupdf4llm")


class SimplePDFProcessor:
    """シンプルなPDF処理クラス"""
    
    def __init__(self, input_dir: str = "input", output_dir: str = "output"):
        """
        初期化
        
        Args:
            input_dir: 入力ディレクトリ
            output_dir: 出力ディレクトリ
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.dpi = 150
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # 出力ディレクトリを作成
        self.output_dir.mkdir(exist_ok=True)
    
    def process_all_pdfs(self):
        """inputフォルダ内の全PDFファイルを処理"""
        if not self.input_dir.exists():
            self.logger.error(f"入力ディレクトリが存在しません: {self.input_dir}")
            return
        
        pdf_files = list(self.input_dir.glob("*.pdf"))
        
        if not pdf_files:
            self.logger.warning(f"PDFファイルが見つかりません: {self.input_dir}")
            return
        
        self.logger.info(f"{len(pdf_files)}個のPDFファイルを検出")
        
        # 処理対象ファイルをフィルタリング
        new_files = []
        skipped_files = []
        
        for pdf_file in pdf_files:
            output_folder = self.output_dir / pdf_file.stem
            if output_folder.exists() and output_folder.is_dir():
                # 処理済みフォルダが存在する場合はスキップ
                skipped_files.append(pdf_file.name)
                self.logger.info(f"スキップ（処理済み）: {pdf_file.name}")
            else:
                new_files.append(pdf_file)
        
        # 処理結果のサマリー表示
        if skipped_files:
            self.logger.info(f"処理済みファイル（スキップ）: {len(skipped_files)}個")
        if new_files:
            self.logger.info(f"新規処理対象ファイル: {len(new_files)}個")
        else:
            self.logger.info("新規処理対象ファイルはありません")
            return
        
        # 新規ファイルのみ処理
        for pdf_file in new_files:
            try:
                self.process_single_pdf(pdf_file)
            except Exception as e:
                self.logger.error(f"処理エラー {pdf_file.name}: {str(e)}")
    
    def process_single_pdf(self, pdf_path: Path):
        """単一PDFファイルの処理"""
        if not PYMUPDF_AVAILABLE:
            self.logger.error("PyMuPDFが利用できません。処理をスキップします。")
            return
        
        self.logger.info(f"処理開始: {pdf_path.name}")
        
        # 出力用ディレクトリを作成（PDFファイル名ベース）
        pdf_output_dir = self.output_dir / pdf_path.stem
        pdf_output_dir.mkdir(exist_ok=True)
        
        try:
            # PDFファイルを開く
            doc = fitz.open(str(pdf_path))
            
            # 抽出結果の初期化
            results = {
                'pdf_name': pdf_path.name,
                'output_dir': str(pdf_output_dir),
                'extraction_time': datetime.now().isoformat(),
                'page_count': len(doc),
                'metadata': self._extract_metadata(doc),
                'pages': []
            }
            
            self.logger.info(f"PDF情報: {pdf_path.name} ({len(doc)}ページ)")
            
            # ページ単位で処理
            for page_num in range(len(doc)):
                page_result = self._process_page(doc, page_num, pdf_output_dir)
                results['pages'].append(page_result)
                
                # 進捗ログ（10ページごと）
                if (page_num + 1) % 10 == 0:
                    self.logger.info(f"処理済み: {page_num + 1}/{len(doc)}ページ")
            
            # LLM向けフォーマット変換（利用可能な場合）
            if PYMUPDF4LLM_AVAILABLE:
                results['llm_format'] = self._convert_to_llm_format(str(pdf_path))
            
            # 結果をJSONファイルに保存
            self._save_results(results, pdf_output_dir)
            
            doc.close()
            self.logger.info(f"処理完了: {pdf_path.name}")
            
        except Exception as e:
            self.logger.error(f"PDF処理エラー {pdf_path.name}: {str(e)}")
            raise
    
    def _extract_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """PDFメタデータの抽出"""
        metadata = doc.metadata
        
        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', ''),
            'page_count': len(doc)
        }
    
    def _process_page(self, doc: fitz.Document, page_num: int, output_dir: Path) -> Dict[str, Any]:
        """ページ単位の処理"""
        page = doc[page_num]
        page_info = {
            'page_number': page_num + 1,
            'text_file': None,
            'image_file': None,
            'text_content': '',
            'embedded_images': [],
            'image_count': 0
        }
        
        # テキスト抽出
        text_content = self._extract_text_from_page(page)
        if text_content.strip():
            text_file = output_dir / f"page_{page_num + 1:03d}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            page_info['text_file'] = str(text_file)
            page_info['text_content'] = text_content
        
        # ページ全体を画像として保存
        image_file = self._extract_page_as_image(page, page_num, output_dir)
        if image_file:
            page_info['image_file'] = str(image_file)
        
        # 埋め込み画像の抽出
        embedded_images = self._extract_embedded_images(page, page_num, output_dir)
        page_info['embedded_images'] = [str(img) for img in embedded_images]
        page_info['image_count'] = len(embedded_images)
        
        return page_info
    
    def _extract_text_from_page(self, page: fitz.Page) -> str:
        """ページからテキストを抽出"""
        try:
            # テキストを抽出（辞書形式で詳細情報付き）
            text_dict = page.get_text("dict")
            
            # テキストブロックを処理
            text_content = []
            for block in text_dict["blocks"]:
                if block.get("type") == 0:  # テキストブロック
                    for line in block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                        if line_text.strip():
                            text_content.append(line_text.strip())
            
            return "\n".join(text_content)
            
        except Exception as e:
            self.logger.warning(f"テキスト抽出エラー: {str(e)}")
            # フォールバック：簡単なテキスト抽出
            return page.get_text()
    
    def _extract_page_as_image(self, page: fitz.Page, page_num: int, output_dir: Path) -> Optional[Path]:
        """ページを画像として抽出"""
        try:
            # ページを画像に変換
            mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            
            # 画像ファイルを保存
            image_file = output_dir / f"page_{page_num + 1:03d}.png"
            pix.save(str(image_file))
            
            return image_file
            
        except Exception as e:
            self.logger.warning(f"ページ画像抽出エラー (ページ {page_num + 1}): {str(e)}")
            return None
    
    def _extract_embedded_images(self, page: fitz.Page, page_num: int, output_dir: Path) -> List[Path]:
        """ページ内の埋め込み画像を抽出"""
        extracted_images = []
        
        try:
            # ページ内の画像を取得
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # 画像データを取得
                    xref = img[0]
                    pix = fitz.Pixmap(page.parent, xref)
                    
                    # CMYK画像の場合はRGBに変換
                    if pix.n - pix.alpha < 4:
                        # 画像ファイルを保存
                        image_file = output_dir / f"page_{page_num + 1:03d}_img_{img_index + 1:03d}.png"
                        pix.save(str(image_file))
                        extracted_images.append(image_file)
                    else:
                        # CMYK画像をRGBに変換
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                        image_file = output_dir / f"page_{page_num + 1:03d}_img_{img_index + 1:03d}.png"
                        pix.save(str(image_file))
                        extracted_images.append(image_file)
                    
                    pix = None
                    
                except Exception as e:
                    self.logger.warning(f"埋め込み画像抽出エラー (ページ {page_num + 1}, 画像 {img_index + 1}): {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.warning(f"埋め込み画像取得エラー (ページ {page_num + 1}): {str(e)}")
        
        return extracted_images
    
    def _convert_to_llm_format(self, pdf_path: str) -> Dict[str, Any]:
        """pymupdf4llmを使用してLLM向けフォーマットに変換"""
        try:
            # pymupdf4llmを使用してMarkdown形式に変換
            md_text = pymupdf4llm.to_markdown(pdf_path)
            
            return {
                'markdown': md_text,
                'format': 'markdown',
                'conversion_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"LLM形式変換エラー: {str(e)}")
            return {
                'markdown': '',
                'format': 'error',
                'error': str(e)
            }
    
    def _save_results(self, results: Dict[str, Any], output_dir: Path):
        """抽出結果をJSONファイルに保存"""
        try:
            results_file = output_dir / "extraction_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"抽出結果保存: {results_file}")
            
        except Exception as e:
            self.logger.error(f"結果保存エラー: {str(e)}")


def main():
    """メイン実行関数"""
    print("PDF処理スクリプト開始")
    print("="*50)
    
    # 必要なライブラリの確認
    if not PYMUPDF_AVAILABLE:
        print("エラー: PyMuPDFがインストールされていません。")
        print("インストール: pip install PyMuPDF")
        return
    
    # 処理インスタンスを作成
    processor = SimplePDFProcessor()
    
    # 全PDFファイルを処理
    try:
        processor.process_all_pdfs()
        print("\n" + "="*50)
        print("PDF処理完了")
        print(f"結果は {processor.output_dir} フォルダに保存されました")
        
    except Exception as e:
        print(f"\nエラーが発生しました: {str(e)}")
        return


if __name__ == "__main__":
    main()