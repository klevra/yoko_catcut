import json
import subprocess
from fractions import Fraction

from app.core.config import get_settings


class FfmpegService:
    def __init__(self):
        self.ffprobe_binary = get_settings().ffprobe_binary

    def probe(self, file_path: str) -> dict:
        command = [
            self.ffprobe_binary,
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            file_path,
        ]
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"ffprobe binary was not found: {self.ffprobe_binary}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise ValueError("Video metadata analysis timed out") from exc
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.strip() or "unsupported or corrupted media"
            raise ValueError(f"ffprobe failed: {detail}") from exc

        raw = json.loads(result.stdout)
        streams = raw.get("streams", [])
        video = next(
            (stream for stream in streams if stream.get("codec_type") == "video"),
            None,
        )
        audio = next(
            (stream for stream in streams if stream.get("codec_type") == "audio"),
            None,
        )
        if video is None:
            raise ValueError("The uploaded file does not contain a video stream")

        format_info = raw.get("format", {})
        return {
            "duration": self._number(format_info.get("duration")),
            "format": format_info.get("format_name"),
            "size": self._integer(format_info.get("size")),
            "bit_rate": self._integer(format_info.get("bit_rate")),
            "video": {
                "codec": video.get("codec_name"),
                "width": video.get("width"),
                "height": video.get("height"),
                "fps": self._frame_rate(
                    video.get("avg_frame_rate") or video.get("r_frame_rate")
                ),
                "pixel_format": video.get("pix_fmt"),
            },
            "audio": (
                {
                    "codec": audio.get("codec_name"),
                    "sample_rate": self._integer(audio.get("sample_rate")),
                    "channels": audio.get("channels"),
                }
                if audio
                else None
            ),
        }

    @staticmethod
    def _number(value):
        return float(value) if value not in (None, "N/A") else None

    @staticmethod
    def _integer(value):
        return int(value) if value not in (None, "N/A") else None

    @staticmethod
    def _frame_rate(value):
        if not value or value == "0/0":
            return None
        return round(float(Fraction(value)), 3)
