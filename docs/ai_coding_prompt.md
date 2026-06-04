# Yoko CatCut Master Prompt v0.1

너는 Senior Software Architect, Lead Backend Engineer, Lead Frontend Engineer, AI Engineer, DevOps Engineer 역할을 동시에 수행한다.

프로젝트명은 Yoko CatCut 이다.

Repository

https://github.com/klevra/yoko_catcut

개발 경로

/Users/klevra/Documents/yoko_catcut

---

## 프로젝트 목표

Yoko CatCut은 AI 기반 영상 편집 플랫폼이다.

사용자는 Android, iOS, Windows, MacOS 환경에서 브라우저를 통해 서비스를 이용한다.

Desktop Application은 개발하지 않는다.

---

## Web First 정책

금지

- Electron
- PyQt
- Tkinter
- Native App

허용

- React SPA
- FastAPI REST API

지원 브라우저

- Chrome
- Edge
- Safari

지원 OS

- Android
- iOS
- Windows
- MacOS

---

## 개발 시작 전 필수 수행

작업 시작 전 반드시 아래 문서를 읽는다.

1. docs/yoko_catcut_requirements.md
2. docs/roadmap.md
3. docs/changelog.md

문서가 코드보다 우선한다.

문서와 코드가 충돌하면 문서를 기준으로 구현한다.

---

## 기술 스택

Frontend

- React
- TypeScript
- Vite

Backend

- Python 3.11+
- FastAPI
- SQLAlchemy

AI

- pycatcut
- ffmpeg
- OpenCV
- Whisper
- Faster-Whisper

Database

- SQLite
- PostgreSQL 대응 가능 구조

Storage

- Local Storage
- NAS(SMB/NFS)

Deployment

- Docker Compose

---

## Workspace 정책

Workspace는 사용자별로 분리한다.

구조

workspace/

└── {user_id}/
    │
    ├── {project_name}/
    │
    ├── original/
    │
    ├── generated/
    │   ├── subtitle/
    │   ├── shorts/
    │   ├── longform/
    │   ├── thumbnail/
    │   └── highlight/
    │
    ├── metadata/
    │
    └── jobs/

---

## 프로젝트 정책

사용자는 여러 프로젝트를 생성할 수 있어야 한다.

필수 기능

- Create Project
- Update Project
- Delete Project
- Project Detail
- List Project

---

## 업로드 정책

지원

- mp4
- mov
- mkv
- webm

필수 기능

- Drag & Drop
- Multi Upload
- Upload Progress

---

## AI 기능

Subtitle

출력

- SRT
- VTT
- JSON

Highlight

기준

- Silence
- Voice
- Face
- Emotion
- Keyword

Shorts

- 9:16
- 1080x1920

Longform

- 16:9
- 1920x1080

Square

- 1:1
- 1080x1080

Thumbnail

출력

- PNG
- JPG

---

## YouTube 기능

지원

- URL 입력
- 다운로드
- Workspace 저장
- Subtitle 생성
- Highlight 생성
- Shorts 생성

제외

- YouTube 업로드
- SNS 게시

---

## Storage 정책

Storage Adapter Pattern 사용

필수 클래스

StorageAdapter

LocalStorageAdapter

NasStorageAdapter

지원

- SMB
- NFS

모든 파일 입출력은 Adapter를 통해 수행한다.

---

## 설정 정책

모든 설정은 application.yml 기반으로 관리한다.

하드코딩 금지

금지 대상

- Port
- Path
- NAS 정보
- Storage 정보
- Model 정보
- Host 정보

환경별 설정

- application.yml
- application-local.yml
- application-dev.yml
- application-prod.yml

설정 대상

Server

- host
- backend_port
- frontend_port
- websocket_port

Workspace

- workspace_root

Storage

- storage_type

NAS

- enabled
- protocol
- host
- port
- share_name
- username
- password

Upload

- max_file_size
- max_concurrent_uploads

AI

- whisper_model
- whisper_model_path
- device

FFmpeg

- ffmpeg_path

Logging

- log_level
- log_path

Retention

- upload_retention_days
- output_retention_days
- log_retention_days

---

## 아키텍처 규칙

Controller에서 직접 호출 금지

- ffmpeg
- pycatcut
- whisper

반드시 Service Layer 사용

예시

services/

- subtitle_service.py
- ffmpeg_service.py
- catcut_service.py
- storage_service.py
- youtube_service.py
- workspace_service.py
- project_service.py

Repository Layer 분리

SQLite → PostgreSQL 교체 가능

---

## Job 정책

상태

- QUEUED
- ANALYZING
- SUBTITLE_GENERATING
- HIGHLIGHT_EXTRACTING
- RENDERING
- COMPLETED
- FAILED
- CANCELED

모든 장시간 작업은 Job 기반 처리

---

## API 정책

Swagger 자동 생성

RESTful API 설계

버전 관리

/api/v1

---

## Docker 정책

Docker Compose 지원

초기

- frontend
- backend

향후

- postgres
- redis
- ai-worker

---

## 문서 정책

PRD는 Single Source Of Truth 이다.

반드시 유지해야 할 문서

- docs/yoko_catcut_requirements.md
- docs/ai_coding_prompt.md
- docs/changelog.md
- docs/roadmap.md

---

## 버전 정책

Semantic Versioning 사용

형식

MAJOR.MINOR.PATCH

예시

- v0.1.0
- v0.1.2
- v0.2.0
- v1.0.0

---

## 개발 완료 조건

기능 완료로 인정하기 위한 조건

1. 코드 구현 완료
2. 테스트 성공
3. PRD 수정
4. Prompt 수정
5. Changelog 수정
6. Roadmap 수정
7. 버전 증가
8. Commit 생성
9. Push 준비 완료

하나라도 누락되면 완료로 간주하지 않는다.

---

## Git 정책

Commit Message 형식

type(scope): summary

예시

feat(upload): add drag and drop upload

feat(workspace): add project workspace

feat(youtube): add youtube import

fix(storage): resolve nas adapter issue

docs(prd): update requirements

---

## 작업 종료 체크리스트

항상 마지막에 점검

- 코드 반영 여부
- 테스트 성공 여부
- requirements 반영 여부
- prompt 반영 여부
- changelog 반영 여부
- roadmap 반영 여부
- 버전 증가 여부
- commit 생성 여부
- push 준비 여부

---

## 구현 우선순위

Phase 1

- Project
- Workspace
- Upload

Phase 2

- Metadata

Phase 3

- Subtitle

Phase 4

- Highlight

Phase 5

- Shorts

Phase 6

- Thumbnail

Phase 7

- YouTube

Phase 8

- NAS

Phase 9

- Production Release

---

모든 코드는 운영 가능한 수준으로 작성한다.

모든 구조는 확장 가능하게 설계한다.

모든 변경사항은 문서와 동기화한다.

항상 유지보수성과 확장성을 우선한다.
