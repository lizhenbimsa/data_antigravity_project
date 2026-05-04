import os
import json
import logging
from pathlib import Path
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarkdownPaperExtractor:
    def __init__(self, papers_dir: str, output_path: str):
        self.papers_dir = Path(papers_dir)
        self.output_path = Path(output_path)
        self.papers_data = []

    def extract_text_from_md(self, md_path: Path, max_chars: int = 8000) -> str:
        """
        Extract text from OCR markdown files. Limits to max_chars to capture Abstract/Intro 
        for LLM batch evaluation, without overflowing context.
        """
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                text = f.read()
                # Clean up typical OCR artifacts if necessary
                return text[:max_chars]
        except Exception as e:
            logger.error(f"Error reading {md_path.name}: {str(e)}")
            return ""

    def process_all_papers(self):
        logger.info(f"Scanning for Markdown PDF conversions in: {self.papers_dir}")
        md_files = list(self.papers_dir.rglob("*.md"))
        
        if not md_files:
            logger.warning("No markdown files found in the specified directory.")
            return

        logger.info(f"Found {len(md_files)} Markdown files. Starting extraction...")
        
        for md_path in tqdm(md_files, desc="Extracting text"):
            raw_text = self.extract_text_from_md(md_path)
            
            if not raw_text.strip():
                continue

            paper_info = {
                "file_name": md_path.name,
                "file_path": str(md_path.relative_to(self.papers_dir)),
                "raw_text_prefix": raw_text,
                "status": "extracted"
            }
            self.papers_data.append(paper_info)

    def save_results(self):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(self.papers_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Extraction complete. Results saved to: {self.output_path}")
        logger.info(f"Total papers successfully processed: {len(self.papers_data)}")

if __name__ == "__main__":
    PROJECT_ROOT = Path(r"f:\WiseSearch\data_antigravity_project\news_process")
    PAPERS_DIR = PROJECT_ROOT / "papers"
    OUTPUT_JSON = PROJECT_ROOT / "data" / "processed" / "papers_extracted.json"  # Phase 8: data_processed → data/processed
    
    extractor = MarkdownPaperExtractor(
        papers_dir=str(PAPERS_DIR),
        output_path=str(OUTPUT_JSON)
    )
    
    extractor.process_all_papers()
    extractor.save_results()
