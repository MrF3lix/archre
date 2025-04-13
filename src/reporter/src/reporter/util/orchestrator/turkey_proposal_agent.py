"""
Standalone agent to generate a Turkey underwriting proposal report
using direct file loading and LLM synthesis with complex total calculation.
"""

import argparse
import json
import re
from pathlib import Path

from dotenv import load_dotenv
from llama_index.llms.google_genai import GoogleGenAI

# --- Configuration --- #
load_dotenv()

# LLM Configuration
LLM_PROVIDER = "google"
MODEL_NAME = "gemini-2.0-flash"  # Using the consistent model
TEMPERATURE = 0.1
MAX_OUTPUT_TOKENS = 4096

# File Paths
OUTPUT_REPORT_FILE = (
    Path(__file__).resolve().parent.parent / "generated_turkey_proposal_report.md"
)

# Report Structure Template (Corrected to match LLM instructions)
REPORT_STRUCTURE_TEMPLATE = """
# Underwriting Proposal Report: Turkey

## Summary
[Provide a concise summary of the submission for [Cedant Name], key terms (e.g., layers, limits), and overall recommendation based *only* on the provided data files.]

## Key Findings
[List key findings from analyzing the data. Focus on important aspects like limits, premium, structure, perils, notable clauses based *only* on the provided data files. **Specifically analyze and report on any significant changes in the underlying exposure (e.g., Total Sum Insured growth, changes in per-policy limits mentioned in submission data or wording) and explicitly link these changes to the observed increases in contract limits, excesses, and premiums.** Consider the significant changes context when identifying findings.]

## Structure / Key Changes
[Provide a brief description of the contract structure (e.g., layers, limits, attachment points from terms_data) and any key changes identified *only* from the provided submission/terms/wording/changes files.]

## Historical Losses
[Summarize the key historical loss information found within the provided submission data context (e.g., from turkey_submission.json). Mention significant losses, trends, or relevant metrics.]

## Why this opportunity:
[Provide key reasons why this is a good opportunity based *only* on the provided data files. Consider the significant changes context.]

## Suggested Participation
Based on the analysis, I suggest the following participation percentages (provide ONLY the numbers):
All Layers: [Percentage for all non-top layers e.g., 5.00%]
Top Layer: [Percentage for the identified top layer e.g., 2.50%]

## ROL Calculation (Placeholder - Script Calculated)
Layer 1: ROL: [ROL Layer 1 %]
Layer 2: ROL: [ROL Layer 2 %]
Layer 3: ROL: [ROL Layer 3 %]
# Add more layers placeholders if needed

## Total Line (Placeholder - Script Calculated)
Total Limit: [Calculated Total Limit TRY]
Total Premium: [Calculated Total Premium TRY]
"""


# --- Helper Functions --- #
def load_file(file_path: Path) -> str | None:
    """Loads content from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def load_json_data(file_path: Path) -> dict | None:
    """Loads JSON data from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data from {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error loading JSON data from {file_path}: {e}")
        return None


def initialize_llm():
    """Initializes the LLM."""
    try:
        if LLM_PROVIDER == "google":
            llm = GoogleGenAI(
                model_name=MODEL_NAME,
                temperature=TEMPERATURE,
            )
            return llm
        else:
            print(f"Error: LLM provider '{LLM_PROVIDER}' not supported.")
            return None
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return None


# --- Helper Function to Find Top Layer --- #
def identify_top_layer(layers: list[dict]) -> str | None:
    """Identifies the top layer based on the highest occurrenceAttachment."""
    top_layer_name = None
    max_attachment = -1

    for layer in layers:
        if not isinstance(layer, dict):
            print(f"Warning: Skipping invalid layer data: {layer}")
            continue

        layer_name = layer.get("name")
        attachment = layer.get("occurrenceAttachment")

        if layer_name is None or attachment is None:
            print(f"Warning: Skipping layer with missing name or attachment: {layer}")
            continue

        try:
            attachment_val = float(attachment)
            if attachment_val > max_attachment:
                max_attachment = attachment_val
                top_layer_name = layer_name
        except (ValueError, TypeError):
            print(
                f"Warning: Could not parse occurrenceAttachment for layer '{layer_name}': {attachment}"
            )
            continue

    if top_layer_name:
        print(f"Identified top layer: {top_layer_name} (Attachment: {max_attachment})")
    else:
        print("Warning: Could not identify top layer.")

    return top_layer_name


# --- Helper Function to Parse Suggested Percentages --- #
def parse_suggested_percentages(llm_output: str) -> tuple[float | None, float | None]:
    """Parses the suggested participation percentages from the LLM output."""
    all_layers_perc = None
    top_layer_perc = None

    all_layers_match = re.search(
        r"^\s*All Layers:\s*\[?(\d+\.?\d*)\%?\s*\]?",
        llm_output,
        re.MULTILINE | re.IGNORECASE,
    )
    top_layer_match = re.search(
        r"^\s*Top Layer:\s*\[?(\d+\.?\d*)\%?\s*\]?",
        llm_output,
        re.MULTILINE | re.IGNORECASE,
    )

    if all_layers_match:
        try:
            all_layers_perc = float(all_layers_match.group(1)) / 100.0
        except (ValueError, IndexError):
            print("Error converting 'All Layers' percentage.")
            all_layers_perc = None

    if top_layer_match:
        try:
            top_layer_perc = float(top_layer_match.group(1)) / 100.0
        except (ValueError, IndexError):
            print("Error converting 'Top Layer' percentage.")
            top_layer_perc = None

    if all_layers_perc is not None and top_layer_perc is not None:
        print(
            f"Parsed percentages: All Layers={all_layers_perc*100:.2f}%, Top Layer={top_layer_perc*100:.2f}%"
        )
    elif all_layers_perc is not None:
        print(
            f"Parsed percentages: All Layers={all_layers_perc*100:.2f}%, Top Layer=Not Found"
        )
    elif top_layer_perc is not None:
        print(
            f"Parsed percentages: All Layers=Not Found, Top Layer={top_layer_perc*100:.2f}%"
        )
    else:
        print("Could not parse participation percentages from LLM output.")

    return all_layers_perc, top_layer_perc


# --- Helper Function to Calculate Weighted Totals and ROLs --- #
def calculate_weighted_totals_and_rols(
    layers: list[dict],
    all_layers_perc: float,
    top_layer_perc: float,
    top_layer_name: str,
) -> tuple[float, float, dict]:
    """Calculates the weighted totals and ROLs for the layers."""
    total_limit_calc = 0
    total_premium_calc = 0
    layer_rols = {}

    for layer in layers:
        if not isinstance(layer, dict):
            print(f"Warning: Skipping invalid layer data: {layer}")
            continue

        layer_name = layer.get("name")
        limit = layer.get("occurrenceLimit")
        premium = layer.get("depositPremium")

        if layer_name is None or limit is None or premium is None:
            print(
                f"Warning: Skipping layer with missing name, limit, or premium: {layer}"
            )
            continue

        try:
            limit_val = float(limit)
            premium_val = float(premium)
        except (ValueError, TypeError):
            print(
                f"Warning: Could not parse limit or premium for layer '{layer_name}': {limit}, {premium}"
            )
            continue

        participation = (
            top_layer_perc if layer_name == top_layer_name else all_layers_perc
        )
        total_limit_calc += limit_val * participation
        total_premium_calc += premium_val * participation

        # Store the raw float ROL value
        if limit_val > 0:
            rol = (premium_val / limit_val) * 100
            layer_rols[layer_name] = rol
        else:
            layer_rols[layer_name] = 0.0  # Or handle zero limit appropriately
            print(f"Warning: Limit is zero for layer '{layer_name}', ROL set to 0.")

    return total_limit_calc, total_premium_calc, layer_rols


# --- Helper Function to Extract Concise Subject --- #
def extract_concise_subject(question):
    """Attempts to extract a concise subject phrase from an investigation question."""
    question = question.strip().rstrip("?")
    # Try specific patterns first
    match = re.search(
        r"What are the (specific )?(.*?)($| for | per | in )", question, re.IGNORECASE
    )
    if match:
        return match.group(2).strip().capitalize()

    match = re.search(
        r"Is there any mention of (.*?)( in .*?)?$", question, re.IGNORECASE
    )
    if match:
        # For 'mention' questions, perhaps return subject + 'mention'
        return match.group(1).strip().capitalize() + " mention"

    match = re.search(r"Confirm the (.*)", question, re.IGNORECASE)
    if match:
        return match.group(1).strip().capitalize()

    # Fallback: Return the question, maybe trimmed
    return question[:70] + ("..." if len(question) > 70 else "")


# --- Main Generation Function --- #
def generate_turkey_proposal(
    local_data_path: Path, investigation_points: list[str] | None = None
):
    """
    Generates the Turkey underwriting proposal report, incorporating calculations,
    LLM insights, and user-defined investigation points.

    Args:
        local_data_path: Path to the local data directory.
        investigation_points: A list of specific points the user wants investigated.
    """
    # Placeholder for structured response
    response = {
        "report_markdown": "",
        "status": "error",
        "error": "Generation not fully implemented",
    }

    print("--- Starting Turkey Proposal Generation (Standard Calc) ---")
    print(f"Using local data path: {local_data_path}")

    # Construct input file paths using the provided local_data_path
    terms_file = local_data_path / "turkey_terms.json"
    submission_info_file = local_data_path / "turkey_submission.json"
    contract_file = local_data_path / "turkey_2024_contract.md"

    # 1. Load Data
    print("Loading submission data...")
    terms_data = load_file(terms_file)
    submission_info_data = load_file(submission_info_file)
    contract_data = load_file(contract_file)

    if not all([terms_data, submission_info_data, contract_data]):
        error_msg = (
            "Error: One or more essential data files could not be loaded. Aborting."
        )
        print(error_msg)
        response["error"] = error_msg
        return response

    # Initialize LLM
    llm = initialize_llm()
    if not llm:
        return response

    # --- First LLM Pass to get suggestions and initial report --- #
    # Reverted prompt_pass1 to use placeholders
    prompt_pass1_template_str = """
    Analyze the following 'SUBMISSION DATA CONTEXT' for a Turkey Earthquake XoL proposal.
    Generate a concise underwriting proposal report draft using the structure and instructions below. 
    Focus ONLY on the information available in the context.

    **Report Structure & Instructions:**

    1.  **## Quotation line**
        - Suggest participation percentages for 'All Layers' and the 'Top Layer'.
        - Format: Present **EACH** suggestion on a **SEPARATE new line**. Use the EXACT formats:
          All Layers: [PERCENTAGE]%
          Top Layer: [PERCENTAGE]%
        - Ensure PERCENTAGE is a number (e.g., 5.0, 2.5).

    2.  **## Total Line**
        - Placeholders: '[Total Limit]', '[Total Premium]'.

    3.  **## Quotation Proposal**
        - Proposed values: 'Proposed Limit: [Total Limit Calculated]', 'Proposed Premium: [Total Premium Calculated]'.
        - For expiring details: If found, state 'Expiring Limit: [Value]', 'Expiring Premium: [Value]'. **If not found, output ONLY the placeholder '[MISSING: Expiring Details]' on a new line.**

    4.  **## Why this opportunity?**
        - Provide a brief justification based on context. Look for reasons like market type (e.g., Turkey Earthquake XoL), exposure stabilization (e.g., inflation control, end of step-change limits), and **financial performance (e.g., positive reinsurance balance, payback percentage).**

    5.  **## ROL Calculation**
        - Placeholders for each layer: '[ROL Layer Name %]'.

    6.  **## Historical Losses**
        - Summarize historical loss info if found. **If none found, output ONLY the placeholder '[MISSING: Historical Losses]' on a new line.**

    7.  **## Structure / Key Changes**
        - Describe structure and key changes from context.

    8.  **## Key Findings**
        - List key factual findings.

    **SUBMISSION DATA CONTEXT:**
    {submission_context}
    """
    # Dynamically add ROL placeholders based on layers found
    rol_placeholders = "\n".join(
        ["[ROL Layer Name %]" for _ in json.loads(terms_data).get("layers", [])]
    )
    prompt_pass1_template_str = prompt_pass1_template_str.replace(
        "[ROL Layer 1 %]\n[ROL Layer 2 %]\n[ROL Layer 3 %]\n(Adjust number of lines based on actual layers)",
        rol_placeholders,
    )

    print("Invoking LLM (Pass 1) to get suggestions and initial report...")
    try:
        # Combine data into a single context
        submission_context = f"""
# TURKEY SUBMISSION DATA

## Terms ({terms_file.name})
{terms_data}

---

## Submission Info ({submission_info_file.name})
{submission_info_data}

---

## Contract ({contract_file.name})
{contract_data}

# END OF SUBMISSION DATA
"""
        prompt_value_pass1 = prompt_pass1_template_str.format(
            submission_context=submission_context
        )
        response_pass1 = llm.complete(prompt_value_pass1)
        initial_report_content = response_pass1.text
    except Exception as e:
        print(f"Error during LLM invocation (Pass 1): {e}")
        return response

    # --- Parse Percentages and Calculate Totals (Pass 2 - Script Logic) --- #
    print("Parsing suggested percentages from LLM output...")
    all_layers_perc, top_layer_perc = parse_suggested_percentages(
        initial_report_content
    )

    if all_layers_perc is None or top_layer_perc is None:
        print(
            "Warning: Could not parse percentages from LLM. Using defaults (e.g., 0%)."
        )
        # Handle default or error scenario if needed
        all_layers_perc = all_layers_perc if all_layers_perc is not None else 0.0
        top_layer_perc = top_layer_perc if top_layer_perc is not None else 0.0
    else:
        print(
            f"Parsed percentages: All Layers={all_layers_perc*100:.2f}%, Top Layer={top_layer_perc*100:.2f}%"
        )

    # --- Calculations (Existing Logic) --- #
    # (Keep the calculation logic for top layer, weighted totals, ROLs as before)
    print("Identifying top layer (highest occurrenceAttachment)...")
    layers_for_calc = json.loads(terms_data).get("layers", [])
    top_layer_name = identify_top_layer(layers_for_calc)
    print(
        f"Identified top layer (highest attachment using 'occurrenceAttachment'): {top_layer_name}"
    )

    print("Calculating weighted totals and ROLs...")
    total_limit_calc, total_premium_calc, layer_rols = (
        calculate_weighted_totals_and_rols(
            layers_for_calc, all_layers_perc, top_layer_perc, top_layer_name
        )
    )

    formatted_total_limit = f"TRY {total_limit_calc:,.2f}"
    formatted_total_premium = f"TRY {total_premium_calc:,.2f}"
    print(
        f"Calculated Weighted Totals: Limit={formatted_total_limit}, Premium={formatted_total_premium}"
    )

    # Replace placeholders in the initial report
    final_report_content = initial_report_content.replace(
        "[Total Limit]", f"Total Limit: {formatted_total_limit}"
    )
    final_report_content = final_report_content.replace(
        "[Total Premium]", f"Total Premium: {formatted_total_premium}"
    )

    print("Replacing ROL placeholders...")
    # Sort layers by name (e.g., Layer 1, Layer 2) to ensure order if needed, though sequential replacement might be sufficient
    sorted_layer_names = sorted(
        layer_rols.keys(),
        key=lambda x: int(re.search(r"\d+", x).group())
        if re.search(r"\d+", x)
        else float("inf"),
    )
    for layer_name in sorted_layer_names:
        rol_value_str = f"{layer_rols[layer_name]:.2f}%"
        placeholder_generic = (
            "[ROL Layer Name %]"  # The placeholder the LLM was asked to generate
        )
        # Replace the *first* occurrence of the generic placeholder
        final_report_content = final_report_content.replace(
            placeholder_generic, rol_value_str, 1
        )
        print(
            f"  - Replaced one instance of '{placeholder_generic}' with '{rol_value_str}'"
        )

    # Check if any generic placeholders remain (indicates mismatch between LLM output and calculation)
    if placeholder_generic in final_report_content:
        print(
            f"Warning: Some '{placeholder_generic}' placeholders might remain unreplaced."
        )

    # --- Replace Quotation Proposal placeholders --- #
    # These placeholders appear in the ## Quotation Proposal section
    final_report_content = final_report_content.replace(
        "[Total Limit Calculated]", f"{formatted_total_limit}"
    )
    final_report_content = final_report_content.replace(
        "[Total Premium Calculated]", f"{formatted_total_premium}"
    )
    print("Replaced Quotation Proposal placeholders.")

    # --- Pass 3: User Investigation Points (Optional) --- #
    if investigation_points:
        print("\nInvoking LLM (Pass 3) to investigate user points...")
        prompt_pass3_template_str = """
        Based *only* on the provided 'SUBMISSION DATA CONTEXT', answer the following 'POINTS TO INVESTIGATE'.

        **Instructions:**
        1.  For each point listed under 'POINTS TO INVESTIGATE', format your output EXACTLY as follows, starting each part on a new line:
            - **Question:** <Full Original Investigation Point Text>
            - **Answer:** <Your concise answer derived strictly from the context>
        2.  If the question asks about the *mention* or *existence* of something (e.g., starts 'Is there any mention...', 'Does the text state...') AND the context confirms its **absence**, the **Answer:** should simply be `No`.
        3.  If the question asks *for specific information* (e.g., 'What are...', 'Provide...') AND that information is *not found* or *not mentioned* in the context, the **Answer:** MUST start with the marker `[INFO_MISSING] No mention found in provided documents.` (or similar brief explanation).
        4.  If answering the question *requires calculation*, the **Answer:** MUST start with the marker `[CALC_NEEDED] Cannot perform calculation based on provided documents.`
        5.  If the information IS found in the context (and doesn't fall into rules 2, 3, or 4), provide the factual answer directly after **Answer:**.
        6.  Do not make assumptions or use external knowledge.
        7.  Ensure the final output under the '## User Investigation Points' heading contains these Question/Answer pairs.

        **POINTS TO INVESTIGATE:**
        {investigation_points_list}

        **SUBMISSION DATA CONTEXT:**
        {submission_context}
        """
        # Format the points for the prompt
        points_list_str = "\n".join([f"- {p}" for p in investigation_points])
        prompt_pass3 = prompt_pass3_template_str.format(
            investigation_points_list=points_list_str,
            submission_context=submission_context,
        )

        try:
            # Use llm.complete with the formatted prompt string
            response_pass3 = llm.complete(prompt_pass3)
            investigation_results = response_pass3.text
            print("Investigation results received.")
            # Append results (or placeholders) to the main report
            final_report_content += "\n\n" + investigation_results

        except Exception as e:
            print(f"Error during LLM invocation (Pass 3): {e}")
            # Append a note about the error, keeping existing investigation section structure if needed
            if "## User Investigation Points" not in final_report_content:
                final_report_content += "\n\n## User Investigation Points"
            final_report_content += "\n\nError processing investigation points."

    else:
        print("\nNo user investigation points provided. Skipping Pass 3.")

    # --- Post-Processing: Extract Missing Data Placeholders and Parse Investigation Answers --- #
    missing_data_points = []
    pass1_missing_pattern = re.compile(r"^\s*\[MISSING:\s*(.*?)\]\s*$", re.MULTILINE)

    # Process Pass 1 missing placeholders
    pass1_matches = pass1_missing_pattern.findall(final_report_content)
    if pass1_matches:
        print(f"Found {len(pass1_matches)} missing data placeholders from Pass 1.")
        missing_data_points.extend(pass1_matches)
        # Remove the placeholder lines from the report body
        final_report_content = pass1_missing_pattern.sub(
            "", final_report_content
        ).strip()
        # Clean up potentially empty lines
        final_report_content = "\n".join(
            [line for line in final_report_content.split("\n") if line.strip()]
        )

    # Process Pass 3 investigation results if they exist
    investigation_section_pattern = re.compile(
        r"(## User Investigation Points\s*)(.*)", re.DOTALL | re.IGNORECASE
    )
    investigation_match = investigation_section_pattern.search(final_report_content)

    if investigation_match:
        investigation_text = investigation_match.group(
            2
        )  # Get the text after the heading
        print("Parsing Pass 3 investigation results for missing data triggers...")

        # Pattern to find Question/Answer pairs
        qa_pattern = re.compile(
            r"-\s*\*\*Question:\*\*\s*(.*?)\s*-\s*\*\*Answer:\*\*\s*(.*)", re.IGNORECASE
        )

        pass3_matches = qa_pattern.findall(investigation_text)
        missing_triggered_count = 0

        if pass3_matches:
            for question_text, answer_text in pass3_matches:
                question_text = question_text.strip()
                answer_text = answer_text.strip()
                # Check if the answer triggers inclusion in Missing Data
                if answer_text.startswith("[CALC_NEEDED]") or answer_text.startswith(
                    "[INFO_MISSING]"
                ):
                    missing_triggered_count += 1
                    concise_subject = extract_concise_subject(question_text)
                    missing_data_points.append(concise_subject)
                    print(f"  - Added '{concise_subject}' to Missing Data list.")

            if missing_triggered_count > 0:
                print(
                    f"Found {missing_triggered_count} investigation points triggering Missing Data."
                )
            else:
                print("No investigation points triggered Missing Data in Pass 3.")
        else:
            print("Could not parse Question/Answer pairs from investigation text.")
    else:
        # This case handles if Pass 3 wasn't run or produced no '## User Investigation Points' heading
        if investigation_points:
            print(
                "Warning: Could not find '## User Investigation Points' section to parse."
            )

    # --- Append Missing Data Section if needed --- #
    # Ensure uniqueness
    unique_missing_points = sorted(list(set(missing_data_points)))

    if unique_missing_points:
        final_report_content += "\n\n## Missing Data\n"
        for point in unique_missing_points:
            final_report_content += f"- {point}\n"
        # Remove trailing newline if added
        final_report_content = final_report_content.rstrip()

    # --- Save Final Report --- #
    print(f"Saving final report to: {OUTPUT_REPORT_FILE}")
    try:
        with open(OUTPUT_REPORT_FILE, "w", encoding="utf-8") as f:
            # Ensure the LLM output starts with the expected markdown format if needed
            if not initial_report_content.strip().startswith(
                "# Underwriting Proposal Report: Turkey"
            ):
                # Prepend standard header if LLM omitted it (less likely now with template)
                # f.write("# Underwriting Proposal Report: Turkey\n\n")
                pass  # Assume template ensures header
            # Write the main report content generated
            f.write(final_report_content)
    except IOError as e:
        print(f"Error writing report file: {e}")

    print("--- Report generation complete. ---")

    print(f"Successfully generated report to {OUTPUT_REPORT_FILE}")
    response["report_markdown"] = final_report_content
    response["status"] = "success"
    response["error"] = None
    return response  # Return the structured response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Turkey Proposal Report")
    parser.add_argument(
        "--investigation_points",
        type=str,
        help="Path to investigation points JSON file",
    )
    parser.add_argument(
        "--local_data_path",
        type=str,
        required=True,
        help="Path to local data directory (required for direct run)",
    )
    args = parser.parse_args()

    investigation_points_list = None
    if args.investigation_points:
        # Use the standalone loader within the agent for direct runs
        investigation_points_list = load_json_data(
            Path(args.investigation_points).resolve()
        )

    data_path = Path(args.local_data_path).resolve()
    if not data_path.is_dir():
        print(f"Error: Local data directory not found: {data_path}. Aborting.")
    else:
        result = generate_turkey_proposal(data_path, investigation_points_list)
        print("\n--- Direct Run Result ---")
        print(json.dumps(result, indent=2))
