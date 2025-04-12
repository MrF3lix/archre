from typing import List

from pydantic import BaseModel


class DiffRequest(BaseModel):
    contract_old: str
    contract_new: str


class DiffResponse(BaseModel):
    significant_changes: List[str]
    overall_impression: str
    suggestions_for_investigation: List[str]
