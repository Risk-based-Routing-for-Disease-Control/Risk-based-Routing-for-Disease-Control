from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from routers import directions, farms  # noqa: E402

app = FastAPI(title="가축전염병 방역 배치 시스템 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(farms.router, prefix="/api")
app.include_router(directions.router, prefix="/api")


@app.get("/")
def read_root():
    return {"status": "ok", "service": "livestock-backend"}
