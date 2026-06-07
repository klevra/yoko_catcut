# Yoko CatCut ChangeLog

모든 변경사항은 Semantic Versioning 기준으로 관리한다.

## v0.5.1

완료일: 2026-06-08

상태: Completed

### Added

- 로그인 페이지 계정 등록 버튼
- 계정 등록 API
- 신규 계정 폴더 생성
- `workspace/{account}/lock.lck` 기반 로그인 승인
- 기본 계정 및 등록 승인 설명 문서 `readme_account.txt`

### Verified

- 기본 계정 로그인
- 신규 계정 등록
- `lock.lck` 존재 시 신규 계정 로그인 차단
- `lock.lck` 삭제 후 신규 계정 로그인 허용
- 신규 계정 프로젝트 생성 및 본인 프로젝트 조회

## v0.5.0

완료일: 2026-06-07

상태: Completed

### Added

- 파일 기반 계정/비밀번호 저장
- 기본 계정 `default-user`와 기본 비밀번호 `yoko1234`
- 로그인 토큰 기반 API 인증
- 계정별 프로젝트, 업로드, Job, 결과물 접근 제한
- 미디어 URL 쿼리 토큰 인증
- 접속 호스트 기준 동적 API URL
- 배경음악 제거 옵션
- 배경음악 파일 업로드 및 결과 영상 믹스

### Changed

- 프론트엔드가 `localhost` 고정 API 대신 현재 접속 호스트의 백엔드 포트를 사용
- 대시보드가 로그인 계정의 프로젝트만 표시

### Verified

- 로그인 후 계정 프로젝트 조회
- 인증 토큰 없는 프로젝트 API 접근 차단
- 다른 계정의 프로젝트 접근 차단
- 배경음악 업로드 API와 내보내기 옵션 연결

## v0.4.3

완료일: 2026-06-07

상태: Completed

### Added

- 음성 대역 강화와 배경 잡음 감소 전처리
- Whisper VAD 기반 육성 후보 분석
- 음정, 스펙트럼, 반복 문구 기반 노래/음악 후보 분류
- 음향 특징 기반 최대 4개 화자 군집화
- 화자별 최대 5초 대표 음성 MP3
- 화자 체크박스와 브라우저 미리듣기
- 선택 화자 전용 자막 생성
- 자막 구간별 `speaker_id`

### Verified

- 39.97초 한국어 영상에서 발화 8개와 화자 1명 분석
- 화자 대표 음성 API `audio/mpeg` 200 응답
- 선택 화자 자막 8개 생성 및 `speaker_id` 보존
- 지속 음정 노래형 신호 점수 0.897
- 변화형 발화 신호 점수 0.070
- 노래 후보 기준값 0.72 분리 확인

### Limitations

- 현재 음악 제거는 완전한 음원 분리가 아닌 음성 강화와 음향 분류 방식이다.
- 정밀 화자 분리는 향후 Demucs 및 pyannote.audio 어댑터로 교체한다.

## v0.4.2

완료일: 2026-06-07

상태: Completed

### Added

- 출력 설정 전 영상 옵션 패널
- 자동 자막 음성 구간 기반 무음 파트 제거
- 자막 문구의 편집 구간 코멘트 변환
- 제외 구간 x2, x4, x8, x16 배속 드롭다운
- 선택 구간 중앙 작업부 확대 크롭
- 영상 재적용 및 초기화 버튼
- 배속 구간을 반영한 자막 타임라인 재매핑

### Fixed

- 다중 구간 연결 시 원본 타임스탬프가 남아 결과 길이가 늘어나는 문제
- FFmpeg 입력 구간 길이와 배속 후 출력 길이가 혼동되는 문제

### Verified

- 자동 자막 8개를 음성 구간과 코멘트로 변환
- 제외 구간 4개에 x16 배속 적용
- 원본 39.97초를 옵션 적용 결과 34.27초로 렌더링
- 9:16, 1080x1920 중앙 확대 결과 프레임 확인
- 한글 자막과 H.264/AAC 스트림 확인

## v0.4.1

완료일: 2026-06-07

상태: Completed

### Fixed

- 자막이 포함된 결과 영상에서 한글이 네모 문자로 렌더링되는 문제
- FFmpeg 자막 입력 인코딩을 UTF-8로 명시
- 렌더링 컨테이너에 Noto CJK 폰트를 설치하고 한글 폰트를 명시적으로 적용

### Added

- 선택된 자막 우측 햄버거 메뉴
- 플로팅 메뉴에서 선택 자막 편집 열기
- 선택 상태를 유지하면서 지속 반복 재생 해제

### Verified

- 컨테이너의 `Noto Sans CJK KR` 폰트 매칭
- 한글 자막 2개가 포함된 5초 MP4 재렌더링
- 결과 프레임에서 한글 자막이 깨짐 없이 표시되는 것 확인
- 자막 메뉴 변경 후 TypeScript 및 Vite 프로덕션 빌드

## v0.4.0

완료일: 2026-06-07

상태: Completed

### Added

- 자막 선택 시 구간 반복 재생
- 자막 시작/종료 초와 문구 직접 수정
- 현재 재생 위치 기준 자막 두 개 분할
- 수정 자막 JSON, SRT, VTT 동기화 저장
- CapCut, Premiere Pro, DaVinci Resolve, Final Cut Pro 프리셋
- 모든 페이지 하단 우측 버전 Footer
- 다중 편집 구간 FFmpeg 렌더링
- 수정 자막 새 타임라인 재매핑
- 자막 포함 H.264/AAC MP4 다운로드
- CapCut 호환 MP4, SRT, manifest ZIP
- 결과 렌더링 백그라운드 Job

### Verified

- 자막 8개에서 9개로 분할 저장 후 원본 복구
- 자막 시간과 문구 저장 및 SRT/VTT/JSON 재생성
- 0~5초 편집 구간 렌더링 성공
- 결과 영상 길이 5.038초, 크기 1,390,306 byte
- CapCut ZIP 내 MP4, SRT, manifest 확인
- MP4와 ZIP 다운로드 API 200 응답
- TypeScript 프로덕션 빌드

### CapCut 제한

- CapCut 공식 가져오기는 Desktop/Web에서 SRT를 지원한다.
- 공개된 자동 프로젝트 삽입 API가 없어 ZIP 다운로드와 Web Editor 실행으로 제공한다.

## v0.3.0

완료일: 2026-06-07

상태: Completed

### Added

- 영상별 다중 편집 구간 추가
- 편집 구간별 코멘트 입력 및 삭제
- 다중 구간과 코멘트 Local Storage 초안 저장
- Faster-Whisper 기반 자동 자막 생성
- 백그라운드 Subtitle Job 및 상태 조회
- 언어 자동 감지와 언어 지정
- 활성 자막 영상 오버레이
- 클릭 가능한 Subtitle Viewer
- SRT, VTT, JSON 생성 및 다운로드
- Whisper 모델 Workspace 볼륨 캐시

### Changed

- 로컬 CPU 기본 Whisper 모델을 다국어 `base`로 설정
- CPU 자막 추론에 int8 연산 적용
- SubtitleService에서 로드된 모델 재사용

### Verified

- 39.97초 한국어 MP4 자동 자막 생성 성공
- 한국어 자막 8개 구간 생성
- 언어 감지 결과 `ko`, 확률 1.0
- Subtitle Job `QUEUED → SUBTITLE_GENERATING → COMPLETED`
- SRT, VTT, JSON 파일 생성
- Faster-Whisper 런타임 import
- TypeScript 프로덕션 빌드

## v0.2.1

완료일: 2026-06-07

상태: Completed

### Added

- 프로젝트별 업로드 영상 목록 API 및 UI
- 브라우저 재생용 원본 영상 응답 API
- 업로드 영상 편집 버튼
- `/editor` 영상 편집 페이지
- 원본 영상 재생 및 타임라인 탐색
- 편집 시작점과 끝점 지정
- 원본, 9:16, 16:9, 1:1 출력 비율 선택
- 브라우저 Local Storage 기반 편집 초안 저장

### Verified

- test 프로젝트 업로드 목록 조회 성공
- 8,071,981 byte MP4 영상 Range 요청 `206 Partial Content`
- 편집 URL SPA 응답
- TypeScript 프로덕션 빌드
- 백엔드 Python 모듈 컴파일

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

완료일: 2026-06-07

상태: Completed

목표: 파일 검증 및 메타데이터 분석

### Added

- 청크 기반 스트리밍 업로드
- mp4, mov, mkv, webm 확장자 검증
- ffprobe 기반 실제 비디오 스트림 및 손상 파일 검증
- 영상, 오디오, 컨테이너 메타데이터 분석
- Workspace 기반 Upload Repository와 조회 API
- FastAPI lifespan 기반 Job Processor
- 프로젝트별 Job 상태 조회 및 주기적 갱신 UI
- TypeScript 및 Vite 프로덕션 빌드 설정

### Changed

- Project와 Job 저장소를 `workspace/.system`으로 이동
- Project와 Job 메타데이터를 원자적으로 저장
- 업로드 전체 메모리 적재 방식을 청크 처리로 변경
- Job 상태 변경 API의 JSON 요청 계약 통일
- 애플리케이션 버전을 v0.2.0으로 통일

### Fixed

- 업로드 Job이 계속 QUEUED에 머무는 문제
- Upload 조회 API가 구현되지 않은 문제
- 여러 개의 점이 포함된 파일명 처리 문제
- 프로젝트명과 사용자 ID의 경로 이탈 가능성
- 프로젝트 삭제 후 관련 Job 메타데이터가 남는 문제
- 기존 Workspace 프로젝트가 새 메타데이터 인덱스에서 누락되는 문제
- 프론트엔드 프로덕션 빌드 설정 및 React 타입 누락
