from pydantic import BaseModel


class ResolutionRequest(BaseModel):
    """
    Request sent by the client to ask ResolveAI
    to process a support case.
    """

    case_id: int


class ResolutionResponse(BaseModel):
    """
    Response returned after the resolution logic runs.
    """

    case_id: int
    status: str
    resolution: str | None