"""
Standalone agent to generate a Netherlands underwriting proposal report
using direct file loading and LLM synthesis (no RAG).
"""

# Imports
import argparse
import json
import locale
import re
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core.prompts import PromptTemplate

# LlamaIndex Imports instead of LangChain
from llama_index.llms.google_genai import GoogleGenAI

# --- Configuration ---
load_dotenv()

# LLM Configuration
LLM_PROVIDER = "google"
MODEL_NAME = "gemini-2.0-flash"  # Or your preferred model
TEMPERATURE = 0.1
MAX_OUTPUT_TOKENS = 4096

# File Paths
OUTPUT_REPORT_FILE = (
    Path(__file__).resolve().parent.parent / "generated_netherlands_proposal_report.md"
)

# Report Structure Template (Aligned with Turkey/Florida, ROL section preserved)
REPORT_STRUCTURE_TEMPLATE = """
# **Quotation line**
Suggest to offer quotation line of [Calculated %] across all layers except TOP layer at [Calculated % for Top Layer]

# **Total Line**
Auth Limit: [Total Limit EUR] gross Premium [Total Premium EUR]

## **Quotation Proposal**
Proposed Limit: [Total Limit Calculated EUR]
Proposed Premium: [Total Premium Calculated EUR]
Expiring Limit: [Value from Data or 'Not Found']
Expiring Premium: [Value from Data or 'Not Found']

## **Why this opportunity?**
[Rationale based on Data Analysis, including financial performance]

# ROL Calculation (Calculated by Script)
Layer 1: ROL: [ROL Layer 1 %]
Layer 2: ROL: [ROL Layer 2 %]
Layer 3: ROL: [ROL Layer 3 %]
Layer 4: ROL: [ROL Layer 4 %]
# Add more layers placeholders if needed

## **Historical Losses**
[Summary or indicator of missing data]

## **Structure / Key Changes**
[Summary of structure/contract changes based on Data Analysis]

## **Key Findings**
[Summary of key findings based on data analysis]
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


def initialize_llm():
    """Initializes the LLM."""
    try:
        if LLM_PROVIDER == "google":
            llm = GoogleGenAI(
                model_name=MODEL_NAME,
                temperature=TEMPERATURE,
                # max_output_tokens=MAX_OUTPUT_TOKENS # Check LlamaIndex equivalent if needed
            )
            return llm
        else:
            print(f"Error: LLM provider '{LLM_PROVIDER}' not supported.")
            return None
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return None


def extract_concise_subject(question: str) -> str:
    """Generates a concise summary phrase from an investigation question."""
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
            break
    subject = subject.rstrip("?.").capitalize()
    return subject[:75]


def load_investigation_json(json_path: Path) -> list[str] | None:
    """Loads active investigation points from a JSON file."""
    active_points = []
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "investigation_points" not in data:
            print(
                f"Error: Invalid format in {json_path}. Expected a dictionary with 'investigation_points' key."
            )
            return None
        points_list = data.get("investigation_points")
        if not isinstance(points_list, list):
            print(f"Error: 'investigation_points' in {json_path} should be a list.")
            return None
        for item in points_list:
            if isinstance(item, dict) and item.get("active") is True:
                point_text = item.get("point")
                if isinstance(point_text, str) and point_text:
                    active_points.append(point_text)
                else:
                    print(
                        f"Warning: Skipping active item with invalid 'point' in {json_path}."
                    )
            elif isinstance(item, dict) and item.get("active") is not True:
                pass
            else:
                print(
                    f"Warning: Skipping invalid item in 'investigation_points' list in {json_path}."
                )
        if not active_points:
            print(f"No active investigation points found in {json_path}.")
            return None
        return active_points
    except FileNotFoundError:
        print(f"Error: Investigation JSON file not found at {json_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred loading {json_path}: {e}")
        return None


# --- Calculation and Identification Helpers (Adapted from Florida) ---


def identify_top_layer(layers_data: list) -> str | None:
    """Identifies the top layer based on the highest attachment point."""
    top_layer_name = None
    max_attachment = -1
    # Assuming 'aggregateAttachment' defines the layers' order/position
    attachment_key = "aggregateAttachment"

    for layer in layers_data:
        attachment = layer.get(attachment_key)
        if isinstance(attachment, (int, float)) and attachment > max_attachment:
            max_attachment = attachment
            top_layer_name = layer.get("name")

    if top_layer_name:
        print(
            f"Identified top layer (highest attachment using '{attachment_key}'): {top_layer_name}"
        )
    else:
        print(
            f"Warning: Could not identify top layer using key '{attachment_key}'. Check terms data."
        )
    return top_layer_name


def calculate_totals_and_rols(
    layers_data: list, base_rate: float, top_rate: float, top_layer_name: str | None
) -> tuple[dict, dict]:
    """Calculates weighted totals and ROLs for Netherlands.
    Assumes 'aggregateLimit' for limit and 'depositPremium' for premium in terms data.
    """
    total_limit = 0.0
    total_premium = 0.0
    rol_dict = {}
    currency_symbol = "€"  # Use EUR symbol

    try:
        # Attempt locale for Dutch formatting, fallback if needed
        locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, "en_US.UTF-8")  # Fallback to US
        except locale.Error:
            locale.setlocale(locale.LC_ALL, "")  # System default

    for i, layer in enumerate(layers_data, 1):  # Add index for ROL placeholder mapping
        # Using keys confirmed from JSON data
        limit = float(layer.get("aggregateLimit", 0.0))
        absolute_premium = float(
            layer.get("depositPremium", 0.0)
        )  # Correct key based on JSON data
        layer_name = layer.get("name", f"Layer {i}")  # Fallback name

        # Determine participation rate for this layer
        participation_rate = top_rate if layer_name == top_layer_name else base_rate

        # Calculate weighted limit and premium for this layer
        layer_limit_weighted = limit * participation_rate
        layer_premium_weighted = absolute_premium * participation_rate

        total_limit += layer_limit_weighted
        total_premium += layer_premium_weighted

        # Calculate ROL (Rate on Line) = Premium / Limit
        layer_rol = (
            (layer_premium_weighted / layer_limit_weighted * 100.0)
            if layer_limit_weighted
            else 0.0
        )
        # Store ROL with the specific placeholder key format
        rol_placeholder_key = f"[ROL Layer {i} %]"
        rol_dict[rol_placeholder_key] = layer_rol

    # Format results
    formatted_limit = (
        f"{currency_symbol}{locale.format_string('%.2f', total_limit, grouping=True)}"
    )
    formatted_premium = (
        f"{currency_symbol}{locale.format_string('%.2f', total_premium, grouping=True)}"
    )

    print(
        f"Calculated Weighted Totals: Limit={formatted_limit}, Premium={formatted_premium}"
    )

    results = {"total_limit": formatted_limit, "total_premium": formatted_premium}
    return results, rol_dict


# --- Main Execution --- #
def generate_netherlands_proposal(
    local_data_path: Path, investigation_points: list[str] | None = None
):
    # Placeholder for structured response
    response = {
        "report_markdown": "",
        "status": "error",
        "error": "Generation not fully implemented",
    }

    print("--- Starting Netherlands Proposal Generation (Standard Calc) ---")
    print(f"Using local data path: {local_data_path}")

    # Construct input file paths using the provided local_data_path
    terms_file = local_data_path / "netherlands_terms.json"
    submission_info_file = local_data_path / "netherlands_submission.json"
    contract_file = local_data_path / "netherlands_2024_contract.md"

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

    try:
        terms_data_dict = json.loads(terms_data)  # Keep this for calculation step
    except json.JSONDecodeError as e:
        print(f"Error parsing terms JSON data: {e}")
        return
    except TypeError:
        print("Error: terms_data is None, cannot parse JSON.")
        return

    # Combine data into a single context
    submission_context = f"""
# NETHERLANDS SUBMISSION DATA

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
        return

    # --- First LLM Pass to get suggestions and initial report --- #
    print("\nInvoking LLM (Pass 1) to get suggestions and initial report...")
    master_prompt_template_pass1 = """
You are an expert Senior Reinsurance Underwriter specializing in the Netherlands market, tasked with creating a proposal report.

Analyze the following comprehensive submission data meticulously:
{submission_data_context}

Your goal is to generate a concise, insightful proposal report that STRICTLY adheres to the structure outlined below.
Fill in the details for every section based *ONLY* on the provided submission data context.
**Critically, you MUST provide a suggestion for the quotation line percentages in the format '# **Quotation line**\nSuggest to offer quotation line of X% across all layers except TOP layer at Y%' where X and Y are numbers.**
Leave the '[Total Limit EUR]', '[Total Premium EUR]', '[Total Limit Calculated EUR]', '[Total Premium Calculated EUR]' and ALL '[ROL Layer ... %]' placeholders exactly as they are. These will be calculated later.
Extract information like Expiring Limit/Premium if available, otherwise use 'Not Found'. Fill other sections based ONLY on the data.
If specific data for a section (e.g., Historical Losses) is clearly missing from the context, write "[INFO_MISSING] Details not found in provided documents."

**REQUIRED REPORT STRUCTURE OUTLINE (Fill text based on data, suggest percentages, leave specific placeholders):**

{report_structure_template}

**IMPORTANT INSTRUCTIONS:**
- Fill all bracketed placeholders EXCEPT '[Total Limit EUR]', '[Total Premium EUR]', '[Total Limit Calculated EUR]', '[Total Premium Calculated EUR]', and '[ROL Layer ... %]'.
- Provide the participation suggestion clearly on its own line after '# **Quotation line**'.
- If data is missing for a section, use "[INFO_MISSING] Details not found in provided documents."
- Replicate markdown formatting.
- Base the entire report solely on the provided data context.

Generate the report now.
"""

    prompt_pass1 = PromptTemplate(
        input_variables=["submission_data_context", "report_structure_template"],
        template=master_prompt_template_pass1,
    )
    chain_pass1 = prompt_pass1 | llm

    try:
        initial_report_content = chain_pass1.invoke(
            {
                "submission_data_context": submission_context,
                "report_structure_template": REPORT_STRUCTURE_TEMPLATE,
            }
        )
        print("LLM Pass 1 complete.")
    except Exception as e:
        print(f"Error during LLM invocation (Pass 1): {e}")
        return

    final_report_content = initial_report_content  # Start with Pass 1 output
    missing_data_from_pass1 = []

    # --- Parse Suggested Percentages --- #
    print("Parsing suggested percentages from LLM output...")
    participation_all_perc = None
    participation_top_perc = None
    # Regex adjusted for the specific prompt format
    match = re.search(
        r"Suggest to offer quotation line of (\d{1,3}(?:\.\d{1,2})?)% across all layers except TOP layer at (\d{1,3}(?:\.\d{1,2})?)%",
        final_report_content,
        re.IGNORECASE,
    )

    if match:
        try:
            participation_all_perc = float(match.group(1))
            participation_top_perc = float(match.group(2))
            print(
                f"Parsed percentages: All Layers={participation_all_perc:.2f}%, Top Layer={participation_top_perc:.2f}%"
            )
        except ValueError:
            print("Error converting parsed percentages to float.")
            participation_all_perc = None
            participation_top_perc = None
    else:
        print(
            "Could not parse participation percentages from LLM output. Proceeding without calculations."
        )

    # --- Calculate Weighted Totals & ROLs (if percentages parsed) --- #
    calculated_totals = {
        "total_limit": "[Calculation Error]",
        "total_premium": "[Calculation Error]",
    }
    calculated_rols = {}

    if (
        participation_all_perc is not None
        and participation_top_perc is not None
        and "layers" in terms_data_dict
    ):
        base_rate = participation_all_perc / 100.0
        top_rate = participation_top_perc / 100.0

        # Identify top layer
        layers_data = terms_data_dict["layers"]
        top_layer_name = identify_top_layer(layers_data)

        # Calculate
        try:
            calculated_totals, calculated_rols = calculate_totals_and_rols(
                layers_data, base_rate, top_rate, top_layer_name
            )
        except Exception as e:
            print(f"Error during calculation: {e}")
            # Keep default error placeholders
            num_layers = len(layers_data)
            calculated_rols = {
                f"[ROL Layer {i} %]": 0.0 for i in range(1, num_layers + 1)
            }
    else:
        # Set default ROL placeholders if calculations can't run
        if "layers" in terms_data_dict:
            num_layers = len(terms_data_dict["layers"])
            calculated_rols = {
                f"[ROL Layer {i} %]": 0.0 for i in range(1, num_layers + 1)
            }  # Store 0.0 to format later
        print("Skipping calculations due to missing percentages or layers data.")

    # --- Replace Placeholders --- #
    print("Replacing placeholders in the report...")

    # Replace Total Limit/Premium
    final_report_content = final_report_content.replace(
        "[Total Limit EUR]", calculated_totals["total_limit"]
    )
    final_report_content = final_report_content.replace(
        "[Total Premium EUR]", calculated_totals["total_premium"]
    )
    final_report_content = final_report_content.replace(
        "[Total Limit Calculated EUR]", calculated_totals["total_limit"]
    )
    final_report_content = final_report_content.replace(
        "[Total Premium Calculated EUR]", calculated_totals["total_premium"]
    )

    # Replace Suggested Percentages
    perc_all_str = (
        f"{participation_all_perc:.2f}%"
        if participation_all_perc is not None
        else "[Not Parsed]"
    )
    perc_top_str = (
        f"{participation_top_perc:.2f}%"
        if participation_top_perc is not None
        else "[Not Parsed]"
    )
    final_report_content = final_report_content.replace("[Calculated %]", perc_all_str)
    final_report_content = final_report_content.replace(
        "[Calculated % for Top Layer]", perc_top_str
    )

    # Replace ROL placeholders using the keys from calculated_rols
    for rol_placeholder, rol_value in calculated_rols.items():
        # Format the ROL value as percentage string
        rol_str = (
            f"{rol_value:.2f}%"
            if isinstance(rol_value, (float, int))
            else "[Calc Error]"
        )
        final_report_content = final_report_content.replace(rol_placeholder, rol_str)
        print(f"  - Replaced {rol_placeholder} with {rol_str}")

    # --- Collect Missing Data from Pass 1 --- #
    print("Checking for missing data tags from Pass 1...")
    missing_tags = re.findall(
        r"(\[INFO_MISSING\](?:\s*Details not found|\s*Information not found)[^\]]*)",
        final_report_content,
    )
    for tag in missing_tags:
        # Extract a concise subject if possible, otherwise use a default
        # Example: Try to find the preceding section header
        try:
            # Find position of the tag
            tag_pos = final_report_content.find(tag)
            # Search backwards for the nearest '##' header
            header_match = re.search(
                r"## \*\*(.*?)\*\*", final_report_content[:tag_pos][::-1]
            )
            if header_match:
                subject = header_match.group(1)[::-1].strip()
            else:
                subject = "Specific section data"
        except Exception:
            subject = "Specific section data"  # Fallback

        if subject not in missing_data_from_pass1:
            missing_data_from_pass1.append(subject)
            print(f"  - Found missing data tag related to: {subject}")
        # Remove the tag itself from the report
        final_report_content = final_report_content.replace(tag, "")

    # --- Pass 3: Handle Investigation Points (If any) --- #
    print("Checking for investigation points...")
    if investigation_points:
        print(f"Processing {len(investigation_points)} investigation point(s)...")
        investigation_qa_section = (
            "\n\n## **Further Investigation Points & LLM Analysis**\n"
        )
        investigation_qa_section += "Based on the provided documents:\n\n"

        master_prompt_template_pass3 = """
You are an AI assistant analyzing specific questions against the provided Netherlands submission data.

**Submission Data Context:**
{submission_data_context}

**User Question:**
{user_question}

Based *strictly* on the Submission Data Context, provide a concise answer to the User Question. If the information is not present, state clearly: '[CANNOT_ANSWER] Information not found in the provided documents.' Do not make assumptions or use external knowledge.

**Answer:**
"""

        prompt_pass3 = PromptTemplate(
            input_variables=["submission_data_context", "user_question"],
            template=master_prompt_template_pass3,
        )
        chain_pass3 = prompt_pass3 | llm

        for i, question in enumerate(investigation_points):
            print(f"  - Invoking LLM for question {i+1}: '{question[:50]}...' ")
            try:
                answer = chain_pass3.invoke(
                    {
                        "submission_data_context": submission_context,
                        "user_question": question,
                    }
                )
                investigation_qa_section += (
                    f"**Q{i+1}:** {question}\n**A{i+1}:** {answer}\n\n"
                )
            except Exception as e:
                print(f"    Error invoking LLM for question {i+1}: {e}")
                investigation_qa_section += f"**Q{i+1}:** {question}\n**A{i+1}:** [LLM_ERROR] Could not process this question.\n\n"

        final_report_content += investigation_qa_section
        print("Investigation points processed.")
    else:
        print("No investigation points provided.")

    # --- Append Missing Data Summary (If any) --- #
    if missing_data_from_pass1:
        print("Adding summary of missing data identified in Pass 1...")
        missing_summary = "\n\n## **Missing Information Summary**\n"
        missing_summary += "The initial analysis indicated that specific details might be missing or were not found in the provided documents for the following areas:\n"
        for item in missing_data_from_pass1:
            missing_summary += f"- {item}\n"
        missing_summary += "Please review the source documents or request clarification if this information is critical.\n"
        final_report_content += missing_summary

    # --- 4. Write Final Report --- #
    print(f"\nWriting final proposal report to: {OUTPUT_REPORT_FILE}")
    try:
        with open(OUTPUT_REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(final_report_content)
        print("Report generation complete.")
        response["report_markdown"] = final_report_content
        response["status"] = "success"
        response["error"] = None
    except Exception as e:
        error_msg = f"Error during final report generation or saving: {e}"
        print(error_msg)
        response["error"] = error_msg

    return response  # Return the structured response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Netherlands Proposal Report")
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
        investigation_points_list = load_investigation_json(
            Path(args.investigation_points).resolve()
        )

    data_path = Path(args.local_data_path).resolve()
    if not data_path.is_dir():
        print(f"Error: Local data directory not found: {data_path}. Aborting.")
    else:
        result = generate_netherlands_proposal(data_path, investigation_points_list)
        print("\n--- Direct Run Result ---")
        print(json.dumps(result, indent=2))
