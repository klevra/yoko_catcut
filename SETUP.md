# 🎯 Yoko CatCut - 초기 설정 가이드

## 📋 체크리스트

초기 실행 전에 다음을 확인하세요:

- [ ] Docker Desktop 설치 및 실행 중
- [ ] Git 설치 확인
- [ ] 웹 브라우저 설치 (Chrome/Edge/Safari)
- [ ] 디스크 공간 20GB 이상 확보

---

## 1️⃣ macOS 초기 설정 (첫 실행)

### 1.1 보안 경고 우회

`start.command` 파일을 처음 실행할 때 다음 메시지가 나타날 수 있습니다:

```
"start.command"은(는) 식별할 수 없는 개발자가 만들었기 때문에
열 수 없습니다.
```

**해결 방법:**

1. **방법 A (권장)** - 우클릭으로 열기
   ```
   start.command 파일 우클릭
   → "열기" 선택
   → 보안 경고 창에서 "열기" 클릭
   ```

2. **방법 B** - 시스템 설정에서 허용
   ```
   시스템 설정 → 개인정보 보보 및 보안
   → "start.command"이(가) 차단되었습니다 항목에서 "열기" 클릭
   ```

3. **방법 C** - 터미널에서 실행
   ```bash
   cd ~/Documents/yoko_catcut
   chmod +x start.command
   ./start.command
   ```

### 1.2 Docker Desktop 권한 요청

**처음 실행 시:**
```
Docker에 시스템 암호가 필요합니다.
sudo 사용 권한을 위해 암호를 입력하세요.
```

→ Mac 로그인 암호 입력 후 Enter

---

## 2️⃣ 첫 실행 (모든 OS)

### 2.1 GUI 실행

**macOS:**
```
Finder → yoko_catcut → start.command 더블클릭
```

**Windows (PowerShell):**
```powershell
cd C:\Users\[사용자명]\Documents\yoko_catcut
.\start.command
```

### 2.2 첫 실행 시 소요 시간

| 단계 | 시간 | 설명 |
|------|------|------|
| 이미지 빌드 | 5-10분 | Docker 이미지 다운로드 및 빌드 |
| 컨테이너 시작 | 1-2분 | 백엔드/프론트엔드 서버 시작 |
| **총 소요 시간** | **6-12분** | 첫 실행만 오래 걸림 |

이후 실행은 **30초 정도**만 소요됩니다.

### 2.3 브라우저 자동 실행

정상 실행 시 자동으로 브라우저가 열립니다:

```
http://localhost:3000
```

열리지 않으면 수동으로 열기:
1. 웹 브라우저 실행
2. 주소창에 `http://localhost:3000` 입력
3. Enter 키 누르기

---

## 3️⃣ Dock에 추가하기 (macOS)

편의상 Dock에 추가할 수 있습니다:

### 방법 A: 직접 추가 (권장)

1. Finder에서 `yoko_catcut` 폴더 열기
2. `start.command` 파일 마우스로 잡기
3. Dock으로 드래그
4. 마우스 놓기

이제 Dock의 아이콘을 클릭해서 실행 가능!

### 방법 B: 자동 추가 스크립트

```bash
cd ~/Documents/yoko_catcut
./add-to-dock.command
```

---

## 4️⃣ 첫 프로젝트 생성

### 4.1 웹 인터페이스 접속

```
http://localhost:3000
```

### 4.2 프로젝트 만들기

```
왼쪽 패널 "New Project"
├─ Project name 입력: "My First Project"
└─ "Create Project" 버튼 클릭
```

### 4.3 완료!

오른쪽에 프로젝트 카드가 생성됩니다.

---

## 5️⃣ 중지하기

### GUI로 중지

```
Finder → yoko_catcut → stop.command 더블클릭
```

### 터미널로 중지

```bash
cd ~/Documents/yoko_catcut
docker compose down
```

또는 Ctrl+C (터미널에서 실행 중인 경우)

---

## 🚨 문제 해결

### 문제: "Docker not found"

**원인:** Docker Desktop이 설치되지 않음

**해결:**
1. https://www.docker.com/products/docker-desktop 방문
2. 운영체제에 맞는 버전 다운로드
3. 설치 후 Docker 애플리케이션 실행
4. 메뉴바에 Docker 아이콘이 표시될 때까지 대기

### 문제: 포트 충돌 (Port 3000 already in use)

**원인:** 다른 앱이 포트 3000을 사용 중

**해결책:**

```bash
# 포트 사용 프로세스 확인
lsof -i :3000

# 프로세스 강제 종료 (macOS/Linux)
kill -9 <PID>

# 또는 다른 포트 사용 (application.yml 수정)
# frontend_port를 3001로 변경
```

### 문제: 느린 성능

**원인:** Docker 메모리 부족

**해결:**
1. Docker Desktop 설정 열기
2. Preferences → Resources
3. Memory: 최소 4GB 이상 설정
4. Docker 재시작

### 문제: 브라우저가 열리지 않음

**수동 실행:**
1. 웹 브라우저 수동으로 열기
2. 주소: `http://localhost:3000` 입력
3. Enter 키 누르기

---

## 📚 다음 단계

### 자세한 사용법

[manual.txt](manual.txt) 참조:
- 전체 기능 설명
- 고급 설정
- 명령어 레퍼런스

### 개발 모드 (개발자용)

```bash
# 백엔드 개발 모드
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 프론트엔드 개발 모드
cd frontend
npm install
npm run dev
```

### API 문서

```
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
```

---

## 🎓 팁과 트릭

### 팁 1: 터미널에서 logs 실시간 보기

```bash
cd ~/Documents/yoko_catcut
docker compose logs -f
```

### 팁 2: 특정 서버만 재시작

```bash
# 백엔드만 재시작
docker compose restart backend

# 프론트엔드만 재시작
docker compose restart frontend
```

### 팁 3: 컨테이너 내부 접속 (디버깅)

```bash
# 백엔드 컨테이너 셸 접속
docker compose exec backend bash

# 프론트엔드 컨테이너 셸 접속
docker compose exec frontend sh
```

### 팁 4: 데이터 백업

```bash
# workspace 폴더 백업
cp -r workspace ~/Documents/yoko_catcut_backup
```

---

## ✅ 설정 완료!

이제 Yoko CatCut을 사용할 준비가 되었습니다!

### 다음:
1. `start.command` 더블클릭으로 시작
2. 브라우저에서 http://localhost:3000 접속
3. 첫 프로젝트 생성해보기

---

## 📞 지원

- 📖 문서: [manual.txt](manual.txt)
- 🐛 버그 보고: https://github.com/klevra/yoko_catcut/issues
- 📧 피드백: GitHub Issues에서 질문

---

**Happy Editing! 🎬**
