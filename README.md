# Yoko CatCut

AI 기반 영상 편집 웹 플랫폼.

## 🚀 빠른 시작 (Quick Start)

### GUI를 통한 실행 (권장)

**macOS:**
1. Finder에서 `yoko_catcut` 폴더 열기
2. `start.command` 파일 **더블클릭**
3. 자동으로 브라우저에서 http://localhost:3000 열림
4. 완료! ✅

**Windows:**
1. `yoko_catcut` 폴더에서 우클릭
2. "PowerShell 여기서 열기" 선택
3. `.\start.command` 입력

### 중지하기

`stop.command` 파일 **더블클릭** → 완료!

---

## 프로젝트 정보

- Repository: https://github.com/klevra/yoko_catcut
- 개발 경로: `/Users/klevra/Documents/yoko_catcut`
- Architecture: Web First (React + FastAPI)
- Backend: FastAPI
- Frontend: React + TypeScript + Vite
- AI: pycatcut, ffmpeg, Whisper/Faster-Whisper

---

## 📚 상세 문서

자세한 사용법은 [manual.txt](manual.txt) 참조:
- 시스템 요구사항
- 설치 방법
- 터미널 명령어
- 문제 해결
- 고급 설정

---

## 터미널 실행

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker Compose

```bash
docker compose up --build
```

---

## 🌐 액세스 주소

| 서비스 | URL | 설명 |
|--------|-----|------|
| 프론트엔드 | http://localhost:3000 | 웹 UI |
| 백엔드 API | http://localhost:8000 | REST API |
| Swagger Docs | http://localhost:8000/docs | API 문서 |
| ReDoc | http://localhost:8000/redoc | API 참조 |

---

## 📖 문서

- [yoko_catcut_requirements.md](docs/yoko_catcut_requirements.md) - 프로덕트 요구사항
- [ai_coding_prompt.md](docs/ai_coding_prompt.md) - AI 코딩 프롬프트
- [roadmap.md](docs/roadmap.md) - 개발 로드맵
- [changelog.md](docs/changelog.md) - 변경 기록
- [manual.txt](manual.txt) - 사용자 매뉴얼

---

## ✨ 주요 기능 (v0.5.0)

### 프로젝트 관리
- ✅ 프로젝트 생성/삭제
- ✅ Workspace 자동 생성
- ✅ 프로젝트 목록 조회
- ✅ 컨테이너 재시작 후 프로젝트 상태 복원

### 아키텍처
- ✅ Storage Adapter Pattern
- ✅ Repository Layer
- ✅ Service Layer
- ✅ REST API with Swagger

### 프론트엔드
- ✅ React Dashboard
- ✅ Project Management UI
- ✅ Responsive Design
- ✅ 영상 Drag & Drop 업로드
- ✅ Job 상태 및 영상 메타데이터 표시
- ✅ 업로드 영상 목록 및 편집 페이지
- ✅ 영상 재생, 구간 지정, 출력 비율 초안
- ✅ 다중 편집 구간 및 구간별 코멘트
- ✅ Faster-Whisper 자동 자막
- ✅ 영상 자막 오버레이 및 SRT/VTT/JSON 다운로드
- ✅ 자막 구간 반복, 시간/문구 수정 및 분할
- ✅ 다중 구간 MP4 렌더링 및 다운로드
- ✅ CapCut 호환 MP4/SRT 패키지
- ✅ 편집 도구 프리셋과 버전 Footer
- ✅ 자막 음성 구간 기반 무음 파트 제거
- ✅ 제외 구간 x2/x4/x8/x16 배속 연결
- ✅ 조립 작업부 중앙 확대 크롭
- ✅ 영상 옵션 재적용 및 초기화
- ✅ 음악 후보와 육성 구간 분류
- ✅ 음향 특징 기반 화자 군집화
- ✅ 화자별 대표 음성 미리듣기 및 선택
- ✅ 선택 화자 전용 자막 생성
- ✅ 파일 기반 계정/비밀번호 관리
- ✅ 계정별 프로젝트 격리
- ✅ 다른 PC/모바일 접속용 동적 API URL
- ✅ 배경음악 제거 및 추가 믹스 옵션

### 영상 업로드
- ✅ 청크 기반 스트리밍 저장
- ✅ mp4, mov, mkv, webm 검증
- ✅ ffprobe 기반 영상/오디오 메타데이터 분석
- ✅ Upload 및 Job 상태 영속화

---

## 🔄 다음 버전 (v0.4.0)

- [ ] Multi Upload
- [ ] 실시간 Upload Progress
- [ ] Scene Detection
- [ ] Highlight Viewer

---

## 🛠️ 개발 팀

Senior Software Architect, Lead Backend Engineer, Lead Frontend Engineer,  
AI Engineer, DevOps Engineer

---

## 📝 라이선스

MIT License - 자유롭게 사용 가능합니다.

---

## 🤝 지원

- Issues: https://github.com/klevra/yoko_catcut/issues
- Documentation: [manual.txt](manual.txt)
