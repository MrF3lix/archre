"""
Standalone agent to generate a Florida underwriting proposal report
using direct file loading and LLM synthesis with complex total calculation.
"""

import argparse
import json
import locale
import re
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# LlamaIndex Imports instead of LangChain
from llama_index.llms.google_genai import GoogleGenAI  # Correct class name

# We might use f-strings directly or LlamaIndex PromptTemplate later
# from llama_index.core.prompts import PromptTemplate

# --- Configuration --- #
load_dotenv()

# LLM Configuration
LLM_PROVIDER = "google"
MODEL_NAME = "gemini-2.0-flash"
TEMPERATURE = 0.1
MAX_OUTPUT_TOKENS = 4096

# File Paths
OUTPUT_REPORT_FILE = (
    Path(__file__).resolve().parent.parent / "generated_florida_proposal_report.md"
)

# Report Structure Template (Aligned with Turkey Agent)
REPORT_STRUCTURE_TEMPLATE = """
# **Quotation line**
Suggest to offer quotation line of [Calculated %] across all layers except TOP layer at [Calculated % for Top Layer]

# **Total Line**
Auth Limit: [Total Limit $] gross Premium [Total Premium $]

## **Quotation Proposal**
Proposed Limit: [Total Limit Calculated $]
Proposed Premium: [Total Premium Calculated $]
Expiring Limit: [Value]
Expiring Premium: [Value]

## **Why this opportunity?**
[Rationale based on Data Analysis, including financial performance]

## **ROL Calculation**
[ROL Layer Name %]
[ROL Layer Name %]
# Add/remove lines based on actual layers

## **Historical Losses**
[Summary or indicator of missing data]

## **Structure / Key Changes**
[Summary of structure/contract changes based on Data Analysis]

## **Key Findings**
[Summary of key findings based on data analysis]
"""


# --- Helper Functions --- #
def read_text_file(filepath: Path) -> str:
    """Loads content from a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        return None
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None


def initialize_llm():
    """Initializes the LLM provider based on configuration."""
    print(f"Initializing LLM: {LLM_PROVIDER} - Model: {MODEL_NAME}")
    if LLM_PROVIDER == "google":
        llm = GoogleGenAI(
            model_name=MODEL_NAME,
            temperature=TEMPERATURE,
            # max_output_tokens=MAX_OUTPUT_TOKENS # Check LlamaIndex equivalent if needed
        )
        print("Google GenAI LLM initialized successfully.")
        return llm
    else:
        print(f"Error: Unsupported LLM provider '{LLM_PROVIDER}' specified.")
        return None


def extract_concise_subject(question: str) -> str:
    """Generates a concise summary phrase from an investigation question."""
    # Simple approach: try to extract text after 'about', 'regarding', 'for', or the main verb/noun phrase
    # More robust NLP could be used here if needed.
    question_lower = question.lower().strip()
    triggers = [
        "about the ",
        "regarding the ",
        "for the ",
        "confirm the ",
        "what are the ",
        "what is the ",
        "is there any mention of ",
    ]
    subject = question_lower
    for trigger in triggers:
        if trigger in question_lower:
            subject = question_lower.split(trigger, 1)[1]
            break  # Take the first match

    # Remove trailing punctuation and capitalize
    subject = subject.rstrip("?.").capitalize()
    # Limit length if necessary
    return subject[:75]  # Limit to 75 chars for brevity


# --- Main Execution --- #
def generate_florida_proposal(
    investigation_points: list[str],
    local_data_path: Path,
    significant_changes_json: Optional[str] = None,
):
    """Generates the underwriting proposal report for Florida client.

    Args:
        investigation_points: A list of strings representing user-defined questions.
        local_data_path: Path object pointing to the downloaded client data directory.
        significant_changes_json: Optional JSON string of significant changes.
            # TODO: Incorporate significant_changes_json into the report generation process if needed.
    """
    print(f"--- Florida Proposal Agent --- Using data from: {local_data_path}")

    # Placeholder for structured response
    response = {
        "report_markdown": "",
        "status": "error",
        "error": "Generation not fully implemented",
    }

    print("--- Starting Florida Proposal Generation (Complex Calc) ---")
    print(f"Using local data path: {local_data_path}")

    # Construct input file paths using the provided local_data_path
    terms_file = local_data_path / "florida_terms.json"
    submission_info_file = local_data_path / "florida_submission.json"
    contract_file = local_data_path / "florida_2024_contract.md"

    # 1. Load Data
    print("Loading submission data...")
    terms_data = read_text_file(terms_file)
    submission_info_data = read_text_file(submission_info_file)
    contract_data = read_text_file(contract_file)

    if not all([terms_data, submission_info_data, contract_data]):
        error_msg = (
            "Error: One or more essential data files could not be loaded. Aborting."
        )
        print(error_msg)
        response["error"] = error_msg
        return response

    try:
        terms_data_dict = json.loads(terms_data)
        # contract_data is markdown, no JSON parsing needed
    except json.JSONDecodeError as e:
        error_msg = f"Error parsing JSON data: {e}. Aborting."
        print(error_msg)
        response["error"] = error_msg
        return response
    except Exception as e:  # Catch other potential errors during loading/parsing
        error_msg = (
            f"An unexpected error occurred loading/parsing initial data: {e}. Aborting."
        )
        print(error_msg)
        response["error"] = error_msg
        return response

    # Combine data into a single context
    submission_context = f"""
# FLORIDA SUBMISSION DATA

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

    # 2. Initialize LLM
    llm = initialize_llm()
    if not llm:
        error_msg = "LLM initialization failed. Aborting."
        print(error_msg)
        response["error"] = error_msg
        return response

    # Dynamically add ROL placeholders based on layers found
    # Assuming terms_data_dict is loaded and valid
    rol_placeholders = "\n".join(
        ["[ROL Layer Name %]" for _ in terms_data_dict.get("layers", [])]
    )
    formatted_report_structure = REPORT_STRUCTURE_TEMPLATE.replace(
        "[ROL Layer Name %]\n[ROL Layer Name %]\n# Add/remove lines based on actual layers",
        rol_placeholders if rol_placeholders else "[No Layers Found in Data]",
    )

    # --- First LLM Pass to get suggestions and initial report --- #
    prompt_pass1_template_str = f"""
You are an expert Senior Reinsurance Underwriter specializing in the Florida market, tasked with creating a proposal report for the Florida submission.

Analyze the following comprehensive submission data meticulously:
{submission_context}

Your goal is to generate a concise, insightful proposal report that STRICTLY adheres to the structure outlined below. You MUST fill in the details for every section based *ONLY* on the provided submission data context.
**Critically, you MUST provide a suggestion for the quotation line percentages in the format '# **Quotation line**\nSuggest to offer quotation line of X% across all layers except TOP layer at Y%' where X and Y are numbers.**

Leave the '[Total Limit $]', '[Total Premium $]', '[Total Limit Calculated $]', '[Total Premium Calculated $]', and ALL '[ROL Layer Name %]' placeholders exactly as they are. These will be calculated later by the script.
Determine the cedant's name and fill in all other bracketed placeholders based ONLY on the data. Do not invent information.

**REQUIRED REPORT STRUCTURE OUTLINE (Fill text based on data, suggest percentages, leave specific placeholders):**

{formatted_report_structure}

**IMPORTANT INSTRUCTIONS:**
1.  **Quotation Line:** MUST start with '# **Quotation line**' and include the suggested percentages 'X%' and 'Y%'.
2.  **Total Line Placeholders:** Leave '[Total Limit $]' and '[Total Premium $]' EXACTLY as they are.
3.  **Quotation Proposal Placeholders:** Leave '[Total Limit Calculated $]' and '[Total Premium Calculated $]' EXACTLY as they are.
4.  **Expiring Details:** If found, state 'Expiring Limit: [Value]', 'Expiring Premium: [Value]'. **If not found, output ONLY the placeholder '[MISSING: Expiring Details]' on a new line under Quotation Proposal.**
5.  **Why this opportunity?:** Provide a brief justification based on context. Look for reasons like market conditions, exposure details, legislative impacts, and financial performance (e.g., positive balance if mentioned).
6.  **ROL Placeholders:** Leave ALL '[ROL Layer Name %]' placeholders EXACTLY as they are (one per layer found in the data).
7.  **Historical Losses:** If specific loss data/summary is found, include it. **If not found, output ONLY the placeholder '[MISSING: Historical Losses]' on a new line under this section.**
8.  **Other Sections:** Fill 'Structure / Key Changes' and 'Key Findings' based ONLY on the provided data context.
9.  **Accuracy:** Generate the complete report based solely on the provided data context and the required structure outline. Do not add extra commentary.
10. **Formatting:** Replicate markdown formatting precisely.

Generate the report now.
"""

    print("Invoking LLM (Pass 1) to get suggestions and initial report...")
    try:
        response_pass1 = llm.complete(prompt_pass1_template_str)
        initial_report_content = response_pass1.text  # Access response text
        print("LLM Pass 1 complete.")
        # Debug: Print initial LLM output
        # print("--- LLM Pass 1 Raw Output ---")
        # print(initial_report_content)
        # print("-----------------------------")

    except Exception as e:
        print(f"Error during LLM invocation (Pass 1): {e}")
        return

    # --- Data structures for results ---
    calculated_results = {}
    layer_rols = {}
    missing_data_from_pass1 = []  # Store missing placeholders

    # --- Parse Suggested Percentages --- #
    print("Parsing suggested percentages from LLM output...")

    def parse_suggested_percentages(text: str) -> tuple[float | None, float | None]:
        pattern = r"Suggest to offer quotation line of ([0-9.]+)% across all layers except TOP layer at ([0-9.]+)%"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                all_layers_perc = float(match.group(1))
                top_layer_perc = float(match.group(2))
                print(
                    f"Parsed percentages: All Layers={all_layers_perc:.2f}%, Top Layer={top_layer_perc:.2f}%"
                )
                return (
                    all_layers_perc / 100.0,
                    top_layer_perc / 100.0,
                )  # Convert to decimal for calculation
            except ValueError:
                print("Error: Could not convert parsed percentages to float.")
                return None, None
        else:
            print("Error: Could not find or parse suggestion pattern in LLM output.")
            # Debug: Print text being searched
            # print("--- Text Searched for Percentages ---")
            # print(text)
            # print("-----------------------------------")
            return None, None

    all_layers_rate, top_layer_rate = parse_suggested_percentages(
        initial_report_content
    )

    if all_layers_rate is None or top_layer_rate is None:
        print("Aborting due to parsing error.")
        return

    # --- Identify Top Layer --- #
    print("Identifying top layer (highest attachment)...")

    def identify_top_layer(layers_data: list) -> str | None:
        if not layers_data:
            return None
        top_layer_name = None
        max_attachment = -1

        for layer in layers_data:
            attachment_key = None
            if "occurrenceAttachment" in layer:
                attachment_key = "occurrenceAttachment"
            elif "aggregateAttachment" in layer:
                attachment_key = "aggregateAttachment"
            # Add other potential keys if needed

            if attachment_key and isinstance(layer.get(attachment_key), (int, float)):
                attachment = float(layer[attachment_key])
                if attachment > max_attachment:
                    max_attachment = attachment
                    top_layer_name = layer.get("name")
            else:
                print(
                    f"Warning: Layer '{layer.get('name', 'Unnamed')}' missing or has invalid attachment value."
                )

        if top_layer_name:
            print(
                f"Identified top layer (highest attachment using '{attachment_key}'): {top_layer_name}"
            )
        else:
            print(
                "Warning: Could not definitively identify the top layer based on attachment."
            )
        return top_layer_name

    top_layer_identified_name = identify_top_layer(terms_data_dict.get("layers", []))

    # --- Calculate Totals and ROLs --- #
    print("Calculating weighted totals and ROLs...")

    def calculate_totals_and_rols(
        layers_data: list, base_rate: float, top_rate: float, top_layer_name: str | None
    ) -> tuple[dict, dict]:
        total_limit = 0.0
        total_premium = 0.0
        rol_dict = {}
        currency_symbol = "$"  # Default to USD for Florida

        for layer in layers_data:
            limit = float(
                layer.get("occurrenceLimit", layer.get("aggregateLimit", 0.0))
            )
            absolute_premium = float(
                layer.get("depositPremium", 0.0)
            )  # Use the absolute premium value
            layer_name = layer.get("name")

            # Determine participation rate for this layer
            participation_rate = top_rate if layer_name == top_layer_name else base_rate

            # Calculate weighted limit and premium for this layer
            layer_limit_weighted = limit * participation_rate
            layer_premium_weighted = (
                absolute_premium * participation_rate
            )  # Weighted premium is Rate * Absolute Premium

            total_limit += layer_limit_weighted
            total_premium += layer_premium_weighted

            # Calculate ROL (Rate on Line) = Premium / Limit
            # Ensure limit is not zero to avoid division error
            layer_rol = (
                (layer_premium_weighted / layer_limit_weighted * 100.0)
                if layer_limit_weighted
                else 0.0
            )
            if layer_name:
                rol_dict[layer_name] = layer_rol

            # Attempt to get currency (might be per layer or global)
            if "currency" in layer and layer["currency"] == "USD":
                currency_symbol = "$"
            # Add other currency checks if necessary

        # Format results
        try:
            locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
        except locale.Error:
            locale.setlocale(locale.LC_ALL, "")  # Use default locale as fallback

        formatted_limit = f"{currency_symbol}{locale.format_string('%.2f', total_limit, grouping=True)}"
        formatted_premium = f"{currency_symbol}{locale.format_string('%.2f', total_premium, grouping=True)}"

        print(
            f"Calculated Weighted Totals: Limit={formatted_limit}, Premium={formatted_premium}"
        )

        results = {"total_limit": formatted_limit, "total_premium": formatted_premium}
        return results, rol_dict

    calculated_results, layer_rols = calculate_totals_and_rols(
        terms_data_dict.get("layers", []),
        all_layers_rate,
        top_layer_rate,
        top_layer_identified_name,
    )

    # --- Placeholder Replacement --- #
    final_report_content = initial_report_content

    # Replace Total Line placeholders
    final_report_content = final_report_content.replace(
        "[Total Limit $]", calculated_results["total_limit"]
    )
    final_report_content = final_report_content.replace(
        "[Total Premium $]", calculated_results["total_premium"]
    )
    print("Replaced Total Line placeholders.")

    # Replace ROL placeholders sequentially
    print("Replacing ROL placeholders...")
    sorted_layer_names = sorted(
        layer_rols.keys(),
        key=lambda x: int(re.search(r"\d+", x).group())
        if re.search(r"\d+", x)
        else float("inf"),
    )
    placeholder_generic = "[ROL Layer Name %]"
    for layer_name in sorted_layer_names:
        rol_value = layer_rols[layer_name]
        rol_value_str = f"{rol_value:.2f}%"  # Format ROL as percentage string
        # Replace the *first* occurrence of the generic placeholder
        final_report_content = final_report_content.replace(
            placeholder_generic, rol_value_str, 1
        )
        print(
            f"  - Replaced one instance of '{placeholder_generic}' with '{rol_value_str}'"
        )

    # Check if any generic ROL placeholders remain
    if placeholder_generic in final_report_content:
        print(
            f"Warning: Some '{placeholder_generic}' placeholders might remain unreplaced."
        )

    # Replace Quotation Proposal placeholders
    final_report_content = final_report_content.replace(
        "[Total Limit Calculated $]", calculated_results["total_limit"]
    )
    final_report_content = final_report_content.replace(
        "[Total Premium Calculated $]", calculated_results["total_premium"]
    )
    print("Replaced Quotation Proposal placeholders.")

    # Find and store [MISSING: ...] placeholders from Pass 1 output
    missing_pattern = r"(\[MISSING: ([^]]+)\])"
    matches = re.findall(missing_pattern, final_report_content)
    for full_match, missing_item in matches:
        missing_data_from_pass1.append(missing_item.strip())
        # Remove the placeholder itself from the report
        final_report_content = final_report_content.replace(full_match, "")
        print(f"  - Found and stored missing item: {missing_item.strip()}")

    # --- LLM Pass 2: Address Investigation Points --- #
    investigation_analysis_content = (
        "\n## Investigation Point Analysis\n\n*No specific points provided.*"
    )
    if investigation_points and len(investigation_points) > 0:
        print("\n--- LLM Pass 2: Addressing Investigation Points ---")
        points_list_str = "\n".join([f"- {point}" for point in investigation_points])

        # Define the prompt template (using f-string)
        prompt_pass2_template_str = f"""
You are an expert Senior Reinsurance Underwriter analyzing a draft report and specific investigation points raised about a Florida property submission.

**Draft Report Content:**
```markdown
{initial_report_content}
```

**Submission Data Context (for reference):**
```
{submission_context}
```

**Investigation Points to Address:**
{points_list_str}

**Your Task:**
Carefully review the **Draft Report Content** and the **Submission Data Context** to answer each **Investigation Point**. Provide clear, concise answers based *only* on the provided information. If the information to answer a point is not present, state that clearly.

**Output Format:**
Generate *only* the 'Investigation Point Analysis' section in Markdown format:
```markdown
## Investigation Point Analysis

*   **Regarding '{investigation_points[0]}':** [Your concise answer based on data or state if info is missing]
*   **Regarding '{investigation_points[1]}':** [Your concise answer based on data or state if info is missing]
*   ... (include a bullet point for each investigation point)
```

**Strict Instructions:**
- Address *each* investigation point individually.
- Base answers strictly on the provided **Draft Report Content** and **Submission Data Context**.
- If information is missing, explicitly state 'Information not found in the provided documents.'
- Do NOT add any other sections or introductory/concluding remarks.
- Maintain the exact markdown format specified.

**Begin Output (Investigation Point Analysis Section Only):**
"""

        print(f"Invoking LLM (Pass 2) for {len(investigation_points)} points...")
        try:
            # Use LlamaIndex llm.complete()
            response_pass2 = llm.complete(prompt_pass2_template_str)
            investigation_analysis_content = response_pass2.text
            print("LLM Pass 2 successful.")
            # print("\n--- LLM Pass 2 Raw Output: ---\n", investigation_analysis_content)
        except Exception as e:
            error_msg = (
                f"Error during LLM invocation (Pass 2 - Investigation Points): {e}"
            )
            print(error_msg)
            # Decide if we should return error or continue with default message
            # For now, let's keep the default message and log the error
            investigation_analysis_content = f"\n## Investigation Point Analysis\n\n*Error processing investigation points: {e}*"
            response["error"] = error_msg  # Still record the error in the response
    else:
        print("\nSkipping LLM Pass 2 as no investigation points were provided.")

    # --- Combine and Finalize Report --- #
    print("\nAssembling final report...")

    # Combine missing data points (ensure uniqueness)
    missing_data_points = sorted(list(set(missing_data_from_pass1)))

    # Append Investigation Points section if applicable
    if investigation_points:
        final_report_content += (
            "\n\n## User Investigation Points\n"
            + investigation_analysis_content.strip()
        )

    # Append Missing Data section if applicable
    if missing_data_points:
        final_report_content += "\n\n## Missing Data\n"
        final_report_content += "\n".join([f"- {item}" for item in missing_data_points])
    else:
        final_report_content += "\n\n## Missing Data\n- None identified."

    # Save the final report
    output_file_path = OUTPUT_REPORT_FILE
    print(f"\nSaving final report to: {output_file_path}")
    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(final_report_content)
        print(f"Successfully generated report to {output_file_path}")
        response["report_markdown"] = final_report_content
        response["status"] = "success"
        response["error"] = None
    except IOError as e:
        error_msg = f"Error writing report file: {e}"
        print(error_msg)
        response["error"] = error_msg
        # Keep status as error

    return response  # Return the structured response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Florida Proposal Report")
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
        investigation_points_list = None

    data_path = Path(args.local_data_path).resolve()
    if not data_path.is_dir():
        print(f"Error: Local data directory not found: {data_path}. Aborting.")
    else:
        result = generate_florida_proposal(data_path, investigation_points_list)
        print("\n--- Direct Run Result ---")
        print(json.dumps(result, indent=2))
