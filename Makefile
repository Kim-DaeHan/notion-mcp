# Notion MCP Server Makefile

.PHONY: help install install-dev test lint format clean run setup

# 기본 타겟
help:
	@echo "사용 가능한 명령어:"
	@echo "  setup       - 프로젝트 초기 설정"
	@echo "  install     - 기본 의존성 설치"
	@echo "  install-dev - 개발용 의존성 설치"
	@echo "  test        - 테스트 실행"
	@echo "  lint        - 코드 린팅"
	@echo "  format      - 코드 포맷팅"
	@echo "  run         - 서버 실행"
	@echo "  clean       - 임시 파일 정리"

# 프로젝트 초기 설정
setup:
	@echo "🔧 프로젝트 초기 설정 중..."
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "📝 .env 파일이 생성되었습니다. NOTION_TOKEN을 설정해주세요."; \
	else \
		echo "✅ .env 파일이 이미 존재합니다."; \
	fi
	@make install-dev
	@echo "✅ 설정 완료!"

# 기본 의존성 설치
install:
	@echo "📦 기본 의존성 설치 중..."
	pip install -r requirements.txt

# 개발용 의존성 설치
install-dev:
	@echo "📦 개발용 의존성 설치 중..."
	pip install -r requirements-dev.txt

# 테스트 실행
test:
	@echo "🧪 테스트 실행 중..."
	python -m pytest tests/ -v --cov=src --cov-report=term-missing

# 코드 린팅
lint:
	@echo "🔍 코드 린팅 중..."
	flake8 src/ tests/
	mypy src/

# 코드 포맷팅
format:
	@echo "✨ 코드 포맷팅 중..."
	black src/ tests/ scripts/

# 서버 실행
run:
	@echo "🚀 서버 실행 중..."
	python scripts/run_server.py

# 임시 파일 정리
clean:
	@echo "🧹 임시 파일 정리 중..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete

# 패키지 빌드
build:
	@echo "📦 패키지 빌드 중..."
	python setup.py sdist bdist_wheel

# 개발 환경 확인
check:
	@echo "🔍 개발 환경 확인 중..."
	@python -c "import sys; print(f'Python 버전: {sys.version}')"
	@python -c "import os; print(f'NOTION_TOKEN 설정: {\"✅\" if os.getenv(\"NOTION_TOKEN\") else \"❌\"}')" 