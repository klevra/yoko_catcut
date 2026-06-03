class FfmpegService:
    def probe(self, file_path: str) -> dict:
        # TODO: ffprobe 기반 metadata 분석 구현
        return {
            "file_path": file_path,
            "duration": None,
            "codec": None,
            "fps": None,
            "resolution": None,
        }
