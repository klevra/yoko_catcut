import mimetypes

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.api.deps import current_user
from app.schemas.project import (
    ExportRequest,
    SubtitleGenerateRequest,
    SubtitleUpdate,
)
from app.services.storage_service import StorageService
from app.services.job_service import JobService

router = APIRouter()
storage_service = StorageService()
job_service = JobService()


@router.post("")
async def upload_file(
    user_id: str = Form(...),
    project_name: str = Form(...),
    file: UploadFile = File(...),
    authenticated: str = Depends(current_user),
):
    """파일 업로드"""
    try:
        if user_id != authenticated:
            raise ValueError("You can only upload to your own projects")
        upload_info = await storage_service.save_original(user_id, project_name, file)

        job = job_service.create_job(
            user_id,
            project_name,
            "UPLOAD",
            {
                "upload_id": upload_info["upload_id"],
                "path": upload_info["path"],
                "media": upload_info["metadata"],
            },
        )

        return {
            "message": "uploaded",
            "upload": upload_info,
            "job": job,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
def list_uploads(
    user_id: str,
    project_name: str,
    authenticated: str = Depends(current_user),
):
    """프로젝트 업로드 파일 목록 조회"""
    try:
        if user_id != authenticated:
            raise ValueError("You can only list your own uploads")
        return storage_service.list_uploads(user_id, project_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{upload_id}/content")
def stream_upload(upload_id: str, user_id: str = Depends(current_user)):
    """브라우저 영상 재생용 원본 파일 응답"""
    try:
        upload = storage_service.ensure_upload_owner(upload_id, user_id)
        path = storage_service.get_upload_path(upload_id)
        return FileResponse(
            path=path,
            media_type=mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            filename=upload["filename"],
            content_disposition_type="inline",
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{upload_id}/speech-analysis")
def create_speech_analysis(
    upload_id: str,
    language: str = None,
    user_id: str = Depends(current_user),
):
    """음악 후보 분류와 화자 분석 Job 생성"""
    try:
        upload = storage_service.ensure_upload_owner(upload_id, user_id)
        return job_service.create_job(
            upload["user_id"],
            upload["project_name"],
            "SPEECH_ANALYSIS",
            {
                "upload_id": upload_id,
                "path": upload["path"],
                "language": language,
            },
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{upload_id}/speech-analysis")
def get_speech_analysis(upload_id: str, user_id: str = Depends(current_user)):
    """음악 후보와 화자 분석 결과 조회"""
    try:
        storage_service.ensure_upload_owner(upload_id, user_id)
        return storage_service.get_speech_analysis(upload_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{upload_id}/speech-analysis/speakers/{speaker_id}/preview")
def get_speaker_preview(
    upload_id: str,
    speaker_id: str,
    user_id: str = Depends(current_user),
):
    """화자 대표 음성 미리듣기"""
    try:
        storage_service.ensure_upload_owner(upload_id, user_id)
        path = storage_service.get_speaker_preview_path(upload_id, speaker_id)
        return FileResponse(path=path, media_type="audio/mpeg", filename=path.name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{upload_id}/subtitles")
def create_subtitles(
    upload_id: str,
    payload: SubtitleGenerateRequest = None,
    language: str = None,
    user_id: str = Depends(current_user),
):
    """자동 자막 생성 Job 생성"""
    try:
        upload = storage_service.ensure_upload_owner(upload_id, user_id)
        return job_service.create_job(
            upload["user_id"],
            upload["project_name"],
            "SUBTITLE",
            {
                "upload_id": upload_id,
                "path": upload["path"],
                "language": payload.language if payload else language,
                "selected_speakers": payload.selected_speakers if payload else [],
            },
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{upload_id}/subtitles")
def get_subtitles(upload_id: str, user_id: str = Depends(current_user)):
    """생성된 자동 자막 조회"""
    try:
        storage_service.ensure_upload_owner(upload_id, user_id)
        return storage_service.get_subtitle(upload_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{upload_id}/subtitles")
def update_subtitles(
    upload_id: str,
    payload: SubtitleUpdate,
    user_id: str = Depends(current_user),
):
    """자막 텍스트와 시간 범위 저장"""
    try:
        storage_service.ensure_upload_owner(upload_id, user_id)
        return storage_service.save_subtitle(
            upload_id,
            [segment.model_dump() for segment in payload.segments],
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{upload_id}/subtitles/{file_format}")
def download_subtitles(
    upload_id: str,
    file_format: str,
    user_id: str = Depends(current_user),
):
    """생성된 자막 파일 다운로드"""
    try:
        storage_service.ensure_upload_owner(upload_id, user_id)
        path = storage_service.get_subtitle_path(upload_id, file_format)
        return FileResponse(path=path, filename=path.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{upload_id}/background-music")
async def upload_background_music(
    upload_id: str,
    file: UploadFile = File(...),
    user_id: str = Depends(current_user),
):
    """결과 영상에 믹스할 배경음악 업로드"""
    try:
        storage_service.ensure_upload_owner(upload_id, user_id)
        return await storage_service.save_background_music(upload_id, file)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{upload_id}/exports")
def create_export(
    upload_id: str,
    payload: ExportRequest,
    user_id: str = Depends(current_user),
):
    """편집 결과 MP4 렌더링 Job 생성"""
    try:
        upload = storage_service.ensure_upload_owner(upload_id, user_id)
        background_music = storage_service.get_background_music_path(upload_id)
        metadata = payload.model_dump()
        if background_music:
            metadata["background_music_path"] = str(background_music)
        return job_service.create_job(
            upload["user_id"],
            upload["project_name"],
            "EXPORT",
            {
                "upload_id": upload_id,
                "path": upload["path"],
                **metadata,
            },
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{upload_id}/exports/{export_id}")
def download_export(
    upload_id: str,
    export_id: str,
    user_id: str = Depends(current_user),
):
    """렌더링된 MP4 다운로드"""
    try:
        storage_service.ensure_upload_owner(upload_id, user_id)
        path = storage_service.get_export_path(upload_id, export_id)
        return FileResponse(path=path, filename=f"yoko-catcut-{export_id}.mp4")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{upload_id}/exports/{export_id}/capcut")
def download_capcut_package(
    upload_id: str,
    export_id: str,
    user_id: str = Depends(current_user),
):
    """CapCut 가져오기용 MP4, SRT 패키지 다운로드"""
    try:
        storage_service.ensure_upload_owner(upload_id, user_id)
        path = storage_service.get_capcut_package_path(upload_id, export_id)
        return FileResponse(path=path, filename=f"yoko-capcut-{export_id}.zip")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{upload_id}")
def get_upload_info(upload_id: str, user_id: str = Depends(current_user)):
    """업로드 파일 정보 조회"""
    try:
        return storage_service.ensure_upload_owner(upload_id, user_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
