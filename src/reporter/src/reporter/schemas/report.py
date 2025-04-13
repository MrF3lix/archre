from typing import List, Optional

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    client: str = Field(
        ...,
        description="The client identifier (e.g., 'florida', 'turkey', 'netherlands'). Corresponds to the data subfolder name prefix.",
    )
    investigation_points: Optional[List[str]] = Field(
        None, description="A list of specific questions or points to investigate."
    )
    significant_changes_json: Optional[str] = Field(
        None, description="JSON string for significant changes"
    )


class ReportResponse(BaseModel):
    report_markdown: str = Field(
        ..., description="The generated report content in Markdown format."
    )
    status: str = Field(
        ..., description="The status of the generation process ('success' or 'error')."
    )
    error: Optional[str] = Field(
        None, description="Error message if the status is 'error'."
    )
