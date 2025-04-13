"""
Orchestrates the generation of underwriting proposal reports based on client and user input.
"""

import argparse
import json
from pathlib import Path
from typing import Optional

from .florida_proposal_agent import generate_florida_proposal
from .netherlands_proposal_agent import generate_netherlands_proposal
from .turkey_proposal_agent import generate_turkey_proposal

# --- Configuration ---
# Determine the project's base data directory relative to this orchestrator file
# Assumes orchestrator.py is at src/reporter/src/reporter/util/orchestrator/orchestrator.py
# and data is at src/reporter/files/
ORCHESTRATOR_DIR = Path(__file__).parent
CORRECT_FILES_DIR = (
    ORCHESTRATOR_DIR.parent.parent.parent.parent / "files"
)  # Go up 4 levels (orchestrator->util->reporter->src) then into 'files'
LOCAL_DATA_BASE_PATH = CORRECT_FILES_DIR.resolve()  # Use this corrected absolute path


def load_investigation_json(json_path: Path) -> list[str] | None:
    """Loads investigation points from a JSON file, filtering for active ones."""
    active_points = []
    if not json_path.is_file():
        print(f"Error: Investigation JSON file not found at {json_path}")
        return None  # Return None if file not found
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # Access the list under the 'investigation_points' key
            points_list = data.get("investigation_points")

            if not isinstance(points_list, list):
                print(
                    f"Error: 'investigation_points' key in {json_path} does not contain a valid list."
                )
                return None  # Return None if structure is wrong

            for item in points_list:
                # Check if item is a dictionary, 'active' is true, and 'point' is a string
                if (
                    isinstance(item, dict)
                    and item.get("active", False)
                    and isinstance(item.get("point"), str)
                ):
                    active_points.append(item["point"])
                elif not isinstance(item, dict):
                    print(
                        f"Warning: Skipping non-dictionary item in investigation points: {item}"
                    )
                # Optionally add warnings for inactive points or points without a string value

            return active_points  # Return the list of active point strings

    except FileNotFoundError:  # Should be caught by is_file(), but good practice
        print(f"Error: File not found - {json_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_path}")
        return None
    except Exception as e:
        print(f"Error loading investigation JSON from {json_path}: {e}")
        return None


def generate_report_for_client(
    client_name: str,
    investigation_points: list[str] | None = None,
    significant_changes_json: Optional[str] = None,
):
    """Loads data and calls the appropriate agent based on the client name.

    Args:
        client_name: The name of the client (e.g., 'turkey', 'florida').
        investigation_points: A list of strings representing investigation points, or None.
        significant_changes_json: A JSON string containing significant changes, or None.
    """
    print(f"--- Starting Orchestration for Client: {client_name} ---")

    # Use the passed list directly
    points_to_investigate = investigation_points if investigation_points else []
    print(f"Received {len(points_to_investigate)} investigation points directly.")

    # Select and call the appropriate agent
    client_lower = client_name.lower()

    # Construct the local data path relative to the API files directory
    data_subpath = f"submission_{client_lower}"
    local_data_path = LOCAL_DATA_BASE_PATH / data_subpath

    print(f"Expecting local data for {client_name} at: {local_data_path}")

    if not local_data_path.is_dir():
        print(f"Error: Local data directory not found at {local_data_path}.")
        return {
            "report_markdown": "",
            "status": "error",
            "error": f"Data directory not found for client: {client_name}",
        }

    agent_response = None  # Variable to hold the response from the agent
    if client_lower == "turkey":
        print("\nCalling Turkey Proposal Agent...")
        agent_response = generate_turkey_proposal(
            investigation_points=points_to_investigate,
            local_data_path=local_data_path,
            significant_changes_json=significant_changes_json,
        )
    elif client_lower == "florida":
        print("\nCalling Florida Proposal Agent...")
        agent_response = generate_florida_proposal(
            investigation_points=points_to_investigate,
            local_data_path=local_data_path,
            significant_changes_json=significant_changes_json,
        )
    elif client_lower == "netherlands":
        print("\nCalling Netherlands Proposal Agent...")
        agent_response = generate_netherlands_proposal(
            investigation_points=points_to_investigate,
            local_data_path=local_data_path,
            significant_changes_json=significant_changes_json,
        )
    else:
        # This case should theoretically not be reached due to the path check above,
        # but kept for robustness.
        print(
            f"Error: Logic error - agent call attempted for unknown client '{client_name}'."
        )
        return {
            "status": "error",
            "error": "Internal server error: Unknown client agent.",
            "report_markdown": "",
        }

    print(f"--- Orchestration Complete for Client: {client_name} ---")
    # Return the structured response received from the agent
    return agent_response


def main(
    client_name: str,
    investigation_file_path: Path,
    significant_changes_json: Optional[str] = None,
):
    # We will adjust main/entry point later for API usage
    result = generate_report_for_client(
        client_name,
        load_investigation_json(investigation_file_path),
        significant_changes_json,
    )
    if result:
        print("\n--- Agent Result ---")
        print(json.dumps(result, indent=2))
    else:
        print("\nOrchestration failed or agent returned no result.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Orchestrate underwriting proposal generation."
    )
    # Change to named arguments
    parser.add_argument(
        "--client",
        type=str,
        required=True,
        help="Client name (e.g., 'turkey', 'florida', 'netherlands')",
    )
    parser.add_argument(
        "--investigation_json",
        type=Path,
        required=True,
        help="Path to the JSON file containing user investigation points.",
    )
    parser.add_argument(
        "--significant_changes_json",
        type=str,
        required=False,
        help="JSON string containing significant changes.",
    )

    args = parser.parse_args()

    # Resolve the path relative to the current working directory if it's not absolute
    investigation_file_path = args.investigation_json.resolve()

    main(args.client, investigation_file_path, args.significant_changes_json)
