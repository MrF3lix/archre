import logging

from diff_match_patch import diff_match_patch

from reporter.util.contract_diff import clean_document, generate_llm_diff_summary
from reporter.util.significant_analysis import SignificantAnalysis

logger = logging.getLogger(__name__)


def compare_contracts(file1_path: str, file2_path: str):
    """Compares two markdown contract files from MinIO and returns significant change analysis."""

    analysis_json = None

    # 1. Read and Clean Documents
    with open(file1_path, "r", encoding="utf-8") as f:
        text1_raw = f.read()
    with open(file2_path, "r", encoding="utf-8") as f:
        text2_raw = f.read()

    logger.info("Cleaning documents...")
    text1 = clean_document(text1_raw)
    text2 = clean_document(text2_raw)
    logger.info("Documents cleaned.")

    # 2. Perform Diff
    logger.info("Performing diff...")
    dmp = diff_match_patch()
    diffs = dmp.diff_main(text1, text2)
    dmp.diff_cleanupSemantic(diffs)
    logger.info("Diff calculation complete.")

    # 3. Generate Summary Text (with context)
    logger.info("Generating LLM summary text...")
    summary_text = generate_llm_diff_summary(diffs)
    logger.info("LLM summary text generated.")

    # 4. Perform Significant Analysis (JSON Output)
    logger.info("Running significant changes analysis...")
    analyzer = SignificantAnalysis(summary_text)
    analysis_json = analyzer.run_analysis()
    logger.info("Significant changes analysis complete.")

    # Check if analysis itself reported an error
    if isinstance(analysis_json, dict) and "error" in analysis_json:
        logger.error(f"Significant analysis failed: {analysis_json['error']}")
        raise RuntimeError(f"LLM analysis failed: {analysis_json['error']}")

    return analysis_json
