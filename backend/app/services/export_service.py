import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from app.core.config import get_settings
from app.services.subtitle_service import SubtitleService


class ExportService:
    def __init__(self):
        self.settings = get_settings()

    def render(
        self,
        source_path: Path,
        output_dir: Path,
        export_id: str,
        options: dict,
        subtitle_payload: dict = None,
    ) -> dict:
        output_dir.mkdir(parents=True, exist_ok=True)
        final_path = output_dir / f"{export_id}.mp4"
        capcut_path = output_dir / f"{export_id}_capcut.zip"
        manifest_path = output_dir / f"{export_id}.json"
        processing_options = {
            "remove_silence": False,
            "speed_up_excluded": False,
            "excluded_speed": 2,
            "assembly_only": False,
            "remove_background_music": False,
            "add_background_music": False,
            "background_music_volume": 0.22,
            **options.get("processing_options", {}),
        }
        source_segments = options.get("segments", [])
        if processing_options["remove_silence"]:
            if not subtitle_payload or not subtitle_payload.get("segments"):
                raise ValueError(
                    "Automatic subtitles are required to remove silent parts"
                )
            source_segments = [
                {
                    "start": item["start"],
                    "end": item["end"],
                    "comment": item["text"],
                }
                for item in subtitle_payload["segments"]
            ]
        segments = self._normalize_segments(source_segments)
        media = self._probe_media(source_path)
        timeline = self._build_timeline(
            segments,
            media["duration"],
            processing_options,
        )

        with tempfile.TemporaryDirectory(prefix="yoko-export-") as temporary:
            temporary_dir = Path(temporary)
            concat_path = temporary_dir / "concat.mp4"
            self._render_timeline(
                source_path,
                concat_path,
                timeline,
                temporary_dir,
                media["has_audio"],
            )

            mapped_subtitles = self._map_subtitles(
                subtitle_payload.get("segments", []) if subtitle_payload else [],
                timeline,
            )
            srt_path = output_dir / f"{export_id}.srt"
            if mapped_subtitles:
                srt_path.write_text(
                    SubtitleService._to_srt(mapped_subtitles),
                    encoding="utf-8",
                )

            self._render_final(
                concat_path,
                final_path,
                options.get("aspect_ratio", "original"),
                srt_path if options.get("burn_subtitles") and mapped_subtitles else None,
                processing_options["assembly_only"],
                processing_options,
                Path(options["background_music_path"])
                if options.get("background_music_path")
                else None,
            )

        manifest = {
            "export_id": export_id,
            "editor_tool": options.get("editor_tool", "generic"),
            "aspect_ratio": options.get("aspect_ratio", "original"),
            "segments": segments,
            "timeline": timeline,
            "processing_options": processing_options,
            "subtitle_count": len(mapped_subtitles),
            "video": str(final_path),
            "subtitle": str(srt_path) if mapped_subtitles else None,
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        with zipfile.ZipFile(capcut_path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.write(final_path, final_path.name)
            archive.write(manifest_path, "yoko-catcut-manifest.json")
            if mapped_subtitles:
                archive.write(srt_path, srt_path.name)

        return {
            **manifest,
            "capcut_package": str(capcut_path),
        }

    def _render_timeline(
        self,
        source_path: Path,
        output_path: Path,
        timeline: list,
        temporary_dir: Path,
        has_audio: bool,
    ) -> None:
        if not timeline:
            shutil.copy2(source_path, output_path)
            return

        parts = []
        for index, segment in enumerate(timeline):
            part_path = temporary_dir / f"part-{index:04d}.mp4"
            command = [
                self.settings.ffmpeg_binary,
                "-y",
                "-ss",
                str(segment["start"]),
                "-t",
                str(round(segment["end"] - segment["start"], 3)),
                "-i",
                str(source_path),
            ]
            speed = segment["speed"]
            command.extend(
                [
                    "-vf",
                    (
                        f"setpts=(PTS-STARTPTS)/{speed}"
                        if speed > 1
                        else "setpts=PTS-STARTPTS"
                    ),
                ]
            )
            if has_audio:
                command.extend(
                    [
                        "-af",
                        (
                            f"atempo={speed},asetpts=PTS-STARTPTS"
                            if speed > 1
                            else "asetpts=PTS-STARTPTS"
                        ),
                    ]
                )
            command.extend(
                [
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "20",
                    "-fps_mode",
                    "vfr",
                ]
            )
            if has_audio:
                command.extend(["-c:a", "aac"])
            else:
                command.append("-an")
            command.extend(["-movflags", "+faststart", str(part_path)])
            self._run(command)
            parts.append(part_path)

        concat_list = temporary_dir / "concat.txt"
        concat_list.write_text(
            "\n".join(f"file '{path.name}'" for path in parts),
            encoding="utf-8",
        )
        self._run(
            [
                self.settings.ffmpeg_binary,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_list),
                "-c",
                "copy",
                str(output_path),
            ],
            cwd=temporary_dir,
        )

    def _render_final(
        self,
        source_path: Path,
        output_path: Path,
        aspect_ratio: str,
        subtitle_path: Path = None,
        assembly_only: bool = False,
        processing_options: dict = None,
        background_music_path: Path = None,
    ) -> None:
        processing_options = processing_options or {}
        filters = []
        aspect_filters = {
            "9:16": "scale=1080:1920:force_original_aspect_ratio=decrease,"
            "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
            "16:9": "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black",
            "1:1": "scale=1080:1080:force_original_aspect_ratio=decrease,"
            "pad=1080:1080:(ow-iw)/2:(oh-ih)/2:black",
        }
        if assembly_only:
            filters.append(
                "crop=trunc(iw/1.35/2)*2:trunc(ih/1.35/2)*2:"
                "(iw-ow)/2:(ih-oh)/2,"
                "scale=trunc(iw*1.35/2)*2:trunc(ih*1.35/2)*2"
            )
        if aspect_ratio in aspect_filters:
            filters.append(aspect_filters[aspect_ratio])
        if subtitle_path:
            escaped = str(subtitle_path).replace("\\", "\\\\").replace(":", "\\:")
            filters.append(
                f"subtitles='{escaped}':charenc=UTF-8:"
                "fontsdir=/usr/share/fonts/opentype/noto:"
                f"force_style='FontName={self.settings.subtitle_font},FontSize=18,"
                "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
                "BorderStyle=1,Outline=2'"
            )

        add_background_music = (
            processing_options.get("add_background_music")
            and background_music_path
            and background_music_path.is_file()
        )
        remove_background_music = processing_options.get("remove_background_music")
        volume = max(
            0.0,
            min(1.0, float(processing_options.get("background_music_volume", 0.22))),
        )
        command = [self.settings.ffmpeg_binary, "-y", "-i", str(source_path)]
        if add_background_music:
            command.extend(["-stream_loop", "-1", "-i", str(background_music_path)])
        if filters:
            video_filter = ",".join(filters)
        else:
            video_filter = None

        speech_filter = (
            "highpass=f=120,lowpass=f=5200,afftdn=nf=-28,"
            "acompressor=threshold=-18dB:ratio=3:attack=20:release=250"
        )
        if add_background_music:
            audio_base = (
                f"[0:a]{speech_filter}[base];"
                if remove_background_music
                else "[0:a]anull[base];"
            )
            filter_complex = (
                f"{audio_base}[1:a]volume={volume}[bgm];"
                "[base][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
            if video_filter:
                filter_complex = f"[0:v]{video_filter}[vout];{filter_complex}"
                command.extend(["-filter_complex", filter_complex, "-map", "[vout]"])
            else:
                command.extend(["-filter_complex", filter_complex, "-map", "0:v"])
            command.extend(["-map", "[aout]"])
        else:
            if video_filter:
                command.extend(["-vf", video_filter])
            if remove_background_music:
                command.extend(["-af", speech_filter])
        command.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "20",
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                str(output_path),
            ]
        )
        self._run(command)

    @staticmethod
    def _normalize_segments(segments: list) -> list:
        normalized = []
        for segment in segments:
            start = round(float(segment["start"]), 3)
            end = round(float(segment["end"]), 3)
            if start < 0 or end <= start:
                raise ValueError("Invalid export segment")
            normalized.append(
                {
                    "start": start,
                    "end": end,
                    "comment": str(segment.get("comment", "")),
                }
            )
        return normalized

    @staticmethod
    def _build_timeline(
        segments: list,
        duration: float,
        processing_options: dict,
    ) -> list:
        if not segments:
            return [
                {
                    "start": 0.0,
                    "end": round(duration, 3),
                    "speed": 1,
                    "kind": "selected",
                    "comment": "",
                }
            ]
        if not processing_options.get("speed_up_excluded"):
            return [
                {
                    **segment,
                    "speed": 1,
                    "kind": "selected",
                }
                for segment in segments
            ]

        selected = sorted(segments, key=lambda item: item["start"])
        merged = []
        for segment in selected:
            if merged and segment["start"] <= merged[-1]["end"]:
                merged[-1]["end"] = max(merged[-1]["end"], segment["end"])
                if segment["comment"]:
                    merged[-1]["comment"] = " / ".join(
                        filter(None, [merged[-1]["comment"], segment["comment"]])
                    )
            else:
                merged.append({**segment})

        timeline = []
        cursor = 0.0
        excluded_speed = int(processing_options.get("excluded_speed", 2))
        for segment in merged:
            if segment["start"] > cursor:
                timeline.append(
                    {
                        "start": round(cursor, 3),
                        "end": segment["start"],
                        "speed": excluded_speed,
                        "kind": "excluded",
                        "comment": "",
                    }
                )
            timeline.append(
                {
                    **segment,
                    "speed": 1,
                    "kind": "selected",
                }
            )
            cursor = max(cursor, segment["end"])
        if cursor < duration:
            timeline.append(
                {
                    "start": round(cursor, 3),
                    "end": round(duration, 3),
                    "speed": excluded_speed,
                    "kind": "excluded",
                    "comment": "",
                }
            )
        return [
            item
            for item in timeline
            if item["end"] - item["start"] >= 0.01
        ]

    @staticmethod
    def _map_subtitles(subtitles: list, timeline: list) -> list:
        if not subtitles:
            return []

        mapped = []
        timeline_offset = 0.0
        for edit_segment in timeline:
            speed = edit_segment.get("speed", 1)
            for subtitle in subtitles:
                overlap_start = max(subtitle["start"], edit_segment["start"])
                overlap_end = min(subtitle["end"], edit_segment["end"])
                if overlap_end <= overlap_start:
                    continue
                mapped.append(
                    {
                        "id": len(mapped) + 1,
                        "start": timeline_offset
                        + (overlap_start - edit_segment["start"]) / speed,
                        "end": timeline_offset
                        + (overlap_end - edit_segment["start"]) / speed,
                        "text": subtitle["text"],
                    }
                )
            timeline_offset += (
                edit_segment["end"] - edit_segment["start"]
            ) / speed
        return mapped

    def _probe_media(self, source_path: Path) -> dict:
        command = [
            self.settings.ffprobe_binary,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type",
            "-of",
            "json",
            str(source_path),
        ]
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(exc.stderr.strip() or "FFprobe failed") from exc
        payload = json.loads(result.stdout)
        duration = float(payload.get("format", {}).get("duration") or 0)
        if duration <= 0:
            raise ValueError("Video duration could not be detected")
        return {
            "duration": duration,
            "has_audio": any(
                stream.get("codec_type") == "audio"
                for stream in payload.get("streams", [])
            ),
        }

    @staticmethod
    def _run(command: list, cwd: Path = None) -> None:
        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                cwd=cwd,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(exc.stderr.strip() or "FFmpeg export failed") from exc
