"""
YouTube Shorts Script Service

키워드를 받아서 유튜브 쇼츠용 대본을 생성하고 파일로 저장하는 서비스입니다.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


class YouTubeScriptService:
    """유튜브 쇼츠 대본 생성 서비스"""

    def __init__(self, scripts_dir: str = "scripts"):
        """
        Args:
            scripts_dir: 대본 파일을 저장할 디렉토리
        """
        self.scripts_dir = scripts_dir

    def _ensure_scripts_directory(self):
        """스크립트 디렉토리가 존재하지 않으면 생성합니다"""
        try:
            if not os.path.exists(self.scripts_dir):
                os.makedirs(self.scripts_dir, exist_ok=True)
                logger.info(f"스크립트 디렉토리 생성: {self.scripts_dir}")
        except Exception as e:
            logger.error(f"스크립트 디렉토리 생성 실패: {e}")
            raise

    def create_script_file(self, keyword: str, script_content: str) -> str:
        """
        키워드와 대본 내용을 받아서 파일을 생성합니다

        Args:
            keyword: 대본의 주제 키워드
            script_content: AI가 생성한 대본 내용

        Returns:
            생성된 파일의 경로
        """
        try:
            # 디렉토리 존재 확인 및 생성
            self._ensure_scripts_directory()

            # 파일명 생성 (키워드 + 타임스탬프)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_keyword = self._sanitize_filename(keyword)
            filename = f"youtube_shorts_{safe_keyword}_{timestamp}.md"
            filepath = os.path.join(self.scripts_dir, filename)

            # 대본 메타데이터와 함께 파일 내용 구성
            file_content = self._format_script_content(keyword, script_content)

            # 파일 저장
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(file_content)

            logger.info(f"유튜브 쇼츠 대본 파일 생성 완료: {filepath}")

            return json.dumps(
                {
                    "success": True,
                    "message": "유튜브 쇼츠 대본 파일이 성공적으로 생성되었습니다.",
                    "file_path": filepath,
                    "keyword": keyword,
                    "created_at": datetime.now().isoformat(),
                },
                ensure_ascii=False,
                indent=2,
            )

        except Exception as e:
            logger.error(f"대본 파일 생성 중 오류 발생: {e}")
            return json.dumps(
                {
                    "success": False,
                    "error": f"파일 생성 중 오류가 발생했습니다: {str(e)}",
                },
                ensure_ascii=False,
                indent=2,
            )

    def _sanitize_filename(self, keyword: str) -> str:
        """파일명에 사용할 수 없는 문자를 제거합니다"""
        # 파일명에 사용할 수 없는 문자들을 언더스코어로 대체
        invalid_chars = '<>:"/\\|?*'
        safe_keyword = keyword
        for char in invalid_chars:
            safe_keyword = safe_keyword.replace(char, "_")

        # 공백을 언더스코어로 대체하고 길이 제한
        safe_keyword = safe_keyword.replace(" ", "_").strip()[:50]

        return safe_keyword

    def _format_script_content(self, keyword: str, script_content: str) -> str:
        """대본 내용을 마크다운 형식으로 포맷팅합니다"""
        timestamp = datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")

        formatted_content = f"""# 유튜브 쇼츠 대본

## 메타데이터
- **키워드**: {keyword}
- **생성일시**: {timestamp}
- **대본 길이**: 약 {len(script_content)}자

---

## 대본 내용

{script_content}

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

---

*이 대본은 AI에 의해 생성되었으며, 실제 사용 전 검토 및 수정이 필요할 수 있습니다.*
"""

        return formatted_content

    def list_script_files(self) -> str:
        """생성된 대본 파일 목록을 반환합니다"""
        try:
            if not os.path.exists(self.scripts_dir):
                return json.dumps(
                    {
                        "success": True,
                        "message": "아직 생성된 대본 파일이 없습니다.",
                        "files": [],
                    },
                    ensure_ascii=False,
                    indent=2,
                )

            files = []
            for filename in os.listdir(self.scripts_dir):
                if filename.endswith(".md") and filename.startswith("youtube_shorts_"):
                    filepath = os.path.join(self.scripts_dir, filename)
                    stat = os.stat(filepath)

                    files.append(
                        {
                            "filename": filename,
                            "filepath": filepath,
                            "size": stat.st_size,
                            "created_at": datetime.fromtimestamp(
                                stat.st_ctime
                            ).isoformat(),
                            "modified_at": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }
                    )

            # 생성일시 기준으로 정렬 (최신순)
            files.sort(key=lambda x: x["created_at"], reverse=True)

            return json.dumps(
                {
                    "success": True,
                    "message": f"총 {len(files)}개의 대본 파일이 있습니다.",
                    "files": files,
                },
                ensure_ascii=False,
                indent=2,
            )

        except Exception as e:
            logger.error(f"파일 목록 조회 중 오류 발생: {e}")
            return json.dumps(
                {
                    "success": False,
                    "error": f"파일 목록 조회 중 오류가 발생했습니다: {str(e)}",
                },
                ensure_ascii=False,
                indent=2,
            )

    def get_script_content(self, filename: str) -> str:
        """특정 대본 파일의 내용을 반환합니다"""
        try:
            filepath = os.path.join(self.scripts_dir, filename)

            if not os.path.exists(filepath):
                return json.dumps(
                    {"success": False, "error": f"파일을 찾을 수 없습니다: {filename}"},
                    ensure_ascii=False,
                    indent=2,
                )

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            return json.dumps(
                {"success": True, "filename": filename, "content": content},
                ensure_ascii=False,
                indent=2,
            )

        except Exception as e:
            logger.error(f"파일 내용 읽기 중 오류 발생: {e}")
            return json.dumps(
                {
                    "success": False,
                    "error": f"파일 읽기 중 오류가 발생했습니다: {str(e)}",
                },
                ensure_ascii=False,
                indent=2,
            )

    def delete_script_file(self, filename: str) -> str:
        """특정 대본 파일을 삭제합니다"""
        try:
            filepath = os.path.join(self.scripts_dir, filename)

            if not os.path.exists(filepath):
                return json.dumps(
                    {"success": False, "error": f"파일을 찾을 수 없습니다: {filename}"},
                    ensure_ascii=False,
                    indent=2,
                )

            os.remove(filepath)

            return json.dumps(
                {
                    "success": True,
                    "message": f"파일이 성공적으로 삭제되었습니다: {filename}",
                },
                ensure_ascii=False,
                indent=2,
            )

        except Exception as e:
            logger.error(f"파일 삭제 중 오류 발생: {e}")
            return json.dumps(
                {
                    "success": False,
                    "error": f"파일 삭제 중 오류가 발생했습니다: {str(e)}",
                },
                ensure_ascii=False,
                indent=2,
            )
