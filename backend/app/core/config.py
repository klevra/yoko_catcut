from functools import lru_cache
from pathlib import Path
from typing import Any

import os
import platform
import yaml
from pydantic import BaseModel


class Settings(BaseModel):
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_port: int = 3000
    websocket_port: int = 8001

    workspace_root: str = "./workspace"
    storage_type: str = "local"
    users_file: str = "./workspace/.system/accounts/users.json"
    runtime_os: str = "auto"
    supported_os: list[str] = ["win", "mac", "rhel", "ubuntu", "docker-image"]
    detected_os: str = "unknown"

    max_file_size_gb: int = 10
    max_concurrent_uploads: int = 5

    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"
    subtitle_font: str = "Noto Sans CJK KR"
    whisper_path: str = "./models/whisper"
    whisper_model: str = "base"
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
    auth = app.get("auth", {})
    runtime = app.get("runtime", {})
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
        users_file=auth.get(
            "users_file",
            "./workspace/.system/accounts/users.json",
        ),
        runtime_os=runtime.get("os") or os.getenv("YOKO_RUNTIME_OS", "auto"),
        supported_os=runtime.get(
            "supported_os",
            ["win", "mac", "rhel", "ubuntu", "docker-image"],
        ),
        detected_os=_detect_os(),
        max_file_size_gb=upload.get("max_file_size_gb", 10),
        max_concurrent_uploads=upload.get("max_concurrent_uploads", 5),
        ffmpeg_binary=ffmpeg.get("binary", "ffmpeg"),
        ffprobe_binary=ffmpeg.get("probe_binary", "ffprobe"),
        subtitle_font=ffmpeg.get("subtitle_font", "Noto Sans CJK KR"),
        whisper_path=model.get("whisper_path", "./models/whisper"),
        whisper_model=model.get("whisper_model", "base"),
        device=model.get("device", "cpu"),
        log_level=logging.get("level", "INFO"),
        log_path=logging.get("path", "./logs"),
        cors_allowed_origins=cors.get("allowed_origins", ["*"]),
    )


def _detect_os() -> str:
    system = platform.system().lower()
    if Path("/.dockerenv").exists() or os.getenv("YOKO_RUNTIME_OS") == "docker-image":
        return "docker-image"
    if system == "darwin":
        return "mac"
    if system == "windows":
        return "win"
    if system == "linux":
        try:
            os_release = Path("/etc/os-release").read_text(encoding="utf-8").lower()
        except FileNotFoundError:
            return "ubuntu"
        if "rhel" in os_release or "red hat" in os_release or "centos" in os_release or "rocky" in os_release:
            return "rhel"
        return "ubuntu"
    return system


def validate_runtime_os(settings: Settings) -> None:
    configured = settings.runtime_os
    if configured in {"", "auto"}:
        configured = settings.detected_os
    if configured not in settings.supported_os:
        raise RuntimeError(f"Unsupported configured OS: {configured}")
    if settings.detected_os not in settings.supported_os:
        raise RuntimeError(f"Unsupported detected OS: {settings.detected_os}")
    if configured != "docker-image" and settings.detected_os == "docker-image":
        return
    if configured != settings.detected_os:
        raise RuntimeError(
            f"Configured OS '{configured}' does not match detected OS "
            f"'{settings.detected_os}'"
        )
