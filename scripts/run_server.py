#!/usr/bin/env python3
"""
Notion MCP Server 실행 스크립트

이 스크립트는 Notion MCP 서버를 실행하기 위한 편의 스크립트입니다.
"""

import sys
import os
import asyncio
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.notion_mcp_server import main


def check_environment():
    """환경 설정을 확인합니다"""
    notion_token = os.getenv("NOTION_TOKEN")
    
    if not notion_token:
        print("❌ 오류: NOTION_TOKEN 환경 변수가 설정되지 않았습니다.")
        print("📝 해결 방법:")
        print("1. .env 파일을 생성하고 NOTION_TOKEN을 설정하세요")
        print("2. 또는 환경 변수로 직접 설정하세요: export NOTION_TOKEN=your_token")
        print("3. Notion 통합 토큰은 https://www.notion.so/my-integrations 에서 생성할 수 있습니다")
        return False
    
    print("✅ 환경 설정이 올바르게 되어 있습니다.")
    print(f"🔑 Notion 토큰: {notion_token[:10]}...")
    return True


def main_script():
    """메인 실행 함수"""
    print("🚀 Notion MCP Server 시작 중...")
    print("=" * 50)
    
    # 환경 확인
    if not check_environment():
        sys.exit(1)
    
    print("📡 MCP 서버를 시작합니다...")
    print("💡 팁: Ctrl+C로 서버를 중지할 수 있습니다.")
    print("=" * 50)
    
    try:
        # 서버 실행
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 서버가 사용자에 의해 중지되었습니다.")
    except Exception as e:
        print(f"\n❌ 서버 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main_script() 