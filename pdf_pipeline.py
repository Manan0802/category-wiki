import os
import json
import logging
import argparse
from pathlib import Path
import base64

from config import PROJECT_ROOT, RAW_DIR
from utils.llm import call_llm
from utils.file_handler import load_skill

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PDFS_ROOT_DIR = PROJECT_ROOT / "pdfs"

def get_pdf_base64(pdf_path: Path) -> str:
    """Read PDF and encode to base64 data URI for the LLM gateway."""
    try:
        pdf_bytes = pdf_path.read_bytes()
        b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        return f"data:application/pdf;base64,{b64}"
    except Exception as e:
        logger.error(f"Error reading PDF {pdf_path.name}: {e}")
        return None

def extract_single_pdf(pdf_path: Path, mcat_name: str, output_path: Path) -> bool:
    """Extract a single PDF using the LLM and save the JSON to output_path."""
    skill_prompt = load_skill("pdf_extractor.md")
    if not skill_prompt:
        skill_prompt = "Extract key information from this PDF."

    pdf_base64 = get_pdf_base64(pdf_path)
    if not pdf_base64:
        return False
        
    user_prompt = f"Target Category: {mcat_name}\nPDF Filename: {pdf_path.name}\n\nPlease extract structured product data from the attached PDF document."
    
    try:
        logger.info(f"📄 Extracting {pdf_path.name} via LLM...")
        response = call_llm(system_prompt=skill_prompt, user_prompt=user_prompt, pdf_base64=pdf_base64)
        
        clean_response = response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:-3].strip()
        elif clean_response.startswith("```"):
            clean_response = clean_response[3:-3].strip()
            
        output_path.write_text(clean_response, encoding="utf-8")
        return True
    except Exception as e:
        logger.error(f"Failed to process {pdf_path.name}: {e}")
        return False

def process_pdfs(mcat_id: str, mcat_name: str):
    pdf_dir = PDFS_ROOT_DIR / f"pdf_{mcat_id}"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    # Write to a pool directory instead of the active input directory
    input_dir = PDFS_ROOT_DIR / f"pdf_json_{mcat_id}"
    input_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_path = pdf_dir / ".pdf_manifest.json"
    
    # Load manifest
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
            
    # Determine next pdf index
    next_idx = 1
    for data in manifest.values():
        idx = data.get("pdf_idx", 0)
        if idx >= next_idx:
            next_idx = idx + 1
            
    # Find current PDFs
    current_pdfs = [f for f in pdf_dir.iterdir() if f.suffix.lower() == ".pdf"]
    current_pdf_names = {f.name for f in current_pdfs}
    
    # Determine NEW and REMOVED
    previous_pdf_names = set(manifest.keys())
    
    new_pdfs = current_pdf_names - previous_pdf_names
    removed_pdfs = previous_pdf_names - current_pdf_names
    
    if not new_pdfs and not removed_pdfs:
        logger.info(f"No changes detected in {pdf_dir}. Everything is up to date.")
        return
        
    logger.info(f"Detected {len(new_pdfs)} NEW PDFs and {len(removed_pdfs)} REMOVED PDFs.")
    
    # Handle REMOVED
    for pdf_name in removed_pdfs:
        data = manifest.get(pdf_name, {})
        json_name = data.get("output_file")
        
        # Fallback to old naming style if not found in manifest
        if not json_name:
            json_name = f"{Path(pdf_name).stem}.json"
            
        json_path = input_dir / json_name
        if json_path.exists():
            json_path.unlink()
            logger.info(f"Deleted corresponding JSON for removed PDF: {json_name}")
        else:
            logger.warning(f"Could not find JSON to delete for {pdf_name}")
            
        del manifest[pdf_name]
        
    # Handle NEW
    skill_prompt = load_skill("pdf_extractor.md")
    if not skill_prompt:
        logger.warning("skills/pdf_extractor.md is empty or missing! Please write your prompt.")
        skill_prompt = "Extract key information from this PDF."

    for pdf_name in new_pdfs:
        logger.info(f"Processing new PDF: {pdf_name}...")
        pdf_path = pdf_dir / pdf_name
        
        # 1. Read PDF as base64
        pdf_base64 = get_pdf_base64(pdf_path)
        if not pdf_base64:
            logger.warning(f"Failed to read PDF file: {pdf_name}. Skipping LLM.")
            manifest[pdf_name] = {"status": "failed_read"}
            continue
            
        # 2. Call LLM
        user_prompt = f"Target Category: {mcat_name}\nPDF Filename: {pdf_name}\n\nPlease extract structured product data from the attached PDF document."
        
        try:
            logger.info(f"Sending {pdf_name} (base64 attached) to LLM for extraction...")
            response = call_llm(system_prompt=skill_prompt, user_prompt=user_prompt, pdf_base64=pdf_base64)
            
            # Clean up the response to just save the JSON
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:-3].strip()
            elif clean_response.startswith("```"):
                clean_response = clean_response[3:-3].strip()
                
            # 3. Save JSON
            json_name = f"pdf {next_idx} - {Path(pdf_name).stem}.json"
            json_path = input_dir / json_name
            
            # Write exactly what the LLM gave us
            json_path.write_text(clean_response, encoding="utf-8")
            logger.info(f"Successfully extracted and saved: {json_name}")
            
            # Update manifest
            manifest[pdf_name] = {
                "status": "processed",
                "pdf_idx": next_idx,
                "output_file": json_name
            }
            next_idx += 1
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_name} via LLM: {e}")

    # Save manifest
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    
    # Save token usage
    from utils.llm import get_token_log, get_total_usage, reset_token_log
    from utils.wiki_manager import save_token_usage
    
    token_log = get_token_log()
    if token_log:
        total = get_total_usage()
        for t in token_log:
            t["step"] = "PDF Extractor"
            t["node"] = "pdf_pipeline"
        save_token_usage(mcat_name, token_log, total, mcat_id, "PDF Processing")
        reset_token_log()
        
    logger.info("PDF pipeline complete! The input folder is now ready for the Wiki Agent.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Extraction Pipeline")
    parser.add_argument("mcat_id", type=str, help="The MCAT ID (e.g., 2047)")
    parser.add_argument("mcat_name", type=str, help="The Name of the Category (e.g., 'PVC Pipes')")
    
    args = parser.parse_args()
    process_pdfs(args.mcat_id, args.mcat_name)
