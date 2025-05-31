# Notion MCP Server

Cursor와 Claude에서 사용할 수 있는 **Model Context Protocol (MCP)** 서버입니다. 이 서버를 통해 AI 어시스턴트가 Notion API와 상호작용하여 페이지 읽기, 쓰기, 데이터베이스 조회 등의 작업을 수행할 수 있습니다.

## 🚀 주요 기능

### Notion 관련 기능

- **페이지 검색**: Notion에서 페이지나 데이터베이스 검색
- **페이지 읽기**: 페이지 내용과 메타데이터 조회
- **페이지 생성**: 새로운 페이지 생성 (마크다운 지원)
- **페이지 업데이트**: 기존 페이지 내용 수정 및 추가
- **데이터베이스 쿼리**: 데이터베이스 항목 조회 및 필터링
- **데이터베이스 항목 생성**: 새로운 데이터베이스 항목 추가

### 유튜브 쇼츠 대본 생성 기능

- **대본 파일 생성**: 키워드와 AI 생성 대본을 받아서 마크다운 파일로 저장
- **대본 목록 조회**: 생성된 모든 대본 파일 목록 확인
- **대본 내용 읽기**: 특정 대본 파일의 내용 조회
- **대본 파일 삭제**: 불필요한 대본 파일 삭제

## 📋 사전 요구사항

1. **Python 3.8+**
2. **Notion API 토큰** ([Notion 통합 페이지](https://www.notion.so/my-integrations)에서 생성)
3. **MCP 클라이언트** (Cursor, Claude Desktop 등)

## 🛠️ 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 Notion API 토큰을 설정합니다:

```bash
cp env.example .env
```

`.env` 파일을 편집하여 실제 토큰을 입력합니다:

```env
NOTION_TOKEN=your_actual_notion_integration_token_here
LOG_LEVEL=INFO
```

### 3. Notion 통합 설정

1. [Notion 통합 페이지](https://www.notion.so/my-integrations)에서 새로운 통합을 생성합니다
2. 생성된 **Internal Integration Token**을 복사합니다
3. 사용하려는 Notion 페이지나 데이터베이스에 통합을 연결합니다:
   - 페이지 우상단 `...` → `연결` → 생성한 통합 선택

## 🔧 MCP 클라이언트 설정

### Cursor 설정

Cursor의 설정 파일에 다음을 추가합니다:

```json
{
  "mcpServers": {
    "notion": {
      "command": "/path/to/your/notion-mcp-server/venv/bin/python",
      "args": ["/path/to/your/notion-mcp-server/src/notion_mcp_server.py"],
      "env": {
        "NOTION_TOKEN": "your_notion_token_here"
      }
    }
  }
}
```

### Claude Desktop 설정

Claude Desktop의 설정 파일 (`~/Library/Application Support/Claude/claude_desktop_config.json`)에 추가:

```json
{
  "mcpServers": {
    "notion": {
      "command": "/path/to/your/notion-mcp-server/venv/bin/python",
      "args": ["/path/to/your/notion-mcp-server/src/notion_mcp_server.py"],
      "env": {
        "NOTION_TOKEN": "your_notion_token_here"
      }
    }
  }
}
```

## 🎯 사용법

MCP 서버가 설정되면 Cursor나 Claude에서 다음과 같은 요청을 할 수 있습니다:

### Notion 관련 예시 명령어

1. **페이지 검색**:

   ```
   "프로젝트 관리"라는 제목의 페이지를 찾아줘
   ```

2. **페이지 내용 읽기**:

   ```
   페이지 ID abc123의 내용을 읽어줘
   ```

3. **새 페이지 생성**:

   ```
   "회의 노트"라는 제목으로 새 페이지를 만들어줘. 내용은 "오늘의 회의 내용을 정리합니다"로 해줘
   ```

4. **페이지 업데이트**:

   ```
   페이지 ID xyz789에 "추가 내용: 다음 회의는 내일 오후 2시"라는 내용을 추가해줘
   ```

5. **데이터베이스 조회**:
   ```
   데이터베이스 ID def456의 모든 항목을 조회해줘
   ```

### 유튜브 쇼츠 대본 생성 예시 명령어

1. **대본 생성**:

   ```
   "AI 기술 트렌드"라는 키워드로 유튜브 쇼츠 대본을 생성해줘.
   대본 내용: "안녕하세요! 오늘은 2024년 가장 핫한 AI 기술 트렌드를 소개해드릴게요..."
   ```

2. **대본 목록 조회**:

   ```
   생성된 유튜브 쇼츠 대본 파일 목록을 보여줘
   ```

3. **대본 내용 읽기**:

   ```
   youtube_shorts_AI_기술_트렌드_20241201_143022.md 파일의 내용을 읽어줘
   ```

4. **대본 파일 삭제**:
   ```
   youtube_shorts_AI_기술_트렌드_20241201_143022.md 파일을 삭제해줘
   ```

## 🔧 사용 가능한 도구

### Notion 관련 도구

| 도구 이름               | 설명                      | 필수 매개변수               |
| ----------------------- | ------------------------- | --------------------------- |
| `search_notion`         | Notion에서 페이지/DB 검색 | `query`                     |
| `get_page`              | 페이지 정보 조회          | `page_id`                   |
| `get_page_content`      | 페이지 내용 조회          | `page_id`                   |
| `create_page`           | 새 페이지 생성            | `parent_id`, `title`        |
| `update_page`           | 페이지 업데이트           | `page_id`                   |
| `query_database`        | 데이터베이스 쿼리         | `database_id`               |
| `create_database_entry` | DB 항목 생성              | `database_id`, `properties` |

### 유튜브 쇼츠 대본 관련 도구

| 도구 이름               | 설명                       | 필수 매개변수               |
| ----------------------- | -------------------------- | --------------------------- |
| `create_youtube_script` | 유튜브 쇼츠 대본 파일 생성 | `keyword`, `script_content` |
| `list_youtube_scripts`  | 대본 파일 목록 조회        | 없음                        |
| `get_youtube_script`    | 대본 파일 내용 읽기        | `filename`                  |
| `delete_youtube_script` | 대본 파일 삭제             | `filename`                  |

## 📁 파일 구조

```
notion-mcp/
├── src/
│   ├── mcp_server.py           # MCP 서버 메인 파일
│   ├── notion_service.py       # Notion API 서비스
│   ├── youtube_script_service.py # 유튜브 쇼츠 대본 서비스
│   └── __init__.py
├── scripts/                    # 생성된 대본 파일들이 저장되는 디렉토리
├── requirements.txt
├── .env.example
└── README.md
```

### 생성되는 대본 파일 형식

유튜브 쇼츠 대본 파일은 다음과 같은 구조로 생성됩니다:

```markdown
# 유튜브 쇼츠 대본

## 메타데이터

- **키워드**: AI 기술 트렌드
- **생성일시**: 2024년 12월 01일 14:30:22
- **대본 길이**: 약 150자

---

## 대본 내용

안녕하세요! 오늘은 2024년 가장 핫한 AI 기술 트렌드를 소개해드릴게요...

---

## 제작 가이드라인

### 📱 유튜브 쇼츠 최적화 팁

- **길이**: 15-60초 (권장: 30초 이내)
- **화면비**: 9:16 (세로형)
- **해상도**: 1080x1920px 이상
- **첫 3초**: 시청자의 관심을 끌 수 있는 강력한 훅 필요

### 🎬 촬영 및 편집 포인트

- 빠른 컷과 전환으로 시청자의 집중력 유지
- 자막 추가로 접근성 향상
- 트렌딩 음악이나 효과음 활용
- 명확한 CTA(Call to Action) 포함

### 📊 성과 측정

- 조회수, 좋아요, 댓글, 공유 수 모니터링
- 시청 유지율 분석
- 구독자 전환율 확인
```
