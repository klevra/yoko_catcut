# Yoko CatCut Roadmap

## v0.1.0

상태: Completed

목표: 프로젝트 기반 구조 생성

- [x] Repository 구조 정의
- [x] Backend 생성
- [x] Frontend 생성
- [x] Docker Compose 생성
- [x] application.yml 생성
- [x] Workspace 구조 생성
- [x] Project API 완전 구현
- [x] Upload API 완전 구현
- [x] Job API 완전 구현
- [x] Storage Adapter Pattern 구현
- [x] Repository Layer 구현
- [x] Service Layer 구현
- [x] Frontend Dashboard 구현

## v0.2.0

상태: Completed

목표: 파일 검증 및 메타데이터 분석

- [x] File Validation 구현
- [x] 스트리밍 업로드 구현
- [x] ffprobe 기반 Metadata 분석
- [x] Upload Repository 구현
- [x] Upload 조회 API 구현
- [x] Job 상태 저장 개선
- [x] Job Processor 애플리케이션 연결
- [x] Job 상태 조회 UI
- [x] TypeScript 빌드 설정 및 검증

## v0.2.x

상태: Completed

목표: 업로드 사용자 경험 및 자동화 테스트 개선

- [x] 업로드 영상 목록
- [x] 영상 편집 페이지 진입
- [x] 원본 영상 재생 및 탐색
- [x] 시작/끝 구간 지정
- [x] 출력 화면 비율 선택
- [x] 브라우저 로컬 편집 초안 저장
- [x] 다중 편집 구간 추가
- [x] 구간별 코멘트 추가 및 삭제
- [ ] Multi Upload
- [ ] 실시간 Upload Progress
- [ ] 업로드 취소
- [ ] 편집 결과 서버 저장
- [ ] ffmpeg 편집 결과 렌더링
- [ ] 브라우저 E2E 테스트 자동화

## v0.3.0

상태: Completed

목표: 자동 자막 생성

- [x] Faster-Whisper 연동
- [x] 백그라운드 Subtitle Job
- [x] 언어 자동 감지 및 언어 지정
- [x] SRT 생성 및 다운로드
- [x] VTT 생성 및 다운로드
- [x] JSON 생성 및 다운로드
- [x] Subtitle Viewer
- [x] 영상 위 활성 자막 오버레이

## v0.4.0

상태: Completed

목표: 자막 편집, 결과 내보내기 및 하이라이트 추출

- [x] 자막 선택 구간 반복 재생
- [x] 자막 시작/종료 시간 및 문구 수정
- [x] 자막 두 구간 분할
- [x] 수정 자막 SRT/VTT/JSON 동기화
- [x] 편집 도구 프리셋 드롭다운
- [x] 화면 하단 버전 Footer
- [x] 다중 구간 FFmpeg 결과 렌더링
- [x] 자막 포함 MP4 다운로드
- [x] CapCut 호환 MP4/SRT 패키지
- [ ] Scene Detection
- [ ] Silence Detection
- [ ] Voice Activity Detection
- [ ] Face Detection
- [ ] Emotion Detection
- [ ] Keyword Detection
- [ ] Highlight Viewer

## v0.4.2

상태: Completed

목표: 영상 재처리 옵션

- [x] 자동 자막 음성 구간 기반 무음 파트 제거
- [x] 자막 문구를 편집 구간 코멘트로 변환
- [x] 제외 구간 x2, x4, x8, x16 배속 연결
- [x] 조립 작업부 중앙 확대 크롭
- [x] 영상 옵션 재적용
- [x] 옵션 및 자동 생성 구간 초기화
- [x] 배속 타임라인 자막 재매핑

## v0.4.3

상태: Completed

목표: 육성 중심 자막과 화자 선택

- [x] 음성 대역 강화 및 잡음 감소
- [x] Whisper VAD 기반 발화 후보 검출
- [x] 노래/음악 후보 음향 분류
- [x] 음향 특징 기반 로컬 화자 군집화
- [x] 화자별 대표 음성 MP3 생성
- [x] 화자 체크박스 및 미리듣기 UI
- [x] 선택 화자 전용 자막 생성
- [x] 자막 `speaker_id` 보존
- [ ] Demucs 음원 분리 어댑터
- [ ] pyannote.audio 정밀 화자 분리 어댑터

## v0.5.0

상태: Completed

목표: 계정 격리, 네트워크 접속 및 배경음악 옵션

- [x] 파일 기반 계정/비밀번호 관리
- [x] 로그인 토큰 발급 및 저장
- [x] 계정별 프로젝트 격리
- [x] 업로드, Job, 결과물 소유자 검증
- [x] 다른 PC/모바일 접속용 동적 API URL
- [x] 미디어 URL 쿼리 토큰 인증
- [x] 배경음악 제거 옵션
- [x] 배경음악 추가 업로드 및 믹스

## v0.5.1

상태: Completed

목표: 계정 등록 및 파일 승인

- [x] 로그인 페이지 계정 등록 버튼
- [x] 계정 등록 API
- [x] 계정별 `lock.lck` 승인 파일 생성
- [x] `lock.lck` 존재 시 로그인 차단
- [x] 기본 계정 및 등록 절차 문서화
- [x] `readme_account.txt` 추가

## v0.6.0

상태: Completed

목표: OS별 설치와 런타임 설정

- [x] 로그인 버튼 폭 정렬
- [x] 계정 등록 안내 문구 변경
- [x] `application.yml` OS 정보 추가
- [x] 백엔드 기동 시 OS 정보 체크
- [x] macOS 설치 스크립트
- [x] Windows 설치 스크립트
- [x] Ubuntu 설치 스크립트
- [x] RHEL 계열 설치 스크립트
- [x] Docker image 설치 스크립트
- [x] 설치 경로 지정
- [x] 설치 시 default-user 비밀번호 입력
- [x] 비밀번호 재설정 스크립트
- [x] OS별 설치 매뉴얼
- [x] manual.txt 설치 항목 갱신

## v0.7.0

상태: Planned

목표: 숏폼 생성

- [ ] 9:16 레이아웃
- [ ] 1080x1920 해상도
- [ ] Shorts Generator
- [ ] Shorts Viewer

## v0.8.0

상태: Planned

목표: 썸네일 생성

- [ ] Thumbnail Generator
- [ ] PNG/JPG 출력
- [ ] Thumbnail Viewer

## v0.9.0

상태: Planned

목표: YouTube 통합

- [ ] YouTube URL Parser
- [ ] Video Downloader
- [ ] Subtitle 생성
- [ ] Highlight 생성
- [ ] Shorts 생성

## v0.10.0

상태: Planned

목표: NAS 스토리지

- [ ] SMB 프로토콜 구현
- [ ] NFS 프로토콜 구현
- [ ] NAS 연결 테스트

## v1.0.0

상태: Target

목표: 프로덕션 릴리스

- [ ] 성능 최적화
- [ ] 보안 감시
- [ ] 사용자 인증
- [ ] 다중 사용자 지원
- [ ] 데이터베이스 마이그레이션 (SQLite → PostgreSQL)
