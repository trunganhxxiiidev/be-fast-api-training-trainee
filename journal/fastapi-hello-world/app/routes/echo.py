from fastapi import APIRouter

from app.schemas import EchoRequest, EchoResponse
from app.services import build_echo_response

router = APIRouter(tags=["echo"])


@router.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest) -> EchoResponse:
    return build_echo_response(payload.message)
