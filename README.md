# Notion MCP Server

Cursor와 Claude에서 사용할 수 있는 **Model Context Protocol (MCP)** 서버입니다. 이 서버를 통해 AI 어시스턴트가 Notion API와 상호작용하여 페이지 읽기, 쓰기, 데이터베이스 조회 등의 작업을 수행할 수 있습니다.

## 🚀 주요 기능

- **페이지 검색**: Notion에서 페이지나 데이터베이스 검색
- **페이지 읽기**: 페이지 내용과 메타데이터 조회
- **페이지 생성**: 새로운 페이지 생성 (마크다운 지원)
- **페이지 업데이트**: 기존 페이지 내용 수정 및 추가
- **데이터베이스 쿼리**: 데이터베이스 항목 조회 및 필터링
- **데이터베이스 항목 생성**: 새로운 데이터베이스 항목 추가

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
      "command": "python",
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
      "command": "python",
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

### 예시 명령어

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

## 🔧 사용 가능한 도구

| 도구 이름               | 설명                      | 필수 매개변수               |
| ----------------------- | ------------------------- | --------------------------- |
| `search_notion`         | Notion에서 페이지/DB 검색 | `query`                     |
| `get_page`              | 페이지 정보 조회          | `page_id`                   |
| `get_page_content`      | 페이지 내용 조회          | `page_id`                   |
| `create_page`           | 새 페이지 생성            | `parent_id`, `title`        |
| `update_page`           | 페이지 업데이트           | `page_id`                   |
| `query_database`        | 데이터베이스 쿼리         | `database_id`               |
| `create_database_entry` | DB 항목 생성              | `database_id`, `properties` |

## 🐛 문제 해결

### 일반적인 오류

1. **"NOTION_TOKEN 환경 변수가 설정되지 않았습니다"**

   - `.env` 파일에 올바른 토큰이 설정되어 있는지 확인

2. **"권한이 없습니다" 오류**

   - Notion 통합이 해당 페이지/데이터베이스에 연결되어 있는지 확인

3. **"페이지를 찾을 수 없습니다" 오류**
   - 페이지 ID가 올바른지 확인
   - 페이지가 삭제되지 않았는지 확인

### 로그 확인

로그 레벨을 `DEBUG`로 설정하여 자세한 정보를 확인할 수 있습니다:

```env
LOG_LEVEL=DEBUG
```

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🔗 관련 링크

- [Notion API 문서](https://developers.notion.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Cursor 문서](https://cursor.sh/)
- [Claude Desktop](https://claude.ai/)
