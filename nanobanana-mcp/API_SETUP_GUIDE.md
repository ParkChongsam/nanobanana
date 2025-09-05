# 🔑 Google Gemini API 키 설정 가이드

## Gemini API 키 발급받기

### 1. Google AI Studio 접속
1. [Google AI Studio](https://aistudio.google.com/) 접속
2. Google 계정으로 로그인

### 2. API 키 생성
1. 우측 상단의 "Get API key" 클릭
2. "Create API key" 선택  
3. 새 프로젝트 생성 또는 기존 프로젝트 선택
4. API 키가 생성되면 **반드시 복사해서 안전한 곳에 저장**

⚠️ **중요**: API 키는 한 번만 표시되므로 반드시 복사해두세요!

### 3. API 활성화 확인
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 해당 프로젝트 선택
3. "APIs & Services" > "Library" 이동
4. "Generative Language API" 검색하여 활성화

## 환경 설정

### 1. .env 파일 생성
```bash
# .env.example을 .env로 복사
copy .env.example .env
```

### 2. API 키 입력
`.env` 파일을 편집하여 다음과 같이 설정:

```bash
# Google AI 설정
GOOGLE_GENAI_USE_VERTEXAI=False
GEMINI_API_KEY=your-actual-api-key-here

# 모델 설정  
GEMINI_MODEL=gemini-2.5-flash-image-preview

# 기타 설정은 기본값 사용
AUTO_TRANSLATE=True
DEFAULT_LANGUAGE=ko
```

### 3. 설정 확인
```bash
# 서버 실행해서 확인
python src/server.py
```

로그에서 다음 메시지 확인:
```
Using Gemini API with direct API key
Initialized Gemini client with model: gemini-2.5-flash-image-preview
```

## Claude Desktop 연동

`claude_desktop_config.json`에 추가:

```json
{
  "mcpServers": {
    "nanobanana": {
      "command": "python",
      "args": ["D:/nanobananamcp/nanobanana-mcp/src/server.py"],
      "env": {
        "GOOGLE_GENAI_USE_VERTEXAI": "False",
        "GEMINI_API_KEY": "your-actual-api-key-here"
      }
    }
  }
}
```

## 비용 및 할당량

### API 사용 요금
- **무료 할당량**: 분당 15회 요청, 일일 1,500회
- **유료**: 이미지 생성 시 약 1,290 토큰 소모
- **요금**: $0.00003 per token (약 $0.04 per image)

### 할당량 모니터링
1. [Google Cloud Console](https://console.cloud.google.com/)
2. "APIs & Services" > "Quotas"
3. "Generative Language API" 확인

## 트러블슈팅

### 1. API 키 인증 오류
```
Error: Invalid API key
```
**해결책**: 
- API 키 정확성 재확인
- 프로젝트에서 Generative Language API 활성화 확인

### 2. 할당량 초과
```
Error: Quota exceeded
```
**해결책**:
- 요청 간격 조정
- 유료 플랜 고려
- 다른 Google 계정 사용

### 3. 모델 접근 불가
```
Error: Model not found
```
**해결책**:
- 모델명 확인: `gemini-2.5-flash-image-preview`
- API 버전 확인
- 지역 제한 확인

## 보안 주의사항

🚨 **API 키 보안**:
- `.env` 파일을 Git에 커밋하지 마세요
- API 키를 코드에 하드코딩하지 마세요  
- 정기적으로 API 키 교체하세요
- 불필요한 권한 제거하세요

## 대안: Vertex AI 사용

더 안전하고 확장 가능한 방식:

```bash
# .env 파일에서
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global

# Google Cloud SDK 인증
gcloud auth application-default login
```