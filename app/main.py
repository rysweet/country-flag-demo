from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .models import ErrorResponse, FlagMeta
from .services import FlagNotFound, get_flag

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, q: str | None = Query(None, description="Country name or code")):
    flag: FlagMeta | None = None
    error: str | None = None
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
