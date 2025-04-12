from fastapi import APIRouter

from reporter.core.config import settings
from reporter.schemas.health import HealthCheck

# --------------------------------------------------------------------------------------
# router
# --------------------------------------------------------------------------------------
router = APIRouter(tags=["health"])


# --------------------------------------------------------------------------------------
# routes
# --------------------------------------------------------------------------------------
@router.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(
        status="ok",
        version=settings.VERSION,
    )
