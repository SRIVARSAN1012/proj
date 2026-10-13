from pydantic import BaseModel

class StatusResponse(BaseModel):
    status: str
    message: str = "ok"

__all__=["StatusResponse"]
