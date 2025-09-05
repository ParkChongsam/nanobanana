# 🍌 Nanobanana MCP Server

Claude Code용 Gemini 2.5 Flash Image (nanobanana) MCP 서버입니다.

## 기능

- ✨ **텍스트→이미지 생성**: 자연어 프롬프트로 고품질 이미지 생성
- 🎨 **이미지 편집**: 기존 이미지를 자연어로 편집 및 변환
- 🌍 **다국어 지원**: 한국어→영어 자동 번역
- 🔒 **안전 필터**: Google의 안전성 정책 준수
- 💧 **워터마크**: SynthID 자동 삽입으로 AI 생성 이미지 표시

## 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 API 키 설정
```

## 설정

### Gemini API 사용 (간단 설정 - 권장)
```bash
# .env 파일에서 API 키 설정
GOOGLE_GENAI_USE_VERTEXAI=False
GEMINI_API_KEY=your-gemini-api-key
```

**API 키 발급**: [Google AI Studio](https://aistudio.google.com/)에서 "Get API key" 클릭
상세 가이드: [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) 참조

### Vertex AI 사용 (고급 설정)
```bash
# .env 파일에서 설정
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
```

## 사용법

### MCP 서버 시작
```bash
python src/server.py
```

### Claude Desktop 연동
`claude_desktop_config.json`에 추가:

**Gemini API 사용 시**:
```json
{
  "mcpServers": {
    "nanobanana": {
      "command": "python",
      "args": ["D:/nanobananamcp/nanobanana-mcp/src/server.py"],
      "env": {
        "GOOGLE_GENAI_USE_VERTEXAI": "False",
        "GEMINI_API_KEY": "your-actual-api-key"
      }
    }
  }
}
```

**Vertex AI 사용 시**:
```json
{
  "mcpServers": {
    "nanobanana": {
      "command": "python", 
      "args": ["D:/nanobananamcp/nanobanana-mcp/src/server.py"],
      "env": {
        "GOOGLE_GENAI_USE_VERTEXAI": "True",
        "GOOGLE_CLOUD_PROJECT": "your-project"
      }
    }
  }
}
```

## MCP 툴

### nanobanana_generate
텍스트 프롬프트로 이미지 생성

**매개변수:**
- `prompt` (필수): 이미지 생성을 위한 텍스트 설명
- `style` (선택): 이미지 스타일 (photo, illustration, art 등)
- `quality` (선택): 품질 설정 (high, medium, low)

### nanobanana_edit  
기존 이미지를 편집/변환

**매개변수:**
- `image_path` (필수): 편집할 이미지 파일 경로
- `instruction` (필수): 편집 지시사항
- `style` (선택): 변환할 스타일

## 제한사항

- 이미지 단독 출력 불가 (항상 텍스트와 함께 반환)
- SynthID 워터마크 자동 삽입 (제거 불가)
- 이미지당 약 1290 토큰 소모
- 안전 필터로 부적절한 콘텐츠 차단

## 라이선스

MIT License