from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .services import get_flag, FlagNotFound
from .models import FlagMeta, ErrorResponse
from typing import Optional

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request, q: Optional[str] = Query(None, description="Country name or code")
):
    flag: Optional[FlagMeta] = None
    error: Optional[str] = None
    if q:
        try:
            flag = await get_flag(q)
        except FlagNotFound as e:
            error = str(e)
        except Exception:
            error = "Unexpected error"
    return templates.TemplateResponse(
        "index.html", {"request": request, "flag": flag, "error": error}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(error="Invalid input").dict(),
    )
