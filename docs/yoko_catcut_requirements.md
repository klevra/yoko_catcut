# Yoko CatCut Requirements v0.1

## 프로젝트 정보

- 프로젝트명: yoko_catcut
- Repository: https://github.com/klevra/yoko_catcut
- 개발 경로: `/Users/klevra/Documents/catcut/yoko_catcut`

## 프로젝트 목표

AI 기반 영상 편집 플랫폼 구축.

사용자는 Android, iOS, Windows, MacOS 환경에서 브라우저만으로 서비스를 사용할 수 있어야 한다.

## Web First 정책

Desktop Application 개발 금지.

지원 브라우저:

- Chrome
- Edge
- Safari

## 기술 스택

Frontend:

- React
- TypeScript
- Vite

Backend:

- Python 3.11+
- FastAPI
- SQLAlchemy

AI:

- pycatcut
- ffmpeg
- OpenCV
- Whisper
- Faster-Whisper

Storage:

- Local Storage
- NAS(SMB/NFS)

## Workspace 구조

```text
workspace/
└── {user_id}/
    └── {project_name}/
        ├── original/
        ├── generated/
        │   ├── subtitle/
        │   ├── shorts/
        │   ├── longform/
        │   ├── thumbnail/
        │   └── highlight/
        ├── metadata/
        └── jobs/
```

## YouTube 기능

지원:

- URL 입력
- 다운로드
- Workspace 저장
- Subtitle
- Highlight
- Shorts

제외:

- YouTube 업로드
- SNS 게시

## 설정파일 정책

모든 설정은 `application.yml` 기반으로 관리한다.

하드코딩 금지:

- Port
- Path
- NAS 정보
- Storage 정보
- Model 정보

## 문서 관리 정책

PRD는 프로젝트의 Single Source Of Truth이다.

작업 완료 후 반드시 갱신:

- docs/yoko_catcut_requirements.md
- docs/ai_coding_prompt.md
- docs/changelog.md
- docs/roadmap.md

## 버전 정책

Semantic Versioning 적용.

예:

- v0.1.0
- v0.1.1
- v0.2.0
- v1.0.0
