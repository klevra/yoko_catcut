class YoutubeService:
    def import_url(self, url: str, user_id: str, project_name: str) -> dict:
        # TODO: yt-dlp 등 다운로드 Adapter 연동
        return {
            "url": url,
            "user_id": user_id,
            "project_name": project_name,
            "status": "TODO"
        }
