#!/usr/bin/env python3
"""
Notion MCP Server

Cursor와 Claude에서 사용할 수 있는 MCP 서버로, Notion API와 상호작용하여
페이지 읽기, 쓰기, 데이터베이스 조회 등의 기능을 제공합니다.
"""

import json
import logging
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from notion_client import Client

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
logger = logging.getLogger(__name__)

# Notion 클라이언트 초기화
notion_token = os.getenv("NOTION_TOKEN")
if not notion_token:
    raise ValueError("NOTION_TOKEN 환경 변수가 설정되지 않았습니다.")

notion = Client(auth=notion_token)

# FastMCP 서버 생성
mcp = FastMCP("notion-mcp-server")


def extract_title(page_or_db: Dict[str, Any]) -> str:
    """페이지나 데이터베이스에서 제목을 추출합니다"""
    if "properties" in page_or_db:
        # 페이지의 경우
        for prop_name, prop_value in page_or_db["properties"].items():
            if prop_value.get("type") == "title":
                title_array = prop_value.get("title", [])
                if title_array:
                    return "".join([t.get("plain_text", "") for t in title_array])
    
    # 데이터베이스의 경우 또는 title 속성이 없는 경우
    if "title" in page_or_db:
        title_array = page_or_db["title"]
        if title_array:
            return "".join([t.get("plain_text", "") for t in title_array])
    
    return "제목 없음"


def rich_text_to_plain_text(rich_text: List[Dict[str, Any]]) -> str:
    """리치 텍스트를 일반 텍스트로 변환합니다"""
    return "".join([rt.get("plain_text", "") for rt in rich_text])


def blocks_to_text(blocks: List[Dict[str, Any]]) -> str:
    """블록 배열을 텍스트로 변환합니다"""
    text_parts = []
    
    for block in blocks:
        block_type = block.get("type")
        
        if block_type == "paragraph":
            text = rich_text_to_plain_text(block["paragraph"]["rich_text"])
            text_parts.append(text)
        elif block_type == "heading_1":
            text = rich_text_to_plain_text(block["heading_1"]["rich_text"])
            text_parts.append(f"# {text}")
        elif block_type == "heading_2":
            text = rich_text_to_plain_text(block["heading_2"]["rich_text"])
            text_parts.append(f"## {text}")
        elif block_type == "heading_3":
            text = rich_text_to_plain_text(block["heading_3"]["rich_text"])
            text_parts.append(f"### {text}")
        elif block_type == "bulleted_list_item":
            text = rich_text_to_plain_text(block["bulleted_list_item"]["rich_text"])
            text_parts.append(f"- {text}")
        elif block_type == "numbered_list_item":
            text = rich_text_to_plain_text(block["numbered_list_item"]["rich_text"])
            text_parts.append(f"1. {text}")
        elif block_type == "to_do":
            text = rich_text_to_plain_text(block["to_do"]["rich_text"])
            checked = "✅" if block["to_do"]["checked"] else "☐"
            text_parts.append(f"{checked} {text}")
        elif block_type == "code":
            text = rich_text_to_plain_text(block["code"]["rich_text"])
            language = block["code"].get("language", "")
            text_parts.append(f"```{language}\n{text}\n```")
        
        # 하위 블록이 있는 경우 재귀적으로 처리
        if block.get("has_children"):
            children = notion.blocks.children.list(block["id"])
            child_text = blocks_to_text(children["results"])
            if child_text:
                text_parts.append(child_text)
    
    return "\n\n".join(text_parts)


def text_to_blocks(text: str) -> List[Dict[str, Any]]:
    """텍스트를 Notion 블록으로 변환합니다"""
    blocks = []
    lines = text.split("\n")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                }
            })
        elif line.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                }
            })
        elif line.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                }
            })
        elif line.startswith("- "):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                }
            })
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line}}]
                }
            })
    
    return blocks


@mcp.tool()
def search_notion(query: str, filter_type: str = None) -> str:
    """Notion에서 페이지나 데이터베이스를 검색합니다
    
    Args:
        query: 검색할 텍스트
        filter_type: 검색할 객체 타입 (page 또는 database, 선택사항)
    """
    try:
        search_params = {"query": query}
        if filter_type:
            search_params["filter"] = {"value": filter_type, "property": "object"}
        
        results = notion.search(**search_params)
        
        formatted_results = []
        for result in results["results"]:
            if result["object"] == "page":
                title = extract_title(result)
                formatted_results.append({
                    "id": result["id"],
                    "type": "page",
                    "title": title,
                    "url": result["url"]
                })
            elif result["object"] == "database":
                title = extract_title(result)
                formatted_results.append({
                    "id": result["id"],
                    "type": "database",
                    "title": title,
                    "url": result["url"]
                })
        
        result_text = f"검색 결과 ({len(formatted_results)}개):\n" + json.dumps(formatted_results, ensure_ascii=False, indent=2)
        return result_text
        
    except Exception as e:
        logger.error(f"검색 중 오류: {str(e)}")
        return f"검색 중 오류가 발생했습니다: {str(e)}"


@mcp.tool()
def get_page(page_id: str) -> str:
    """Notion 페이지의 정보를 가져옵니다
    
    Args:
        page_id: 페이지 ID
    """
    try:
        page = notion.pages.retrieve(page_id)
        title = extract_title(page)
        
        page_info = {
            "id": page["id"],
            "title": title,
            "url": page["url"],
            "created_time": page["created_time"],
            "last_edited_time": page["last_edited_time"],
            "properties": page.get("properties", {})
        }
        
        result_text = f"페이지 정보:\n{json.dumps(page_info, ensure_ascii=False, indent=2)}"
        return result_text
        
    except Exception as e:
        logger.error(f"페이지 조회 중 오류: {str(e)}")
        return f"페이지 조회 중 오류가 발생했습니다: {str(e)}"


@mcp.tool()
def get_page_content(page_id: str) -> str:
    """Notion 페이지의 블록 내용을 가져옵니다
    
    Args:
        page_id: 페이지 ID
    """
    try:
        # 페이지 정보 가져오기
        page = notion.pages.retrieve(page_id)
        title = extract_title(page)
        
        # 블록 내용 가져오기
        blocks = notion.blocks.children.list(page_id)
        content = blocks_to_text(blocks["results"])
        
        result_text = f"# {title}\n\n{content}"
        return result_text
        
    except Exception as e:
        logger.error(f"페이지 내용 조회 중 오류: {str(e)}")
        return f"페이지 내용 조회 중 오류가 발생했습니다: {str(e)}"


@mcp.tool()
def create_page(parent_id: str, title: str, content: str = "") -> str:
    """새로운 Notion 페이지를 생성합니다
    
    Args:
        parent_id: 부모 페이지 또는 데이터베이스 ID
        title: 페이지 제목
        content: 페이지 내용 (마크다운 형식, 선택사항)
    """
    try:
        # 페이지 생성
        new_page = notion.pages.create(
            parent={"page_id": parent_id},
            properties={
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
        )
        
        # 내용이 있으면 블록 추가
        if content:
            blocks = text_to_blocks(content)
            if blocks:
                notion.blocks.children.append(
                    block_id=new_page["id"],
                    children=blocks
                )
        
        result_text = f"페이지가 성공적으로 생성되었습니다!\nID: {new_page['id']}\nURL: {new_page['url']}"
        return result_text
        
    except Exception as e:
        logger.error(f"페이지 생성 중 오류: {str(e)}")
        return f"페이지 생성 중 오류가 발생했습니다: {str(e)}"


@mcp.tool()
def update_page(page_id: str, title: str = None, content: str = None) -> str:
    """기존 Notion 페이지를 업데이트합니다
    
    Args:
        page_id: 업데이트할 페이지 ID
        title: 새로운 제목 (선택사항)
        content: 추가할 내용 (마크다운 형식, 선택사항)
    """
    try:
        # 제목 업데이트
        if title:
            notion.pages.update(
                page_id=page_id,
                properties={
                    "title": {
                        "title": [{"text": {"content": title}}]
                    }
                }
            )
        
        # 내용 추가
        if content:
            blocks = text_to_blocks(content)
            if blocks:
                notion.blocks.children.append(
                    block_id=page_id,
                    children=blocks
                )
        
        return "페이지가 성공적으로 업데이트되었습니다!"
        
    except Exception as e:
        logger.error(f"페이지 업데이트 중 오류: {str(e)}")
        return f"페이지 업데이트 중 오류가 발생했습니다: {str(e)}"


@mcp.tool()
def query_database(database_id: str, filter_condition: dict = None, sorts: list = None) -> str:
    """Notion 데이터베이스를 쿼리합니다
    
    Args:
        database_id: 데이터베이스 ID
        filter_condition: 필터 조건 (선택사항)
        sorts: 정렬 조건 (선택사항)
    """
    try:
        query_params = {"database_id": database_id}
        if filter_condition:
            query_params["filter"] = filter_condition
        if sorts:
            query_params["sorts"] = sorts
        
        results = notion.databases.query(**query_params)
        
        formatted_results = []
        for page in results["results"]:
            title = extract_title(page)
            formatted_results.append({
                "id": page["id"],
                "title": title,
                "url": page["url"],
                "properties": page.get("properties", {})
            })
        
        result_text = f"데이터베이스 쿼리 결과 ({len(formatted_results)}개):\n" + json.dumps(formatted_results, ensure_ascii=False, indent=2)
        return result_text
        
    except Exception as e:
        logger.error(f"데이터베이스 쿼리 중 오류: {str(e)}")
        return f"데이터베이스 쿼리 중 오류가 발생했습니다: {str(e)}"


@mcp.tool()
def create_database_entry(database_id: str, properties: dict) -> str:
    """데이터베이스에 새로운 항목을 생성합니다
    
    Args:
        database_id: 데이터베이스 ID
        properties: 항목 속성들
    """
    try:
        new_page = notion.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        
        result_text = f"데이터베이스 항목이 성공적으로 생성되었습니다!\nID: {new_page['id']}\nURL: {new_page['url']}"
        return result_text
        
    except Exception as e:
        logger.error(f"데이터베이스 항목 생성 중 오류: {str(e)}")
        return f"데이터베이스 항목 생성 중 오류가 발생했습니다: {str(e)}"


if __name__ == "__main__":
    mcp.run() 