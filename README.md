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

## ✨ 주요 기능 (v0.1.1)

### 프로젝트 관리
- ✅ 프로젝트 생성/삭제
- ✅ Workspace 자동 생성
- ✅ 프로젝트 목록 조회

### 아키텍처
- ✅ Storage Adapter Pattern
- ✅ Repository Layer
- ✅ Service Layer
- ✅ REST API with Swagger

### 프론트엔드
- ✅ React Dashboard
- ✅ Project Management UI
- ✅ Responsive Design

---

## 🔄 다음 버전 (v0.2.0)

- [ ] 파일 검증
- [ ] ffprobe 메타데이터 분석
- [ ] Upload 기능 활성화
- [ ] Job 상태 관리 개선

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
