from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402

from routers import directions, dispatch, farms, facilities  # noqa: E402
from services.db import get_cursor  # noqa: E402

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
app.include_router(facilities.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "bioroute"}


@app.get("/api/health/db")
def db_health_check():
    with get_cursor() as cur:
        cur.execute("SELECT 1")
    return {"status": "ok", "db": "postgresql"}


# React 정적 파일 서빙 (dist/ 는 배포 시 wwwroot/dist 에 위치)
# API 라우터 등록 이후에 마운트해야 /api/* 가 catch-all에 걸리지 않는다
DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "dist")

if os.path.isdir(DIST_DIR):
    _assets_dir = os.path.join(DIST_DIR, "assets")
    _icons_dir = os.path.join(DIST_DIR, "livestock-icons")
    if os.path.isdir(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")
    if os.path.isdir(_icons_dir):
        app.mount("/livestock-icons", StaticFiles(directory=_icons_dir), name="livestock-icons")

    @app.get("/favicon.svg")
    def favicon():
        return FileResponse(os.path.join(DIST_DIR, "favicon.svg"))

    @app.get("/manifest.webmanifest")
    def manifest():
        return FileResponse(os.path.join(DIST_DIR, "manifest.webmanifest"))

    @app.get("/icons.svg")
    def icons():
        return FileResponse(os.path.join(DIST_DIR, "icons.svg"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        return FileResponse(os.path.join(DIST_DIR, "index.html"))
