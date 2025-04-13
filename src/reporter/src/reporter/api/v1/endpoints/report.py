from fastapi import APIRouter, HTTPException

from reporter.schemas.report import ReportRequest, ReportResponse
from reporter.util.orchestrator.orchestrator import generate_report_for_client

# --------------------------------------------------------------------------------------
# router
# --------------------------------------------------------------------------------------
router = APIRouter(tags=["report_generation"])


# --------------------------------------------------------------------------------------
# routes
# --------------------------------------------------------------------------------------
@router.post("/generate", response_model=ReportResponse)
async def generate_report_endpoint(request: ReportRequest):
    """
    Generates an underwriting proposal report based on the specified client
    and optional investigation points.
    """
    try:
        print(f"API received request for client: {request.client}")
        # Call the orchestrator with the client name and investigation points list
        result = generate_report_for_client(
            client_name=request.client,
            investigation_points=request.investigation_points,
            significant_changes_json=request.significant_changes_json,
        )

        # Handle cases where the orchestrator signals an error
        if result is None:
            # This might happen if the data directory wasn't found
            raise HTTPException(
                status_code=404,
                detail=f"Could not find local data for client: {request.client}. Ensure data exists in the expected location.",
            )

        if isinstance(result, dict) and result.get("status") == "error":
            # Specific error reported by the agent or orchestrator
            error_detail = result.get(
                "error", "Unknown error during report generation."
            )
            # Use 400 for client errors (like unknown client), 500 for internal agent errors?
            # Let's start with 500 for simplicity.
            raise HTTPException(
                status_code=500,
                detail=f"Report generation failed: {error_detail}",
            )

        # Check if the result looks like a valid success response structure
        if (
            isinstance(result, dict)
            and "report_markdown" in result
            and "status" in result
        ):
            # Construct the response model - Pydantic will validate
            return ReportResponse(**result)
        else:
            # Should not happen if agents return the correct structure, but handle defensively
            print(f"Warning: Orchestrator returned unexpected result format: {result}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error: Unexpected response format from report generator.",
            )

    except HTTPException as http_exc:
        # Re-raise HTTPException to let FastAPI handle it
        raise http_exc
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"ERROR generating report: {e}")  # Log the full error server-side
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during report generation: {e}",
        )
