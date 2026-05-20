# Adobe Stock & Freepik Automator

AI 스톡 이미지 자동 생성, 최적화 및 멀티플랫폼 게시 도구입니다. Codex CLI(ChatGPT 구독) 또는 OpenAI/Stability/Replicate 등 여러 이미지 생성 엔진을 지원하며, Adobe Stock 및 Freepik 사양에 맞는 이미지와 메타데이터를 자동으로 생성하고 FTPS 또는 CloakBrowser 자동 웹 업로드를 통해 게시합니다.

## 파이프라인

```
프롬프트 ──> AI 생성 ──> 6MP 업스케일 ──> 메타데이터 CSV (Adobe / Freepik) ──> 웹/FTP/FTPS 자동 업로드
```

## 기능

*   **멀티플랫폼 CSV 지원**:
    *   **Adobe Stock**: 쉼표로 구분된 CSV 출력, 카테고리 이름을 Adobe Stock 지정 숫자 ID로 자동 변환.
    *   **Freepik**: 세미콜론(`;`)으로 구분된 CSV 출력 (필드: `File name;Title;Keywords;Prompt;Model`). AI 생성 콘텐츠는 키워드 끝에 `_ai_generated`가 자동으로 추가되며, 제목 길이는 오류 방지를 위해 100자로 자동 제한됩니다.
*   **자동 해상도 최적화 (업스케일)**: 이미지 해상도를 자동 감지하여 6MP 미만일 경우 Lanczos 필터를 사용해 6MP+(3000x2000)로 무손실 확대하여 스톡 플랫폼 심사를 100% 통과합니다.
*   **강력한 웹 자동 업로드 (CloakBrowser)**: Stealth Chromium을 사용해 Cloudflare 봇 방지 메커니즘을 우회하며, 수동/쿠키 로그인 유지, 드래그 앤 드롭 이미지 업로드를 지원하고 전용 `metadata_freepik.csv` 원클릭 가져오기로 일괄 적용을 안내합니다.
*   **안전한 FTPS 연결**: Freepik 레벨 3 이상 계정의 FTPS(Explicit TLS) 대량 고속 업로드를 지원합니다.

## 빠른 시작

```bash
# 의존성 설치
pip install -r requirements.txt

# 설정 파일 초기화
cp config.example.yaml config.yaml
# config.yaml에 스톡 계정 자격 증명 또는 API 키 입력

# 이미지 생성 테스트 (API 키 불필요한 더미 모드, Adobe와 Freepik 정보 모두 생성)
python3 main.py generate "neon retro synthwave sunset" -n 1 -p dummy --freepik

# output 디렉토리의 모든 기존 JPEG 이미지 업로드 (Freepik 웹 업로드 예시)
python3 main.py upload --platform freepik
```

## CLI 명령어

| 명령어 | 설명 |
|--------|------|
| `generate` | AI 생성 → 6MP 업스케일 → CSV 생성 → 웹 업로드 (`--freepik` 사용 시 Freepik 출력도 함께 생성) |
| `upload` | CloakBrowser를 사용해 output 디렉토리의 모든 기존 이미지 업로드 (adobe-stock, freepik 지원) |
| `cloak` | CloakBrowser 통합 "생성 + 웹 자동 업로드" 워크플로우 |
| `portal_upload` | Adobe Stock Portal 전용 업로드 모듈 |
| `batch` | 프롬프트 파일 일괄 처리 |
| `requirements` | 각 스톡 플랫폼 이미지 사양 표시 |

### 일괄 생성 (50장)

```bash
bash run_50.sh
```

`dashboard/scripts/codex-gen-wrapper.sh`를 사용해 Codex CLI 병렬 생성 실행. 배치당 10장, 약 3-5분 안에 50장 완료.
생성 후 `./gen_metadata.py`를 실행하여 모든 CSV를 재생성 및 업데이트합니다.

## 프로젝트 구조

```
adobe-stock-automator/
├── main.py                     # CLI 진입점 (Click)
├── src/
│   ├── config.py               # YAML 설정 로드 및 환경 변수 오버라이드
│   ├── generate.py             # 이미지 생성 (dummy/openai/stability/replicate/local)
│   ├── image_utils.py          # 이미지 해상도 감지 및 6MP+ Lanczos 최적화
│   ├── metadata.py             # 메타데이터 생성 및 Adobe/Freepik 이중 CSV 형식 출력
│   ├── upload.py               # FTP / FTPS (Explicit TLS) 업로드 로직
│   ├── submit_browser.py       # Playwright 브라우저 자동화
│   ├── portal_upload.py        # Adobe Portal 전용 업로드
│   └── upload_cloak.py         # CloakBrowser Stealth 업로드 (Adobe Stock / Freepik)
├── config.example.yaml
├── prompts_50.txt              # 50개 상용 프롬프트 템플릿
├── gen_metadata.py             # 이미지 일괄 최적화 및 메타데이터 재생성 도구
├── run_50.sh                   # 50장 일괄 생성 및 최적화 스크립트
├── README.md                   # 원본 (번체 중국어)
├── README.en.md                # 영어
├── README.ja.md                # 일본어
├── README.ko.md                # 한국어
├── README.es.md                # 스페인어
└── README.fr.md                # 프랑스어
```

## 플랫폼 지원

| 플랫폼 | 웹 자동화 (CloakBrowser) | FTP / FTPS 업로드 | 비고 |
|--------|--------------------------|-------------------|------|
| **Adobe Stock** | ✅ 자동 필드 입력 및 AI 태그 | ❌ 공식 미지원 | 웹 모드 또는 CSV 가져오기 권장 |
| **Freepik** | ✅ 자동 드래그 앤 드롭 + CSV 원클릭 가져오기 | ✅ FTPS (Explicit TLS) 지원 | 레벨 3 미만은 웹 모드, 레벨 3 이상은 FTPS 사용 가능 |

## 개인정보 및 보안

- `config.yaml`에는 개인 자격 증명이 포함됩니다 → `.gitignore`에 추가됨
- 쿠키 캐시는 `.cookies/` → `.gitignore`에 추가됨
- 생성된 이미지는 `output/` → `.gitignore`에 추가됨

## 라이선스

MIT — Laban Chen
