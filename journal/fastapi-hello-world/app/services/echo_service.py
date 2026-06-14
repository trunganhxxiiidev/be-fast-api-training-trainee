from datetime import UTC, datetime

from app.schemas import EchoResponse


def build_echo_response(message: str) -> EchoResponse:
    return EchoResponse(
        echo=message,
        received_at=datetime.now(UTC).isoformat(),
    )
