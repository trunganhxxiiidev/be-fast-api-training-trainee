from datetime import UTC, datetime

from fastapi import APIRouter

from app.schemas import EchoRequest, EchoResponse

router = APIRouter(tags=["echo"])


@router.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest) -> EchoResponse:
    return EchoResponse(
        echo=payload.message,
        received_at=datetime.now(UTC).isoformat(),
    )

