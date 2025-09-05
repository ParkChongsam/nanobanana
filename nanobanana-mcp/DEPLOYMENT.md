# 🚀 Nanobanana MCP Server 배포 가이드

## 빠른 설치 (Windows)

```bash
# 1. 저장소 클론
git clone https://github.com/ParkChongsam/nanobanana-mcp.git
cd nanobanana-mcp

# 2. 설치 스크립트 실행
install.bat

# 3. 환경 설정
cp .env.example .env
# .env 파일 편집하여 API 키 설정

# 4. 서버 실행
run_server.bat
```

## 수동 설치

### 1. 환경 준비
```bash
# Python 3.8+ 필요
python --version

# 가상환경 생성
python -m venv nanobanana_env

# Windows 활성화
nanobanana_env\Scripts\activate

# Linux/Mac 활성화
source nanobanana_env/bin/activate
```

### 2. 의존성 설치
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 파일 생성:
```bash
# Vertex AI 사용 (권장)
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global

# 또는 Gemini API 사용
GEMINI_API_KEY=your-api-key
```

## Claude Desktop 연동

`claude_desktop_config.json` 파일에 추가:

```json
{
  "mcpServers": {
    "nanobanana": {
      "command": "python",
      "args": ["D:/nanobananamcp/nanobanana-mcp/src/server.py"],
      "env": {
        "GOOGLE_GENAI_USE_VERTEXAI": "True",
        "GOOGLE_CLOUD_PROJECT": "your-project-id"
      }
    }
  }
}
```

## Docker 배포

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV GOOGLE_GENAI_USE_VERTEXAI=True
EXPOSE 8000

CMD ["python", "src/server.py"]
```

## 검증 테스트

```bash
# 테스트 실행
pytest tests/

# MCP 서버 테스트
python src/server.py --test
```

## 트러블슈팅

### 1. 인증 오류
- Google Cloud 인증 확인: `gcloud auth list`
- API 키 유효성 확인
- 프로젝트 권한 확인

### 2. 의존성 오류
```bash
# 의존성 재설치
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### 3. 이미지 저장 오류
- `images/` 디렉터리 권한 확인
- 디스크 공간 확인

## 성능 최적화

- 이미지 캐싱 활용
- 동시 요청 수 제한
- 로그 레벨 조정 (`LOG_LEVEL=ERROR`)

## 모니터링

서버 상태 확인:
```bash
# 로그 확인
tail -f nanobanana.log

# 프로세스 확인
ps aux | grep nanobanana
```