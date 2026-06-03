# Yoko CatCut ChangeLog

모든 변경사항은 Semantic Versioning 기준으로 관리한다.

## v0.1.0

생성일: 2026-06-03

상태: Completed

### Phase 1: Project, Workspace, Upload 구현 완료

#### Added

- 프로젝트 스캐폴딩 생성
- Web First 정책 정의
- React + FastAPI 구조 정의
- application.yml 기반 설정 구조 추가
- Workspace 구조 정의 및 생성 기능 구현
- Project API 완전 구현 (Create, Read, Update, Delete, List)
- Upload API 완전 구현 (파일 업로드, 크기 검증)
- Job API 완전 구현 (상태 관리, 조회)
- Storage Adapter Pattern 구현 (LocalStorageAdapter, NasStorageAdapter 인터페이스)
- Repository Layer 구현 (ProjectRepository, JobRepository)
- Service Layer 구현 (ProjectService, JobService, StorageService)
- Frontend Dashboard 구현 (React + TypeScript)
- Project 관리 UI 구현
- NAS Adapter 확장 포인트 추가
- YouTube Service 확장 포인트 추가
- 문서 관리 정책 추가

#### Backend

- Models: Project, Job, Upload, JobStatus, JobType
- Repositories: ProjectRepository, JobRepository
- Services: ProjectService, JobService, StorageService
- API Endpoints: /api/v1/projects, /api/v1/uploads, /api/v1/jobs
- Storage: LocalStorageAdapter, NasStorageAdapter (interface)

#### Frontend

- Components: Dashboard, ProjectList, CreateProjectForm
- API Client: Fetch-based REST client
- Pages: Dashboard
- Styling: CSS Grid Layout

## v0.2.0

생성일: 2026-06-03

상태: Planned

목표: 파일 검증 및 메타데이터 분석

### Planned

- File Validation (VideoValidator)
- ffprobe 기반 Metadata 분석
- 작업 상태 저장 개선
- Job 상태 조회 UI
