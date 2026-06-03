# Yoko CatCut

AI 기반 영상 편집 웹 플랫폼.

## 프로젝트 정보

- Repository: https://github.com/klevra/yoko_catcut
- 개발 경로: `/Users/klevra/Documents/catcut/yoko_catcut`
- Architecture: Web First
- Backend: FastAPI
- Frontend: React + TypeScript + Vite
- AI: pycatcut, ffmpeg, Whisper/Faster-Whisper

## 실행

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
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

## 문서

- `docs/yoko_catcut_requirements.md`
- `docs/ai_coding_prompt.md`
- `docs/roadmap.md`
- `docs/changelog.md`
