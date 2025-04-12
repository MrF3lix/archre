import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException

from reporter.core.config import settings
from reporter.schemas.contract_diff import DiffRequest, DiffResponse
from reporter.util.compare_contracts import compare_contracts

# --------------------------------------------------------------------------------------
# router
# --------------------------------------------------------------------------------------
router = APIRouter(tags=["contract_diff"])


# --------------------------------------------------------------------------------------
# routes
# --------------------------------------------------------------------------------------
@router.post("/contractdiff", response_model=DiffResponse)
async def analyze_contract_diff(diff_request: DiffRequest):
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            temp_dir_path = Path(temp_dir)

            file1_path = str(temp_dir_path / "c1.md")
            file2_path = str(temp_dir_path / "c2.md")
            settings.S3_CLIENT.fget_object(
                bucket_name=settings.S3_BUCKET,
                object_name=diff_request.contract_old,
                file_path=file1_path,
            )
            settings.S3_CLIENT.fget_object(
                bucket_name=settings.S3_BUCKET,
                object_name=diff_request.contract_new,
                file_path=file2_path,
            )
            comp = compare_contracts(file1_path, file2_path)

            return comp
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error Processing contracts: {e}"
            )
