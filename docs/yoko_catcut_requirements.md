# Yoko CatCut Requirements v0.5.0

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

## 핵심 사용자 흐름

1. 사용자는 프로젝트를 생성한다.
2. 프로젝트를 열고 원본 영상을 업로드한다.
3. 서버는 파일 크기, 확장자, 실제 비디오 스트림을 검증한다.
4. 서버는 ffprobe로 영상 메타데이터를 추출한다.
5. 장시간 작업은 Job으로 생성하고 상태를 영속화한다.
6. 사용자는 브라우저에서 Job 상태와 결과를 확인한다.
7. 후속 버전에서 자막, 하이라이트, 쇼츠, 썸네일을 생성한다.

## 영상 옵션

- 자동 자막의 음성 구간을 기준으로 무음 파트를 제거한다.
- 음성 구간의 자막 문구를 편집 구간 코멘트로 사용한다.
- 선택 구간 밖의 영상을 삭제하지 않고 x2, x4, x8, x16으로 연결할 수 있다.
- 조립만 추출 옵션은 선택 구간의 중앙 작업부를 확대 크롭한다.
- 옵션은 영상 재적용 버튼을 눌렀을 때 출력 설정에 반영한다.
- 초기화 시 옵션과 자동 생성 구간을 적용 전 상태로 복원한다.
- 배경음악 제거 옵션은 최종 오디오의 음성 대역을 강화하고 배경음을 낮춘다.
- 배경음악 추가 옵션은 사용자가 업로드한 오디오 파일을 지정 볼륨으로 믹스한다.

## 계정 및 접속

- 계정과 비밀번호 해시는 파일로 관리한다.
- 기본 계정 파일 경로는 `workspace/.system/accounts/users.json`이다.
- 기본 계정은 `default-user`, 기본 비밀번호는 `yoko1234`이다.
- 로그인 성공 시 파일에 저장된 토큰을 사용해 API와 미디어 URL을 인증한다.
- 사용자는 본인 계정의 프로젝트, 업로드, Job, 결과물만 조회하고 수정할 수 있다.
- 프론트엔드는 접속한 호스트 기준으로 `http://{host}:8000/api/v1`을 사용해 다른 PC와 모바일에서도 동작한다.

## 음성 및 화자 분석

- FFmpeg 필터로 음성 대역을 강화하고 배경 잡음을 낮춘다.
- Faster-Whisper VAD로 실제 발화 후보 구간을 검출한다.
- 음정 지속성, 스펙트럼 집중도, 문구 반복성을 사용해 노래/음악 후보를 분류한다.
- 음성 구간의 음향 특징을 군집화해 화자를 구분한다.
- 각 화자의 대표 음성을 최대 5초 MP3로 제공한다.
- 노래/음악 후보는 기본 선택에서 제외한다.
- 사용자가 체크한 화자의 구간만 SRT, VTT, JSON 자막으로 생성한다.
- 자막 수정 및 저장 후에도 `speaker_id`를 유지한다.

현재 로컬 분석은 별도 인증 토큰 없이 동작하는 경량 구현이다. 더 정밀한
음원 분리와 화자 분리가 필요하면 분석 서비스 경계에서 Demucs와
pyannote.audio 기반 구현으로 교체한다.

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
├── .system/
│   ├── projects/
│   └── jobs/
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

Project와 Job의 런타임 메타데이터는 컨테이너 재시작 후에도 유지되어야 한다.

## 프로젝트 요구사항

- Create, Read, Update, Delete, List 지원
- 중복 프로젝트명 거부
- `user_id`, `project_name`을 이용한 경로 이탈 방지
- 프로젝트 생성 시 전체 Workspace 하위 디렉토리 자동 생성

## 업로드 요구사항

지원 확장자:

- mp4
- mov
- mkv
- webm

검증:

- 설정된 최대 파일 크기 적용
- 대용량 파일을 메모리에 한 번에 적재하지 않는 스트리밍 처리
- 지원 확장자 검증
- ffprobe로 실제 비디오 스트림 및 손상 여부 검증
- 업로드 메타데이터 영속화 및 조회 API 제공

제품 목표:

- Drag & Drop
- Multi Upload
- Upload Progress

v0.2.0에서는 단일 파일 Drag & Drop과 완료 상태 표시를 제공한다.
Multi Upload와 실시간 Upload Progress는 후속 개선 대상으로 유지한다.

## 메타데이터 요구사항

ffprobe를 사용해 최소 다음 정보를 저장한다.

- duration
- container format
- file size
- bit rate
- video codec
- resolution
- frame rate
- pixel format
- audio codec
- sample rate
- channels

## 영상 편집 진입 요구사항

- 프로젝트 화면에서 업로드 영상 목록을 조회한다.
- 각 업로드 영상에 편집 버튼을 제공한다.
- 편집 버튼은 `/editor?uploadId={upload_id}` 페이지로 이동한다.
- 편집 페이지에서 원본 영상 재생과 탐색을 지원한다.
- 현재 재생 위치를 시작점과 끝점으로 지정할 수 있다.
- 원본, 9:16, 16:9, 1:1 출력 비율을 선택할 수 있다.
- 편집 초안은 브라우저 Local Storage에 저장할 수 있다.
- 하나의 영상에 여러 편집 구간을 추가할 수 있다.
- 각 구간은 시작 시각, 종료 시각, 코멘트를 가진다.
- 사용자는 구간 시작 위치로 이동하고 구간을 삭제할 수 있다.
- 다중 구간과 코멘트는 편집 초안에 함께 저장한다.

v0.2.1 범위는 편집 페이지 진입과 초안 설정까지다.
서버 편집 상태 저장과 ffmpeg 결과 렌더링은 후속 범위다.

## 자동 자막 요구사항

- 자동 자막 생성은 Subtitle Job으로 비동기 처리한다.
- Faster-Whisper를 사용한다.
- 언어 자동 감지와 한국어, 영어, 일본어, 중국어 지정을 지원한다.
- CPU 환경은 int8 연산을 사용한다.
- 모델 파일은 `models/whisper`에 캐시한다.
- 생성 결과는 SRT, VTT, JSON 형식으로 저장한다.
- 편집 페이지에서 자막 생성 상태와 오류를 표시한다.
- 자막 행을 선택하면 해당 영상 위치로 이동한다.
- 현재 재생 위치의 자막을 영상 위에 표시한다.
- SRT, VTT, JSON 파일 다운로드를 제공한다.

## 자막 편집 요구사항

- 자막 행을 선택하면 해당 시작 위치부터 종료 위치까지 반복 재생한다.
- 자막 시작과 종료 시각은 0.01초 단위로 수정할 수 있다.
- 시간 수정 즉시 반복 재생 범위에 반영한다.
- 자막 문구를 직접 수정할 수 있다.
- 현재 재생 위치 또는 자막 중앙을 기준으로 자막을 두 개로 분할한다.
- 수정 결과 저장 시 JSON, SRT, VTT 파일을 함께 재생성한다.
- 빈 문구, 역전된 시간 범위, 겹치는 자막 범위는 거부한다.

## 편집 도구 프리셋

드롭다운 지원:

- CapCut
- Adobe Premiere Pro
- DaVinci Resolve
- Final Cut Pro
- Generic Editor

각 프리셋은 호환성이 높은 H.264/AAC MP4와 UTF-8 SRT를 기본으로 한다.
Generic Editor는 VTT와 JSON도 선택적으로 사용할 수 있다.

## 결과 내보내기

Download:

- 선택한 다중 구간을 순서대로 잘라 하나의 MP4로 합친다.
- 출력 비율에 따라 원본, 9:16, 16:9, 1:1 렌더링을 지원한다.
- 수정 자막을 새 편집 타임라인으로 재계산한다.
- 옵션에 따라 자막을 영상에 입힌다.

CapCut:

- CapCut 호환 MP4, UTF-8 SRT, 작업 manifest를 ZIP으로 제공한다.
- 패키지 생성 후 CapCut Web Editor를 연다.
- CapCut은 공개된 제3자 자동 프로젝트 삽입 API를 제공하지 않으므로,
  사용자가 CapCut Desktop/Web에서 MP4와 SRT를 가져오는 단계는 필요하다.

## 버전 표시

- 모든 페이지 하단 우측에 현재 애플리케이션 버전을 표시한다.

## Job 요구사항

상태:

- QUEUED
- ANALYZING
- SUBTITLE_GENERATING
- HIGHLIGHT_EXTRACTING
- RENDERING
- COMPLETED
- FAILED
- CANCELED

모든 장시간 작업은 Job 기반으로 처리한다.

- 백그라운드 Processor가 QUEUED Job을 처리
- 상태와 오류 메시지를 영속화
- 프로젝트별 Job 목록 조회
- 브라우저에서 Job 상태 주기적 갱신

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

필수 FFmpeg 설정:

- `app.ffmpeg.binary`
- `app.ffmpeg.probe_binary`

## 문서 관리 정책

PRD는 프로젝트의 Single Source Of Truth이다.

작업 완료 후 반드시 갱신:

- docs/yoko_catcut_requirements.md
- docs/ai_coding_prompt.md
- docs/changelog.md
- docs/roadmap.md

## v0.2.0 완료 기준

- [x] 지원 영상 확장자 검증
- [x] 스트리밍 업로드 및 최대 크기 제한
- [x] ffprobe 기반 실제 영상 검증
- [x] ffprobe 메타데이터 추출
- [x] Upload Repository 및 조회 API
- [x] Job 백그라운드 Processor 연결
- [x] Project와 Job 재시작 영속성
- [x] Job 상태 조회 UI
- [x] TypeScript 프로덕션 빌드
- [x] Docker Compose 통합 스모크 테스트

## 버전 정책

Semantic Versioning 적용.

예:

- v0.1.0
- v0.1.2
- v0.2.0
- v1.0.0
