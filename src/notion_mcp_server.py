#!/usr/bin/env python3
"""
Notion MCP Server

Cursor와 Claude에서 사용할 수 있는 MCP 서버로, Notion API와 상호작용하여
페이지 읽기, 쓰기, 데이터베이스 조회 등의 기능을 제공합니다.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    TextContent,
    Tool,
)
from notion_client import Client
from pydantic import BaseModel

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
logger = logging.getLogger(__name__)


class NotionMCPServer:
    """Notion MCP 서버 클래스"""
    
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        if not self.notion_token:
            raise ValueError("NOTION_TOKEN 환경 변수가 설정되지 않았습니다.")
        
        self.notion = Client(auth=self.notion_token)
        self.server = Server("notion-mcp-server")
        
        # 도구 등록
        self._register_tools()
    
    def _register_tools(self):
        """MCP 도구들을 등록합니다"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """사용 가능한 도구 목록을 반환합니다"""
            return [
                Tool(
                    name="search_notion",
                    description="Notion에서 페이지나 데이터베이스를 검색합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "검색할 텍스트"
                            },
                            "filter_type": {
                                "type": "string",
                                "enum": ["page", "database"],
                                "description": "검색할 객체 타입 (선택사항)"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_page",
                    description="Notion 페이지의 내용을 가져옵니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {
                                "type": "string",
                                "description": "페이지 ID"
                            }
                        },
                        "required": ["page_id"]
                    }
                ),
                Tool(
                    name="get_page_content",
                    description="Notion 페이지의 블록 내용을 가져옵니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {
                                "type": "string",
                                "description": "페이지 ID"
                            }
                        },
                        "required": ["page_id"]
                    }
                ),
                Tool(
                    name="create_page",
                    description="새로운 Notion 페이지를 생성합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "parent_id": {
                                "type": "string",
                                "description": "부모 페이지 또는 데이터베이스 ID"
                            },
                            "title": {
                                "type": "string",
                                "description": "페이지 제목"
                            },
                            "content": {
                                "type": "string",
                                "description": "페이지 내용 (마크다운 형식)"
                            }
                        },
                        "required": ["parent_id", "title"]
                    }
                ),
                Tool(
                    name="update_page",
                    description="기존 Notion 페이지를 업데이트합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {
                                "type": "string",
                                "description": "업데이트할 페이지 ID"
                            },
                            "title": {
                                "type": "string",
                                "description": "새로운 제목 (선택사항)"
                            },
                            "content": {
                                "type": "string",
                                "description": "추가할 내용 (마크다운 형식)"
                            }
                        },
                        "required": ["page_id"]
                    }
                ),
                Tool(
                    name="query_database",
                    description="Notion 데이터베이스를 쿼리합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database_id": {
                                "type": "string",
                                "description": "데이터베이스 ID"
                            },
                            "filter": {
                                "type": "object",
                                "description": "필터 조건 (선택사항)"
                            },
                            "sorts": {
                                "type": "array",
                                "description": "정렬 조건 (선택사항)"
                            }
                        },
                        "required": ["database_id"]
                    }
                ),
                Tool(
                    name="create_database_entry",
                    description="데이터베이스에 새로운 항목을 생성합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database_id": {
                                "type": "string",
                                "description": "데이터베이스 ID"
                            },
                            "properties": {
                                "type": "object",
                                "description": "항목 속성들"
                            }
                        },
                        "required": ["database_id", "properties"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """도구 호출을 처리합니다"""
            try:
                if name == "search_notion":
                    return await self._search_notion(arguments)
                elif name == "get_page":
                    return await self._get_page(arguments)
                elif name == "get_page_content":
                    return await self._get_page_content(arguments)
                elif name == "create_page":
                    return await self._create_page(arguments)
                elif name == "update_page":
                    return await self._update_page(arguments)
                elif name == "query_database":
                    return await self._query_database(arguments)
                elif name == "create_database_entry":
                    return await self._create_database_entry(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"알 수 없는 도구: {name}")],
                        isError=True
                    )
            except Exception as e:
                logger.error(f"도구 '{name}' 실행 중 오류: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"오류: {str(e)}")],
                    isError=True
                )
    
    async def _search_notion(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Notion에서 검색을 수행합니다"""
        query = arguments["query"]
        filter_type = arguments.get("filter_type")
        
        search_params = {"query": query}
        if filter_type:
            search_params["filter"] = {"value": filter_type, "property": "object"}
        
        results = self.notion.search(**search_params)
        
        formatted_results = []
        for result in results["results"]:
            if result["object"] == "page":
                title = self._extract_title(result)
                formatted_results.append({
                    "id": result["id"],
                    "type": "page",
                    "title": title,
                    "url": result["url"]
                })
            elif result["object"] == "database":
                title = self._extract_title(result)
                formatted_results.append({
                    "id": result["id"],
                    "type": "database",
                    "title": title,
                    "url": result["url"]
                })
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"검색 결과 ({len(formatted_results)}개):\n" + 
                     json.dumps(formatted_results, ensure_ascii=False, indent=2)
            )]
        )
    
    async def _get_page(self, arguments: Dict[str, Any]) -> CallToolResult:
        """페이지 정보를 가져옵니다"""
        page_id = arguments["page_id"]
        
        page = self.notion.pages.retrieve(page_id)
        title = self._extract_title(page)
        
        page_info = {
            "id": page["id"],
            "title": title,
            "url": page["url"],
            "created_time": page["created_time"],
            "last_edited_time": page["last_edited_time"],
            "properties": page.get("properties", {})
        }
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"페이지 정보:\n{json.dumps(page_info, ensure_ascii=False, indent=2)}"
            )]
        )
    
    async def _get_page_content(self, arguments: Dict[str, Any]) -> CallToolResult:
        """페이지의 블록 내용을 가져옵니다"""
        page_id = arguments["page_id"]
        
        # 페이지 정보 가져오기
        page = self.notion.pages.retrieve(page_id)
        title = self._extract_title(page)
        
        # 블록 내용 가져오기
        blocks = self.notion.blocks.children.list(page_id)
        content = self._blocks_to_text(blocks["results"])
        
        result = f"# {title}\n\n{content}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result)]
        )
    
    async def _create_page(self, arguments: Dict[str, Any]) -> CallToolResult:
        """새로운 페이지를 생성합니다"""
        parent_id = arguments["parent_id"]
        title = arguments["title"]
        content = arguments.get("content", "")
        
        # 페이지 생성
        new_page = self.notion.pages.create(
            parent={"page_id": parent_id},
            properties={
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
        )
        
        # 내용이 있으면 블록 추가
        if content:
            blocks = self._text_to_blocks(content)
            if blocks:
                self.notion.blocks.children.append(
                    block_id=new_page["id"],
                    children=blocks
                )
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"페이지가 성공적으로 생성되었습니다!\n"
                     f"ID: {new_page['id']}\n"
                     f"URL: {new_page['url']}"
            )]
        )
    
    async def _update_page(self, arguments: Dict[str, Any]) -> CallToolResult:
        """페이지를 업데이트합니다"""
        page_id = arguments["page_id"]
        title = arguments.get("title")
        content = arguments.get("content")
        
        # 제목 업데이트
        if title:
            self.notion.pages.update(
                page_id=page_id,
                properties={
                    "title": {
                        "title": [{"text": {"content": title}}]
                    }
                }
            )
        
        # 내용 추가
        if content:
            blocks = self._text_to_blocks(content)
            if blocks:
                self.notion.blocks.children.append(
                    block_id=page_id,
                    children=blocks
                )
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="페이지가 성공적으로 업데이트되었습니다!"
            )]
        )
    
    async def _query_database(self, arguments: Dict[str, Any]) -> CallToolResult:
        """데이터베이스를 쿼리합니다"""
        database_id = arguments["database_id"]
        filter_condition = arguments.get("filter")
        sorts = arguments.get("sorts")
        
        query_params = {"database_id": database_id}
        if filter_condition:
            query_params["filter"] = filter_condition
        if sorts:
            query_params["sorts"] = sorts
        
        results = self.notion.databases.query(**query_params)
        
        formatted_results = []
        for page in results["results"]:
            title = self._extract_title(page)
            formatted_results.append({
                "id": page["id"],
                "title": title,
                "url": page["url"],
                "properties": page.get("properties", {})
            })
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"데이터베이스 쿼리 결과 ({len(formatted_results)}개):\n" +
                     json.dumps(formatted_results, ensure_ascii=False, indent=2)
            )]
        )
    
    async def _create_database_entry(self, arguments: Dict[str, Any]) -> CallToolResult:
        """데이터베이스에 새로운 항목을 생성합니다"""
        database_id = arguments["database_id"]
        properties = arguments["properties"]
        
        new_page = self.notion.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"데이터베이스 항목이 성공적으로 생성되었습니다!\n"
                     f"ID: {new_page['id']}\n"
                     f"URL: {new_page['url']}"
            )]
        )
    
    def _extract_title(self, page_or_db: Dict[str, Any]) -> str:
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
    
    def _blocks_to_text(self, blocks: List[Dict[str, Any]]) -> str:
        """블록 배열을 텍스트로 변환합니다"""
        text_parts = []
        
        for block in blocks:
            block_type = block.get("type")
            
            if block_type == "paragraph":
                text = self._rich_text_to_plain_text(block["paragraph"]["rich_text"])
                text_parts.append(text)
            elif block_type == "heading_1":
                text = self._rich_text_to_plain_text(block["heading_1"]["rich_text"])
                text_parts.append(f"# {text}")
            elif block_type == "heading_2":
                text = self._rich_text_to_plain_text(block["heading_2"]["rich_text"])
                text_parts.append(f"## {text}")
            elif block_type == "heading_3":
                text = self._rich_text_to_plain_text(block["heading_3"]["rich_text"])
                text_parts.append(f"### {text}")
            elif block_type == "bulleted_list_item":
                text = self._rich_text_to_plain_text(block["bulleted_list_item"]["rich_text"])
                text_parts.append(f"- {text}")
            elif block_type == "numbered_list_item":
                text = self._rich_text_to_plain_text(block["numbered_list_item"]["rich_text"])
                text_parts.append(f"1. {text}")
            elif block_type == "to_do":
                text = self._rich_text_to_plain_text(block["to_do"]["rich_text"])
                checked = "✅" if block["to_do"]["checked"] else "☐"
                text_parts.append(f"{checked} {text}")
            elif block_type == "code":
                text = self._rich_text_to_plain_text(block["code"]["rich_text"])
                language = block["code"].get("language", "")
                text_parts.append(f"```{language}\n{text}\n```")
            
            # 하위 블록이 있는 경우 재귀적으로 처리
            if block.get("has_children"):
                children = self.notion.blocks.children.list(block["id"])
                child_text = self._blocks_to_text(children["results"])
                if child_text:
                    text_parts.append(child_text)
        
        return "\n\n".join(text_parts)
    
    def _rich_text_to_plain_text(self, rich_text: List[Dict[str, Any]]) -> str:
        """리치 텍스트를 일반 텍스트로 변환합니다"""
        return "".join([rt.get("plain_text", "") for rt in rich_text])
    
    def _text_to_blocks(self, text: str) -> List[Dict[str, Any]]:
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
    
    async def run(self):
        """서버를 실행합니다"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="notion-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )


async def main():
    """메인 함수"""
    try:
        server = NotionMCPServer()
        await server.run()
    except Exception as e:
        logger.error(f"서버 실행 중 오류: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 