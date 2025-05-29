#!/usr/bin/env python3
"""
Notion MCP Server 테스트
"""

import asyncio
import json
import os
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.mcp_server import NotionMCPServer


class TestNotionMCPServer:
    """NotionMCPServer 테스트 클래스"""
    
    @pytest.fixture
    def mock_notion_token(self):
        """Notion 토큰 모킹"""
        with patch.dict(os.environ, {"NOTION_TOKEN": "test_token"}):
            yield "test_token"
    
    @pytest.fixture
    def mock_notion_client(self):
        """Notion 클라이언트 모킹"""
        with patch("src.notion_mcp_server.Client") as mock_client:
            yield mock_client.return_value
    
    @pytest.fixture
    def server(self, mock_notion_token, mock_notion_client):
        """테스트용 서버 인스턴스"""
        return NotionMCPServer()
    
    def test_server_initialization(self, server, mock_notion_client):
        """서버 초기화 테스트"""
        assert server.notion_token == "test_token"
        assert server.notion == mock_notion_client
        assert server.server.name == "notion-mcp-server"
    
    def test_server_initialization_without_token(self):
        """토큰 없이 서버 초기화 시 오류 테스트"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="NOTION_TOKEN 환경 변수가 설정되지 않았습니다"):
                NotionMCPServer()
    
    def test_extract_title_from_page(self, server):
        """페이지에서 제목 추출 테스트"""
        page_data = {
            "properties": {
                "title": {
                    "type": "title",
                    "title": [
                        {"plain_text": "테스트 페이지"}
                    ]
                }
            }
        }
        
        title = server._extract_title(page_data)
        assert title == "테스트 페이지"
    
    def test_extract_title_from_database(self, server):
        """데이터베이스에서 제목 추출 테스트"""
        db_data = {
            "title": [
                {"plain_text": "테스트 데이터베이스"}
            ]
        }
        
        title = server._extract_title(db_data)
        assert title == "테스트 데이터베이스"
    
    def test_extract_title_no_title(self, server):
        """제목이 없는 경우 테스트"""
        empty_data = {}
        
        title = server._extract_title(empty_data)
        assert title == "제목 없음"
    
    def test_rich_text_to_plain_text(self, server):
        """리치 텍스트를 일반 텍스트로 변환 테스트"""
        rich_text = [
            {"plain_text": "안녕하세요 "},
            {"plain_text": "세상!"}
        ]
        
        plain_text = server._rich_text_to_plain_text(rich_text)
        assert plain_text == "안녕하세요 세상!"
    
    def test_text_to_blocks_paragraph(self, server):
        """텍스트를 블록으로 변환 테스트 - 문단"""
        text = "이것은 테스트 문단입니다."
        
        blocks = server._text_to_blocks(text)
        
        assert len(blocks) == 1
        assert blocks[0]["type"] == "paragraph"
        assert blocks[0]["paragraph"]["rich_text"][0]["text"]["content"] == text
    
    def test_text_to_blocks_heading(self, server):
        """텍스트를 블록으로 변환 테스트 - 제목"""
        text = "# 제목 1\n## 제목 2\n### 제목 3"
        
        blocks = server._text_to_blocks(text)
        
        assert len(blocks) == 3
        assert blocks[0]["type"] == "heading_1"
        assert blocks[0]["heading_1"]["rich_text"][0]["text"]["content"] == "제목 1"
        assert blocks[1]["type"] == "heading_2"
        assert blocks[1]["heading_2"]["rich_text"][0]["text"]["content"] == "제목 2"
        assert blocks[2]["type"] == "heading_3"
        assert blocks[2]["heading_3"]["rich_text"][0]["text"]["content"] == "제목 3"
    
    def test_text_to_blocks_list(self, server):
        """텍스트를 블록으로 변환 테스트 - 리스트"""
        text = "- 첫 번째 항목\n- 두 번째 항목"
        
        blocks = server._text_to_blocks(text)
        
        assert len(blocks) == 2
        assert blocks[0]["type"] == "bulleted_list_item"
        assert blocks[0]["bulleted_list_item"]["rich_text"][0]["text"]["content"] == "첫 번째 항목"
        assert blocks[1]["type"] == "bulleted_list_item"
        assert blocks[1]["bulleted_list_item"]["rich_text"][0]["text"]["content"] == "두 번째 항목"
    
    def test_blocks_to_text_paragraph(self, server):
        """블록을 텍스트로 변환 테스트 - 문단"""
        blocks = [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "테스트 문단입니다."}]
                }
            }
        ]
        
        text = server._blocks_to_text(blocks)
        assert text == "테스트 문단입니다."
    
    def test_blocks_to_text_heading(self, server):
        """블록을 텍스트로 변환 테스트 - 제목"""
        blocks = [
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"plain_text": "제목 1"}]
                }
            },
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"plain_text": "제목 2"}]
                }
            }
        ]
        
        text = server._blocks_to_text(blocks)
        assert text == "# 제목 1\n\n## 제목 2"
    
    @pytest.mark.asyncio
    async def test_search_notion(self, server, mock_notion_client):
        """Notion 검색 테스트"""
        # Mock 검색 결과
        mock_notion_client.search.return_value = {
            "results": [
                {
                    "object": "page",
                    "id": "test-page-id",
                    "url": "https://notion.so/test-page",
                    "properties": {
                        "title": {
                            "type": "title",
                            "title": [{"plain_text": "테스트 페이지"}]
                        }
                    }
                }
            ]
        }
        
        arguments = {"query": "테스트"}
        result = await server._search_notion(arguments)
        
        assert not result.isError
        assert "검색 결과 (1개)" in result.content[0].text
        
        # 검색 호출 확인
        mock_notion_client.search.assert_called_once_with(query="테스트")
    
    @pytest.mark.asyncio
    async def test_get_page(self, server, mock_notion_client):
        """페이지 조회 테스트"""
        # Mock 페이지 데이터
        mock_notion_client.pages.retrieve.return_value = {
            "id": "test-page-id",
            "url": "https://notion.so/test-page",
            "created_time": "2023-01-01T00:00:00.000Z",
            "last_edited_time": "2023-01-02T00:00:00.000Z",
            "properties": {
                "title": {
                    "type": "title",
                    "title": [{"plain_text": "테스트 페이지"}]
                }
            }
        }
        
        arguments = {"page_id": "test-page-id"}
        result = await server._get_page(arguments)
        
        assert not result.isError
        assert "페이지 정보:" in result.content[0].text
        
        # 페이지 조회 호출 확인
        mock_notion_client.pages.retrieve.assert_called_once_with("test-page-id")
    
    @pytest.mark.asyncio
    async def test_create_page(self, server, mock_notion_client):
        """페이지 생성 테스트"""
        # Mock 페이지 생성 결과
        mock_notion_client.pages.create.return_value = {
            "id": "new-page-id",
            "url": "https://notion.so/new-page"
        }
        
        arguments = {
            "parent_id": "parent-page-id",
            "title": "새 페이지",
            "content": "페이지 내용입니다."
        }
        result = await server._create_page(arguments)
        
        assert not result.isError
        assert "페이지가 성공적으로 생성되었습니다!" in result.content[0].text
        assert "new-page-id" in result.content[0].text
        
        # 페이지 생성 호출 확인
        mock_notion_client.pages.create.assert_called_once()
        # 블록 추가 호출 확인
        mock_notion_client.blocks.children.append.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__]) 