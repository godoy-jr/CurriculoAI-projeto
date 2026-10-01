from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .schemas import AnalysisRequest, AnalysisResponse
from .services import AIServiceError, analyze

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="CurrículoAI API",
    description="Compara um currículo com uma vaga usando IA generativa.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def create_analysis(payload: AnalysisRequest) -> AnalysisResponse:
    try:
        return await analyze(payload)
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [{"field": ".".join(map(str, err["loc"][1:])), "message": err["msg"]} for err in exc.errors()]
    return JSONResponse(status_code=400, content={"detail": "Dados inválidos.", "errors": errors})

