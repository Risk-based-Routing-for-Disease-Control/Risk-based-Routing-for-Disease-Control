from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402

from routers import directions, dispatch, farms  # noqa: E402

app = FastAPI(title="방역로 (BioRoute) API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(farms.router, prefix="/api")
app.include_router(directions.router, prefix="/api")
app.include_router(dispatch.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "bioroute"}


# React 정적 파일 서빙 (dist/ 는 배포 시 wwwroot/dist 에 위치)
# API 라우터 등록 이후에 마운트해야 /api/* 가 catch-all에 걸리지 않는다
DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "dist")

if os.path.isdir(DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets")

    @app.get("/favicon.svg")
    def favicon():
        return FileResponse(os.path.join(DIST_DIR, "favicon.svg"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        return FileResponse(os.path.join(DIST_DIR, "index.html"))
