import json
import subprocess
import wave
from pathlib import Path

import numpy as np

from app.core.config import get_settings


class SpeechAnalysisService:
    """Local speech-first analysis with acoustic speaker clustering."""

    def __init__(self):
        self.settings = get_settings()
        self._model = None

    def analyze(
        self,
        file_path: str,
        output_dir: Path,
        upload_id: str,
        language: str = None,
    ) -> dict:
        output_dir.mkdir(parents=True, exist_ok=True)
        speech_path = output_dir / f"{upload_id}_speech.wav"
        self._extract_speech_audio(file_path, speech_path)
        model = self._get_model()
        source_segments, info = model.transcribe(
            str(speech_path),
            language=language,
            vad_filter=True,
            vad_parameters={
                "min_speech_duration_ms": 300,
                "min_silence_duration_ms": 450,
            },
            beam_size=5,
            word_timestamps=True,
            condition_on_previous_text=False,
        )
        raw_segments = list(source_segments)
        if not raw_segments:
            raise ValueError("No spoken voice was detected in the uploaded video")

        sample_rate, samples = self._read_wave(speech_path)
        analyzed = []
        features = []
        for index, segment in enumerate(raw_segments, start=1):
            text = segment.text.strip()
            if not text:
                continue
            audio = samples[
                max(0, int(segment.start * sample_rate)):
                min(len(samples), int(segment.end * sample_rate))
            ]
            feature, music_score = self._acoustic_features(audio, sample_rate, text)
            features.append(feature)
            analyzed.append(
                {
                    "id": index,
                    "start": round(segment.start, 3),
                    "end": round(segment.end, 3),
                    "text": text,
                    "music_score": round(music_score, 3),
                    "content_type": "music" if music_score >= 0.72 else "speech",
                }
            )
        if not analyzed:
            raise ValueError("No spoken voice was detected in the uploaded video")

        speech_indexes = [
            index
            for index, item in enumerate(analyzed)
            if item["content_type"] == "speech"
        ]
        if not speech_indexes:
            speech_index = min(
                range(len(analyzed)),
                key=lambda index: analyzed[index]["music_score"],
            )
            analyzed[speech_index]["content_type"] = "speech"
            speech_indexes = [speech_index]
        labels = self._cluster_speakers(
            [features[index] for index in speech_indexes]
        )
        for item in analyzed:
            item["speaker_id"] = "music"
        for index, label in zip(speech_indexes, labels):
            analyzed[index]["speaker_id"] = f"speaker-{label + 1}"

        speakers = self._build_speakers(
            analyzed,
            file_path,
            output_dir,
            upload_id,
        )
        payload = {
            "upload_id": upload_id,
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "pipeline": [
                "speech_enhancement",
                "voice_activity_detection",
                "speech_music_classification",
                "speaker_clustering",
            ],
            "speakers": speakers,
            "segments": analyzed,
        }
        analysis_path = output_dir / f"{upload_id}_analysis.json"
        analysis_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return payload

    def create_subtitles(
        self,
        analysis: dict,
        selected_speakers: list[str],
    ) -> list:
        selected = set(selected_speakers)
        segments = [
            {
                "id": index,
                "start": item["start"],
                "end": item["end"],
                "text": item["text"],
                "speaker_id": item["speaker_id"],
            }
            for index, item in enumerate(
                (
                    item
                    for item in analysis.get("segments", [])
                    if item.get("content_type") == "speech"
                    and item.get("speaker_id") in selected
                ),
                start=1,
            )
        ]
        if not segments:
            raise ValueError("Select at least one spoken-voice speaker")
        return segments

    def _get_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError(
                    "faster-whisper is not installed in the backend environment"
                ) from exc
            self._model = WhisperModel(
                self.settings.whisper_model,
                device=self.settings.device,
                compute_type="int8" if self.settings.device == "cpu" else "float16",
                download_root=self.settings.whisper_path,
            )
        return self._model

    def _extract_speech_audio(self, source: str, target: Path) -> None:
        command = [
            self.settings.ffmpeg_binary,
            "-y",
            "-i",
            source,
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-af",
            (
                "highpass=f=80,lowpass=f=7600,"
                "afftdn=nf=-25,acompressor=threshold=-18dB:ratio=3:"
                "attack=20:release=250"
            ),
            "-c:a",
            "pcm_s16le",
            str(target),
        ]
        self._run(command)

    @staticmethod
    def _read_wave(path: Path) -> tuple[int, np.ndarray]:
        with wave.open(str(path), "rb") as source:
            sample_rate = source.getframerate()
            frames = source.readframes(source.getnframes())
        return sample_rate, np.frombuffer(frames, dtype=np.int16).astype(np.float32)

    @staticmethod
    def _acoustic_features(
        audio: np.ndarray,
        sample_rate: int,
        text: str,
    ) -> tuple[np.ndarray, float]:
        if len(audio) < 512:
            return np.zeros(34, dtype=np.float32), 0.5
        audio = audio / max(1.0, float(np.max(np.abs(audio))))
        frame_size = 512
        hop = 256
        frame_count = max(1, 1 + (len(audio) - frame_size) // hop)
        frames = np.stack(
            [
                np.pad(
                    audio[index * hop:index * hop + frame_size],
                    (0, max(0, frame_size - len(audio[index * hop:index * hop + frame_size]))),
                )[:frame_size]
                for index in range(frame_count)
            ]
        )
        frames *= np.hanning(frame_size)
        spectrum = np.abs(np.fft.rfft(frames, axis=1)) + 1e-7
        log_spectrum = np.log1p(spectrum)
        bands = np.array_split(log_spectrum[:, 2:], 16, axis=1)
        band_energy = np.stack([band.mean(axis=1) for band in bands], axis=1)
        band_mean = band_energy.mean(axis=0)
        band_std = band_energy.std(axis=0)
        feature = np.concatenate([band_mean, band_std]).astype(np.float32)
        feature = (feature - feature.mean()) / (feature.std() + 1e-6)

        dominant = spectrum[:, 2:].max(axis=1) / spectrum[:, 2:].sum(axis=1)
        tonal = float(np.clip((dominant.mean() - 0.04) / 0.12, 0, 1))
        dominant_bins = np.argmax(spectrum[:, 2:], axis=1)
        pitch_stability = 1 - float(
            np.clip(np.std(dominant_bins) / max(1, spectrum.shape[1] * 0.2), 0, 1)
        )
        tokens = [token for token in text.replace(",", " ").split() if token]
        repetition = (
            1 - len(set(tokens)) / len(tokens)
            if len(tokens) >= 4
            else 0
        )
        duration_bonus = min(1.0, len(audio) / sample_rate / 8)
        music_score = (
            0.38 * tonal
            + 0.28 * pitch_stability
            + 0.2 * repetition
            + 0.14 * duration_bonus
        )
        return feature, float(np.clip(music_score, 0, 1))

    @staticmethod
    def _cluster_speakers(features: list[np.ndarray]) -> list[int]:
        if not features:
            return []
        if len(features) < 3:
            return [0] * len(features)
        clusters: list[list[np.ndarray]] = []
        labels = []
        for feature in features:
            normalized = feature / (np.linalg.norm(feature) + 1e-6)
            if not clusters:
                clusters.append([normalized])
                labels.append(0)
                continue
            centroids = [
                np.mean(cluster, axis=0)
                / (np.linalg.norm(np.mean(cluster, axis=0)) + 1e-6)
                for cluster in clusters
            ]
            distances = [1 - float(np.dot(normalized, center)) for center in centroids]
            nearest = int(np.argmin(distances))
            if distances[nearest] > 0.16 and len(clusters) < 4:
                clusters.append([normalized])
                labels.append(len(clusters) - 1)
            else:
                clusters[nearest].append(normalized)
                labels.append(nearest)
        return labels

    def _build_speakers(
        self,
        segments: list[dict],
        source_path: str,
        output_dir: Path,
        upload_id: str,
    ) -> list[dict]:
        grouped: dict[str, list[dict]] = {}
        for segment in segments:
            grouped.setdefault(segment["speaker_id"], []).append(segment)
        speakers = []
        speech_number = 0
        for speaker_id, items in grouped.items():
            is_music = speaker_id == "music"
            if not is_music:
                speech_number += 1
            representative = max(items, key=lambda item: item["end"] - item["start"])
            preview_path = output_dir / f"{upload_id}_{speaker_id}.mp3"
            self._run(
                [
                    self.settings.ffmpeg_binary,
                    "-y",
                    "-ss",
                    str(representative["start"]),
                    "-t",
                    str(min(5, representative["end"] - representative["start"])),
                    "-i",
                    source_path,
                    "-vn",
                    "-ac",
                    "1",
                    "-c:a",
                    "libmp3lame",
                    "-b:a",
                    "96k",
                    str(preview_path),
                ]
            )
            speakers.append(
                {
                    "speaker_id": speaker_id,
                    "label": "노래/음악 후보" if is_music else f"화자 {speech_number}",
                    "content_type": "music" if is_music else "speech",
                    "segment_count": len(items),
                    "duration": round(
                        sum(item["end"] - item["start"] for item in items),
                        3,
                    ),
                    "selected": not is_music,
                    "preview": preview_path.name,
                }
            )
        return speakers

    @staticmethod
    def _run(command: list[str]) -> None:
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(exc.stderr.strip() or "Audio analysis failed") from exc
