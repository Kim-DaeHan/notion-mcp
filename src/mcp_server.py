#!/usr/bin/env python3
"""
Notion MCP Server

Cursor와 Claude에서 사용할 수 있는 MCP 서버로, Notion API와 상호작용하여
페이지 읽기, 쓰기, 데이터베이스 조회 등의 기능을 제공합니다.
"""

import logging
import os

from mcp.server.fastmcp import FastMCP

from notion_service import NotionService

# 로깅 설정
logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
logger = logging.getLogger(__name__)

# Notion 서비스 초기화
try:
    notion_service = NotionService.create()
except ValueError as e:
    logger.error(f"Notion 서비스 초기화 실패: {e}")
    raise

# FastMCP 서버 생성
mcp = FastMCP("notion-mcp-server")


@mcp.tool()
def search_notion(query: str, filter_type: str = None) -> str:
    """Notion에서 페이지나 데이터베이스를 검색합니다

    Args:
        query: 검색할 텍스트
        filter_type: 검색할 객체 타입 (page 또는 database, 선택사항)
    """
    return notion_service.search(query, filter_type)


@mcp.tool()
def get_page(page_id: str) -> str:
    """Notion 페이지의 정보를 가져옵니다

    Args:
        page_id: 페이지 ID
    """
    return notion_service.get_page_info(page_id)


@mcp.tool()
def get_page_content(page_id: str) -> str:
    """Notion 페이지의 블록 내용을 가져옵니다

    Args:
        page_id: 페이지 ID
    """
    return notion_service.get_page_content(page_id)


@mcp.tool()
def create_page(parent_id: str, title: str, content: str = "") -> str:
    """새로운 Notion 페이지를 생성합니다

    Args:
        parent_id: 부모 페이지 또는 데이터베이스 ID
        title: 페이지 제목
        content: 페이지 내용 (마크다운 형식, 선택사항)
    """
    return notion_service.create_page(parent_id, title, content)


@mcp.tool()
def update_page(page_id: str, title: str = None, content: str = None) -> str:
    """기존 Notion 페이지를 업데이트합니다

    Args:
        page_id: 업데이트할 페이지 ID
        title: 새로운 제목 (선택사항)
        content: 추가할 내용 (마크다운 형식, 선택사항)
    """
    return notion_service.update_page(page_id, title, content)


@mcp.tool()
def query_database(
    database_id: str, filter_condition: dict = None, sorts: list = None
) -> str:
    """Notion 데이터베이스를 쿼리합니다

    Args:
        database_id: 데이터베이스 ID
        filter_condition: 필터 조건 (선택사항)
        sorts: 정렬 조건 (선택사항)
    """
    return notion_service.query_database(database_id, filter_condition, sorts)


@mcp.tool()
def create_database_entry(database_id: str, properties: dict) -> str:
    """데이터베이스에 새로운 항목을 생성합니다

    Args:
        database_id: 데이터베이스 ID
        properties: 항목 속성들
    """
    return notion_service.create_database_entry(database_id, properties)


if __name__ == "__main__":
    mcp.run()
