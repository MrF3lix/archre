"""
Orchestrates the generation of underwriting proposal reports based on client and user input.
"""

import argparse
import json
from pathlib import Path

from .florida_proposal_agent import generate_florida_proposal
from .netherlands_proposal_agent import generate_netherlands_proposal

# Import agent functions (assuming they will be refactored)
from .turkey_proposal_agent import generate_turkey_proposal

# --- Configuration ---
# Base directory where data downloaded from MinIO is expected
# Example: if MinIO path is 'data/submission_florida', local path might be './data/submission_florida'
# IMPORTANT: This path is relative to where the orchestrator is *run* from.
LOCAL_DATA_BASE_PATH = Path("./data")


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
    client_name: str, investigation_points: list[str] | None = None
):
    """Loads data and calls the appropriate agent based on the client name.

    Args:
        client_name: The name of the client (e.g., 'turkey', 'florida').
        investigation_points: A list of strings representing investigation points, or None.
    """
    print(f"--- Starting Orchestration for Client: {client_name} ---")

    # Use the passed list directly
    points_to_investigate = investigation_points if investigation_points else []
    print(f"Received {len(points_to_investigate)} investigation points directly.")

    # Select and call the appropriate agent
    client_lower = client_name.lower()
    data_subpath = f"submission_{client_lower}"
    local_data_path = (LOCAL_DATA_BASE_PATH / data_subpath).resolve()

    print(f"Expecting local data for {client_name} at: {local_data_path}")

    if not local_data_path.is_dir():
        print(
            f"Error: Local data directory not found at {local_data_path}. Ensure data exists relative to execution directory."
        )
        # In API context, we'll want to return an error, not just print
        # For now, returning None to signal failure
        return None

    agent_response = None  # Variable to hold the response from the agent
    if client_lower == "turkey":
        print("\nCalling Turkey Proposal Agent...")
        agent_response = generate_turkey_proposal(
            investigation_points=points_to_investigate,
            local_data_path=local_data_path,
            # We will add significant_changes path later
        )
    elif client_lower == "florida":
        print("\nCalling Florida Proposal Agent...")
        agent_response = generate_florida_proposal(
            investigation_points=points_to_investigate,
            local_data_path=local_data_path,
            # We will add significant_changes path later
        )
    elif client_lower == "netherlands":
        print("\nCalling Netherlands Proposal Agent...")
        agent_response = generate_netherlands_proposal(
            investigation_points=points_to_investigate,
            local_data_path=local_data_path,
            # We will add significant_changes path later
        )
    else:
        print(
            f"Error: Unknown client name '{client_name}'. Supported clients: turkey, florida, netherlands."
        )
        # Return an error structure suitable for API
        return {
            "report_markdown": "",
            "status": "error",
            "error": f"Unknown client name: {client_name}",
        }

    print(f"--- Orchestration Complete for Client: {client_name} ---")
    # Return the structured response received from the agent
    return agent_response


def main(client_name: str, investigation_file_path: Path):
    # We will adjust main/entry point later for API usage
    result = generate_report_for_client(
        client_name, load_investigation_json(investigation_file_path)
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

    args = parser.parse_args()

    # Resolve the path relative to the current working directory if it's not absolute
    investigation_file_path = args.investigation_json.resolve()

    main(args.client, investigation_file_path)
