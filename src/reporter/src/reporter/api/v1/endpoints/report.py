import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException

from reporter.core.config import settings
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
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            client_data_dir = Path(temp_dir)

            objects = settings.S3_CLIENT.list_objects(
                bucket_name=settings.S3_BUCKET,
                prefix=f"submission_{request.client.lower()}",
                recursive=True,
            )

            for obj in objects:
                object_name = obj.object_name
                local_file_path = client_data_dir / str(obj.object_name)

                # Download file from MinIO
                settings.S3_CLIENT.fget_object(
                    bucket_name=settings.S3_BUCKET,
                    object_name=str(object_name),
                    file_path=str(local_file_path),
                )

            result = generate_report_for_client(
                client_name=request.client,
                data_path=client_data_dir / f"submission_{request.client.lower()}",
                investigation_points=request.investigation_points,
            )

            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Processing report: {e}")
