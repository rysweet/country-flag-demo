from pydantic import BaseModel


class FlagMeta(BaseModel):
    country: str
    code: str
    flag_url: str


class ErrorResponse(BaseModel):
    error: str
