class SubtitleService:
    def generate(self, file_path: str) -> dict:
        # TODO: Whisper/Faster-Whisper 연동
        return {
            "file_path": file_path,
            "srt": None,
            "vtt": None,
            "json": None,
        }
