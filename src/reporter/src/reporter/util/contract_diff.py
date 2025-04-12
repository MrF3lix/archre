import argparse
import html
import os
import re
import sys

from diff_match_patch import diff_match_patch


def clean_document(text):
    """Remove page numbers, headers, footers and page break indicators."""
    # Remove page numbers with various formats
    text = re.sub(
        r"^Page\s+\d+\s+X$", "", text, flags=re.MULTILINE
    )  # Format: "Page 16 X"
    text = re.sub(r"^Page\s+\d+$", "", text, flags=re.MULTILINE)  # Format: "Page 5"
    text = re.sub(
        r"^Page\s+[A-Z]-\d+$", "", text, flags=re.MULTILINE
    )  # Format: "Page X-5"

    # Remove page break indicators
    text = re.sub(r"\*\*---\s*PAGE BREAK\s*---\*\*", "", text)

    # Remove standalone contract headers/footers that often appear at page breaks
    # (Adjust patterns if needed based on actual contract headers/footers)
    text = re.sub(r"^\s*Contract X\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*Broker ABC\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(
        r"^\s*2[34]\\X\s*$", "", text, flags=re.MULTILINE
    )  # Example: 23\X or 24\X (Corrected: Escaped backslash)

    # Optional: Remove lines containing "page" anywhere (can be aggressive)
    # text = re.sub(r'^.*?page\s+\d+.*?$', '', text, flags=re.IGNORECASE|re.MULTILINE)

    # Remove any extra blank lines that might have been created by removals
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove leading/trailing whitespace from the whole document
    text = text.strip()

    return text


def generate_custom_html_diff(diffs, file1_name, file2_name, text1_len, text2_len):
    """Generate a custom HTML visualization of the diff based on dmp_compare style."""
    html_parts = []

    # HTML header with styles from dmp_compare
    html_parts.append(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Contract Comparison: {file1_name} vs {file2_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.5; margin: 20px; }}
        .diff-container {{ display: flex; flex-direction: column; }}
        .diff-block {{ margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
        .diff-equal {{ background-color: #f9f9f9; }}
        .diff-insert {{ background-color: #e6ffe6; border-left: 3px solid #00cc00; }}
        .diff-delete {{ background-color: #ffe6e6; border-left: 3px solid #cc0000; }}
        .stats {{ margin-bottom: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px; border: 1px solid #e0e0e0; }}
        .diff-text {{ white-space: pre-wrap; font-family: 'Courier New', Courier, monospace; font-size: 0.9em; }}
        h1 {{ color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
        .summary {{ margin-top: 20px; }}
        .context-preview {{ color: #888; font-style: italic; }}
    </style>
</head>
<body>
    <h1>Contract Comparison: {file1_name} vs {file2_name}</h1>
    <div class="stats">
        <p><strong>{file1_name}:</strong> {text1_len:,} characters (cleaned)</p>
        <p><strong>{file2_name}:</strong> {text2_len:,} characters (cleaned)</p>
    </div>
    <div class="diff-container">
""")

    # Process diffs to create contextual chunks (grouping consecutive ops)
    current_op = None
    current_chunk = []
    chunks = []

    for op, text in diffs:
        if op != current_op and current_chunk:
            chunks.append((current_op, "".join(current_chunk)))
            current_chunk = []
        current_op = op
        current_chunk.append(text)

    if current_chunk:
        chunks.append((current_op, "".join(current_chunk)))

    # Generate HTML for each chunk
    for op, text in chunks:
        # Skip generating HTML for insertion/deletion blocks containing only whitespace
        if op != 0 and not text.strip():
            continue

        # Escape text and replace newlines AFTER escaping
        text_html = html.escape(text).replace("\n", "<br>")
        if op == 0:  # Equal
            # Only show preview for large unchanged chunks
            if len(text) > 300:  # Reduced threshold slightly
                preview = (
                    text[:150]
                    + "... ["
                    + str(len(text))
                    + " matching characters] ..."
                    + text[-150:]
                )
                preview_html = html.escape(preview).replace("\n", "<br>")
                html_parts.append(
                    f'<div class="diff-block diff-equal"><div class="diff-text context-preview">{preview_html}</div></div>'
                )
            else:
                html_parts.append(
                    f'<div class="diff-block diff-equal"><div class="diff-text">{text_html}</div></div>'
                )
        elif op == 1:  # Insertion
            html_parts.append(
                f'<div class="diff-block diff-insert"><div class="diff-text">{text_html}</div></div>'
            )
        elif op == -1:  # Deletion
            html_parts.append(
                f'<div class="diff-block diff-delete"><div class="diff-text">{text_html}</div></div>'
            )

    # HTML footer
    html_parts.append("""
    </div>
</body>
</html>
""")

    return "".join(html_parts)


def merge_numerical_diffs(diffs):
    """
    Attempts to merge adjacent numerical diffs with surrounding context.
    Looks for patterns like [EQUAL, DELETE, INSERT, EQUAL] where DELETE/INSERT
    are number-like and merges them with number context from EQUAL blocks.
    """
    print("Attempting to merge numerical diffs...")
    new_diffs = []
    i = 0
    n = len(diffs)
    # Allow symbols/space around digits/dots/commas/hyphens, robust to internal whitespace
    num_part_pattern = re.compile(r"^[^\da-zA-Z]*[\d,\.\s\-]+[^\da-zA-Z]*$")
    # Prefix: Capture symbol/bracket/space + optional digits/dots/spaces at end
    prefix_pattern = re.compile(r"([\$\€\£\(\s\{\[])([\d,\.\s]*)$")
    # Suffix: Capture optional digits/dots/spaces + %/bracket/space/unit/hyphen at start
    suffix_pattern = re.compile(
        r"^([\d,\.\s]*)([\%\)\s\}\]kKmMBb\-]|(?:\s*(?:million|billion|thousand)))",
        re.IGNORECASE,
    )

    processed_indices = set()

    while i < n:
        if i in processed_indices:
            i += 1
            continue

        op1, text1 = diffs[i]
        merged = False  # Flag to track if merge happens

        # Look for EQUAL, DEL/INS, INS/DEL, EQUAL pattern
        if op1 == 0 and i + 3 < n:
            op2, text2 = diffs[i + 1]
            op3, text3 = diffs[i + 2]
            op4, text4 = diffs[i + 3]

            if op2 != 0 and op3 == -op2 and op4 == 0:
                # Check if changed parts look number-like (ignoring surrounding whitespace)
                if num_part_pattern.match(text2.strip()) and num_part_pattern.match(
                    text3.strip()
                ):
                    prefix, text1_remainder = "", text1
                    prefix_match = prefix_pattern.search(text1)
                    if prefix_match and (
                        not prefix_match.group(1).isalnum()
                        or prefix_match.group(1) in "$€£(["
                    ):
                        prefix = prefix_match.group(1) + prefix_match.group(
                            2
                        )  # Symbol + digits/spaces
                        text1_remainder = text1[: prefix_match.start(1)]

                    suffix, text4_remainder = "", text4
                    suffix_match = suffix_pattern.search(text4)
                    if suffix_match:
                        match_grp1 = suffix_match.group(1)  # digits/dots/spaces
                        match_grp2 = suffix_match.group(2)  # suffix char/unit
                        if match_grp2 and (
                            not match_grp2.strip().isalnum()
                            or match_grp2.strip().lower()
                            in [
                                "k",
                                "m",
                                "b",
                                "%",
                                "-",
                                "million",
                                "thousand",
                                "billion",
                            ]
                            or match_grp2 in ")]}"
                        ):
                            suffix = match_grp1 + match_grp2
                            text4_remainder = text4[
                                suffix_match.end(0) :
                            ]  # Use end(0) to get end of entire match

                    # If we found a prefix or suffix, perform merge
                    if prefix or suffix:
                        print(
                            f"  Merging: '{prefix}{text2.strip()}{suffix}' vs '{prefix}{text3.strip()}{suffix}'"
                        )
                        if text1_remainder:
                            new_diffs.append((0, text1_remainder))
                        new_diffs.append((op2, prefix + text2 + suffix))
                        new_diffs.append((op3, prefix + text3 + suffix))
                        if text4_remainder:
                            new_diffs.append((0, text4_remainder))

                        processed_indices.update([i, i + 1, i + 2, i + 3])
                        i += 4
                        merged = True  # Mark merge occurred
                        # No 'continue' here, let loop check 'merged' flag

        # Default: If no merge happened, process current diff normally
        if not merged:
            new_diffs.append((op1, text1))
            # Mark this index as processed since we are adding it to new_diffs
            processed_indices.add(i)
            i += 1  # Only increment by 1 if no merge happened

    print(f"Finished merging. Original diffs: {n}, Merged diffs: {len(new_diffs)}")
    return new_diffs


def generate_llm_diff_summary(diffs, context_chars=75):
    """Generates a summary of diffs suitable for LLM analysis, including context."""
    summary_parts = ["Summary of Contract Changes:\n==============================\n"]
    change_count = 0
    text1_pos = 0
    text2_pos = 0
    # Reconstruct original texts to easily get context
    original_text1 = "".join([text for op, text in diffs if op != 1])
    original_text2 = "".join([text for op, text in diffs if op != -1])

    processed_insertion_index = -1  # To skip adjacent insertions already handled

    for i, (op, data) in enumerate(diffs):
        if i == processed_insertion_index:
            continue  # Skip insertion that was handled along with previous deletion

        current_len = len(data)
        if op == 0:  # Equal
            text1_pos += current_len
            text2_pos += current_len
        elif op == -1 or op == 1:  # Deletion or Insertion
            change_count += 1
            summary_parts.append(
                f"\n\n==================== CHANGE {change_count} ===================="
            )

            # --- Calculate Context --- Context based on position *before* this change
            start_context1 = max(0, text1_pos - context_chars)
            # Use original_text1 for context before deletion/change start
            context_before = (
                original_text1[start_context1:text1_pos].replace("\n", " ").strip()
            )
            summary_parts.append(f"CONTEXT_BEFORE: ...{context_before}")

            # --- Process Change --- Handle deletions and adjacent/standalone insertions
            deleted_text = "(No text deleted)"
            inserted_text = "(No text inserted)"

            if op == -1:  # Deletion
                deleted_text = data.strip()
                text1_pos += current_len
                # Check for adjacent insertion
                if i + 1 < len(diffs) and diffs[i + 1][0] == 1:
                    inserted_text = diffs[i + 1][1].strip()
                    text2_pos += len(diffs[i + 1][1])  # Advance text2 pointer
                    processed_insertion_index = i + 1  # Mark insertion as processed
            elif op == 1:  # Standalone Insertion (already checked it wasn't processed)
                inserted_text = data.strip()
                text2_pos += current_len
                # text1_pos remains unchanged for standalone insertion

            summary_parts.append(f"--- DELETED ---\n{deleted_text}")
            summary_parts.append(f"+++ INSERTED +++\n{inserted_text}")

            # --- Context After --- Context based on position *after* this change in the *new* text
            end_context2 = min(len(original_text2), text2_pos + context_chars)
            context_after = (
                original_text2[text2_pos:end_context2].replace("\n", " ").strip()
            )
            summary_parts.append(f"CONTEXT_AFTER: {context_after}...")

            summary_parts.append("=============================================")

    summary = "\n".join(summary_parts)
    print(f"LLM summary generated with {change_count} change blocks.")
    # Optional: Print a snippet for verification
    # print("\n--- LLM Diff Summary Snippet ---")
    # print(summary[:2000]) # Print first 2000 chars
    # print("--- End Snippet ---")
    return summary


def main():
    """Main function to compare two files and generate HTML diff."""
    parser = argparse.ArgumentParser(
        description="Compare two files using diff-match-patch and generate an HTML diff."
    )
    parser.add_argument("file1", help="Path to the first file (e.g., older version).")
    parser.add_argument("file2", help="Path to the second file (e.g., newer version).")
    parser.add_argument(
        "-o", "--output", help="Path to save the HTML diff output file.", default=None
    )
    parser.add_argument(
        "-so",
        "--summary-output",
        help="Path to save the LLM summary text file.",
        default=None,
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Disable document cleaning before diffing.",
    )
    args = parser.parse_args()

    # Read file contents
    try:
        with open(args.file1, "r", encoding="utf-8") as f1:
            text1 = f1.read()
        with open(args.file2, "r", encoding="utf-8") as f2:
            text2 = f2.read()
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading files: {e}", file=sys.stderr)
        sys.exit(1)

    # Clean the text before diffing
    print("Cleaning documents...")
    cleaned_text1 = clean_document(text1)
    cleaned_text2 = clean_document(text2)
    print("Documents cleaned.")

    # Initialize diff-match-patch
    dmp = diff_match_patch()
    dmp.Diff_Timeout = 0  # Set timeout to 0 for potentially long contracts

    # Compute the diff on cleaned text
    print("Computing diff...")
    diffs = dmp.diff_main(cleaned_text1, cleaned_text2)
    print("Diff computed.")

    # Improve human readability
    print("Cleaning up diff...")
    dmp.diff_cleanupSemantic(diffs)
    print("Diff cleaned up.")

    # Merge numerical diffs
    diffs = merge_numerical_diffs(diffs)

    # Generate HTML representation of the diff using the custom function
    print("Generating HTML...")
    file1_basename = os.path.basename(args.file1)
    file2_basename = os.path.basename(args.file2)
    output_content = generate_custom_html_diff(
        diffs, file1_basename, file2_basename, len(cleaned_text1), len(cleaned_text2)
    )
    print("HTML generated.")

    # Determine output filename
    if args.output:
        output_filename = args.output
    else:
        base1 = os.path.splitext(os.path.basename(args.file1))[0]
        base2 = os.path.splitext(os.path.basename(args.file2))[0]
        output_filename = f"simple_diff_{base1}_vs_{base2}.html"

    # Write the HTML diff to the output file
    try:
        with open(output_filename, "w", encoding="utf-8") as f_out:
            f_out.write(output_content)  # Write the generated HTML directly
        print(f"HTML diff saved to {output_filename}")
    except Exception as e:
        print(f"Error writing HTML file: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate LLM Summary
    llm_summary = generate_llm_diff_summary(diffs)
    print("\n--- LLM Diff Summary --- <see file for full content>")
    # print(llm_summary) # Optionally keep printing short version or disable
    print(f"[... {len(llm_summary)} characters generated ...]")
    print("--- End LLM Diff Summary ---")

    # Determine summary filename
    summary_filename = args.summary_output
    if not summary_filename:
        if args.output:
            # Derive from HTML output name
            base, _ = os.path.splitext(args.output)
            summary_filename = base + "_summary.txt"
        else:
            # Default name if no HTML output specified
            summary_filename = "llm_diff_summary.txt"

    # Save summary to file
    try:
        with open(summary_filename, "w", encoding="utf-8") as f:
            f.write(llm_summary)
        print(f"LLM summary saved to {summary_filename}")
    except Exception as e:
        print(f"Error writing LLM summary file: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
