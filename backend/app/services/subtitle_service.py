import json
from pathlib import Path

from app.core.config import get_settings


class SubtitleService:
    def __init__(self):
        self.settings = get_settings()
        self._model = None

    def generate(
        self,
        file_path: str,
        output_dir: Path,
        upload_id: str,
        language: str = None,
    ) -> dict:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper is not installed in the backend environment"
            ) from exc

        output_dir.mkdir(parents=True, exist_ok=True)
        if self._model is None:
            self._model = WhisperModel(
                self.settings.whisper_model,
                device=self.settings.device,
                compute_type="int8" if self.settings.device == "cpu" else "float16",
                download_root=self.settings.whisper_path,
            )
        model = self._model
        source_segments, info = model.transcribe(
            file_path,
            language=language,
            vad_filter=True,
            beam_size=5,
        )
        segments = [
            {
                "id": index,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
            }
            for index, segment in enumerate(source_segments, start=1)
        ]
        if not segments:
            raise ValueError("No speech was detected in the uploaded video")

        stem = upload_id
        json_path = output_dir / f"{stem}.json"
        srt_path = output_dir / f"{stem}.srt"
        vtt_path = output_dir / f"{stem}.vtt"
        payload = {
            "upload_id": upload_id,
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "segments": segments,
        }
        with json_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)
        srt_path.write_text(self._to_srt(segments), encoding="utf-8")
        vtt_path.write_text(self._to_vtt(segments), encoding="utf-8")

        return {
            "upload_id": upload_id,
            "language": info.language,
            "language_probability": info.language_probability,
            "segments": segments,
            "json": str(json_path),
            "srt": str(srt_path),
            "vtt": str(vtt_path),
        }

    def save(self, output_dir: Path, upload_id: str, payload: dict) -> dict:
        segments = self._validate_segments(payload.get("segments", []))
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / f"{upload_id}.json"
        srt_path = output_dir / f"{upload_id}.srt"
        vtt_path = output_dir / f"{upload_id}.vtt"
        updated = {
            **payload,
            "upload_id": upload_id,
            "segments": segments,
        }
        with json_path.open("w", encoding="utf-8") as file:
            json.dump(updated, file, indent=2, ensure_ascii=False)
        srt_path.write_text(self._to_srt(segments), encoding="utf-8")
        vtt_path.write_text(self._to_vtt(segments), encoding="utf-8")
        return updated

    @staticmethod
    def _validate_segments(segments: list) -> list:
        normalized = []
        previous_end = 0.0
        for index, segment in enumerate(
            sorted(segments, key=lambda item: item["start"]), start=1
        ):
            start = round(float(segment["start"]), 3)
            end = round(float(segment["end"]), 3)
            text = str(segment["text"]).strip()
            if start < 0 or end <= start:
                raise ValueError("Subtitle end time must be after start time")
            if start < previous_end:
                raise ValueError("Subtitle segments cannot overlap")
            if not text:
                raise ValueError("Subtitle text cannot be empty")
            normalized.append(
                {
                    "id": index,
                    "start": start,
                    "end": end,
                    "text": text,
                    **(
                        {"speaker_id": str(segment["speaker_id"])}
                        if segment.get("speaker_id")
                        else {}
                    ),
                }
            )
            previous_end = end
        return normalized

    @classmethod
    def _to_srt(cls, segments: list) -> str:
        blocks = []
        for segment in segments:
            blocks.append(
                f'{segment["id"]}\n'
                f'{cls._timestamp(segment["start"], ",")} --> '
                f'{cls._timestamp(segment["end"], ",")}\n'
                f'{segment["text"]}'
            )
        return "\n\n".join(blocks) + "\n"

    @classmethod
    def _to_vtt(cls, segments: list) -> str:
        blocks = ["WEBVTT"]
        for segment in segments:
            blocks.append(
                f'{cls._timestamp(segment["start"], ".")} --> '
                f'{cls._timestamp(segment["end"], ".")}\n'
                f'{segment["text"]}'
            )
        return "\n\n".join(blocks) + "\n"

    @staticmethod
    def _timestamp(seconds: float, separator: str) -> str:
        milliseconds = round(seconds * 1000)
        hours, milliseconds = divmod(milliseconds, 3_600_000)
        minutes, milliseconds = divmod(milliseconds, 60_000)
        whole_seconds, milliseconds = divmod(milliseconds, 1000)
        return (
            f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}"
            f"{separator}{milliseconds:03d}"
        )
