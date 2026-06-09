from fastapi import APIRouter, Request

from app.schemas import VersionResponse

router = APIRouter(tags=["version"])


@router.get("/version", response_model=VersionResponse)
def version(request: Request) -> VersionResponse:
    return VersionResponse(version=request.app.state.settings.app_version)

