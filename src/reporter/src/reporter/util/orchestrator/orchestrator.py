"""
Orchestrates the generation of underwriting proposal reports based on client and user input.
"""

import json
from pathlib import Path

from .florida_proposal_agent import generate_florida_proposal
from .netherlands_proposal_agent import generate_netherlands_proposal

# Import agent functions (assuming they will be refactored)
from .turkey_proposal_agent import generate_turkey_proposal


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
    data_path: Path,
    investigation_points: list[str] | None = None,
):
    """Loads data and calls the appropriate agent based on the client name.

    Args:
        client_name: The name of the client (e.g., 'turkey', 'florida').
        investigation_points: A list of strings representing investigation points, or None.
    """
    # Use the passed list directly
    points_to_investigate = investigation_points if investigation_points else []

    # Select and call the appropriate agent
    client_lower = client_name.lower()
    agent_response = None  # Variable to hold the response from the agent
    if client_lower == "turkey":
        print("\nCalling Turkey Proposal Agent...")
        agent_response = generate_turkey_proposal(
            investigation_points=points_to_investigate,
            local_data_path=data_path,
        )
    elif client_lower == "florida":
        print("\nCalling Florida Proposal Agent...")
        agent_response = generate_florida_proposal(
            investigation_points=points_to_investigate,
            local_data_path=data_path,
        )
    elif client_lower == "netherlands":
        print("\nCalling Netherlands Proposal Agent...")
        agent_response = generate_netherlands_proposal(
            investigation_points=points_to_investigate,
            local_data_path=data_path,
        )
    else:
        return {
            "report_markdown": "",
            "status": "error",
            "error": f"Unknown client name: {client_name}",
        }

    return agent_response
