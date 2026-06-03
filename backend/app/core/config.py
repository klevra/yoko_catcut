from functools import lru_cache
from pathlib import Path
from typing import Any

import os
import yaml
from pydantic import BaseModel


class Settings(BaseModel):
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_port: int = 3000
    websocket_port: int = 8001

    workspace_root: str = "./workspace"
    storage_type: str = "local"

    max_file_size_gb: int = 10
    max_concurrent_uploads: int = 5

    ffmpeg_binary: str = "ffmpeg"
    whisper_path: str = "./models/whisper"
    whisper_model: str = "large-v3"
    device: str = "cpu"

    log_level: str = "INFO"
    log_path: str = "./logs"

    cors_allowed_origins: list[str] = ["*"]


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache
def get_settings() -> Settings:
    config_path = Path(os.getenv("YOKO_CONFIG", "application.yml"))
    data = _load_yaml(config_path)
    app = data.get("app", {})

    server = app.get("server", {})
    workspace = app.get("workspace", {})
    storage = app.get("storage", {})
    upload = app.get("upload", {})
    model = app.get("model", {})
    ffmpeg = app.get("ffmpeg", {})
    logging = app.get("logging", {})
    cors = app.get("cors", {})

    return Settings(
        backend_host=server.get("host", "0.0.0.0"),
        backend_port=server.get("backend_port", 8000),
        frontend_port=server.get("frontend_port", 3000),
        websocket_port=server.get("websocket_port", 8001),
        workspace_root=workspace.get("root_path", "./workspace"),
        storage_type=storage.get("type", "local"),
        max_file_size_gb=upload.get("max_file_size_gb", 10),
        max_concurrent_uploads=upload.get("max_concurrent_uploads", 5),
        ffmpeg_binary=ffmpeg.get("binary", "ffmpeg"),
        whisper_path=model.get("whisper_path", "./models/whisper"),
        whisper_model=model.get("whisper_model", "large-v3"),
        device=model.get("device", "cpu"),
        log_level=logging.get("level", "INFO"),
        log_path=logging.get("path", "./logs"),
        cors_allowed_origins=cors.get("allowed_origins", ["*"]),
    )
